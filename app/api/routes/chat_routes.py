from fastapi import APIRouter, Body, HTTPException
from app.services.chat_service import ChatService
from pydantic import BaseModel
from app.core.logger import logger

router = APIRouter(tags=["Chat"])
chat_service = ChatService()

class ChatRequest(BaseModel):
    message: str
    # O session_id pode ser o ID do processo no Supabase
    process_id: str = None 

@router.post("/chat")
async def chat_endpoint(payload: ChatRequest):
    try:
        # Se não houver um processo ativo, iniciamos um automaticamente
        # (Isso garante que o site nunca trave)
        current_pid = payload.process_id
        
        if not current_pid:
            logger.info("🆕 Iniciando novo mapeamento via Chat do Site...")
            current_pid = await chat_service.start_new_mapping("Processo via Chat Online")

        # Chama o serviço que: Extrai dados -> Salva no Banco -> Gera Resposta
        # Passamos uma lista vazia para o histórico por enquanto (ou podemos buscar no banco)
        response_text = await chat_service.get_next_question(
            chat_history=[], 
            user_input=payload.message,
            process_id=current_pid
        )
        
        return {
            "response": response_text,
            "process_id": current_pid
        }

    except Exception as e:
        logger.error(f"❌ Erro na rota de chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno no assistente.")