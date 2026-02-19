from google import genai

client = genai.Client(api_key="AIzaSyCgSwmDG8cGVcfKKrfZ0Oosw-t5RhXzRv4")

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="Responda apenas OK"
)

print(response.text)
