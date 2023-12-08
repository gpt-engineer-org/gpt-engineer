"""
This module provides tools and data structures for supporting a feedback loop in the GPT Engineer application.

The primary intent of this module is to gather feedback from the user on the output of the gpt-engineer tool,
with their consent, and to store this feedback for further analysis and improvement of the tool.

Classes:
----------
Review:
    Represents user's review of the generated code.
Learning:
    Represents the metadata and feedback collected for a session in which gpt-engineer was used.

Functions:
----------
human_review_input() -> Review:
    Interactively gathers feedback from the user regarding the performance of generated code.

check_consent() -> bool:
    Checks if the user has previously given consent to store their data and if not, asks for it.

collect_consent() -> bool:
    Verifies if the user has given consent to store their data or prompts for it.

ask_if_can_store() -> bool:
    Asks the user if it's permissible to store their data for gpt-engineer improvement.

logs_to_string(steps: List[Step], logs: DB) -> str:
    Converts logs of steps into a readable string format.

extract_learning(model: str, temperature: float, steps: List[Step], dbs: DBs, steps_file_hash) -> Learning:
    Extracts feedback and session details to create a Learning instance.

get_session() -> str:
    Retrieves a unique identifier for the current user session.

Constants:
----------
TERM_CHOICES:
    Terminal color choices for user interactive prompts.
"""

import json
import random
import tempfile

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from dataclasses_json import dataclass_json
from termcolor import colored

from gpt_engineer.core.default.disk_memory import DiskMemory


@dataclass_json
@dataclass
class Review:
    ran: Optional[bool]
    perfect: Optional[bool]
    works: Optional[bool]
    comments: str
    raw: str


@dataclass_json
@dataclass
class Learning:
    prompt: str
    model: str
    temperature: float
    config: str
    logs: str
    session: str
    review: Optional[Review]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: str = "0.3"


TERM_CHOICES = (
    colored("y", "green")
    + "/"
    + colored("n", "red")
    + "/"
    + colored("u", "yellow")
    + "(ncertain): "
)


def human_review_input() -> Review | None:
    """
    Ask the user to review the generated code and return their review.

    Returns
    -------
    Review
        The user's review of the generated code.
    """
    print()
    if not check_collection_consent():
        return None
    print()
    print(
        colored("To help gpt-engineer learn, please answer 3 questions:", "light_green")
    )
    print()

    ran = input("Did the generated code run at all? " + TERM_CHOICES)
    while ran not in ("y", "n", "u"):
        ran = input("Invalid input. Please enter y, n, or u: ")

    perfect = ""
    useful = ""

    if ran == "y":
        perfect = input(
            "Did the generated code do everything you wanted? " + TERM_CHOICES
        )
        while perfect not in ("y", "n", "u"):
            perfect = input("Invalid input. Please enter y, n, or u: ")

        if perfect != "y":
            useful = input("Did the generated code do anything useful? " + TERM_CHOICES)
            while useful not in ("y", "n", "u"):
                useful = input("Invalid input. Please enter y, n, or u: ")

    comments = ""
    if perfect != "y":
        comments = input(
            "If you have time, please explain what was not working "
            + colored("(ok to leave blank)\n", "light_green")
        )

    return Review(
        raw=", ".join([ran, perfect, useful]),
        ran={"y": True, "n": False, "u": None, "": None}[ran],
        works={"y": True, "n": False, "u": None, "": None}[useful],
        perfect={"y": True, "n": False, "u": None, "": None}[perfect],
        comments=comments,
    )


def check_collection_consent() -> bool:
    """
    Check if the user has given consent to store their data.
    If not, ask for their consent.
    """
    path = Path(".gpte_consent")
    if path.exists() and path.read_text() == "true":
        return True
    else:
        return ask_collection_consent()


def ask_collection_consent() -> bool:
    """
    Ask the user for consent to store their data.
    """
    answer = input(
        "Is it ok if we store your prompts to help improve GPT Engineer? (y/n)"
    )
    while answer.lower() not in ("y", "n"):
        answer = input("Invalid input. Please enter y or n: ")

    if answer.lower() == "y":
        path = Path(".gpte_consent")
        path.write_text("true")
        print(colored("Thank you️", "light_green"))
        print()
        print(
            "(If you no longer wish to participate in data collection, delete the file .gpte_consent)"
        )
        return True
    else:
        print(
            colored(
                "No worries! GPT Engineer will not collect your prompts. ❤️",
                "light_green",
            )
        )
        return False


def extract_learning(
    prompt: str,
    model: str,
    temperature: float,
    config: Tuple[str, ...],
    memory: DiskMemory,
    review: Review,
) -> Learning:
    """
    Extract the learning data from the steps and databases.

    Parameters
    ----------
    model : str
        The name of the model used.
    temperature : float
        The temperature used.
    steps : List[Step]
        The list of steps.
    dbs : DBs
        The databases containing the input, logs, memory, and workspace.
    steps_file_hash : str
        The hash of the steps file.

    Returns
    -------
    Learning
        The extracted learning data.
    """
    learning = Learning(
        prompt=prompt,
        model=model,
        temperature=temperature,
        config=json.dumps(config),
        session=get_session(),
        logs=memory.to_json(),
        review=review,
    )
    return learning


def get_session() -> str:
    """
    Returns a unique user id for the current user project (session).

    Returns
    -------
    str
        The unique user id.
    """
    path = Path(tempfile.gettempdir()) / "gpt_engineer_user_id.txt"

    try:
        if path.exists():
            user_id = path.read_text()
        else:
            # random uuid:
            user_id = str(random.randint(0, 2**32))
            path.write_text(user_id)
        return user_id
    except IOError:
        return "ephemeral_" + str(random.randint(0, 2**32))
