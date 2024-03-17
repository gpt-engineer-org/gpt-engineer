from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

temperature = 0.1
model_name = "CodeLlama"

model = ChatOpenAI(
    model=model_name,
    temperature=temperature,
    callbacks=[StreamingStdOutCallbackHandler()],
    streaming=True
)

prompt = "Provide me with only the code for a simple python function that sums two numbers."

model.invoke(prompt)
