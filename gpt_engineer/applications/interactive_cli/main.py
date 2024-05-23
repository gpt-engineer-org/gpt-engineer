import typer
from dotenv import load_dotenv

from gpt_engineer.applications.interactive_cli.agents.feature_agent import FeatureAgent
from gpt_engineer.applications.interactive_cli.agents.chat_agent import ChatAgent
from gpt_engineer.applications.interactive_cli.feature import Feature
from gpt_engineer.applications.interactive_cli.repository import Repository
from gpt_engineer.applications.interactive_cli.domain import Settings

from gpt_engineer.core.ai import AI

app = typer.Typer()


# @app.command()
# def task(
#     new: bool = typer.Option(False, "--new", "-n", help="Initialize a new task."),
#     **options,
# ):
#     """
#     Handle tasks in the project.
#     """
#     # TO BE IMPLEMENTED


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

    agent = FeatureAgent(ai, project_path, feature, repository)

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
    Initiate a chat about the current repository.
    """
    ai = AI(
        model_name=model,
        temperature=temperature,
    )

    repository = Repository(project_path)

    feature = Feature(project_path, repository)
    chat_agent = ChatAgent(ai, project_path, feature, repository)

    chat_agent.start()


if __name__ == "__main__":
    app()
