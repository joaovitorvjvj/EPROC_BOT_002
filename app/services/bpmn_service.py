import os
from app.core.config import settings
from app.core.logger import logger
from app.services.ai_service import AIService

class BPMNService:
    def __init__(self):
        self.output_dir = os.path.join(settings.STORAGE_PATH, "bpmn")
        self.ai_service = AIService()

    async def generate_bpmn(self, process_id: str, canvas_data: dict) -> str:
        """
        Orquestra a geração do BPMN usando Inteligência Artificial e o prompt de raias.
        """
        try:
            activities = canvas_data.get("macroactivities", [])
            process_name = canvas_data.get("name", "Processo Sem Nome")

            logger.info(f"Solicitando geração de BPMN via IA para o processo {process_id}...")

            # 1. Chama o Gemini para gerar o XML inteligente com base no seu prompt
            xml_content = await self.ai_service.generate_bpmn_xml(process_name, activities)

            # 2. Define o caminho do arquivo
            file_path = os.path.join(self.output_dir, f"{process_id}.bpmn")

            # 3. Salva o conteúdo gerado pela IA no arquivo físico
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(xml_content)

            logger.info(f"BPMN Hierárquico gerado com sucesso em: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Falha ao gerar BPMN via IA: {str(e)}")
            # Fallback ou Raise conforme necessidade
            raise e