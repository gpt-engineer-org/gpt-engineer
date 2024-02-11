"""
Entrypoint for the CLI tool.

Main Functionality:
---------------------
- Load environment variables needed to work with OpenAI.
- Allow users to specify parameters such as:
  - Project path
  - LLM
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

import logging
import os

from pathlib import Path

import openai
import typer

from dotenv import load_dotenv

from gpt_engineer.applications.cli.cli_agent import CliAgent
from gpt_engineer.applications.cli.collect import collect_and_send_human_review
from gpt_engineer.applications.cli.file_selector import FileSelector
from gpt_engineer.core.ai import AI
from gpt_engineer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.file_store import FileStore
from gpt_engineer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_engineer.core.default.steps import execute_entrypoint, gen_code, improve
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.tools.custom_steps import clarified_gen, lite_gen, self_heal

app = typer.Typer()  # creates a CLI app


def load_env_if_needed():
    if os.getenv("OPENAI_API_KEY") is None:
        load_dotenv()
    if os.getenv("OPENAI_API_KEY") is None:
        # if there is no .env file, try to load from the current working directory
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))
    openai.api_key = os.getenv("OPENAI_API_KEY")


def load_prompt(input_repo: DiskMemory, improve_mode, direct_prompt: Optional[str] = None):
    if input_repo.get("prompt"):
        return direct_prompt if direct_prompt is not None else input_repo.get("prompt")

    if not improve_mode:
        input_repo["prompt"] = input(
            "\nWhat application do you want gpt-engineer to generate?\n"
        )
    else:
        input_repo["prompt"] = input("\nHow do you want to improve the application?\n")
    return direct_prompt if direct_prompt is not None else input_repo.get("prompt")


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
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Enter interactive mode to chat with the codebase."),
    create_new: bool = typer.Option(False, "--create", "-n", help="Create a new codebase."),
    improve_existing: bool = typer.Option(False, "--improve", "-e", help="Improve an existing codebase."),
    project_path: str = typer.Option(None, prompt="Enter the directory path for the codebase:", help="The directory path where the new or existing codebase is located."),
    direct_prompt: Optional[str] = typer.Option(None, prompt="Enter your prompt:", help="Directly input the prompt instead of using a prompt file."),
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
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """
    Generates a project from a prompt in PROJECT_PATH/prompt,
    or improves an existing project (with -i) in PROJECT_PATH.

    See README.md for more details.
    """
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    #

    if improve_existing:
        if project_path is None:
            project_path = input("Enter the directory path for the existing codebase to improve:")
        improve_mode = True
    elif create_new:
        if project_path is None:
            project_path = input("Enter the directory path where the new codebase should be created:")
        improve_mode = False
    else:
        typer.echo("You must choose to either create a new codebase or improve an existing one.")
        raise typer.Exit()
        assert not (
            clarify_mode or lite_mode
        ), "Clarify and lite mode are not active for improve mode"

    load_env_if_needed()

    ai = AI(
        model_name=model,
        temperature=temperature,
        azure_endpoint=azure_endpoint,
    )

    path = Path(project_path)
    print("Running gpt-engineer in", path.absolute(), "\n")
    prompt = load_prompt(DiskMemory(path), improve_mode, direct_prompt)

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
    if interactive:
        start_interactive_session(agent, path)
        return
    elif improve_mode:
        fileselector = FileSelector(project_path)
        files_dict = fileselector.ask_for_files()
        files_dict = agent.improve(files_dict, prompt)
    else:
        files_dict = agent.init(prompt)
        # collect user feedback if user consents
        config = (code_gen_fn.__name__, execution_fn.__name__)
        collect_and_send_human_review(prompt, model, temperature, config, agent.memory)

    store.upload(files_dict)

    print("Total api cost: $ ", ai.token_usage_log.usage_cost())


def start_interactive_session(agent: CliAgent, project_path: Path):
    """Starts an interactive session for live codebase interaction."""
    typer.echo("Entering interactive mode. Type 'exit' to end the session.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = agent.interact(user_input)
        typer.echo(f"AI: {response}")

if __name__ == "__main__":
    app()
