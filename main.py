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
    project_path: str = typer.Argument(None, help="path"),
    run_prefix: str = typer.Option("", help="run prefix"),
    model: str = "gpt-4",
    temperature: float = 0.1,
    max_tokens: int = 4096,
    n: int = 1,
    stream: bool = True,
):

    if project_path is None:
        project_path = str(pathlib.Path(__file__).parent / "example")

    input_path = project_path
    memory_path = pathlib.Path(project_path) / "memory"
    workspace_path = pathlib.Path(project_path) / (run_prefix + "workspace")

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
        logs=DB(pathlib.Path(memory_path) / "logs"),
        input=DB(input_path),
        workspace=DB(workspace_path),
        identity=DB(pathlib.Path(__file__).parent / "identity"),
    )


    for step in STEPS:
        messages = step(ai, dbs)
        dbs.logs[run_prefix + step.__name__] = json.dumps(messages)


if __name__ == "__main__":
    app()
