from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Agora o caminho vai bater com a realidade física do arquivo
from app.api.routes.chat_routes import router as chat_router

app = FastAPI(title="PMAS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro da rota
app.include_router(chat_router)

@app.get("/")
async def root():
    return {"status": "online", "message": "PMAS corrigido!"}