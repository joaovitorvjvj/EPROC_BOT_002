import os

from langchain_groq import ChatGroq


llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)

response = llm.invoke("Responda com status da conexão: OK")
print(response.content)
