"""
This module provides functionalities to handle and send learning data to RudderStack
for the purpose of analysis and to improve the gpt-engineer system. The data is sent
only when the user gives consent to share.

The module provides the following main functions:

- `send_learning`: Directly send a learning data to RudderStack.
- `collect_learnings`: Extract, possibly adjust, and send the learning data based on
  provided input parameters.
- `steps_file_hash`: Computes the SHA-256 hash of the steps file, which might be used
  for identifying the exact version or changes in the steps.

Dependencies:
- hashlib: For generating SHA-256 hash.
- typing: For type annotations.
- gpt_engineer.core: Core functionalities of gpt-engineer.
- gpt_engineer.cli.learning: Handles the extraction of learning data.

Note:
    Data sent to RudderStack is not shared with third parties and is used solely to
    improve gpt-engineer and allow it to handle a broader range of use cases.
    Consent logic is in gpt_engineer/learning.py.

"""
import hashlib

from typing import List, Tuple

from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.applications.cli.learning import (
    Learning,
    extract_learning,
    human_review_input,
    Review,
)


def send_learning(learning: Learning):
    """
    Send the learning data to RudderStack for analysis.

    Note:
    This function is only called if consent is given to share data.
    Data is not shared to a third party. It is used with the sole purpose of
    improving gpt-engineer, and letting it handle more use cases.
    Consent logic is in gpt_engineer/learning.py

    Parameters
    ----------
    learning : Learning
        The learning data to send.
    """
    import rudderstack.analytics as rudder_analytics

    rudder_analytics.write_key = "2Re4kqwL61GDp7S8ewe6K5dbogG"
    rudder_analytics.dataPlaneUrl = "https://gptengineerezm.dataplane.rudderstack.com"

    rudder_analytics.track(
        user_id=learning.session,
        event="learning",
        properties=learning.to_dict(),  # type: ignore
    )


def collect_learnings(
    prompt: str,
    model: str,
    temperature: float,
    config: any,
    memory: DiskMemory,
    review: Review,
):
    """
    Collect the learning data and send it to RudderStack for analysis.

    Parameters
    ----------
    model : str
        The name of the model used.
    temperature : float
        The temperature used.
    steps : List[Step]
        The list of steps.
    dbs : DBs
        The database containing the workspace.
    """
    learnings = extract_learning(prompt, model, temperature, config, memory, review)
    try:
        send_learning(learnings)
    except RuntimeError as e:
        # try to remove some parts of learning that might be too big
        # rudderstack max event size is 32kb
        max_size = 32 << 10  # 32KB in bytes
        current_size = len(learnings.to_json().encode("utf-8"))  # get size in bytes

        overflow = current_size - max_size

        # Add some extra characters for the "[REMOVED...]" string and for safety margin
        remove_length = overflow + len(f"[REMOVED {overflow} CHARACTERS]") + 100

        learnings.logs = (
            learnings.logs[:-remove_length] + f"\n\n[REMOVED {remove_length} CHARACTERS]"
        )

        print(
            "WARNING: learning too big, removing some parts. "
            "Please report if this results in a crash."
        )
        try:
            send_learning(learnings)
        except RuntimeError as e:
            print(
                "Sending learnings crashed despite truncation. Progressing without saving learnings."
            )


# def steps_file_hash():
#     """
#     Compute the SHA-256 hash of the steps file.
#
#     Returns
#     -------
#     str
#         The SHA-256 hash of the steps file.
#     """
#     with open(steps.__file__, "r") as f:
#         content = f.read()
#         return hashlib.sha256(content.encode("utf-8")).hexdigest()


def collect_and_send_human_review(
    prompt: str,
    model: str,
    temperature: float,
    config: Tuple[str, ...],
    memory: DiskMemory,
):
    """
    Collects human feedback on the code and stores it in memory.

    This function prompts the user for a review of the generated or improved code using the `human_review_input`
    function. If a valid review is provided, it's serialized to JSON format and stored within the database's
    memory under the "review" key.

    Parameters:
    - ai (AI): An instance of the AI model. Although not directly used within the function, it is kept as
      a parameter for consistency with other functions.
    - dbs (DBs): An instance containing the database configurations, user prompts, project metadata,
      and memory storage. This function specifically interacts with the memory storage to save the human review.

    Returns:
    - list: Returns an empty list, indicating that there's no subsequent interaction with the LLM
      or no further messages to be processed.

    Notes:
    - It's assumed that the `human_review_input` function handles all the interactions with the user to
      gather feedback and returns either the feedback or None if no feedback was provided.
    - Ensure that the database's memory has enough space or is set up correctly to store the serialized review data.
    """

    """Collects and stores human review of the code"""
    review = human_review_input()
    if review:
        collect_learnings(prompt, model, temperature, config, memory, review)
