import typer
from dotenv import load_dotenv
from ticket import Ticket

from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError

from gpt_engineer.core.ai import AI
from gpt_engineer.core.prompt import Prompt

from generation_tools import  generate_suggested_tasks
from repository import Repository, GitContext
from file_selection import FileSelection
from files import Files
from agent import FeatureAgent
from feature import Feature

app = typer.Typer()


def get_contenxt_string(feature:Feature ,git_context:GitContext):
        return f"""I am working on a feature but breaking it up into small incremental tasks. Your job is to complete the incremental task provided to you - only that task and nothign more. 
        
The purpose of this message is to give you wider context around the feature you are working on and what incremental tasks have already been completed so far.

## Feature - this is the description fo the current feature we are working on.
{feature.get_description()}

## Completed Tasks - these are the lists of tasks you have completed so far on the feature branch.
{feature.get_progress()["done"]}

## Git Context - these are the code changes made so far while implementing this feature. This may include work completed by you on previous tasks as well as changes made independently by me.
### Branch Changes - this is the cumulative diff of all the commits so far on the feature branch. 
{git_context.branch_changes}

### Staged Changes - this is the diff of the current staged changes. 
{git_context.staged_changes}
"""

def get_full_context_string(ticket, git_context, files: Files):
    return f"""{get_contenxt_string(ticket, git_context)}

## Current Codebase - this is the as is view of the current code base including any unstaged changes. 
{files.to_chat()}
"""
    

def choose_next_task(ai, ticket, git_context: GitContext, files: Files):
    print(f"There are {len(ticket.progress.done)} tasks completed so far. What shall we do next?")

    context_string = get_full_context_string(ticket, git_context, files)

    suggested_tasks_xml  = generate_suggested_tasks()


@app.command()
def main(
    project_path: str = typer.Argument(".", help="path"),
    model: str = typer.Argument("gpt-4-turbo", help="model id string"),
    new: bool = typer.Option(
        False, "--new", "-n", help="Initialize new feature."
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
    )
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

    if new:
        agent.init()
    else:
        agent.resume()

    
if __name__ == "__main__":
    app()