import json
import os
import pathlib

import typer

from gpt_engineer.ai import AI
from gpt_engineer.db import DB, DBs
from gpt_engineer.steps import STEPS

# Load OPENAI_API_KEY variable from .env file if dotenv installed.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print(
        "python-dotenv not installed. Skipping loading environment variables from "
        ".env file."
    )

app = typer.Typer()


@app.command()
def chat(
    project_path: str = typer.Argument(
        str(pathlib.Path(os.path.curdir) / "example"), help="path"
    ),
    run_prefix: str = typer.Option(
        "",
        help=(
            "run prefix, if you want to run multiple variants of the same project and "
            "later compare them"
        ),
    ),
    model: str = "gpt-4",
    temperature: float = 0.1,
):
    app_dir = pathlib.Path(os.path.curdir)
    input_path = project_path
    memory_path = pathlib.Path(project_path) / (run_prefix + "memory")
    workspace_path = pathlib.Path(project_path) / (run_prefix + "workspace")

    ai = AI().create(
        model=model,
        temperature=temperature,
    )

    dbs = DBs(
        memory=DB(memory_path),
        logs=DB(memory_path / "logs"),
        input=DB(input_path),
        workspace=DB(workspace_path),
        identity=DB(app_dir / "identity"),
    )

    for step in STEPS:
        messages = step(ai, dbs)
        dbs.logs[step.__name__] = json.dumps(messages)


def execute():
    app()


if __name__ == "__main__":
    execute()
