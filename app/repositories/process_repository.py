from supabase import create_client, Client

from app.core.config import settings


class ProcessRepository:
    def __init__(self):
        # Usando o Service Role Key para garantir permissão total de escrita
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )

    def create_process(self, name: str, user_id: str = None):
        """Inicia um novo mapeamento de processo"""
        data = {"name": name, "user_id": user_id, "status": "em_mapeamento"}
        response = self.supabase.table("processes").insert(data).execute()
        if response.data:
            return response.data[0]
        return None

    def add_activity_node(self, process_id: str, node_data: dict):
        """Adiciona um passo ao processo (Nodo do BPMN)"""
        node_data["process_id"] = process_id
        response = self.supabase.table("activity_nodes").insert(node_data).execute()
        if response.data:
            return response.data[0]
        return None

    def get_full_process(self, process_id: str):
        """Busca o processo e todos os seus nodos ordenados"""
        process = self.supabase.table("processes").select("*").eq("id", process_id).single().execute()
        nodes = (
            self.supabase.table("activity_nodes")
            .select("*")
            .eq("process_id", process_id)
            .order("step_order")
            .execute()
        )

        return {
            "metadata": process.data,
            "nodes": nodes.data if nodes.data else [],
        }

    def get_next_step_order(self, process_id: str) -> int:
        """Retorna a próxima ordem de passo para evitar reinício em cada mensagem."""
        nodes = (
            self.supabase.table("activity_nodes")
            .select("step_order")
            .eq("process_id", process_id)
            .order("step_order", desc=True)
            .limit(1)
            .execute()
        )
        if not nodes.data:
            return 1
        return int(nodes.data[0].get("step_order", 0)) + 1

    def update_process(self, process_id: str, data: dict):
        """Atualiza metadados do processo sem criar novas linhas."""
        response = self.supabase.table("processes").update(data).eq("id", process_id).execute()
        if response.data:
            return response.data[0]
        return None
