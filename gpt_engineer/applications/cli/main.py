"""
This module provides a CLI tool to interact with the GPT Engineer application,
enabling users to use OpenAI's models and define various parameters for the
project they want to generate, improve or interact with.

Main Functionality:
---------------------
- Load environment variables needed to work with OpenAI.
- Allow users to specify parameters such as:
  - Project path
  - Model type (default to GPT-4)
  - Temperature
  - Step configurations
  - Code improvement mode
  - Lite mode for lighter operations
  - Azure endpoint for Azure OpenAI services
  - Using project's preprompts or default ones
  - Verbosity level for logging
- Interact with AI, databases, and archive processes based on the user-defined parameters.

Notes:
- Ensure the .env file has the `OPENAI_API_KEY` or provide it in the working directory.
- The default project path is set to `projects/example`.
- For azure_endpoint, provide the endpoint for Azure OpenAI service.

"""

import os
from pathlib import Path

import openai
import typer
from dotenv import load_dotenv

from gpt_engineer.core.default.on_disk_repository import OnDiskRepository
from gpt_engineer.core.ai import AI
from gpt_engineer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_engineer.applications.cli.file_selector import ask_for_files, get_all_code
from gpt_engineer.tools.custom_steps import (
    lite_gen,
    clarified_gen,
    self_heal,
    vector_improve,
)
from gpt_engineer.core.default.git_version_manager import GitVersionManager
from gpt_engineer.core.default.steps import gen_code, execute_entrypoint, improve
from gpt_engineer.applications.cli.cli_agent import CliAgent
from gpt_engineer.applications.cli.collect import collect_and_send_human_review
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.core.default.on_disk_execution_env import OnDiskExecutionEnv
import logging

app = typer.Typer()  # creates a CLI app


def load_env_if_needed():
    if os.getenv("OPENAI_API_KEY") is None:
        load_dotenv()
    if os.getenv("OPENAI_API_KEY") is None:
        # if there is no .env file, try to load from the current working directory
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))
    openai.api_key = os.getenv("OPENAI_API_KEY")


def load_prompt(input_repo: OnDiskRepository, improve_mode):
    if input_repo.get("prompt"):
        return input_repo.get("prompt")

    if not improve_mode:
        input_repo["prompt"] = input(
            "\nWhat application do you want gpt-engineer to generate?\n"
        )
    else:
        input_repo["prompt"] = input("\nHow do you want to improve the application?\n")
    return input_repo.get("prompt")


def get_preprompts_path(use_custom_preprompts: bool, input_path: Path) -> Path:
    original_preprompts_path = PREPROMPTS_PATH
    if not use_custom_preprompts:
        return original_preprompts_path

    custom_preprompts_path = input_path / "preprompts"
    if not custom_preprompts_path.exists():
        custom_preprompts_path.mkdir()

    for file in original_preprompts_path.glob("*"):
        if not (custom_preprompts_path / file.name).exists():
            (custom_preprompts_path / file.name).write_text(file.read_text())
    return custom_preprompts_path


@app.command()
def main(
    project_path: str = typer.Argument("projects/example", help="path"),
    model: str = typer.Argument("gpt-4-1106-preview", help="model id string"),
    temperature: float = 0.1,
    improve_mode: bool = typer.Option(
        False,
        "--improve",
        "-i",
        help="Improve code from existing project.",
    ),
    vector_improve_mode: bool = typer.Option(
        False,
        "--vector-improve",
        "-vi",
        help="Improve code from existing project using vector store.",
    ),
    lite_mode: bool = typer.Option(
        False,
        "--lite",
        "-l",
        help="Lite mode - run only the main prompt.",
    ),
    clarify_mode: bool = typer.Option(
        False,
        "--clarify",
        "-c",
        help="Lite mode - discuss specification with AI before implementation.",
    ),
    self_heal_mode: bool = typer.Option(
        False,
        "--self-heal",
        "-sh",
        help="Lite mode - discuss specification with AI before implementation.",
    ),
    azure_endpoint: str = typer.Option(
        "",
        "--azure",
        "-a",
        help="""Endpoint for your Azure OpenAI Service (https://xx.openai.azure.com).
            In that case, the given model is the deployment name chosen in the Azure AI Studio.""",
    ),
    use_custom_preprompts: bool = typer.Option(
        False,
        "--use-custom-preprompts",
        help="""Use your project's custom preprompts instead of the default ones.
          Copies all original preprompts to the project's workspace if they don't exist there.""",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    #
    if vector_improve_mode and not improve_mode:
        print("Vector improve mode implies improve mode, setting improve_mode=True")
        improve_mode = True

    if improve_mode:
        assert not (
            clarify_mode or lite_mode
        ), "Clarify and lite mode are not active for improve mode"

    load_env_if_needed()

    ai = AI(
        model_name=model,
        temperature=temperature,
        azure_endpoint=azure_endpoint,
    )

    # project_path = os.path.abspath(
    #     project_path
    # )  # resolve the string to a valid path (eg "a/b/../c" to "a/c")
    path = Path(project_path)  # .absolute()
    print("Running gpt-engineer in", path.absolute(), "\n")
    prompt = load_prompt(OnDiskRepository(path), improve_mode)
    # configure generation function
    if clarify_mode:
        code_gen_fn = clarified_gen
    elif lite_mode:
        code_gen_fn = lite_gen
    else:
        code_gen_fn = gen_code
    # configure execution function
    if self_heal_mode:
        execution_fn = self_heal
    else:
        execution_fn = execute_entrypoint

    if vector_improve_mode:
        improve_fn = vector_improve
    else:
        improve_fn = improve

    preprompts_path = get_preprompts_path(use_custom_preprompts, Path(project_path))
    preprompts_holder = PrepromptsHolder(preprompts_path)
    memory = OnDiskRepository(memory_path(project_path))
    version_manager = GitVersionManager(project_path)
    execution_env = OnDiskExecutionEnv()
    agent = CliAgent.with_default_config(
        memory,
        execution_env,
        ai=ai,
        code_gen_fn=code_gen_fn,
        execute_entrypoint_fn=execution_fn,
        improve_fn=improve_fn,
        preprompts_holder=preprompts_holder,
    )
    if improve_mode:
        if vector_improve_mode:
            code = get_all_code(project_path)
        else:
            code = ask_for_files(project_path)
        code = agent.improve(code, prompt)
    else:
        code = agent.init(prompt)

    # make snapshot of code
    version_manager.snapshot(code)

    # collect user feedback if user consents
    config = (code_gen_fn.__name__, execution_fn.__name__)
    collect_and_send_human_review(prompt, model, temperature, config, agent.memory)

    print("Total api cost: $ ", ai.token_usage_log.usage_cost())


if __name__ == "__main__":
    app()
