import typer
from dotenv import load_dotenv
from pathlib import Path
from gpt_engineer.core.default.paths import memory_path

from gpt_engineer.applications.interactive_cli_loop.agents.task_agent import TaskAgent
from gpt_engineer.applications.interactive_cli_loop.agents.feature_agent import (
    FeatureAgent,
)
from gpt_engineer.applications.interactive_cli_loop.agents.chat_agent import ChatAgent
from gpt_engineer.applications.interactive_cli_loop.feature import Feature
from gpt_engineer.applications.interactive_cli_loop.task import Task
from gpt_engineer.applications.interactive_cli_loop.repository import Repository
from gpt_engineer.applications.interactive_cli_loop.domain import Settings
from gpt_engineer.applications.interactive_cli_loop.file_selection import FileSelector


from gpt_engineer.core.ai import AI

app = typer.Typer()


@app.command()
def feature(
    new: bool = typer.Option(False, "--new", "-n", help="Initialize a new feature."),
    project_path: str = typer.Option(".", "--path", "-p", help="Path to the project."),
    model: str = typer.Option("gpt-4o", "--model", "-m", help="Model ID string."),
    temperature: float = typer.Option(
        0.1,
        "--temperature",
        "-t",
        help="Controls randomness: lower values for more focused, deterministic outputs.",
    ),
    azure_endpoint: str = typer.Option(
        "",
        "--azure",
        "-a",
        help="""Endpoint for your Azure OpenAI Service (https://xx.openai.azure.com).
                In that case, the given model is the deployment name chosen in the Azure AI Studio.""",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging for debugging."
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Enable debug mode for debugging."
    ),
    no_branch: bool = typer.Option(
        False,
        "--no-branch",
        "-nb",
        help="Do not create a new feature branch for this work.",
    ),
):
    """
    Handle features in the project.
    """
    load_dotenv()

    ai = AI(
        model_name=model,
        temperature=temperature,
    )

    repository = Repository(project_path)

    feature = Feature(project_path, repository)

    file_selector = FileSelector(project_path, repository)

    agent = FeatureAgent(ai, project_path, feature, repository, file_selector)

    settings = Settings(no_branch)

    if new:
        agent.init(settings)
    else:
        agent.resume(settings)


@app.command()
def chat(
    project_path: str = typer.Option(".", "--path", "-p", help="Path to the project."),
    model: str = typer.Option("gpt-4o", "--model", "-m", help="Model ID string."),
    temperature: float = typer.Option(
        0.8,
        "--temperature",
        "-t",
        help="Controls randomness: lower values for more focused, deterministic outputs.",
    ),
):
    """
    Initiate a chat about the current repository and feature context
    """
    ai = AI(
        model_name=model,
        temperature=temperature,
    )

    repository = Repository(project_path)

    feature = Feature(project_path, repository)

    file_selector = FileSelector(project_path, repository)

    chat_agent = ChatAgent(ai, project_path, feature, repository, file_selector)

    chat_agent.start()


if __name__ == "__main__":
    app()


@app.command()
def task(
    project_path: str = typer.Option(".", "--path", "-p", help="Path to the project."),
    model: str = typer.Option("gpt-4o", "--model", "-m", help="Model ID string."),
    temperature: float = typer.Option(
        0.1,
        "--temperature",
        "-t",
        help="Controls randomness: lower values for more focused, deterministic outputs.",
    ),
):
    """
    Implement a simple one off task without feature context
    """
    load_dotenv()

    ai = AI(
        model_name=model,
        temperature=temperature,
    )

    repository = Repository(project_path)

    task = Task(project_path)

    file_selector = FileSelector(project_path, repository)

    task_agent = TaskAgent(ai, project_path, task, repository, file_selector)

    task_agent.run()

    # review

    # task.delete()
