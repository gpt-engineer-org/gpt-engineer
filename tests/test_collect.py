import json
import os

from unittest.mock import MagicMock
import pytest
import rudderstack.analytics as rudder_analytics

from gpt_engineer.collect import collect_learnings, extract_learning
from gpt_engineer.db import DB, DBs
from gpt_engineer.steps import gen_code


def test_collect_learnings(monkeypatch):
    monkeypatch.setattr(os, "environ", {"COLLECT_LEARNINGS_OPT_OUT": "false"})
    monkeypatch.setattr(rudder_analytics, "track", MagicMock())

    model = "test_model"
    temperature = 0.5
    steps = [gen_code]
    dbs = DBs(DB("/tmp"), DB("/tmp"), DB("/tmp"), DB("/tmp"), DB("/tmp"))
    dbs.input = {
        "prompt": "test prompt\n with newlines",
        "feedback": "test feedback",
    }
    code = "this is output\n\nit contains code"
    dbs.logs = {gen_code.__name__: json.dumps([{"role": "system", "content": code}])}
    dbs.workspace = {"all_output.txt": "test workspace\n" + code}

    collect_learnings(model, temperature, steps, dbs)

    learnings = extract_learning(model, temperature, steps, dbs)
    assert rudder_analytics.track.call_count == 1
    assert rudder_analytics.track.call_args[1]["event"] == "learning"
    assert rudder_analytics.track.call_args[1]["properties"] == learnings.to_dict()

    assert code in learnings.logs
    assert code in learnings.workspace


if __name__ == "__main__":
    pytest.main(["-v"])
