from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="sk-xxx")

response = client.chat.completions.create(
    model="llama2",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the meaning of life?"},
    ],
)

print(response)
