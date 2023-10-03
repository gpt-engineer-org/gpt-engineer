import logging
import os

from pathlib import Path

import openai
import typer

from dotenv import load_dotenv

from gpt_engineer.core.ai import AI
from gpt_engineer.collect import collect_learnings
from gpt_engineer.core.db import DB, DBs, archive
from gpt_engineer.learning import collect_consent
from gpt_engineer.core.steps import STEPS, Config as StepsConfig

app = typer.Typer()  # creates a CLI app


def load_env_if_needed():
    if os.getenv("OPENAI_API_KEY") is None:
        load_dotenv()
    if os.getenv("OPENAI_API_KEY") is None:
        # if there is no .env file, try to load from the current working directory
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))
    openai.api_key = os.getenv("OPENAI_API_KEY")


@app.command()
def main(
    project_path: str = typer.Argument("projects/example", help="path"),
    model: str = typer.Argument("gpt-4", help="model id string"),
    temperature: float = 0.1,
    steps_config: StepsConfig = typer.Option(
        StepsConfig.DEFAULT, "--steps", "-s", help="decide which steps to run"
    ),
    improve_mode: bool = typer.Option(
        False,
        "--improve",
        "-i",
        help="Improve code from existing project.",
    ),
    lite_mode: bool = typer.Option(
        False,
        "--lite",
        "-l",
        help="Lite mode - run only the main prompt.",
    ),
    azure_endpoint: str = typer.Option(
        "",
        "--azure",
        "-a",
        help="""Endpoint for your Azure OpenAI Service (https://xx.openai.azure.com).
            In that case, the given model is the deployment name chosen in the Azure AI Studio.""",
    ),
    use_project_preprompts: bool = typer.Option(
        False,
        "--use-project-preprompts",
        help="""Use the project's preprompts instead of the default ones.
          Copies all original preprompts to the project's workspace if they don't exist there.""",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    if lite_mode:
        assert not improve_mode, "Lite mode cannot improve code"
        if steps_config == StepsConfig.DEFAULT:
            steps_config = StepsConfig.LITE

    if improve_mode:
        assert (
            steps_config == StepsConfig.DEFAULT
        ), "Improve mode not compatible with other step configs"
        steps_config = StepsConfig.IMPROVE_CODE

    load_env_if_needed()

    ai = AI(
        model_name=model,
        temperature=temperature,
        azure_endpoint=azure_endpoint,
    )

    input_path = Path(project_path).absolute()
    print("Running gpt-engineer in", input_path, "\n")

    workspace_path = input_path / "workspace"
    project_metadata_path = input_path / ".gpteng"
    memory_path = project_metadata_path / "memory"
    archive_path = project_metadata_path / "archive"
    preprompts_path = Path(__file__).parent / "preprompts"

    if use_project_preprompts:
        project_preprompts_path = input_path / "preprompts"
        if not project_preprompts_path.exists():
            project_preprompts_path.mkdir()

        for file in preprompts_path.glob("*"):
            if not (project_preprompts_path / file.name).exists():
                (project_preprompts_path / file.name).write_text(file.read_text())
        preprompts_path = project_preprompts_path

    dbs = DBs(
        memory=DB(memory_path),
        logs=DB(memory_path / "logs"),
        input=DB(input_path),
        workspace=DB(workspace_path),
        preprompts=DB(preprompts_path),
        archive=DB(archive_path),
        project_metadata=DB(project_metadata_path),
    )

    if steps_config not in [
        StepsConfig.EXECUTE_ONLY,
        StepsConfig.USE_FEEDBACK,
        StepsConfig.EVALUATE,
        StepsConfig.IMPROVE_CODE,
    ]:
        archive(dbs)

        if not dbs.input.get("prompt"):
            dbs.input["prompt"] = input(
                "\nWhat application do you want gpt-engineer to generate?\n"
            )

    steps = STEPS[steps_config]
    for step in steps:
        messages = step(ai, dbs)
        dbs.logs[step.__name__] = AI.serialize_messages(messages)

    print("Total api cost: $ ", ai.usage_cost())

    if collect_consent():
        collect_learnings(model, temperature, steps, dbs)

    dbs.logs["token_usage"] = ai.format_token_usage_log()


if __name__ == "__main__":
    app()
