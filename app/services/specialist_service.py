from app.repositories.supabase_repository import SupabaseRepository

class SpecialistService:
    def __init__(self):
        self.repo = SupabaseRepository()

    async def find_by_sector(self, sector: str, secretariat: str):
        # Busca um especialista no banco para o setor específico
        return await self.repo.find_specialist_by_sector(sector, secretariat)