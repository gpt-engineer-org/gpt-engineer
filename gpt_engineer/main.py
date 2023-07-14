# import necessary modules
import json
import logging

# pathlib for handling paths
from pathlib import Path

# typer for creating command-line interfaces
import typer

# import necessary functions/classes from your local packages
from gpt_engineer.ai import AI, fallback_model
from gpt_engineer.collect import collect_learnings
from gpt_engineer.db import DB, DBs, archive
from gpt_engineer.learning import collect_consent
from gpt_engineer.steps import STEPS, Config as StepsConfig

# create a typer app
app = typer.Typer()


@app.command()  # the main function will be the command for the typer app
def main(
    # define arguments and options for the typer command
    project_path: str = typer.Argument("projects/example", help="path"),
    model: str = typer.Argument("gpt-4", help="model id string"),
    temperature: float = 0.1,
    steps_config: StepsConfig = typer.Option(
        StepsConfig.DEFAULT, "--steps", "-s", help="decide which steps to run"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    # configure logging
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    # get the model
    model = fallback_model(model)
    ai = AI(
        model=model,
        temperature=temperature,
    )

    # create paths for the various components of the application
    input_path = Path(project_path).absolute()
    memory_path = input_path / "memory"
    workspace_path = input_path / "workspace"
    archive_path = input_path / "archive"

    # create database objects for each component
    dbs = DBs(
        memory=DB(memory_path),
        logs=DB(memory_path / "logs"),
        input=DB(input_path),
        workspace=DB(workspace_path),
        preprompts=DB(Path(__file__).parent / "preprompts"),
        archive=DB(archive_path),
    )

    # if the steps config is not execute-only, use-feedback, or evaluate, archive the databases
    if steps_config not in [
        StepsConfig.EXECUTE_ONLY,
        StepsConfig.USE_FEEDBACK,
        StepsConfig.EVALUATE,
    ]:
        archive(dbs)

    # execute the steps specified by the steps config
    steps = STEPS[steps_config]
    for step in steps:
        messages = step(ai, dbs)
        dbs.logs[step.__name__] = json.dumps(messages)

    # if the user consents, collect learnings
    if collect_consent():
        collect_learnings(model, temperature, steps, dbs)

    # log token usage
    dbs.logs["token_usage"] = ai.format_token_usage_log()


# if the script is run directly (as opposed to being imported), run the main function
if __name__ == "__main__":
    app()
