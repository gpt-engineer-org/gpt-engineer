"""
Entrypoint for the CLI tool.

This module serves as the entry point for a command-line interface (CLI) tool.
It is designed to interact with OpenAI's language models.
The module provides functionality to:
- Load necessary environment variables,
- Configure various parameters for the AI interaction,
- Manage the generation or improvement of code projects.

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

import difflib
import json
import logging
import os
import platform
import subprocess
import sys

from pathlib import Path

import openai
import typer

from dotenv import load_dotenv
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from termcolor import colored

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
    improve_fn as improve_fn,
)
from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.git import stage_uncommitted_to_git
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.core.prompt import Prompt
from gpt_engineer.tools.custom_steps import clarified_gen, lite_gen, self_heal

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]}
)  # creates a CLI app


def load_env_if_needed():
    """
    Load environment variables if the OPENAI_API_KEY is not already set.

    This function checks if the OPENAI_API_KEY environment variable is set,
    and if not, it attempts to load it from a .env file in the current working
    directory. It then sets the openai.api_key for use in the application.
    """
    # We have all these checks for legacy reasons...
    if os.getenv("OPENAI_API_KEY") is None:
        load_dotenv()
    if os.getenv("OPENAI_API_KEY") is None:
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

    openai.api_key = os.getenv("OPENAI_API_KEY")

    if os.getenv("ANTHROPIC_API_KEY") is None:
        load_dotenv()
    if os.getenv("ANTHROPIC_API_KEY") is None:
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))


def validate_api_key_format(key_name: str, key_value: str) -> tuple[bool, str]:
    """
    Validate the format of an API key.
    
    Parameters
    ----------
    key_name : str
        The name of the API key environment variable.
    key_value : str
        The value of the API key to validate.
    
    Returns
    -------
    tuple[bool, str]
        A tuple of (is_valid, error_message). If valid, error_message is empty.
    """
    if not key_value:
        return False, f"{key_name} is empty"
    
    # Check minimum length (most API keys are at least 20 characters)
    if len(key_value) < 20:
        return False, f"{key_name} appears too short (length: {len(key_value)}). Please check your API key."
    
    # Check for common mistakes
    if key_value.startswith("your-"):
        return False, f"{key_name} appears to be a placeholder. Please use your actual API key."
    
    if key_value == "...":
        return False, f"{key_name} is a placeholder. Please set your actual API key."
    
    # Validate specific formats for known providers
    if key_name == "OPENAI_API_KEY":
        # OpenAI keys typically start with 'sk-' or 'sk-proj-'
        if not (key_value.startswith("sk-") or key_value.startswith("Bearer ")):
            return False, f"{key_name} should start with 'sk-' (found: '{key_value[:10]}...')"
    
    elif key_name == "ANTHROPIC_API_KEY":
        # Anthropic keys typically start with 'sk-ant-'
        if not key_value.startswith("sk-ant-"):
            return False, f"{key_name} should start with 'sk-ant-' (found: '{key_value[:10]}...')"
    
    return True, ""


def validate_api_configuration(
    model: str,
    azure_endpoint: str,
    llm_via_clipboard: bool
) -> None:
    """
    Validate API configuration before execution.
    
    This function checks if the required API keys are set and properly formatted
    based on the selected model and configuration. It provides clear error messages
    with actionable suggestions if validation fails.
    
    Parameters
    ----------
    model : str
        The model name to use (e.g., 'gpt-4', 'claude-3-opus-20240229').
    azure_endpoint : str
        The Azure OpenAI endpoint URL (if using Azure).
    llm_via_clipboard : bool
        Whether using clipboard mode (skips API key validation).
    
    Raises
    ------
    typer.Exit
        If validation fails, exits with code 1 and displays error message.
    """
    # Skip validation for clipboard mode
    if llm_via_clipboard:
        return
    
    # Skip validation for local models
    if os.getenv("LOCAL_MODEL"):
        return
    
    # Determine which API key is needed based on model and configuration
    required_key = None
    key_value = None
    provider_name = ""
    setup_instructions = ""
    
    if azure_endpoint:
        # Azure OpenAI
        required_key = "AZURE_OPENAI_API_KEY"
        key_value = os.getenv(required_key)
        provider_name = "Azure OpenAI"
        setup_instructions = (
            "1. Get your API key from Azure Portal (https://portal.azure.com)\n"
            "2. Set it using: export AZURE_OPENAI_API_KEY='your-key'\n"
            "3. Or add it to a .env file in your project directory"
        )
    elif "claude" in model.lower() or "anthropic" in model.lower():
        # Anthropic
        required_key = "ANTHROPIC_API_KEY"
        key_value = os.getenv(required_key)
        provider_name = "Anthropic"
        setup_instructions = (
            "1. Get your API key from https://console.anthropic.com/\n"
            "2. Set it using: export ANTHROPIC_API_KEY='your-key'\n"
            "3. Or add it to a .env file in your project directory"
        )
    else:
        # OpenAI (default)
        required_key = "OPENAI_API_KEY"
        key_value = os.getenv(required_key)
        provider_name = "OpenAI"
        setup_instructions = (
            "1. Get your API key from https://platform.openai.com/api-keys\n"
            "2. Set it using: export OPENAI_API_KEY='your-key'\n"
            "3. Or add it to a .env file in your project directory"
        )
    
    # Check if API key is set
    if not key_value:
        error_msg = (
            f"\n{colored('Error:', 'red')} {required_key} is not set.\n\n"
            f"To use {provider_name} with model '{model}', you need to configure your API key:\n\n"
            f"{setup_instructions}\n\n"
            f"For more information, see: {colored('README.md', 'cyan')}"
        )
        print(error_msg)
        raise typer.Exit(code=1)
    
    # Validate API key format
    is_valid, error_message = validate_api_key_format(required_key, key_value)
    if not is_valid:
        error_msg = (
            f"\n{colored('Error:', 'red')} {error_message}\n\n"
            f"Please check your {required_key} and ensure it's set correctly.\n\n"
            f"To update your API key:\n"
            f"{setup_instructions}\n"
        )
        print(error_msg)
        raise typer.Exit(code=1)
    
    # Success - API key is set and appears valid
    logging.debug(f"API key validation passed for {provider_name}")


def concatenate_paths(base_path, sub_path):
    # Compute the relative path from base_path to sub_path
    relative_path = os.path.relpath(sub_path, base_path)

    # If the relative path is not in the parent directory, use the original sub_path
    if not relative_path.startswith(".."):
        return sub_path

    # Otherwise, concatenate base_path and sub_path
    return os.path.normpath(os.path.join(base_path, sub_path))


def load_prompt(
    input_repo: DiskMemory,
    improve_mode: bool,
    prompt_file: str,
    image_directory: str,
    entrypoint_prompt_file: str = "",
) -> Prompt:
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

    if os.path.isdir(prompt_file):
        raise ValueError(
            f"The path to the prompt, {prompt_file}, already exists as a directory. No prompt can be read from it. Please specify a prompt file using --prompt_file"
        )
    prompt_str = input_repo.get(prompt_file)
    if prompt_str:
        print(colored("Using prompt from file:", "green"), prompt_file)
        print(prompt_str)
    else:
        if not improve_mode:
            prompt_str = input(
                "\nWhat application do you want gpt-engineer to generate?\n"
            )
        else:
            prompt_str = input("\nHow do you want to improve the application?\n")

    if entrypoint_prompt_file == "":
        entrypoint_prompt = ""
    else:
        full_entrypoint_prompt_file = concatenate_paths(
            input_repo.path, entrypoint_prompt_file
        )
        if os.path.isfile(full_entrypoint_prompt_file):
            entrypoint_prompt = input_repo.get(full_entrypoint_prompt_file)

        else:
            raise ValueError("The provided file at --entrypoint-prompt does not exist")

    if image_directory == "":
        return Prompt(prompt_str, entrypoint_prompt=entrypoint_prompt)

    full_image_directory = concatenate_paths(input_repo.path, image_directory)
    if os.path.isdir(full_image_directory):
        if len(os.listdir(full_image_directory)) == 0:
            raise ValueError("The provided --image_directory is empty.")
        image_repo = DiskMemory(full_image_directory)
        return Prompt(
            prompt_str,
            image_repo.get(".").to_dict(),
            entrypoint_prompt=entrypoint_prompt,
        )
    else:
        raise ValueError("The provided --image_directory is not a directory.")


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


def compare(f1: FilesDict, f2: FilesDict):
    def colored_diff(s1, s2):
        lines1 = s1.splitlines()
        lines2 = s2.splitlines()

        diff = difflib.unified_diff(lines1, lines2, lineterm="")

        RED = "\033[38;5;202m"
        GREEN = "\033[92m"
        RESET = "\033[0m"

        colored_lines = []
        for line in diff:
            if line.startswith("+"):
                colored_lines.append(GREEN + line + RESET)
            elif line.startswith("-"):
                colored_lines.append(RED + line + RESET)
            else:
                colored_lines.append(line)

        return "\n".join(colored_lines)

    for file in sorted(set(f1) | set(f2)):
        diff = colored_diff(f1.get(file, ""), f2.get(file, ""))
        if diff:
            print(f"Changes to {file}:")
            print(diff)


def prompt_yesno() -> bool:
    TERM_CHOICES = colored("y", "green") + "/" + colored("n", "red") + " "
    while True:
        response = input(TERM_CHOICES).strip().lower()
        if response in ["y", "yes"]:
            return True
        if response in ["n", "no"]:
            break
        print("Please respond with 'y' or 'n'")


def get_system_info():
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "packages": format_installed_packages(get_installed_packages()),
    }
    return system_info


def get_installed_packages():
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
        )
        packages = json.loads(result.stdout)
        return {pkg["name"]: pkg["version"] for pkg in packages}
    except Exception as e:
        return str(e)


def format_installed_packages(packages):
    return "\n".join([f"{name}: {version}" for name, version in packages.items()])


@app.command(
    help="""
        GPT-engineer lets you:

        \b
        - Specify a software in natural language
        - Sit back and watch as an AI writes and executes the code
        - Ask the AI to implement improvements
    """
)
def main(
    project_path: str = typer.Argument(".", help="path"),
    model: str = typer.Option(
        os.environ.get("MODEL_NAME", "gpt-4o"), "--model", "-m", help="model id string"
    ),
    temperature: float = typer.Option(
        0.1,
        "--temperature",
        "-t",
        help="Controls randomness: lower values for more focused, deterministic outputs",
    ),
    improve_mode: bool = typer.Option(
        False,
        "--improve",
        "-i",
        help="Improve an existing project by modifying the files.",
    ),
    lite_mode: bool = typer.Option(
        False,
        "--lite",
        "-l",
        help="Lite mode: run a generation using only the main prompt.",
    ),
    clarify_mode: bool = typer.Option(
        False,
        "--clarify",
        "-c",
        help="Clarify mode - discuss specification with AI before implementation.",
    ),
    self_heal_mode: bool = typer.Option(
        False,
        "--self-heal",
        "-sh",
        help="Self-heal mode - fix the code by itself when it fails.",
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
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging for debugging."
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Enable debug mode for debugging."
    ),
    prompt_file: str = typer.Option(
        "prompt",
        "--prompt_file",
        help="Relative path to a text file containing a prompt.",
    ),
    entrypoint_prompt_file: str = typer.Option(
        "",
        "--entrypoint_prompt",
        help="Relative path to a text file containing a file that specifies requirements for you entrypoint.",
    ),
    image_directory: str = typer.Option(
        "",
        "--image_directory",
        help="Relative path to a folder containing images.",
    ),
    use_cache: bool = typer.Option(
        False,
        "--use_cache",
        help="Speeds up computations and saves tokens when running the same prompt multiple times by caching the LLM response.",
    ),
    skip_file_selection: bool = typer.Option(
        False,
        "--skip-file-selection",
        "-s",
        help="Skip interactive file selection in improve mode and use the generated TOML file directly.",
    ),
    no_execution: bool = typer.Option(
        False,
        "--no_execution",
        help="Run setup but to not call LLM or write any code. For testing purposes.",
    ),
    sysinfo: bool = typer.Option(
        False,
        "--sysinfo",
        help="Output system information for debugging",
    ),
    diff_timeout: int = typer.Option(
        3,
        "--diff_timeout",
        help="Diff regexp timeout. Default: 3. Increase if regexp search timeouts.",
    ),
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
    prompt_file : str
        Relative path to a text file containing a prompt.
    entrypoint_prompt_file: str
        Relative path to a text file containing a file that specifies requirements for you entrypoint.
    image_directory: str
        Relative path to a folder containing images.
    use_cache: bool
        Speeds up computations and saves tokens when running the same prompt multiple times by caching the LLM response.
    verbose : bool
        Flag indicating whether to enable verbose logging.
    skip_file_selection: bool
        Skip interactive file selection in improve mode and use the generated TOML file directly
    no_execution: bool
        Run setup but to not call LLM or write any code. For testing purposes.
    sysinfo: bool
        Flag indicating whether to output system information for debugging.

    Returns
    -------
    None
    """

    if debug:
        import pdb

        sys.excepthook = lambda *_: pdb.pm()

    if sysinfo:
        sys_info = get_system_info()
        for key, value in sys_info.items():
            print(f"{key}: {value}")
        raise typer.Exit()

    # Validate arguments
    if improve_mode and (clarify_mode or lite_mode):
        typer.echo("Error: Clarify and lite mode are not compatible with improve mode.")
        raise typer.Exit(code=1)

    # Set up logging
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    if use_cache:
        set_llm_cache(SQLiteCache(database_path=".langchain.db"))
    if improve_mode:
        assert not (
            clarify_mode or lite_mode
        ), "Clarify and lite mode are not active for improve mode"

    load_env_if_needed()

    # Validate API configuration before creating AI
    validate_api_configuration(model, azure_endpoint, llm_via_clipboard)

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

    prompt = load_prompt(
        DiskMemory(path),
        improve_mode,
        prompt_file,
        image_directory,
        entrypoint_prompt_file,
    )

    # todo: if ai.vision is false and not llm_via_clipboard - ask if they would like to use gpt-4-vision-preview instead? If so recreate AI
    if not ai.vision:
        prompt.image_urls = None

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

    preprompts_holder = PrepromptsHolder(
        get_preprompts_path(use_custom_preprompts, Path(project_path))
    )

    memory = DiskMemory(memory_path(project_path))
    memory.archive_logs()

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

    files = FileStore(project_path)
    if not no_execution:
        if improve_mode:
            files_dict_before, is_linting = FileSelector(project_path).ask_for_files(
                skip_file_selection=skip_file_selection
            )

            # lint the code
            if is_linting:
                files_dict_before = files.linting(files_dict_before)

            files_dict = handle_improve_mode(
                prompt, agent, memory, files_dict_before, diff_timeout=diff_timeout
            )
            if not files_dict or files_dict_before == files_dict:
                print(
                    f"No changes applied. Could you please upload the debug_log_file.txt in {memory.path}/logs folder in a github issue?"
                )

            else:
                print("\nChanges to be made:")
                compare(files_dict_before, files_dict)

                print()
                print(colored("Do you want to apply these changes?", "light_green"))
                if not prompt_yesno():
                    files_dict = files_dict_before

        else:
            files_dict = agent.init(prompt)
            # collect user feedback if user consents
            config = (code_gen_fn.__name__, execution_fn.__name__)
            collect_and_send_human_review(prompt, model, temperature, config, memory)

        stage_uncommitted_to_git(path, files_dict, improve_mode)

        files.push(files_dict)

    if ai.token_usage_log.is_openai_model():
        print("Total api cost: $ ", ai.token_usage_log.usage_cost())
    elif os.getenv("LOCAL_MODEL"):
        print("Total api cost: $ 0.0 since we are using local LLM.")
    else:
        print("Total tokens used: ", ai.token_usage_log.total_tokens())


if __name__ == "__main__":
    app()
