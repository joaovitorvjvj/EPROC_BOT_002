from pydantic import BaseModel
from typing import List, Optional

class ProcessCanvas(BaseModel):
    objective: str = ""
    scope: str = ""
    start_event: str = ""
    end_event: str = ""
    inputs: List[str] = []
    outputs: List[str] = []
    macroactivities: List[str] = []
    executors: List[str] = []
    systems: List[str] = []
    frequency: str = ""
    issues: str = ""
    business_rules: str = ""
    exceptions: str = ""
    controls: str = ""
    legal_basis: str = ""
    kpis: str = ""
    risks: str = ""
    improvements: str = ""