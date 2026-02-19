# Deploy checklist (Vercel + Render)

## 1) Estado atual confirmado
- Backend FastAPI com rota `/chat` e endpoint raiz `GET /`.
- Extração estruturada via LangChain + Gemini configurada em `ExtractionService`.
- Persistência no Supabase via `ProcessRepository`.

## 2) Ajustes aplicados neste repositório
- Dependências Python consolidadas em `requirements.txt` (inclui `uvicorn`).
- Configuração de CORS movida para variável de ambiente (`FRONTEND_ORIGINS`).
- Arquivo `render.yaml` criado com:
  - `DISABLE_POETRY=true`.
  - Build com `pip install -r requirements.txt`.
  - Start com `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

## 3) Configurar no Render
1. Criar/editar Web Service e apontar para este repositório.
2. Se o backend estiver em subpasta no futuro, ajustar `rootDir` em `render.yaml` ou no painel.
3. Definir as variáveis de ambiente:
   - `GEMINI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `TAIGA_URL`
   - `TAIGA_API_TOKEN`
   - `TAIGA_PROJECT_ID`
   - `TAIGA_USER_ID`
   - `FRONTEND_ORIGINS` (ex.: `https://seu-frontend.vercel.app`)
4. Fazer deploy e validar:
   - `GET /` deve retornar `{"status":"online"...}`
   - `POST /chat` deve responder e retornar `process_id`.

## 4) Configurar no Vercel
1. Definir variável pública da API no frontend (ex.: `NEXT_PUBLIC_API_URL`).
2. Apontar para a URL do Render (`https://<seu-backend>.onrender.com`).
3. Verificar chamadas para `/chat` e tratamento de `process_id`.

## 5) Pendências recomendadas
- Definir autenticação para endpoints de produção.
- Restringir CORS somente aos domínios oficiais (sem wildcard).
- Adicionar endpoint de healthcheck dedicado para monitoramento.
- Versionar esquema de banco (migrations) para `processes` e `activity_nodes`.
