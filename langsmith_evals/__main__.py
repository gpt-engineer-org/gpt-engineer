from pathlib import Path
from typing import Any, Optional

import typer
from gpt_engineer.benchmark.__main__ import get_agent
from gpt_engineer.benchmark.benchmarks.gpteng.eval_tools import (
    check_evaluation_component,
)
from gpt_engineer.benchmark.benchmarks.gpteng.load import evaluations as gpteng_evals
from gpt_engineer.core.base_agent import BaseAgent
from gpt_engineer.core.chat_to_files import chat_to_files_dict
from langchain.smith import RunEvalConfig
from langsmith import Client, traceable
from langsmith.evaluation.evaluator import EvaluationResults, run_evaluator
from langsmith.schemas import Example, Run


@run_evaluator
def evaluate_run(run: Run, example: Example):
    results = []
    for expected_res in example.outputs["expected_results"]:
        try:
            score = check_evaluation_component(expected_res, run.outputs)
            results.append(EvaluationResults(key=expected_res["type"], score=score))
        except Exception:
            pass

    return EvaluationResults(results=results)


def run_langsmith(path_to_agent: str, dataset: str, verbose=bool) -> dict:
    client = Client()

    @traceable()
    def run_agent(improve_code_prompt: str, code_blob: str, **kwargs: Any) -> dict:
        agent: BaseAgent = get_agent(path_to_agent)
        files_dict = chat_to_files_dict(Path(code_blob).read_text())
        return agent.improve(files_dict, improve_code_prompt)

    test_results = client.run_on_dataset(
        dataset_name=dataset,
        llm_or_chain_factory=run_agent,
        evaluation=RunEvalConfig(
            custom_evaluators=[evaluate_run],
        ),
        verbose=verbose,
        project_metadata={
            "agent": Path(path_to_agent).name,
            "config": "default",
        },
    )
    return test_results


def upload_langsmith(benchmark: str = None):
    client = Client()
    if benchmark != "gpteng":
        raise Exception(f"Benchmark: {benchmark} is not supported.")
    input_keys = ["project_root", "code_blob", "improve_code_prompt"]
    all_inputs = []
    all_outputs = []
    for task_dict in gpteng_evals:
        all_inputs.append({k: task_dict[k] for k in input_keys})
        all_outputs.append({"expected_results": task_dict["expected_results"]})
    try:
        ds = client.create_dataset(dataset_name=benchmark)
    except Exception:
        print(f"Dataset: {benchmark} already exists.")
        return
    client.create_examples(
        inputs=all_inputs,
        outputs=all_outputs,
        dataset_id=ds.id,
    )


def main(
    dataset_name: str = typer.Option(
        default="gpteng", help="The benchmark to run against."
    ),
    path_to_agent: Optional[str] = typer.Option(None, help="The agent to use."),
    verbose: bool = typer.Option(False, help="Verbose output."),
    action: str = typer.Option("run", help="The action to take.", case_sensitive=False),
):
    if action == "run":
        run_langsmith(path_to_agent, dataset_name, verbose)
    elif action == "upload":
        upload_langsmith(dataset_name)
    else:
        raise Exception(f"Action: {action} is not supported.")


if __name__ == "__main__":
    typer.run(main)
