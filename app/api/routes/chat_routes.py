from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.logger import logger
from app.services.chat_service import ChatService

router = APIRouter(tags=["Chat"])
chat_service = ChatService()

# Mapeia uma sessão de cliente para process_id para evitar novo INSERT a cada interação
session_process_map: dict[str, str] = {}


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    process_id: Optional[str] = None
    client_session_id: Optional[str] = None
    chat_history: Optional[List[ChatMessage]] = None


@router.post("/chat")
async def chat_endpoint(payload: ChatRequest):
    try:
        current_pid = payload.process_id

        if not current_pid and payload.client_session_id:
            current_pid = session_process_map.get(payload.client_session_id)

        if not current_pid:
            logger.info("🆕 Iniciando novo mapeamento via Chat do Site...")
            current_pid = await chat_service.start_new_mapping("Processo via Chat Online")

        if payload.client_session_id:
            session_process_map[payload.client_session_id] = current_pid

        parsed_history = [message.model_dump() for message in payload.chat_history] if payload.chat_history else None

        response_text = await chat_service.get_next_question(
            user_input=payload.message,
            process_id=current_pid,
            chat_history=parsed_history,
        )

        return {
            "response": response_text,
            "process_id": current_pid,
            "client_session_id": payload.client_session_id,
        }

    except Exception as e:
        logger.error(f"❌ Erro na rota de chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno no assistente.")
