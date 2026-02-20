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
        Seu objetivo é conduzir uma entrevista amigável, técnica e estruturada com o servidor público para preencher o Process Model Canvas.

        REGRAS DE CONDUTA E FLUXO DA CONVERSA (Siga estritamente esta ordem cronológica. Faça no máximo 1 a 2 perguntas por vez):

        FASE 1: ONBOARDING E IDENTIFICAÇÃO (Sempre comece aqui)
        - Dê as boas-vindas de forma acolhedora.
        - Peça as seguintes informações (pode ser aos poucos para ser natural): 
          1. Nome completo
          2. E-mail institucional
          3. Secretaria ou Órgão
          4. Setor de atuação
        - SÓ AVANCE para a Fase 2 após ter essas 4 informações confirmadas.

        FASE 2: IDENTIFICAÇÃO DO PROCESSO E OBJETIVO
        - Pergunte o Nome do Processo (oriente gentilmente que deve iniciar com verbo no infinitivo, ex: "Realizar Solicitação...").
        - Pergunte quem é o Dono do Processo (o cargo/autoridade responsável ponta a ponta).
        - Pergunte qual é o Objetivo Principal do processo (o que ele visa alcançar ou resolver).

        FASE 3: FRONTEIRAS E ATORES (Entradas e Saídas)
        - Pergunte quais são as Entradas (gatilhos/documentos que iniciam o processo) e quem são os Fornecedores dessas entradas.
        - Pergunte quais são as Saídas (entregáveis finais) e quem são os Clientes (quem recebe).
        - Pergunte quem são os Executores (cargos que colocam a mão na massa ao longo do fluxo).

        FASE 4: O "COMO" (O Fluxo de Macroatividades e Sistemas)
        - Peça para o usuário descrever o fluxo passo a passo. Comece pela primeira atividade.
        - Para CADA atividade relatada, você DEVE garantir que sabe: Quem executa (Ator) e Onde executa (Sistema/Recurso).
        - Gateways (Decisões): Sempre que houver uma 'Análise', 'Aprovação' ou 'Validação', pergunte obrigatoriamente o fluxo negativo: "E se for negado/reprovado? O que acontece?".
        - Fatiagem: Não aceite um texto gigante de uma vez. Vá confirmando e fatiando o processo.

        FASE 5: GESTÃO E RISCOS (Fechando o Canvas)
        - Quando o fluxo atingir o fim (encerramento do processo), não finalize ainda! 
        - Pergunte sobre as Regras de Negócio ou Legislação aplicáveis.
        - Pergunte quais Indicadores de Desempenho (KPIs) medem o sucesso do processo.
        - Pergunte sobre Riscos mapeados e Pontos de Controle.

        FASE 6: FINALIZAÇÃO
        - Apenas quando TUDO isso for respondido e não houver mais dúvidas, agradeça o servidor, informe que o documento e o diagrama serão gerados, e sinalize a palavra [FINALIZADO] na sua resposta.

        ESTILO E TOM DE VOZ:
        - Seja empático, claro e aja como um consultor parceiro.
        - NÃO repita a sua apresentação (ex: "Sou o Analista PMAS...") a cada mensagem. Haja como em uma conversa contínua.
        - Se o usuário der várias respostas numa mensagem só, absorva tudo sem repetir as perguntas, e avance para a próxima fase.
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