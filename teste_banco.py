from app.repositories.process_repository import ProcessRepository

repo = ProcessRepository()

try:
    # 1. Criar um processo de teste
    print("🚀 Criando processo de teste...")
    proc = repo.create_process("Teste de Mapeamento EPROC")
    proc_id = proc['id']
    print(f"✅ Processo criado com ID: {proc_id}")

    # 2. Adicionar um nodo de atividade
    print("📝 Adicionando atividade...")
    repo.add_activity_node(proc_id, {
        "step_order": 1,
        "actor": "Solicitante",
        "activity": "Abrir chamado no SGPe",
        "system": "SGPe"
    })
    print("✅ Atividade salva com sucesso!")

except Exception as e:
    print(f"❌ Erro no teste: {e}")