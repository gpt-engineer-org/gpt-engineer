import typer
from dotenv import load_dotenv

import os
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError

app = typer.Typer()

class FeatureValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text:
            raise ValidationError(message="Feature description cannot be empty", cursor_position=len(text))

def load_feature_description(feature_file_path):
    """
    Load the feature description from a file or prompt the user if the file doesn't exist.
    """
    if os.path.exists(feature_file_path):
        with open(feature_file_path, 'r', encoding='utf-8') as file:
            feature_description = file.read().strip()
    else:
        print(f"No feature file found at {feature_file_path}. Please enter the feature description:")
        feature_description = prompt("Feature: ", validator=FeatureValidator())
        # todo: create feature text file containing the users feature 
         

    return feature_description

@app.command()
def main(
    project_path: str = typer.Argument(".", help="path"),
    model: str = typer.Argument("gpt-4-turbo", help="model id string"),
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
      
    feature_description = load_feature_description(os.path.join(project_path, 'feature'))

    branch_name= 'feature/new' #todo: use ai to generate branch name suggestion

    print("Great, sounds like a useful feature.")
    branch_name = prompt('Please confirm or edit the feature branch name: ', default=branch_name)
    print(f'Creating feature branch: {branch_name}')
    #todo: use gitpython to create new branch. 

    # todo: continue with the rest of the task creation flow. Every time a task is added move it to 



if __name__ == "__main__":
    app()