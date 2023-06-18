import json
import os
import pathlib
import shutil

import typer

from gpt_engineer.ai import AI
from gpt_engineer.db import DB, DBs
from gpt_engineer.steps import STEPS

app = typer.Typer()


@app.command()
def chat(
    project_path: str = typer.Argument("example", help="path"),
    delete_existing: str = typer.Argument(None, help="delete existing files"),
    run_prefix: str = typer.Option(
        "",
        help=(
            "run prefix, if you want to run multiple variants of the same project and "
            "later compare them",
        ),
    ),
    model: str = "gpt-4",
    temperature: float = 0.1,
    steps_config: str = "default",
):
    app_dir = pathlib.Path(os.path.curdir)
    input_path = pathlib.Path(app_dir / "projects" / project_path)
    memory_path = input_path / (run_prefix + "memory")
    workspace_path = input_path / (run_prefix + "workspace")

    if delete_existing == "true":
        # Delete files and subdirectories in paths
        shutil.rmtree(memory_path, ignore_errors=True)
        shutil.rmtree(workspace_path, ignore_errors=True)

    ai = AI(
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

    for step in STEPS[steps_config]:
        messages = step(ai, dbs)
        dbs.logs[step.__name__] = json.dumps(messages)


if __name__ == "__main__":
    app()
