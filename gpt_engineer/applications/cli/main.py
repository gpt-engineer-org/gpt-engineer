"""
Entrypoint for the CLI tool.

This module serves as the entry point for a command-line interface (CLI) tool designed to interact with OpenAI's language models. It provides functionality to load necessary environment variables, configure various parameters for the AI interaction, and manage the generation or improvement of code projects.

Main Functionality
------------------
- Load environment variables required for OpenAI API interaction.
- Parse user-specified parameters for project configuration and AI behavior.
- Facilitate interaction with AI models, databases, and archival processes.

Parameters
----------
None

Notes
-----
- The `OPENAI_API_KEY` must be set in the environment or provided in a `.env` file within the working directory.
- The default project path is `projects/example`.
- When using the `azure_endpoint` parameter, provide the Azure OpenAI service endpoint URL.
"""

import logging
import os

from pathlib import Path

import openai
import typer

from dotenv import load_dotenv

from gpt_engineer.applications.cli.cli_agent import CliAgent
from gpt_engineer.applications.cli.collect import collect_and_send_human_review
from gpt_engineer.applications.cli.file_selector import FileSelector
from gpt_engineer.core.ai import AI, ClipboardAI
from gpt_engineer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.file_store import FileStore
from gpt_engineer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_engineer.core.default.steps import (
    execute_entrypoint,
    gen_code,
    handle_improve_mode,
    improve,
)
from gpt_engineer.core.git import (
    filter_files_with_uncommitted_changes,
    init_git_repo,
    is_git_installed,
    is_git_repo,
    stage_files,
)
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.tools.custom_steps import clarified_gen, lite_gen, self_heal

app = typer.Typer()  # creates a CLI app


def load_env_if_needed():
    """
    Load environment variables if the OPENAI_API_KEY is not already set.

    This function checks if the OPENAI_API_KEY environment variable is set,
    and if not, it attempts to load it from a .env file in the current working
    directory. It then sets the openai.api_key for use in the application.
    """
    if os.getenv("OPENAI_API_KEY") is None:
        load_dotenv()
    if os.getenv("OPENAI_API_KEY") is None:
        # if there is no .env file, try to load from the current working directory
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))
    openai.api_key = os.getenv("OPENAI_API_KEY")


def load_prompt(input_repo: DiskMemory, improve_mode):
    """
    Load or request a prompt from the user based on the mode.

    Parameters
    ----------
    input_repo : DiskMemory
        The disk memory object where prompts and other data are stored.
    improve_mode : bool
        Flag indicating whether the application is in improve mode.

    Returns
    -------
    str
        The loaded or inputted prompt.
    """
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
    """
    Get the path to the preprompts, using custom ones if specified.

    Parameters
    ----------
    use_custom_preprompts : bool
        Flag indicating whether to use custom preprompts.
    input_path : Path
        The path to the project directory.

    Returns
    -------
    Path
        The path to the directory containing the preprompts.
    """
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


def prompt_yesno(question: str) -> bool:
    question += " [y/N] "
    answer = input(question).strip().lower()
    return answer in ["y", "yes"]


@app.command()
def main(
    project_path: str = typer.Argument("projects/example", help="path"),
    model: str = typer.Argument("gpt-4-1106-preview", help="model id string"),
    temperature: float = 0.1,
    improve_mode: bool = typer.Option(
        False,
        "--improve",
        "-i",
        help="Improve files_dict from existing project.",
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
    llm_via_clipboard: bool = typer.Option(
        False,
        "--llm-via-clipboard",
        help="Use the clipboard to communicate with the AI.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """
    The main entry point for the CLI tool that generates or improves a project.

    This function sets up the CLI tool, loads environment variables, initializes
    the AI, and processes the user's request to generate or improve a project
    based on the provided arguments.

    Parameters
    ----------
    project_path : str
        The file path to the project directory.
    model : str
        The model ID string for the AI.
    temperature : float
        The temperature setting for the AI's responses.
    improve_mode : bool
        Flag indicating whether to improve an existing project.
    lite_mode : bool
        Flag indicating whether to run in lite mode.
    clarify_mode : bool
        Flag indicating whether to discuss specifications with AI before implementation.
    self_heal_mode : bool
        Flag indicating whether to enable self-healing mode.
    azure_endpoint : str
        The endpoint for Azure OpenAI services.
    use_custom_preprompts : bool
        Flag indicating whether to use custom preprompts.
    verbose : bool
        Flag indicating whether to enable verbose logging.

    Returns
    -------
    None
    """

    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    if improve_mode:
        assert not (
            clarify_mode or lite_mode
        ), "Clarify and lite mode are not active for improve mode"

    load_env_if_needed()

    if llm_via_clipboard:
        ai = ClipboardAI()
    else:
        ai = AI(
            model_name=model,
            temperature=temperature,
            azure_endpoint=azure_endpoint,
        )

    path = Path(project_path)
    print("Running gpt-engineer in", path.absolute(), "\n")

    # Check if there's a git repo and verify that there aren't any uncommitted changes
    if is_git_installed():
        if not is_git_repo(path) and not improve_mode:
            print("Initializing an empty git repository")
            init_git_repo(path)

    prompt = load_prompt(DiskMemory(path), improve_mode)

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

    improve_fn = improve

    preprompts_path = get_preprompts_path(use_custom_preprompts, Path(project_path))
    preprompts_holder = PrepromptsHolder(preprompts_path)
    memory = DiskMemory(memory_path(project_path))
    execution_env = DiskExecutionEnv()
    agent = CliAgent.with_default_config(
        memory,
        execution_env,
        ai=ai,
        code_gen_fn=code_gen_fn,
        improve_fn=improve_fn,
        process_code_fn=execution_fn,
        preprompts_holder=preprompts_holder,
    )

    store = FileStore(project_path)
    if improve_mode:
        fileselector = FileSelector(project_path)
        original_files_dict = fileselector.ask_for_files()
        files_dict = handle_improve_mode(prompt, agent, memory, original_files_dict)
        if not files_dict or original_files_dict == files_dict:
            print(
                f"No changes applied. Could you please upload the debug_log_file.txt in {memory.path} folder to github?"
            )
            return
        if not prompt_yesno("\nDo you want to apply these changes?"):
            return

    else:
        files_dict = agent.init(prompt)
        # collect user feedback if user consents
        config = (code_gen_fn.__name__, execution_fn.__name__)
        collect_and_send_human_review(prompt, model, temperature, config, agent.memory)

    if is_git_repo(path):
        # Ask whether user wants to stage uncommitted files before overwriting them
        modified_files = filter_files_with_uncommitted_changes(path, files_dict)
        if modified_files:
            print(
                "Staging the following uncommitted files before overwriting: ",
                ", ".join(modified_files),
            )
            stage_files(path, modified_files)

    store.upload(files_dict)

    print("Total api cost: $ ", ai.token_usage_log.usage_cost())


if __name__ == "__main__":
    app()
