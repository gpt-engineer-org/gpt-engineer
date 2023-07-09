import json
import logging
import os
import shutil

from pathlib import Path

import typer

from gpt_engineer import steps
from gpt_engineer.ai import AI, fallback_model
from gpt_engineer.collect import collect_learnings
from gpt_engineer.db import DB, DBs
from gpt_engineer.steps import STEPS

app = typer.Typer()


@app.command()
def main(
    project_path: str = typer.Argument("example", help="path"),
    delete_existing: bool = typer.Argument(False, help="delete existing files"),
    model: str = typer.Argument("gpt-4", help="model id string"),
    temperature: float = 0.1,
    steps_config: steps.Config = typer.Option(
        steps.Config.DEFAULT, "--steps", "-s", help="decide which steps to run"
    ),
    improve_option: bool = typer.Option(
        False,
        "--improve",
        "-i",
        help="Improve code from existing project.",
    ),
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

    # For the improve option take current project as path and add .gpteng folder
    # By now, ignoring the 'project_path' argument
    if improve_option:
        input_path = Path(os.getcwd()).absolute() / ".gpteng"
        input_path.mkdir(parents=True, exist_ok=True)
        # The default option for the --improve is the IMPROVE_CODE, not DEFAULT
        # I know this looks ugly, not sure if it is the best way to do that...
        # we can change that in the future.
        if steps_config == steps.Config.DEFAULT:
            steps_config = steps.Config.IMPROVE_CODE

    memory_path = input_path / f"{run_prefix}memory"
    workspace_path = input_path / f"{run_prefix}workspace"

    if delete_existing:
        # Delete files and subdirectories in paths
        shutil.rmtree(memory_path, ignore_errors=True)
        shutil.rmtree(workspace_path, ignore_errors=True)

    model = fallback_model(model)

    ai = AI(
        model=model,
        temperature=temperature,
    )

    dbs = DBs(
        memory=DB(memory_path),
        logs=DB(memory_path / "logs"),
        input=DB(input_path),
        workspace=DB(workspace_path),
        preprompts=DB(Path(__file__).parent / "preprompts"),
    )

    steps_used = STEPS[steps_config]
    for step in steps_used:
        messages = step(ai, dbs)
        dbs.logs[step.__name__] = json.dumps(messages)

    collect_learnings(model, temperature, steps_used, dbs)


if __name__ == "__main__":
    app()
