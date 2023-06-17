import json
import subprocess

from gpt_engineer.ai import AI
from gpt_engineer.chat_to_files import to_files
from gpt_engineer.db import DBs
from gpt_engineer.chat_to_files import parse_chat
from gpt_engineer.fork.steps import *

def runner_default(ai: AI, dbs: DBs):
    return StepRunner(ai, dbs, [
        GenerateSpec(),
        GenerateUnitTests(),
        GenerateCode(),
        ExecuteWorkspace()
    ])

def runner_benchmark(ai: AI, dbs: DBs):
    return StepRunner(ai, dbs, [
        GenerateSpec(),
        GenerateUnitTests(),
        GenerateCode(),
        GenerateEntrypoint()
    ])

def runner_simple(ai: AI, dbs: DBs):
    return StepRunner(ai, dbs, [
        RunMain(),
        ExecuteWorkspace()
    ])

def runner_clarify(ai: AI, dbs: DBs):
    return StepRunner(ai, dbs, [
        ClarificationStep(),
        RunLatest(),
        ExecuteWorkspace()
    ])

def runner_respec(ai: AI, dbs: DBs):
    return StepRunner(ai, dbs, [
        GenerateSpec(),
        ReSpec(),
        GenerateUnitTests(),
        GenerateCode(),
        ExecuteWorkspace()
    ])

def runner_execute_only(ai: AI, dbs: DBs):
    return StepRunner(ai, dbs, [
        ExecuteEntrypoint()
    ])

# Different configs of what steps to run
STEPS = {
    "default": runner_default,
    "benchmark": runner_benchmark,
    "simple": runner_simple,
    "clarify": runner_clarify,
    "respec": runner_respec,
    "execute_only": runner_execute_only,
}

# Future steps that can be added:
# self_reflect_and_improve_files,
# add_tests
# run_tests_and_fix_files,
# improve_based_on_in_file_feedback_comments
