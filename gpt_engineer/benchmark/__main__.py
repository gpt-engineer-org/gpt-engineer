import typer


def main(
    benchmarks: list[str],
    path_to_agent: str,
    task_name: str | None = None,
):
    benchmarks = [benchmark for benchmark in benchmarks.split(",")]


if __name__ == "__main__":
    typer.run(main)
