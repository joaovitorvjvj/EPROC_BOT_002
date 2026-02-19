from fastapi import APIRouter, HTTPException, status
from app.schemas.process import ProcessCreate, ProcessRead
from app.services.process_service import ProcessService

router = APIRouter(prefix="/process", tags=["Processes"])
service = ProcessService()

@router.post("/start", response_model=ProcessRead, status_code=status.HTTP_201_CREATED)
async def start(payload: ProcessCreate):
    pid = await service.start_process(payload.model_dump())
    return await service.supabase.get_process_by_id(pid)

@router.post("/{process_id}/finalize")
async def finalize(process_id: str):
    return await service.finalize_mapping(process_id)

@router.get("/{process_id}", response_model=ProcessRead)
async def get_one(process_id: str):
    res = await service.supabase.get_process_by_id(process_id)
    if not res: raise HTTPException(status_code=404)
    return res