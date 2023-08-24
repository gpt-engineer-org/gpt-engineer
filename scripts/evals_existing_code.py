from pathlib import Path

import yaml

from eval_tools import check_evaluation_component

EVAL_LIST_NAME = "evaluations"  # the top level list in the YAML file


def single_evaluate(eval_ob: dict) -> None:
    """Evaluates a single prompt."""
    # print(f"running evaluation: {eval_ob['name']}")

    # # Step 1. Setup known project
    # # load the known files into the project
    # # the files can be anywhere in the projects folder

    # workspace = DB(eval_ob['project_root'])
    # file_list_string = ""
    # code_base_abs = Path(os.getcwd()) / eval_ob['project_root']

    # files = parse_chat(open(eval_ob['SNAKE_GAME_CODE_BLOB']).read())
    # for file_name, file_content in files:
    #     absolute_path = code_base_abs / file_name
    #     print("creating: ", absolute_path)
    #     workspace[absolute_path] = file_content
    #     file_list_string += str(absolute_path) + "\n"

    # # create file_list.txt (should be full paths)
    # workspace["file_list.txt"] = file_list_string

    # # create the prompt
    # workspace["prompt"] = eval_ob['IMPROVE_CODE_PROMPT']

    # # Step 2.  run the project in improve code mode,
    # # make sure the flag -sf is set to skip feedback

    # print(f"Modifying code for {eval_ob['project_root']}")

    # log_path = code_base_abs / "log.txt"
    # log_file = open(log_path, "w")
    # process = subprocess.Popen(
    #     [
    #         "python",
    #         "-u",  # Unbuffered output
    #         "-m",
    #         "gpt_engineer.main",
    #         eval_ob['project_root'],
    #         "--steps",
    #         "eval_improve_code",
    #     ],
    #     stdout=log_file,
    #     stderr=log_file,
    #     bufsize=0,
    # )
    # print(f"waiting for {eval_ob['name']} to finish.")
    # process.wait()  # we want to wait until it finishes.

    # Step 3. run test of modified code, tests
    print("running tests on modified code")
    for test_case in eval_ob["expected_results"]:
        print(f"checking: {test_case['type']}")
        test_case["project_root"] = Path(eval_ob["project_root"])
        check_evaluation_component(test_case)


def load_evaluations_from_file(file_path):
    """Loads the evaluations from a YAML file."""
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            if EVAL_LIST_NAME in data:
                return data[EVAL_LIST_NAME]
            else:
                print(f"'{EVAL_LIST_NAME}' not found in {file_path}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")


def run_all_evaluations(eval_list: list[dict]) -> None:
    for eval_ob in eval_list:
        single_evaluate(eval_ob)

    # TODO: roll up evaluations into report


if __name__ == "__main__":
    eval_list = load_evaluations_from_file("scripts/existing_code_eval.yaml")
    run_all_evaluations(eval_list)
