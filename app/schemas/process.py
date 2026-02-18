from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ProcessBase(BaseModel):
    name: str = Field(..., example="Mapeamento de Compras")
    sector: str = Field(..., example="Departamento Administrativo")
    secretariat: str = Field(..., example="Secretaria de Educação")
    owner: str = Field(..., example="João Silva")
    requester_name: str = Field(..., example="Maria Oliveira")
    requester_email: EmailStr
    mode: str = Field(..., pattern="^(AUTOMATIC|SPECIALIST)$")

class ProcessCreate(ProcessBase):
    pass

class ProcessUpdate(BaseModel):
    status: Optional[str] = None
    canvas_data: Optional[Dict[str, Any]] = None
    taiga_card_id: Optional[int] = None
    bpmn_path: Optional[str] = None
    docx_path: Optional[str] = None
    availability_dates: Optional[List[str]] = None

class ProcessRead(ProcessBase):
    id: UUID
    status: str
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True