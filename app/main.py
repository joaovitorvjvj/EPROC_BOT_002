from fastapi import FastAPI
from app.api.routes import process_routes
from app.services.storage_service import StorageService
from app.core.config import settings
from app.core.logger import logger

app = FastAPI(
    title=settings.SYSTEM_NAME,
    description="Sistema de Automação de Mapeamento de Processos Organizacionais",
    version="1.0.0"
)

# Inicialização de infraestrutura
@app.on_event("startup")
async def startup_event():
    logger.info(f"Iniciando {settings.SYSTEM_NAME}...")
    storage = StorageService()
    storage.ensure_dirs()
    logger.info("Estrutura de diretórios verificada/criada.")

# Inclusão das rotas
app.include_router(process_routes.router)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "system": settings.SYSTEM_NAME}