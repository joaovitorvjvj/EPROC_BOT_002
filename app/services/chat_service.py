from typing import Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.core.config import settings
from app.core.logger import logger
from app.repositories.process_repository import ProcessRepository
from app.services.extraction_service import ExtractionService


class ChatService:
    def __init__(self):
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.2,
        )

        self.repo = ProcessRepository()
        self.extractor = ExtractionService()

        # Memória em runtime por processo (evita amnésia entre mensagens da mesma sessão)
        self.chat_memory: Dict[str, List[dict]] = {}

        self.system_prompt = """
        Você é o Analista PMAS, especialista em BPMN 2.0 e Instrução de Trabalho (IT) do Governo de SC.
        Seu objetivo é extrair dados para preencher um Canvas de Processo e uma IT.

        ESTRATÉGIA DE CONVERSA:
        1. Identificação: Comece pelo Nome e Objetivo do processo.
        2. Gateways (Decisões): Sempre que houver uma 'Análise', 'Aprovação' ou 'Validação', pergunte obrigatoriamente:
           "E se for negado/reprovado? Para onde o processo volta ou ele encerra?".
        3. Detalhamento: Pergunte sobre Atores (quem faz) e Sistemas (onde faz - ex: SGPe, SIGEF).
        4. Fatiagem: Não peça tudo de uma vez. Vá passo a passo.

        ESTILO:
        - Use emojis (🚀, 📝, ⚠️).
        - Seja direto e amigável.
        - Não se reapresente em todas as respostas.
        - Se o usuário der uma lista, confirme os passos antes de avançar.

        Sinalize [FINALIZADO] apenas quando tiver coletado: Objetivo, Atividades (com decisões), Atores e Sistemas.
        """

    async def get_next_question(
        self,
        user_input: str,
        process_id: Optional[str] = None,
        chat_history: Optional[list] = None,
    ):
        try:
            extracted = await self.extractor.extract_data(user_input)

            if process_id and extracted.activities:
                next_step_order = self.repo.get_next_step_order(process_id)

                for activity in extracted.activities:
                    node_data = {
                        "step_order": next_step_order,
                        "actor": activity.actor,
                        "activity": activity.task,
                        "system": activity.system,
                        "is_gateway": activity.is_gateway,
                        "condition_text": activity.negative_flow if activity.is_gateway else None,
                    }
                    self.repo.add_activity_node(process_id, node_data)
                    logger.info(f"✅ Nodo salvo no banco: {activity.task} (ordem {next_step_order})")
                    next_step_order += 1

            messages = [SystemMessage(content=self.system_prompt)]
            source_history = chat_history if chat_history else self.chat_memory.get(process_id or "", [])

            for msg in source_history:
                if not isinstance(msg, dict):
                    continue

                role = msg.get("role", "user")
                content = msg.get("content", "")
                if not content:
                    continue

                if role == "assistant":
                    messages.append(AIMessage(content=content))
                else:
                    messages.append(HumanMessage(content=content))

            messages.append(HumanMessage(content=user_input))

            response = await self.llm.ainvoke(messages)
            response_text = response.content if isinstance(response.content, str) else str(response.content)

            if process_id:
                process_memory = self.chat_memory.setdefault(process_id, [])
                process_memory.append({"role": "user", "content": user_input})
                process_memory.append({"role": "assistant", "content": response_text})

            return response_text

        except Exception as e:
            logger.error(f"Erro no ChatService: {str(e)}")
            return "⚠️ Tive um problema ao processar sua resposta. Pode repetir o último passo do processo?"

    async def start_new_mapping(self, process_name: str):
        new_process = self.repo.create_process(process_name)
        if not new_process:
            raise RuntimeError("Não foi possível criar processo no banco.")
        return new_process["id"]
