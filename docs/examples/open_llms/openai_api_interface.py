import os

from openai import OpenAI

client = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE"), api_key=os.getenv("OPENAI_API_KEY")
)

response = client.chat.completions.create(
    model=os.getenv("MODEL_NAME"),
    messages=[
        {
            "role": "user",
            "content": "Provide me with only the code for a simple python function that sums two numbers.",
        },
    ],
    temperature=0.7,
    max_tokens=200,
)

print(response.choices[0].message.content)
