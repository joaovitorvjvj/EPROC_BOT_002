import httpx
import asyncio

async def testar_fluxo_completo():
    url_base = "http://127.0.0.1:8000"
    
    print("\n--- 🚀 INICIANDO TESTE PMAS (MODO IA + MOCK WHATSAPP) ---")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # 1. TESTE DE SAÚDE
            health = await client.get(f"{url_base}/health")
            print(f"Status do Sistema: {health.json()}")

            # 2. CRIAR PROCESSO
            print("\n1. Criando novo processo...")
            # CORREÇÃO: Payload completo conforme exigido pelo ProcessCreate
            payload_inicio = {
                "name": "Mapeamento de Compras Institucionais",
                "sector": "Departamento de Suprimentos",
                "secretariat": "Secretaria da Administração",
                "owner": "João Junco",
                "requester_name": "João Junco",
                "requester_email": "joao.junco@exemplo.com",
                "mode": "AUTOMATIC"
            }
            
            res_inicio = await client.post(f"{url_base}/process/start", json=payload_inicio)
            res_inicio.raise_for_status()
            processo = res_inicio.json()
            p_id = processo['id']
            print(f"✅ Sucesso! Processo ID: {p_id}")

            # 3. ATUALIZAR CANVAS
            print("\n2. Simulando coleta de dados (Canvas)...")
            canvas_data = {
                "objective": "Otimizar o fluxo de pedidos de compra",
                "macroactivities": [
                    "Solicitar Orçamento", 
                    "Aprovação da Gerência", 
                    "Empenho da Despesa", 
                    "Recebimento do Material"
                ],
                "start_event": "Necessidade de material",
                "end_event": "Material entregue"
            }
            await client.post(f"{url_base}/process/{p_id}/canvas", json=canvas_data)
            print("✅ Canvas atualizado!")

            # 4. FINALIZAR
            print("\n3. Finalizando (Gerando BPMN Hierárquico via Gemini)...")
            res_final = await client.post(f"{url_base}/process/{p_id}/finalize")
            res_final.raise_for_status()
            
            print("\n✅ DOCUMENTOS GERADOS E NOTIFICAÇÃO ENVIADA!")
            print(f"--- 🎉 TESTE CONCLUÍDO COM SUCESSO! ---")
            print(f"Verifique a pasta: storage/whatsapp_emulator/")

        except Exception as e:
            print(f"\n❌ ERRO NO TESTE: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(f"Detalhes do Erro: {e.response.text}")

if __name__ == "__main__":
    asyncio.run(testar_fluxo_completo())