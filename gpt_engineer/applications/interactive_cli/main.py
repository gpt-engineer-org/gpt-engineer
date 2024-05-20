import typer
from dotenv import load_dotenv

from gpt_engineer.applications.interactive_cli.agent import FeatureAgent
from gpt_engineer.applications.interactive_cli.feature import Feature
from gpt_engineer.applications.interactive_cli.repository import Repository
from gpt_engineer.applications.interactive_cli.domain import Settings

from gpt_engineer.core.ai import AI

app = typer.Typer()


@app.command()
def main(
    project_path: str = typer.Argument(".", help="path"),
    model: str = typer.Argument("gpt-4-turbo", help="model id string"),
    new: bool = typer.Option(False, "--new", "-n", help="Initialize new feature."),
    no_branch: bool = typer.Option(
        False,
        "--no-branch",
        "-nb",
        help="Do not create a new feature branch for this work.",
    ),
    temperature: float = typer.Option(
        0.1,
        "--temperature",
        "-t",
        help="Controls randomness: lower values for more focused, deterministic outputs",
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
):
    """
    Run GPTE Interactive Improve
    """

    load_dotenv()

    # todo: check that git repo exists. If not - ask the user to create a git repository with a suitable git ignore which will be used to reduce ai usage
    # todo: check that git repo is clean. If not - ask the user to stash or commit changes.

    ai = AI(
        model_name=model,
        temperature=temperature,
        azure_endpoint=azure_endpoint,
    )

    repository = Repository(project_path)

    feature = Feature(project_path)

    agent = FeatureAgent(project_path, feature, repository, ai)

    settings = Settings(no_branch)

    if new:
        agent.init(settings)
    else:
        agent.resume(settings)


if __name__ == "__main__":
    app()
