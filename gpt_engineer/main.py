import logging

import os

from pathlib import Path

import typer

from gpt_engineer.ai import AI
from gpt_engineer.collect import collect_learnings
from gpt_engineer.db import DB, DBs, archive
from gpt_engineer.learning import collect_consent
from gpt_engineer.steps import STEPS, Config as StepsConfig

app = typer.Typer()


@app.command()
def main(
    project_path: str = typer.Argument("projects/example", help="path"),
    model: str = typer.Argument("gpt-4", help="model id string"),
    temperature: float = 0.1,
    steps_config: StepsConfig = typer.Option(
        StepsConfig.DEFAULT, "--steps", "-s", help="decide which steps to run"
    ),
    improve_option: bool = typer.Option(
        False,
        "--improve",
        "-i",
        help="Improve code from existing project.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)



    memory_path = input_path / "memory"
    workspace_path = input_path / "workspace"
    # For the improve option take current project as path and add .gpteng folder
    # By now, ignoring the 'project_path' argument
    if improve_option:
        input_path = Path(os.getcwd()).absolute() / ".gpteng"
        input_path.mkdir(parents=True, exist_ok=True)
        # The default option for the --improve is the IMPROVE_CODE, not DEFAULT
        # we can change that in the future.
        if steps_config == StepsConfig.DEFAULT:
            steps_config = StepsConfig.IMPROVE_CODE
        memory_path = input_path / "memory"
        workspace_path = Path(os.getcwd()).absolute()

    ai = AI(
        model_name=model,
        temperature=temperature,
    )

    input_path = Path(project_path).absolute()
    memory_path = input_path / "memory"
    workspace_path = input_path / "workspace"
    archive_path = input_path / "archive"

    dbs = DBs(
        memory=DB(memory_path),
        logs=DB(memory_path / "logs"),
        input=DB(input_path),
        workspace=DB(workspace_path),
        preprompts=DB(Path(__file__).parent / "preprompts"),
        archive=DB(archive_path),
    )

    if steps_config not in [
        StepsConfig.EXECUTE_ONLY,
        StepsConfig.USE_FEEDBACK,
        StepsConfig.EVALUATE,
    ]:
        archive(dbs)

    steps = STEPS[steps_config]
    for step in steps:
        messages = step(ai, dbs)
        dbs.logs[step.__name__] = AI.serialize_messages(messages)

    if collect_consent():
        collect_learnings(model, temperature, steps, dbs)

    dbs.logs["token_usage"] = ai.format_token_usage_log()


if __name__ == "__main__":
    app()
