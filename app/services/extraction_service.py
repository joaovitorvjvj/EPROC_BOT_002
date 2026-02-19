from typing import List, Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from app.core.config import settings


class ActivityNodeSchema(BaseModel):
    task: str = Field(description="Ação realizada usando Verbo + Objeto (ex: Analisar Processo)")
    actor: str = Field(description="Quem executa a tarefa (ex: Gestor, RH, Solicitante)")
    system: Optional[str] = Field(description="Sistema utilizado, se mencionado (ex: SGPe, SIGEF)")
    is_gateway: bool = Field(description="Verdadeiro se houver uma decisão, aprovação ou escolha")
    negative_flow: Optional[str] = Field(description="O que acontece se a decisão for negativa ou houver erro")


class CanvasExtraction(BaseModel):
    activities: List[ActivityNodeSchema] = Field(description="Lista de atividades encontradas no texto")
    missing_info_reason: Optional[str] = Field(description="Breve nota se os dados parecerem confusos ou incompletos")


class ExtractionService:
    def __init__(self):
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0,
        )
        self.parser = PydanticOutputParser(pydantic_object=CanvasExtraction)

    async def extract_data(self, user_text: str) -> CanvasExtraction:
        """
        Lê o texto do usuário e transforma em dados estruturados (JSON).
        """
        try:
            prompt = PromptTemplate(
                template="Analise o texto sobre processos e extraia as atividades estruturadas.\n{format_instructions}\nTexto: {text}",
                input_variables=["text"],
                partial_variables={"format_instructions": self.parser.get_format_instructions()},
            )

            chain = prompt | self.llm | self.parser
            result = await chain.ainvoke({"text": user_text})
            return result

        except Exception:
            return CanvasExtraction(activities=[], missing_info_reason="Não foi possível estruturar os dados.")
