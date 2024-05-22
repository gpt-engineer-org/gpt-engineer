import typer
from dotenv import load_dotenv

from gpt_engineer.applications.interactive_cli.agents.feature_agent import FeatureAgent
from gpt_engineer.applications.interactive_cli.feature import Feature
from gpt_engineer.applications.interactive_cli.repository import Repository
from gpt_engineer.applications.interactive_cli.domain import Settings

from gpt_engineer.core.ai import AI

app = typer.Typer()


def common_options(
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
):
    return {
        "project_path": project_path,
        "model": model,
        "no_branch": no_branch,
        "temperature": temperature,
        "azure_endpoint": azure_endpoint,
        "verbose": verbose,
        "debug": debug,
    }


@app.command()
def task(
    new: bool = typer.Option(False, "--new", "-n", help="Initialize a new task."),
    **options,
):
    """
    Handle tasks in the project.
    """
    load_dotenv()
    options = common_options(**options)

    ai = AI(
        model_name=options["model"],
        temperature=options["temperature"],
        azure_endpoint=options["azure_endpoint"],
    )

    repository = Repository(options["project_path"])

    feature = Feature(options["project_path"])

    agent = FeatureAgent(options["project_path"], feature, repository, ai)

    settings = Settings(options["no_branch"])

    if new:
        agent.init(settings)
    else:
        agent.resume(settings)


@app.command()
def feature(
    new: bool = typer.Option(False, "--new", "-n", help="Initialize a new feature."),
    no_branch: bool = typer.Option(
        False,
        "--no-branch",
        "-nb",
        help="Do not create a new feature branch for this work.",
    ),
    **options,
):
    """
    Handle features in the project.
    """
    load_dotenv()
    options = common_options(**options)

    ai = AI(
        model_name=options["model"],
        temperature=options["temperature"],
        azure_endpoint=options["azure_endpoint"],
    )

    repository = Repository(options["project_path"])

    feature = Feature(options["project_path"], repository)

    agent = FeatureAgent(feature, repository, ai)

    settings = Settings(no_branch)

    if new:
        agent.init(settings)
    else:
        agent.resume(settings)


@app.command()
def chat(**options):
    """
    Initiate a chat about the current repository.
    """
    load_dotenv()
    options = common_options(**options)

    ai = AI(
        model_name=options["model"],
        temperature=options["temperature"],
        azure_endpoint=options["azure_endpoint"],
    )

    repository = Repository(options["project_path"])

    # Add the logic for initiating a chat here
    typer.echo(
        f"Initiating a chat about the repo at {options['project_path']} using model {options['model']}."
    )


if __name__ == "__main__":
    app()
