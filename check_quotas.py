import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def listar_modelos_reais():
    print("--- 📜 MODELOS REALMENTE LIBERADOS PARA SUA CHAVE ---")
    try:
        # Nas versões mais recentes da SDK, iteramos sobre os modelos disponíveis
        for model in client.models.list():
            # Verificamos os métodos suportados (o atributo correto é 'supported_methods')
            methods = model.supported_methods if hasattr(model, 'supported_methods') else []
            
            if 'generateContent' in methods or 'generate_content' in str(methods):
                print(f"ID: {model.name}")
    except Exception as e:
        print(f"Erro ao listar: {str(e)}")

if __name__ == "__main__":
    listar_modelos_reais()