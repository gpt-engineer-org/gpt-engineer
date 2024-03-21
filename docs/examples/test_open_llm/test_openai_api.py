from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="sk-xxx")

response = client.chat.completions.create(
    model="CodeLlama",
    messages=[
        {
            "role": "user",
            "content": "Provide me with the code for a simple HTML web site.",
        },
    ],
    temperature=0.7,
    max_tokens=200,
)

print(response.choices[0].message.content)
