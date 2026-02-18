from app.repositories.supabase_repository import SupabaseRepository
from app.repositories.taiga_repository import TaigaRepository
from app.services.bpmn_service import BPMNService
from app.services.docx_service import DocxService
from app.core.logger import logger
from typing import Dict, Any

class ProcessService:
    def __init__(self):
        # Repositórios
        self.supabase = SupabaseRepository()
        self.taiga = TaigaRepository()
        
        # Serviços de Artefatos
        self.bpmn_gen = BPMNService()
        self.docx_gen = DocxService()

    async def start_process(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquestra a criação inicial: Supabase -> Taiga -> Atualização de Status.
        """
        try:
            # 1. Salva no Supabase (nosso banco oficial)
            process_data["status"] = "INITIALIZED"
            new_process = await self.supabase.create_process(process_data)
            process_id = new_process["id"]

            # 2. Cria o Card no Taiga para gestão visual
            taiga_desc = (
                f"**Solicitante:** {new_process['requester_name']}\n"
                f"**Setor:** {new_process['sector']}\n"
                f"**Modo:** {new_process['mode']}\n"
                f"**ID Sistema:** {process_id}"
            )
            
            taiga_card = await self.taiga.create_card(
                title=f"Mapeamento: {new_process['name']}",
                description=taiga_desc
            )

            # 3. Vincula o ID do Taiga ao nosso registro no Supabase
            updated_process = await self.supabase.update_process(
                process_id, 
                {"taiga_card_id": taiga_card["id"]}
            )

            logger.info(f"Orquestração inicial concluída para o processo {process_id}")
            return updated_process

        except Exception as e:
            logger.error(f"Falha na orquestração de início de processo: {str(e)}")
            raise e

    async def finalize_mapping(self, process_id: str) -> Dict[str, Any]:
        """
        Gera os arquivos finais, salva no storage e atualiza o Taiga e Supabase.
        """
        try:
            # 1. Busca os dados completos do processo
            process = await self.supabase.get_process_by_id(process_id)
            if not process or not process.get("canvas_data"):
                raise ValueError("Dados do canvas insuficientes para finalização.")

            # 2. Gera os artefatos (BPMN e DOCX)
            bpmn_path = await self.bpmn_gen.generate_bpmn(process_id, process["canvas_data"])
            docx_path = await self.docx_gen.generate_document(process)

            # 3. Atualiza o card no Taiga com os anexos
            card_id = process.get("taiga_card_id")
            if card_id:
                await self.taiga.add_attachment(card_id, bpmn_path)
                await self.taiga.add_attachment(card_id, docx_path)

            # 4. Atualiza o banco com os caminhos dos arquivos e status final
            update_data = {
                "bpmn_path": bpmn_path,
                "docx_path": docx_path,
                "status": "COMPLETED"
            }
            
            final_process = await self.supabase.update_process(process_id, update_data)
            logger.info(f"Processo {process_id} finalizado com sucesso.")
            return final_process

        except Exception as e:
            logger.error(f"Erro ao finalizar mapeamento {process_id}: {str(e)}")
            raise e