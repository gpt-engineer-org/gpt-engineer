import os
import logging
import json
from pathlib import Path
import shutil

import typer
from typing import Any

from gpt_engineer.ai.models import models, default_model_name, ModelName
from gpt_engineer.chat_to_files import to_files
from gpt_engineer.db import DB, DBs
from gpt_engineer.models import Message, Role, Step

from gpt_engineer.steps import STEPS

app = typer.Typer()


@app.command()
def main(
    project_path: str = typer.Argument("example", help="path"),
    delete_existing: bool = typer.Argument(False, help="delete existing files"),
    model: str = "gpt-4",
    temperature: float = 0.1,
    steps_config: str = "default",
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    run_prefix: str = typer.Option(
        "",
        help=(
            "run prefix, if you want to run multiple variants of the same project and "
            "later compare them"
        ),
    ),
):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    input_path = Path(project_path).absolute()
    memory_path = input_path / (run_prefix + "memory")
    workspace_path = input_path / (run_prefix + "workspace")

    if delete_existing:
        # Delete files and subdirectories in paths
        shutil.rmtree(memory_path, ignore_errors=True)
        shutil.rmtree(workspace_path, ignore_errors=True)

    kwargs = {
            "model": model,
            "temperature": temperature 
        }
    ai = models[model](**kwargs)

    dbs = DBs(
        memory=DB(memory_path),
        logs=DB(memory_path / "logs"),
        input=DB(input_path),
        workspace=DB(workspace_path),
        identity=DB(Path(os.path.curdir) / "identity"),
    )

    for step in STEPS[steps_config]:
        messages = step(ai, dbs)
        dbs.logs[step.__name__] = json.dumps(messages)


if __name__ == "__main__":
    app()