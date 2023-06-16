import json
import pathlib
import typer
from typing import Any

from gpt_engineer.ai import GPT, TestAI
from gpt_engineer.chat_to_files import to_files
from gpt_engineer.db import DB, DBs
from gpt_engineer.models import Message, Role, Step
from gpt_engineer.steps import STEPS

app = typer.Typer()


@app.command()
def chat(
    project_path: str = typer.Argument(None, help="path"),
    run_prefix: str = typer.Option(
        "",
        help="run prefix, if you want to run multiple variants of the same project and later compare them",
    ),
    model: str = "gpt-4",
    temperature: float = 0.1,
):
    app_dir = pathlib.Path(__file__).parent.parent
    if project_path is None:
        project_path = str(app_dir / "example")

    input_path = project_path
    memory_path = pathlib.Path(project_path) / (run_prefix + "memory")
    workspace_path = pathlib.Path(project_path) / (run_prefix + "workspace")

    # ai = GPT(
    #     model=model,
    #     temperature=temperature,
    # )
    ai = TestAI()

    dbs = DBs(
        memory=DB(memory_path),
        logs=DB(memory_path / "logs"),
        input=DB(input_path),
        workspace=DB(workspace_path),
        identity=DB(app_dir / "identity"),
    )

    for step in STEPS:
        messages = step(ai, dbs)
        dbs.logs[step.__name__] = json.dumps([output_message_from(r, m) for r, m in messages])


def output_message_from(r: Role, m: Message) -> Any:
    return {"role": str(r), "content": m.content}


def execute():
    app()


if __name__ == "__main__":
    execute()