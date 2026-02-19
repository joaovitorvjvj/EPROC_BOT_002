from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
# IMPORT CORRIGIDO AQUI:
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate 
from app.core.config import settings

# 1. Definição da estrutura técnica de uma atividade
class ActivityNodeSchema(BaseModel):
    task: str = Field(description="Ação realizada usando Verbo + Objeto (ex: Analisar Processo)")
    actor: str = Field(description="Quem executa a tarefa (ex: Gestor, RH, Solicitante)")
    system: Optional[str] = Field(description="Sistema utilizado, se mencionado (ex: SGPe, SIGEF)")
    is_gateway: bool = Field(description="Verdadeiro se houver uma decisão, aprovação ou escolha")
    negative_flow: Optional[str] = Field(description="O que acontece se a decisão for negativa ou houver erro")

# 2. Schema de saída para a IA
class CanvasExtraction(BaseModel):
    activities: List[ActivityNodeSchema] = Field(description="Lista de atividades encontradas no texto")
    missing_info_reason: Optional[str] = Field(description="Breve nota se os dados parecerem confusos ou incompletos")

class ExtractionService:
    def __init__(self):
        # Usamos o modelo que validamos com cota (2.5-flash)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GEMINI_API_KEY
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
            
            # Executa a extração
            result = await chain.ainvoke({"text": user_text})
            return result
            
        except Exception:
            # Fallback caso a IA não consiga estruturar (evita travar o chat)
            return CanvasExtraction(activities=[], missing_info_reason="Não foi possível estruturar os dados.")