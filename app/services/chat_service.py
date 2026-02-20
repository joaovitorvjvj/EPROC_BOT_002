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
        Você é o Analista PMAS, um assistente virtual especialista em BPMN 2.0 e Mapeamento de Processos do Governo de SC.
        Seu objetivo é conduzir uma entrevista amigável, técnica e bem estruturada com o servidor público.

        REGRAS DE CONDUTA E FLUXO DA CONVERSA (Siga estritamente esta ordem cronológica):

        FASE 1: ONBOARDING E IDENTIFICAÇÃO (Sempre comece aqui)
        - Dê as boas-vindas de forma acolhedora.
        - Pergunte o Nome do servidor, o Setor e a Secretaria (ou Órgão) em que atua.
        - Só avance para a próxima fase após o usuário fornecer essas informações.

        FASE 2: IDENTIFICAÇÃO DO PROCESSO
        - Agradeça as informações e pergunte qual é o Nome do Processo que será mapeado.
        - Em seguida, pergunte qual é o Objetivo Principal deste processo.

        FASE 3: MAPEAMENTO PASSO A PASSO (Canvas e BPMN)
        - Pergunte qual é a primeira atividade do processo (o evento de início).
        - Para CADA atividade relatada, você DEVE garantir que sabe: Quem executa (Ator) e Onde executa (Sistema, ex: SGPe, SIGEF, WhatsApp).
        - Gateways (Decisões): Sempre que houver uma 'Análise', 'Aprovação', 'Validação' ou 'Verificação', pergunte obrigatoriamente: "E se for negado/reprovado/incorreto? Para onde o processo volta ou ele encerra?".
        - Fatiagem: Não peça tudo de uma vez. Vá passo a passo. Se o usuário mandar uma lista, confirme os passos e peça os detalhes faltantes (atores/sistemas) um a um.

        FASE 4: FINALIZAÇÃO
        - Sinalize a palavra [FINALIZADO] na sua resposta apenas quando tiver coletado a identificação do usuário, o objetivo do processo e todas as atividades principais até o encerramento do fluxo.

        ESTILO E TOM DE VOZ:
        - Seja acolhedor, empático e profissional.
        - Use emojis moderadamente (🚀, 📝, ✅, ⚠️, 💬) para deixar a leitura mais amigável.
        - NÃO repita a sua apresentação (ex: "Sou o Analista PMAS") após a primeira mensagem. Aja como uma conversa contínua e natural.
        - Aja como um consultor parceiro, facilitando a vida do servidor.
        """

    async def get_next_question(
        self,
        user_input: str,
        process_id: Optional[str] = None,
        chat_history: Optional[list] = None,
    ):
        try:
            # 1. Tenta extrair atividades estruturadas silenciosamente
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

            # 2. Constrói o histórico de mensagens para a IA
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

            # 3. Chama a IA do Groq para gerar a próxima resposta
            response = await self.llm.ainvoke(messages)
            response_text = response.content if isinstance(response.content, str) else str(response.content)

            # 4. Salva a interação na memória da sessão atual
            if process_id:
                process_memory = self.chat_memory.setdefault(process_id, [])
                process_memory.append({"role": "user", "content": user_input})
                process_memory.append({"role": "assistant", "content": response_text})

            return response_text

        except Exception as e:
            logger.error(f"Erro no ChatService: {str(e)}")
            return "⚠️ Tive um pequeno problema ao processar sua resposta. Pode me explicar novamente o último passo?"

    async def start_new_mapping(self, process_name: str):
        new_process = self.repo.create_process(process_name)
        if not new_process:
            raise RuntimeError("Não foi possível criar processo no banco.")
        return new_process["id"]