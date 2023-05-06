import json
import os
import pathlib
from typing import Optional
import openai
from chat_to_files import to_files
from ai import AI
from steps import STEPS
from db import DB, DBs
import typer


app = typer.Typer()
    


@app.command()
def chat(
    model: str = "gpt-4",
    temperature: float = 0.1,
    max_tokens: int = 4096,
    n: int = 1,
    stream: bool = True,
    input_path: str = typer.Argument(
        None, help="input path"
    ),
    memory_path: str = typer.Argument(
        None, help="memory path"
    ),
    workspace_path: Optional[str] = typer.Option(
        None, "--out", "-c", help="Code to file path"
    ),
):

    if memory_path is None:
        memory_path = pathlib.Path(__file__).parent / 'memory'

    if input_path is None:
        input_path = pathlib.Path(__file__).parent / 'input'
    
    ai = AI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        n=n,
        stream=stream,
        stop=None,
    )

    dbs = DBs(
        memory=DB(memory_path),
        logs=DB(pathlib.Path(memory_path) / 'logs'),
        input=DB(input_path),
        workspace=DB(workspace_path),
        identity=DB(pathlib.Path(__file__).parent / 'identity'),
    )

    run_prefix= workspace_path.split('/')[-1] + '_' if workspace_path is not None else ''

    for step in STEPS:
        messages = step(ai, dbs)
        dbs.logs[run_prefix + step.__name__] = json.dumps(messages)


if __name__ == "__main__":
    app()
