import hashlib

from typing import List

from gpt_engineer import steps
from gpt_engineer.db import DBs
from gpt_engineer.domain import Step
from gpt_engineer.learning import Learning, extract_learning



def send_learning(learning: Learning):
    """
    Note:
    This function is only called if consent is given to share data.

    Data is not shared to a third party. It is used with the sole purpose of
    improving gpt-engineer, and letting it handle more use cases.

    Consent logic is in gpt_engineer/learning.py
    """
    import rudderstack.analytics as rudder_analytics

    rudder_analytics.write_key = "2Re4kqwL61GDp7S8ewe6K5dbogG"
    rudder_analytics.dataPlaneUrl = "https://gptengineerezm.dataplane.rudderstack.com"

    try:
        rudder_analytics.track(
            user_id=learning.session,
            event="learning",
            properties=learning.to_dict(),  # type: ignore
        )
    except RuntimeError:
        learning_dict = learning.to_dict()  # type: ignore
        chunk_size = len(learning_dict) // 2
        for i in range(0, len(learning_dict), chunk_size):
            chunk = dict(list(learning_dict.items())[i:i+chunk_size])
            rudder_analytics.track(
                user_id=learning.session,
                event="learning",
                properties=chunk,
            )


def collect_learnings(model: str, temperature: float, steps: List[Step], dbs: DBs):
    learnings = extract_learning(
        model, temperature, steps, dbs, steps_file_hash=steps_file_hash()
    )
    send_learning(learnings)


def steps_file_hash():
    with open(steps.__file__, "r") as f:
        content = f.read()
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
