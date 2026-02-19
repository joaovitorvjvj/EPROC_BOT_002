from app.repositories.supabase_repository import SupabaseRepository
from app.repositories.taiga_repository import TaigaRepository
from app.services.bpmn_service import BPMNService
from app.services.notification_service import NotificationService
from app.core.logger import logger

class ProcessService:
    def __init__(self):
        self.supabase = SupabaseRepository()
        self.taiga = TaigaRepository()
        self.bpmn_gen = BPMNService()
        self.notifier = NotificationService()

    async def start_process(self, payload: dict):
        try:
            # 1. Banco
            process_id = await self.supabase.create_process(payload)
            # 2. Taiga
            card = await self.taiga.create_card(payload['name'], f"Setor: {payload['sector']}")
            if card:
                await self.supabase.update_process(process_id, {"taiga_card_id": str(card['id'])})
            return process_id
        except Exception as e:
            logger.error(f"Falha ao iniciar processo: {e}")
            raise e

    async def finalize_mapping(self, process_id: str):
        process = await self.supabase.get_process_by_id(process_id)
        # Gera o BPMN via IA
        path = await self.bpmn_gen.generate_bpmn(process_id, process.get("canvas_data", {}))
        # Notifica (Mock/Emulador)
        await self.notifier.send_whatsapp_message(process['requester_email'], "Mapeamento concluído!")
        await self.notifier.send_whatsapp_file(process['requester_email'], path, "Seu BPMN está pronto.")
        # Finaliza status
        await self.supabase.update_process(process_id, {"status": "FINALIZADO"})
        return {"id": process_id, "status": "Concluído"}