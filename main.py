import os
import pathlib
from typing import Optional
import openai
from chat_to_files import to_files
import typer


app = typer.Typer()


@app.command()
def chat(
    engine: str = "gpt-4",
    temperature: float = 0.0,
    max_tokens: int = 4096,
    n: int = 1,
    stream: bool = True,
    system_prompt: str = typer.Argument("system", help="System prompt file"),
    user_prompt: str = typer.Argument("user", help="User prompt file"),
    code_to_file_path: Optional[str] = typer.Option(
        None, "--out", "-c", help="Code to file path"
    ),
):

    # ensure file path corresponds to file in the same file as this script, using __file__
    if system_prompt == "system":
        # get folder of script
        system_prompt = pathlib.Path(__file__).parent / system_prompt

    if user_prompt == "user":
        user_prompt = pathlib.Path(__file__).parent / user_prompt

    
    with open(system_prompt, "r") as f:
        system_prompt = f.read()
    with open(user_prompt, "r") as f:
        user_prompt = f.read()
    response = openai.ChatCompletion.create(
        model=engine,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        n=n,
        stream=stream,
        stop=None,
    )

    chat = []
    for chunk in response:
        delta = chunk['choices'][0]['delta']
        msg = delta.get('content', '')
        print(msg, end="")
        chat.append(msg)

    if code_to_file_path is not None:
        to_files("".join(chat), code_to_file_path)


if __name__ == "__main__":
    app()
