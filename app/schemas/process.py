from pydantic import BaseModel, EmailStr, Field, ConfigDict
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

class ProcessRead(ProcessBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: str
    created_at: datetime
    # Opcionais na leitura para evitar erros com dados legados ou nulos
    secretariat: Optional[str] = None
    owner: Optional[str] = None
    requester_name: Optional[str] = None
    mode: Optional[str] = None