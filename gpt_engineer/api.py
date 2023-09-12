import os

from pathlib import Path

from agent_protocol import Agent, Step, Task

from gpt_engineer.db import DB
from gpt_engineer.main import main


async def task_handler(task: Task) -> None:
    """task_handler should create initial steps based on the input.

    The project is set up here.

    The prompt will be sent as task.input.
    We will create a working directory in projects/<task_id>.
    """

    # make sure we have a prompt or bail.
    assert task.input is not None, "No input prompt in the 'input' field."

    workspace = DB(f"projects/{task.task_id}")

    # write prompt to a file
    workspace["prompt"] = f"{task.input}\n"

    # write to consent file so we avoid hanging for a prompt
    consent_file = Path(os.getcwd()) / ".gpte_consent"
    consent_file.write_text("false")

    print("Options: task.additional_input: ", task.additional_input)

    # TODO: disable feedback prompt

    await Agent.db.create_artifact(
        task_id=task.task_id,
        relative_path="projects/",
        file_name=f"projects/{task.task_id}",
    )

    await Agent.db.create_step(task_id=task.task_id, name="create_code", is_last=True)


async def step_handler(step: Step) -> Step:
    # run the code here.
    main(
        f"projects/{step.task_id}",
        "gpt-4",
        0.1,
        "benchmark",  # this needs to be headless mode
        False,
        "",
        False,
    )

    return step


Agent.setup_agent(task_handler, step_handler).start()
