import httpx
import asyncio

async def testar_fluxo_completo():
    url_base = "http://127.0.0.1:8000"
    
    print("\n--- 🚀 INICIANDO TESTE PMAS ---")
    
    # 1. TESTE DE SAÚDE
    async with httpx.AsyncClient() as client:
        health = await client.get(f"{url_base}/health")
        print(f"Status do Sistema: {health.json()}")

        # 2. CRIAR PROCESSO (Testa Supabase + Taiga)
        print("\n1. Criando novo processo...")
        payload_inicio = {
            "name": "Processo de Teste Operacional",
            "sector": "TI Institucional",
            "secretariat": "Casa Civil",
            "owner": "João Junco",
            "requester_name": "Validador PMAS",
            "requester_email": "joao.junco@casacivil.sc.gov.br",
            "mode": "AUTOMATIC"
        }
        
        try:
            res_inicio = await client.post(f"{url_base}/process/start", json=payload_inicio)
            res_inicio.raise_for_status()
            processo = res_inicio.json()
            p_id = processo['id']
            print(f"✅ Sucesso! Processo ID: {p_id}")
            print(f"📌 Verifique seu Taiga, o card deve estar lá!")

            # 3. ATUALIZAR CANVAS
            print("\n2. Simulando coleta de dados (Canvas)...")
            canvas_data = {
                "objective": "Testar a integração total do sistema",
                "macroactivities": ["Ativar Servidor", "Rodar Script", "Verificar Taiga"],
                "start_event": "Início do script",
                "end_event": "Fim do teste"
            }
            await client.post(f"{url_base}/process/{p_id}/canvas", json=canvas_data)
            print("✅ Canvas atualizado!")

            # 4. FINALIZAR (Gera arquivos e anexa ao Taiga)
            print("\n3. Finalizando e gerando documentos...")
            res_final = await client.post(f"{url_base}/process/{p_id}/finalize")
            res_final.raise_for_status()
            print("✅ Documentos gerados e anexados!")
            print(f"\n--- 🎉 TESTE CONCLUÍDO COM SUCESSO! ---")
            print(f"Verifique as pastas 'storage/bpmn' e 'storage/docx'")

        except Exception as e:
            print(f"❌ ERRO NO TESTE: {str(e)}")
            if hasattr(e, 'response'):
                print(f"Detalhes: {e.response.text}")

if __name__ == "__main__":
    asyncio.run(testar_fluxo_completo())