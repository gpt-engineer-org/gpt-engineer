import typer
from dotenv import load_dotenv


from gpt_engineer.applications.feature_cli.agents.feature_agent import (
    FeatureAgent,
)
from gpt_engineer.applications.feature_cli.agents.chat_agent import ChatAgent
from gpt_engineer.applications.feature_cli.feature import Feature
from gpt_engineer.applications.feature_cli.repository import Repository
from gpt_engineer.applications.feature_cli.domain import Settings
from gpt_engineer.applications.feature_cli.file_selection import FileSelector


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
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging for debugging."
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Enable debug mode for debugging."
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

    if new:
        agent.initialize_feature()
    else:
        agent.update_feature()


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

    feature = Feature(project_path, repository)

    file_selector = FileSelector(project_path, repository)

    agent = FeatureAgent(ai, project_path, feature, repository, file_selector)

    agent.run_task()
