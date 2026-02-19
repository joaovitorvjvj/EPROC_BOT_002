from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import settings
from app.core.logger import logger
from app.repositories.process_repository import ProcessRepository
from app.services.extraction_service import ExtractionService

class ChatService:
    def __init__(self):
        # Inicializa o LLM principal para conversação
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GEMINI_API_KEY
        )
        
        # Inicializa serviços auxiliares
        self.repo = ProcessRepository()
        self.extractor = ExtractionService()
        
        # Prompt Mestre focado em BPMN e IT (Instrução de Trabalho)
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
        - Seja direto mas amigável.
        - Se o usuário der uma lista, confirme os passos antes de avançar.

        Sinalize [FINALIZADO] apenas quando tiver coletado: Objetivo, Atividades (com decisões), Atores e Sistemas.
        """

    async def get_next_question(self, chat_history: list, user_input: str, process_id: str = None):
        """
        Processa a mensagem, salva dados estruturados e decide a próxima pergunta.
        """
        try:
            # 1. Tenta extrair dados estruturados (Atividades, Atores, Sistemas)
            extracted = await self.extractor.extract_data(user_input)
            
            # 2. Se houver dados novos e um processo ativo, salva no Supabase
            if process_id and extracted.activities:
                for idx, activity in enumerate(extracted.activities):
                    node_data = {
                        "step_order": idx + 1, # Lógica simples de ordem, pode ser refinada
                        "actor": activity.actor,
                        "activity": activity.task,
                        "system": activity.system,
                        "is_gateway": activity.is_gateway,
                        "condition_text": activity.negative_flow if activity.is_gateway else None
                    }
                    self.repo.add_activity_node(process_id, node_data)
                    logger.info(f"✅ Nodo salvo no banco: {activity.task}")

            # 3. Gera a resposta conversacional usando o histórico
            messages = [SystemMessage(content=self.system_prompt)]
            
            # Adiciona histórico para manter o fio da meada
            for msg in chat_history:
                if isinstance(msg, dict):
                    content = msg.get("content", "")
                    role = msg.get("role", "user")
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                else:
                    messages.append(HumanMessage(content=str(msg)))
            
            messages.append(HumanMessage(content=user_input))
            
            response = await self.llm.ainvoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Erro no ChatService: {str(e)}")
            return "⚠️ Tive um problema ao processar sua resposta. Pode repetir o último passo do processo?"

    async def start_new_mapping(self, process_name: str):
        """Inicia um processo no banco e retorna o ID para o chat"""
        new_process = self.repo.create_process(process_name)
        return new_process['id']