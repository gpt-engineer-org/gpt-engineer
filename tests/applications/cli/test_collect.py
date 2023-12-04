"""
Tests the collect_learnings function in the cli/collect module.
"""

import json

from unittest.mock import MagicMock

import pytest
import rudderstack.analytics as rudder_analytics

from gpt_engineer.applications.cli.collect import collect_learnings
from gpt_engineer.core.default.disk_memory import (
    DiskMemory,
)
from gpt_engineer.applications.cli.learning import extract_learning


# def test_collect_learnings(monkeypatch):
#     monkeypatch.setattr(rudder_analytics, "track", MagicMock())
#
#     model = "test_model"
#     temperature = 0.5
#     steps = [simple_gen]
#     dbs = FileRepositories(
#         OnDiskRepository("/tmp"),
#         OnDiskRepository("/tmp"),
#         OnDiskRepository("/tmp"),
#         OnDiskRepository("/tmp"),
#         OnDiskRepository("/tmp"),
#         OnDiskRepository("/tmp"),
#         OnDiskRepository("/tmp"),
#     )
#     dbs.input = {
#         "prompt": "test prompt\n with newlines",
#         "feedback": "test feedback",
#     }
#     code = "this is output\n\nit contains code"
#     dbs.logs = {steps[0].__name__: json.dumps([{"role": "system", "content": code}])}
#     dbs.memory = {"all_output.txt": "test workspace\n" + code}
#
#     collect_learnings(model, temperature, steps, dbs)
#
#     learnings = extract_learning(
#         model, temperature, steps, dbs, steps_file_hash=steps_file_hash()
#     )
#     assert rudder_analytics.track.call_count == 1
#     assert rudder_analytics.track.call_args[1]["event"] == "learning"
#     a = {
#         k: v
#         for k, v in rudder_analytics.track.call_args[1]["properties"].items()
#         if k != "timestamp"
#     }
#     b = {k: v for k, v in learnings.to_dict().items() if k != "timestamp"}
#     assert a == b
#
#     assert json.dumps(code) in learnings.logs
#     assert code in learnings.workspace


if __name__ == "__main__":
    pytest.main(["-v"])
