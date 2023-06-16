import json
import pathlib

import typer

from ai import AI
from db import DB, DBs
from steps import standard_runner

app = typer.Typer()


@app.command()
def chat(
    project_path: str = typer.Argument(None, help="path"),
    run_prefix: str = typer.Option(
        "",
        help="run prefix, if you want to run multiple variants of the same project and later compare them",
    ),
    model: str = "ggml-v3-13b-hermes-q5_1.bin",
    temperature: float = 0.1,
):
    if project_path is None:
        project_path = str(pathlib.Path(__file__).parent / "example")

    input_path = project_path
    memory_path = pathlib.Path(project_path) / (run_prefix + "memory")
    workspace_path = pathlib.Path(project_path) / (run_prefix + "workspace")

    ai = AI(
        model=model,
        temp=temperature,
    )

    dbs = DBs(
        memory=DB(memory_path),
        logs=DB(pathlib.Path(memory_path) / "logs"),
        input=DB(input_path),
        workspace=DB(workspace_path),
        identity=DB(pathlib.Path(__file__).parent / "identity"),
    )

    standard_runner(ai, dbs).run()

if __name__ == "__main__":
    app()
