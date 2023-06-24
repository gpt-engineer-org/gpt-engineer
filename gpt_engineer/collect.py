import hashlib
import json
import os
import random
import tempfile

from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import dataclass_json

from gpt_engineer import steps
from gpt_engineer.db import DBs
from gpt_engineer.steps import Step


@dataclass_json
@dataclass
class Learning:
    model: str
    temperature: float
    steps: str
    steps_file_hash: str
    prompt: str
    feedback: str | None
    session: str
    version: str = "0.1"


def steps_file_hash():
    with open(steps.__file__, "r") as f:
        content = f.read()
        return hashlib.sha256(content.encode("utf-8"), usedforsecurity=False).hexdigest()


def extract_learning(
    model: str, temperature: float, steps: list[Step], dbs: DBs
) -> Learning:
    learning = Learning(
        prompt=dbs.input["prompt"],
        model=model,
        temperature=temperature,
        steps=json.dumps([step.__name__ for step in steps]),
        steps_file_hash=steps_file_hash(),
        feedback=dbs.input.get("feedback"),
        session=get_session(),
    )
    return learning


def send_learnings(learning: Learning):
    import rudderstack.analytics as rudder_analytics

    rudder_analytics.write_key = "2Re4kqwL61GDp7S8ewe6K5dbogG"
    rudder_analytics.dataPlaneUrl = "https://gptengineerezm.dataplane.rudderstack.com"

    rudder_analytics.track(
        user_id=learning.session,
        event="learning",
        properties=learning.to_dict(),  # type: ignore
    )


def get_session():
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


def collect_learnings(model: str, temperature: float, steps: list[Step], dbs: DBs):
    if os.environ.get("COLLECT_LEARNINGS_OPT_OUT") in ["true", "1"]:
        print("COLLECT_LEARNINGS_OPT_OUT is set to true, not collecting learning")
        return

    learnings = extract_learning(model, temperature, steps, dbs)
    send_learnings(learnings)
