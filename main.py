import json
import os
import pathlib
from typing import Optional
import openai
from chat_to_files import to_files
from ai import AI
from steps import STEPS
from db import DB, DBs
import typer
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY") 
# Check if OPENAI_API_KEY is defined
if api_key == None:
    # Raise an error if OPENAI_API_KEY is not defined
    raise ValueError("OPENAI_API_KEY is not defined")
else:
    # Set the OPENAI_API_KEY to the api_key variable
    openai.api_key = api_key

# Get the OPENAI_API_BASE
api_base = os.getenv("OPENAI_API_BASE")
# Check if OPENAI_API_BASE is defined
if api_base != None:   
    # Set the OPENAI_API_BASE to the api_base variable
    openai.api_base = api_base

# Get the GPT model from the environment variable
gpt_model = os.getenv("gpt_model")
# Get the GPT temperature from the environment variable
gpt_temperature = os.getenv("gpt_temperature")

app = typer.Typer()


@app.command()
def chat(
    project_path: str = typer.Argument(None, help="path"),
    run_prefix: str = typer.Option("", help="run prefix, if you want to run multiple variants of the same project and later compare them"),
    model: str = gpt_model,
    temperature: float = gpt_temperature,
):

    if project_path is None:
        project_path = str(pathlib.Path(__file__).parent / "example")

    input_path = project_path
    memory_path = pathlib.Path(project_path) / (run_prefix + "memory")
    workspace_path = pathlib.Path(project_path) / (run_prefix + "workspace")

    ai = AI(
        model=model,
        temperature=temperature,
    )

    dbs = DBs(
        memory=DB(memory_path),
        logs=DB(pathlib.Path(memory_path) / "logs"),
        input=DB(input_path),
        workspace=DB(workspace_path),
        identity=DB(pathlib.Path(__file__).parent / "identity"),
    )


    for step in STEPS:
        messages = step(ai, dbs)
        dbs.logs[step.__name__] = json.dumps(messages)


if __name__ == "__main__":
    app()
