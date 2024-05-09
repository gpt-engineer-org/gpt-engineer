import typer
from dotenv import load_dotenv
from ticket import Ticket

from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError

from gpt_engineer.core.ai import AI

from generation_tools import generate_branch_name, generate_suggested_tasks
from git_context import GitContext

app = typer.Typer()

class FeatureValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text:
            raise ValidationError(message="Feature description cannot be empty", cursor_position=len(text))


def initialize_new_feature(ai, ticket): 
    
    ticket.clear_ticket()

    feature_description = prompt(
            "Write feature description: ",
            multiline=True,
            validator=FeatureValidator(),
            bottom_toolbar="Press Ctrl+O to finish"
        )
    
    ticket.feature = feature_description
    ticket.save_feature()
    
    # print("\n Ticket files created at .ticket \n ")

    branch_name = generate_branch_name(ai, feature_description)

    branch_name = prompt('\nConfirm branch name: ', default=branch_name)

    # todo: use gitpython to create new branch. 
    
    print(f'\nFeature branch created.\n')


def get_context_string(ticket, git_context, code):
    input = f""" 
## Feature
{ticket.feature}

## Completed Tasks 
{ticket.progress.done}

## Git Context
### Commits 
{git_context.commits}

### Staged Changes
{git_context.staged_changes}

## Current Codebase
{code}
"""
    

def choose_next_task(ai, ticket, context):
    print(f"There are {len(ticket.progress.done)} tasks completed so far. What shall we do next?")

    suggested_tasks  = generate_suggested_tasks




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

    ticket = Ticket.load_or_create_at_directory(project_path)

    if new:
        initialize_new_feature(ai, ticket)

    git_context = GitContext.load_from_directory(project_path)

    print(git_context.staged_changes)
    print(git_context.unstaged_changes)
    for commit in git_context.commits:
        print(commit)
        print()

    # todo: continue with the rest of the task creation flow. Every time a task is added move it to a task file



if __name__ == "__main__":
    app()