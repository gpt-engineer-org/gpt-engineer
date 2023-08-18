import hashlib

from typing import List

from gpt_engineer import steps
from gpt_engineer.db import DBs
from gpt_engineer.domain import Step
from gpt_engineer.learning import Learning, extract_learning



def split_learning_data(learning: Learning, chunk_size: int = 1024):
    learning_dict = learning.to_dict()  # type: ignore
    chunks = [learning_dict[i:i + chunk_size] for i in range(0, len(learning_dict), chunk_size)]
    return chunks

def send_learning_chunks(learning: Learning):
    import rudderstack.analytics as rudder_analytics

    rudder_analytics.write_key = "2Re4kqwL61GDp7S8ewe6K5dbogG"
    rudder_analytics.dataPlaneUrl = "https://gptengineerezm.dataplane.rudderstack.com"

    learning_chunks = split_learning_data(learning)
    for chunk in learning_chunks:
        rudder_analytics.track(
            user_id=learning.session,
            event="learning",
            properties=chunk,
        )

def send_learning(learning: Learning):
    send_learning_chunks(learning)



def collect_learnings(model: str, temperature: float, steps: List[Step], dbs: DBs):
    learnings = extract_learning(
        model, temperature, steps, dbs, steps_file_hash=steps_file_hash()
    )
    send_learning(learnings)


def steps_file_hash():
    with open(steps.__file__, "r") as f:
        content = f.read()
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
