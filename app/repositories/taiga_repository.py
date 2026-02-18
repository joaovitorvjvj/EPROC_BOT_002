import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logger import logger

class TaigaRepository:
    def __init__(self):
        self.url = settings.TAIGA_URL
        self.headers = {
            "Authorization": f"Bearer {settings.TAIGA_API_TOKEN}",
            "Content-Type": "application/json",
            "x-disable-pagination": "True"
        }

    async def create_card(self, title: str, description: str) -> Dict[str, Any]:
        """Cria uma User Story no Taiga representando o processo."""
        payload = {
            "project": settings.TAIGA_PROJECT_ID,
            "subject": title,
            "description": description,
            "assigned_to": settings.TAIGA_USER_ID,
            "tags": ["PMAS", "Automated"]
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.url}/userstories",
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                logger.info(f"Card criado no Taiga: ID {data.get('id')}")
                return data
            except Exception as e:
                logger.error(f"Erro ao criar card no Taiga: {str(e)}")
                raise e

    async def add_attachment(self, card_id: int, file_path: str):
        """Anexa arquivos ao card do Taiga."""
        async with httpx.AsyncClient() as client:
            try:
                with open(file_path, "rb") as f:
                    files = {"attached_file": f}
                    data = {
                        "project": settings.TAIGA_PROJECT_ID,
                        "object_id": card_id,
                        "from_comment": False
                    }
                    headers = self.headers.copy()
                    headers.pop("Content-Type")
                    
                    response = await client.post(
                        f"{self.url}/userstories/attachments",
                        data=data,
                        files=files,
                        headers=headers
                    )
                    return response.json()
            except Exception as e:
                logger.error(f"Erro ao anexar arquivo no Taiga: {str(e)}")
                return None