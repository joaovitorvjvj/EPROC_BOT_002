from google import genai
from app.core.config import settings
from app.core.logger import logger

class AIService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        # Usamos o único modelo que validamos com sucesso no seu ambiente
        self.model_id = "models/gemini-2.5-flash" 

    async def generate_bpmn_xml(self, process_name: str, activities_list: list) -> str:
        try:
            # Prompt ultra-curto para economizar tokens e cota
            prompt = f"""Generate a valid BPMN 2.0 XML for Camunda.
            Process: {process_name}
            Activities: {activities_list}
            Rules: Use Lanes (DIRETORIA, OPERACIONAL), avoid overlaps, return ONLY XML."""

            logger.info(f"🤖 Chamando IA ({self.model_id}) para o processo: {process_name}")
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            
            # Limpeza rápida
            xml_output = response.text.strip()
            if "```xml" in xml_output:
                xml_output = xml_output.split("```xml")[1].split("```")[0].strip()
            elif "```" in xml_output:
                xml_output = xml_output.split("```")[1].split("```")[0].strip()
            
            return xml_output

        except Exception as e:
            logger.error(f"❌ Erro na IA: {str(e)}")
            # Fallback: Se a IA falhar, retornamos um XML básico para o sistema não travar
            return self._get_fallback_xml(process_name)

    def _get_fallback_xml(self, name):
        """Retorna um XML básico caso a cota estoure"""
        return f'<?xml version="1.0" encoding="UTF-8"?><bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" targetNamespace="http://bpmn.io/schema/bpmn"><bpmn:process id="Process_1" isExecutable="false"><bpmn:startEvent id="StartEvent_1" name="Erro de Cota: {name}" /></bpmn:process></bpmn:definitions>'