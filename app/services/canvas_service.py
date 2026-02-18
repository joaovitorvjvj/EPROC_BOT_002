from typing import Dict, Any
from app.repositories.supabase_repository import SupabaseRepository
from app.core.logger import logger

class CanvasService:
    def __init__(self):
        self.repo = SupabaseRepository()

    async def update_canvas_incremental(self, process_id: str, new_data: Dict[str, Any]):
        """
        Lógica para atualizar o canvas sem apagar dados anteriores.
        """
        try:
            # 1. Recupera o processo atual para não perder dados já salvos
            current_process = await self.repo.get_process_by_id(process_id)
            if not current_process:
                return None

            # 2. Mescla o canvas antigo com as novas informações
            existing_canvas = current_process.get("canvas_data") or {}
            updated_canvas = {**existing_canvas, **new_data}

            # 3. Salva a versão atualizada no banco
            result = await self.repo.update_process(process_id, {"canvas_data": updated_canvas})
            logger.info(f"Canvas do processo {process_id} atualizado com sucesso.")
            return result
        except Exception as e:
            logger.error(f"Erro ao atualizar canvas incremental: {str(e)}")
            raise e