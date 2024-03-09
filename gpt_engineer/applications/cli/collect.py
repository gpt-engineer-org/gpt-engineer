"""
Module `collect` - Data Handling and RudderStack Integration

This module provides functionalities to handle and send learning data to RudderStack
for the purpose of analysis and to improve the gpt-engineer system. The data is sent
only when the user gives consent to share.

Functions:
    send_learning(learning): Sends learning data to RudderStack.
    collect_learnings(prompt, model, temperature, config, memory, review): Processes and sends learning data.
    collect_and_send_human_review(prompt, model, temperature, config, memory): Collects human feedback and sends it.

Dependencies:
    hashlib: For generating SHA-256 hash.
    typing: For type annotations.
    gpt_engineer.core: Core functionalities of gpt-engineer.
    gpt_engineer.cli.learning: Handles the extraction of learning data.

Notes:
    Data sent to RudderStack is not shared with third parties and is used solely to
    improve gpt-engineer and allow it to handle a broader range of use cases.
    Consent logic is in gpt_engineer/learning.py.
"""

from typing import Tuple

from gpt_engineer.applications.cli.learning import (
    Learning,
    Review,
    extract_learning,
    human_review_input,
)
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.prompt import Prompt


def send_learning(learning: Learning):
    """
    Send the learning data to RudderStack for analysis.

    Parameters
    ----------
    learning : Learning
        An instance of the Learning class containing the data to be sent.

    Notes
    -----
    This function is only called if consent is given to share data.
    Data is not shared to a third party. It is used with the sole purpose of
    improving gpt-engineer, and letting it handle more use cases.
    Consent logic is in gpt_engineer/learning.py.
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
    prompt: Prompt,
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
    prompt : str
        The initial prompt or question that was provided to the model.
    model : str
        The name of the model used for generating the response.
    temperature : float
        The temperature setting used in the model's response generation.
    config : any
        Configuration parameters used for the learning session.
    memory : DiskMemory
        An instance of DiskMemory for storing and retrieving data.
    review : Review
        An instance of Review containing human feedback on the model's response.

    Notes
    -----
    This function attempts to send the learning data to RudderStack. If the data size exceeds
    the maximum allowed size, it trims the data and retries sending it.
    """
    learnings = extract_learning(prompt, model, temperature, config, memory, review)
    try:
        send_learning(learnings)
    except RuntimeError:
        # try to remove some parts of learning that might be too big
        # rudderstack max event size is 32kb
        max_size = 32 << 10  # 32KB in bytes
        current_size = len(learnings.to_json().encode("utf-8"))  # get size in bytes

        overflow = current_size - max_size

        # Add some extra characters for the "[REMOVED...]" string and for safety margin
        remove_length = overflow + len(f"[REMOVED {overflow} CHARACTERS]") + 100

        learnings.logs = (
            learnings.logs[:-remove_length]
            + f"\n\n[REMOVED {remove_length} CHARACTERS]"
        )

        print(
            "WARNING: learning too big, removing some parts. "
            "Please report if this results in a crash."
        )
        try:
            send_learning(learnings)
        except RuntimeError:
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
    prompt: Prompt,
    model: str,
    temperature: float,
    config: Tuple[str, ...],
    memory: DiskMemory,
):
    """
    Collects human feedback on the code and sends it for analysis.

    Parameters
    ----------
    prompt : str
        The initial prompt or question that was provided to the model.
    model : str
        The name of the model used for generating the response.
    temperature : float
        The temperature setting used in the model's response generation.
    config : Tuple[str, ...]
        Configuration parameters used for the learning session.
    memory : DiskMemory
        An instance of DiskMemory for storing and retrieving data.

    Returns
    -------
    None

    Notes
    -----
    This function prompts the user for a review of the generated or improved code using the
    `human_review_input` function. If a valid review is provided, it's serialized to JSON format
    and stored within the database's memory under the "review" key.
    """

    review = human_review_input()
    if review:
        collect_learnings(prompt, model, temperature, config, memory, review)
