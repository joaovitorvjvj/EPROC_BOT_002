from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.process import ProcessCreate, ProcessRead, ProcessUpdate
from app.schemas.canvas import ProcessCanvas
from app.services.process_service import ProcessService
from app.core.logger import logger

router = APIRouter(prefix="/process", tags=["Processes"])
process_service = ProcessService()

@router.post("/start", response_model=ProcessRead, status_code=status.HTTP_201_CREATED)
async def start_new_process(payload: ProcessCreate):
    """
    Inicia um novo mapeamento, registra no banco e cria card no Taiga.
    """
    try:
        return await process_service.start_process(payload.model_dump())
    except Exception as e:
        logger.error(f"Erro na rota start_process: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao iniciar processo.")

@router.post("/{process_id}/canvas", status_code=status.HTTP_200_OK)
async def update_process_canvas(process_id: str, canvas_data: ProcessCanvas):
    """
    Atualiza os dados técnicos do mapeamento (Canvas) de forma incremental.
    """
    from app.services.canvas_service import CanvasService
    canvas_service = CanvasService()
    
    result = await canvas_service.update_canvas_incremental(process_id, canvas_data.model_dump())
    if not result:
        raise HTTPException(status_code=404, detail="Processo não encontrado.")
    return {"message": "Canvas atualizado com sucesso", "data": result}

@router.post("/{process_id}/finalize", status_code=status.HTTP_200_OK)
async def finalize_process(process_id: str):
    """
    Encerra o mapeamento, gera os arquivos BPMN/DOCX e anexa ao Taiga.
    """
    try:
        return await process_service.finalize_mapping(process_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Erro na rota finalize: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao gerar documentos finais.")

@router.get("/{process_id}", response_model=ProcessRead)
async def get_process_details(process_id: str):
    """
    Recupera todos os dados de um processo específico.
    """
    result = await process_service.supabase.get_process_by_id(process_id)
    if not result:
        raise HTTPException(status_code=404, detail="Processo não encontrado.")
    return result