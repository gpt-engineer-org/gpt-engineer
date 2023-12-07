from pathlib import Path

from gpt_engineer.benchmark.benchmarks.gpteng.eval_tools import check_evaluation_component
from gpt_engineer.benchmark.types import Benchmark, Task, Assertable
from gpt_engineer.core import chat_to_files
from gpt_engineer.core.chat_to_files import chat_to_files_dict
from gpt_engineer.core.files_dict import FilesDict

evaluations = [
    {
        "name": "simple_code_modify",
        "project_root": "projects/snake_game_eval",
        "code_blob": "gpt_engineer/benchmark/benchmarks/gpteng/known_code_blobs/snake_game_files.txt",
        "improve_code_prompt": "The grid is currently 10x10, change the grid to be 42x42.",
        "expected_results": [
            {
                "type": "assert_exists_in_source_code",
                "source_file": "grid.py",
                "existing_string": "width=42",
            },
            {
                "type": "assert_exists_in_source_code",
                "source_file": "grid.py",
                "existing_string": "height=42",
            },
            {
                "type": "run_code_class_has_property",
                "language": "python",
                "source_file": "grid.py",
                "class_name": "Grid",
                "property_name": "height",
            },
            {
                "type": "run_code_class_has_property",
                "language": "python",
                "source_file": "grid.py",
                "class_name": "Grid",
                "property_name": "width",
            },
            {
                "type": "run_code_class_has_property_w_value",
                "language": "python",
                "source_file": "grid.py",
                "class_name": "Grid",
                "property_name": "height",
                "expected_value": 42,
            },
            {
                "type": "run_code_class_has_property_w_value",
                "language": "python",
                "source_file": "grid.py",
                "class_name": "Grid",
                "property_name": "width",
                "expected_value": 42,
            },
        ],
    },
    {
        "name": "modify_web_app_appearance",
        "project_root": "projects/web_todo_list",
        "code_blob": "gpt_engineer/benchmark/benchmarks/gpteng/known_code_blobs/web_todo_files.txt",
        "improve_code_prompt": "Fix the margins around the form to be 45px, and make the background color orange.",
        "expected_results": [
            {
                "type": "assert_exists_in_source_code",
                "source_file": "styles.css",
                "existing_string": "#task-form {\\n    margin: 45px;",
            },
            {
                "type": "assert_exists_in_source_code",
                "source_file": "styles.css",
                "existing_string": "background-color: orange;",
            },
        ],
    },
    {
        "name": "modify_functionality",
        "project_root": "projects/snake_game_eval",
        "code_blob": "gpt_engineer/benchmark/benchmarks/gpteng/known_code_blobs/snake_game_files.txt",
        "improve_code_prompt": "Add a 2 second delay before the game starts.",
        "expected_results": [
            {
                "type": "assert_exists_in_source_code",
                "source_file": "game.py",
                "existing_string": "time.sleep(2)",
            }
        ],
    },
]

# Not supporting execution paths that used to exist
# evaluations = [
#     {
#         "name": "currency_converter",
#         "project_root": "projects/currency_converter",
#         "code_prompt": "Build a currency converter CLI tool in Python using an API for exchange rates.  The currency converter should be a python program named currency.py with three required arguments: base currency symbol, target currency symbol and base currency amount.  The currency converter will convert the amount in base currency amount to the target currency.  The output of the program should only be the amount of target currency.  For example the following command: `python currency.py USD CNY 1` should return a number like 7.5.",
#         "expected_results": [
#             {
#                 "type": "check_executable_exits_normally",
#                 "executable_name": "python currency.py",
#                 "executable_arguments": "USD CAD 10"
#             },
#             {
#                 "type": "check_executable_satisfies_function",
#                 "executable_name": "python currency.py",
#                 "executable_arguments": "USD CAD 10",
#                 "output_satisfies": "tf = lambda a : a.replace('.', '').isnumeric()"
#             }
#         ]
#     },
#     {
#         "name": "password_gen",
#         "project_root": "projects/password_gen_eval",
#         "code_prompt": "Create a password generator CLI tool in Python that generates strong, random passwords based on user-specified criteria, such as length and character types (letters, numbers, symbols).  The password generator should be a python program named passwordgenerator.py with two arguments: length, and character types.  The character types argument can be one or more of the the following: l for lowercase, u for uppercase, d for digits, and s for symbols.",
#         "expected_results": [
#             {
#                 "type": "check_executable_exits_normally",
#                 "executable_name": "python passwordgenerator.py",
#                 "executable_arguments": "10 d"
#             },
#             {
#                 "type": "check_executable_satisfies_function",
#                 "executable_name": "python passwordgenerator.py",
#                 "executable_arguments": "10 d",
#                 "output_satisfies": "tf = lambda a : len(a) == 10"
#             }
#         ]
#     }
# ]
#


def expect_to_assertion(expected_result):
    def assertion(assertable: Assertable):
        return check_evaluation_component(expected_result, assertable.files)

    return assertion


def eval_to_task(case):
    if "improve_code_prompt" in case:
        prompt = case["improve_code_prompt"]
    else:
        prompt = case["code_prompt"]

    return Task(
        name=case["name"],
        initial_code=chat_to_files_dict(Path(case["code_blob"]).read_text()),
        prompt=prompt,
        command=None,
        assertions={
            f"{e['type']}_{i}": expect_to_assertion(e)
            for i, e in enumerate(case["expected_results"])
        },
    )


def load_gpteng():
    return Benchmark(name="gpte_eval", tasks=[eval_to_task(case) for case in evaluations])
