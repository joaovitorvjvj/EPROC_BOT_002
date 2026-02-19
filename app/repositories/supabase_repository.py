import httpx
from app.core.config import settings
from app.core.logger import logger
from typing import Optional, Dict, Any

class SupabaseRepository:
    def __init__(self):
        self.url = f"{settings.SUPABASE_URL}/rest/v1"
        self.headers = {
            "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    async def create_process(self, data: dict) -> str:
        async with httpx.AsyncClient() as client:
            try:
                # Adicionamos o status inicial antes de salvar
                data["status"] = "INICIADO"
                data["canvas_data"] = {}
                
                response = await client.post(f"{self.url}/processes", json=data, headers=self.headers)
                response.raise_for_status()
                return response.json()[0]["id"]
            except Exception as e:
                logger.error(f"Erro Supabase: {str(e)}")
                raise e

    async def get_process_by_id(self, process_id: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.url}/processes?id=eq.{process_id}", headers=self.headers)
            res = response.json()
            return res[0] if res else None

    async def update_process(self, process_id: str, data: dict):
        async with httpx.AsyncClient() as client:
            response = await client.patch(f"{self.url}/processes?id=eq.{process_id}", json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()[0]