import os

from google import genai


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="Responda apenas OK",
)

print(response.text)
