import os
import subprocess

from datetime import datetime
from pathlib import Path

import typer

from eval_tools import check_evaluation_component, load_evaluations_from_file, to_emoji
from tabulate import tabulate

from gpt_engineer.chat_to_files import parse_chat
from gpt_engineer.db import DB

app = typer.Typer()  # creates a CLI app


def single_evaluate(eval_ob: dict) -> list[bool]:
    """Evaluates a single prompt."""
    print(f"running evaluation: {eval_ob['name']}")

    # Step 1. Setup known project
    # load the known files into the project
    # the files can be anywhere in the projects folder

    workspace = DB(eval_ob["project_root"])
    file_list_string = ""
    code_base_abs = Path(os.getcwd()) / eval_ob["project_root"]

    files = parse_chat(open(eval_ob["code_blob"]).read())
    for file_name, file_content in files:
        absolute_path = code_base_abs / file_name
        print("creating: ", absolute_path)
        workspace[absolute_path] = file_content
        file_list_string += str(absolute_path) + "\n"

    # create file_list.txt (should be full paths)
    workspace["file_list.txt"] = file_list_string

    # create the prompt
    workspace["prompt"] = eval_ob["improve_code_prompt"]

    # Step 2.  run the project in improve code mode,
    # make sure the flag -sf is set to skip feedback

    print(f"Modifying code for {eval_ob['project_root']}")

    log_path = code_base_abs / "log.txt"
    log_file = open(log_path, "w")
    process = subprocess.Popen(
        [
            "python",
            "-u",  # Unbuffered output
            "-m",
            "gpt_engineer.main",
            eval_ob["project_root"],
            "--steps",
            "eval_improve_code",
        ],
        stdout=log_file,
        stderr=log_file,
        bufsize=0,
    )
    print(f"waiting for {eval_ob['name']} to finish.")
    process.wait()  # we want to wait until it finishes.

    # Step 3. Run test of modified code, tests
    print("running tests on modified code")
    evaluation_results = []
    for test_case in eval_ob["expected_results"]:
        print(f"checking: {test_case['type']}")
        test_case["project_root"] = Path(eval_ob["project_root"])
        evaluation_results.append(check_evaluation_component(test_case))

    return evaluation_results


def generate_report(evals: list[dict], res: list[list[bool]]) -> None:
    # High level shows if all the expected_results passed
    # Detailed shows all the test cases and a pass/fail for each
    output_lines = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_lines.append(f"## {current_date}\n\n")

    # Create a summary table
    headers = ["Project", "Evaluation", "All Tests Pass"]
    rows = []
    for i, eval_ob in enumerate(evals):
        rows.append(
            [eval_ob["project_root"], eval_ob["name"], to_emoji(all(res[i]))]
        )  # logical AND of all tests
    table: str = tabulate(rows, headers, tablefmt="pipe")
    title = "Existing Code Evaluation Summary:"
    print(f"\n{title}\n")
    print(table)
    print()
    output_lines.append(f"### {title}\n\n{table}\n\n")

    # Create a detailed table
    headers = ["Project", "Evaluation", "Test", "Pass"]
    rows = []
    for i, eval_ob in enumerate(evals):
        for j, test in enumerate(eval_ob["expected_results"]):
            rows.append(
                [
                    eval_ob["project_root"],
                    eval_ob["name"],
                    eval_ob["expected_results"][j]["type"],
                    to_emoji(res[i][j]),
                ]
            )
    detail_table: str = tabulate(rows, headers, tablefmt="pipe")
    title = "Detailed Test Results:"
    print(f"\n{title} \n")
    print(detail_table)
    print()

    output_lines.append(f"### {title}\n\n{detail_table}\n\n")
    with open("evals/IMPROVE_CODE_RESULTS.md", "a") as file:
        file.writelines(output_lines)


def run_all_evaluations(eval_list: list[dict]) -> None:
    results = []
    for eval_ob in eval_list:
        results.append(single_evaluate(eval_ob))

    # Step 4. Generate Report
    generate_report(eval_list, results)


@app.command()
def main(
    test_file_path: str = typer.Argument("evals/existing_code_eval.yaml", help="path"),
):
    if not os.path.isfile(test_file_path):
        raise Exception(f"sorry the file: {test_file_path} does not exist.")

    eval_list = load_evaluations_from_file(test_file_path)
    run_all_evaluations(eval_list)


if __name__ == "__main__":
    app()
