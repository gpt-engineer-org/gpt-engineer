import os
from pathlib import Path
from agent_protocol import Agent, Step, Task, models
from gpt_engineer.db import DB
from gpt_engineer.main import main
from openai.error import AuthenticationError
import tempfile


async def task_handler(task: Task) -> None:
    """
    Process the given task to set up the initial steps based on the task input.

    Parameters:
    - task (Task): An object containing task details, including the input prompt.

    Behavior:
    - Checks if the task has valid input.
    - Reads additional input properties and sets up a workspace directory.
    - Writes the prompt to a file.
    - Registers the workspace directory as an artifact.
    - Creates an initial step named "create_code".

    Exceptions:
    - Raises an exception if no input prompt is provided in the 'input' field of the task.

    Returns:
    - None
    """

    # Validate that we have a prompt or terminate.
    if task.input is None:
        raise Exception("No input prompt in the 'input' field.")

    # Extract additional properties from the task if available.
    additional_input = dict()
    if hasattr(task, "additional_input"):
        if hasattr(task.additional_input, "__root__"):
            additional_input = task.additional_input.__root__

    # Set up the root directory for the agent, defaulting to a temporary directory.
    root_dir = additional_input.get("root_dir", tempfile.gettempdir())
    additional_input["root_dir"] = root_dir

    workspace = DB(os.path.join(root_dir, task.task_id))

    # Write prompt to a file in the workspace.
    workspace["prompt"] = f"{task.input}\n"

    # Ensure no prompt hang by writing to the consent file.
    consent_file = Path(os.getcwd()) / ".gpte_consent"
    consent_file.write_text("false")

    await Agent.db.create_artifact(
        task_id=task.task_id,
        relative_path=root_dir,
        file_name=os.path.join(root_dir, task.task_id),
    )

    await Agent.db.create_step(
        task_id=task.task_id,
        name="create_code",
        is_last=True,
        additional_properties=additional_input,
    )


async def step_handler(step: Step) -> Step:
    """
    Handle the provided step by triggering code generation or other operations.

    Parameters:
    - step (Step): An object containing step details and properties.

    Behavior:
    - If not a dummy step, triggers the main code generation process.
    - Handles potential authentication errors during code generation.
    - Creates a dummy step if it's the last step to ensure continuity.

    Returns:
    - step (Step): Returns the processed step, potentially with modifications.
    """

    if not step.name == "Dummy step":
        try:
            main(
                os.path.join(step.additional_properties["root_dir"], step.task_id),
                step.additional_properties.get("model", "gpt-4"),
                step.additional_properties.get("temperature", 0.1),
                "benchmark",
                False,
                step.additional_properties.get("azure_endpoint", ""),
                step.additional_properties.get("verbose", False),
            )
        except AuthenticationError:
            print("The agent lacks a valid OPENAI_API_KEY to execute the requested step.")

    if step.is_last:
        await Agent.db.create_step(
            step.task_id,
            name=f"Dummy step",
            input=f"Creating dummy step to not run out of steps after {step.name}",
            is_last=True,
            additional_properties={},
        )
        step.is_last = False

    return step


Agent.setup_agent(task_handler, step_handler).start()
