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
    if task.input is None:
        raise Exception("No input prompt in the 'input' field.")

    workspace = DB(f"projects/{task.task_id}")

    # write prompt to a file
    workspace["prompt"] = f"{task.input}\n"

    # write to consent file so we avoid hanging for a prompt
    consent_file = Path(os.getcwd()) / ".gpte_consent"
    consent_file.write_text("false")

    await Agent.db.create_artifact(
        task_id=task.task_id,
        relative_path="projects/",
        file_name=f"projects/{task.task_id}",
    )

    # pass options onto additional_properties
    await Agent.db.create_step(
        task_id=task.task_id,
        name="create_code",
        is_last=True,
        additional_properties=task.additional_input.__root__,
    )


async def step_handler(step: Step) -> Step:
    """
    The code generation is run here.  Any options are passed via task.additional_input.

    Improve code mode is not yet supported, but it would not be much work to support it.
    A list of 'focus' files would need to be submitted in: task.additional_input.
    """

    main(
        f"projects/{step.task_id}",  # we could also make this an option
        step.additional_properties.get("model", "gpt-4"),
        step.additional_properties.get("temperature", 0.1),
        "benchmark",  # this needs to be headless mode
        False,
        step.additional_properties.get("azure_endpoint", ""),
        step.additional_properties.get("verbose", False),
    )

    return step


Agent.setup_agent(task_handler, step_handler).start()
