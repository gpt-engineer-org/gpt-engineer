import json
import pathlib

from typing import Union

import typer

from gpt_engineer.ai import AI
from gpt_engineer.chat_to_files import to_files

app = typer.Typer()


@app.command()
def main(
    messages_path: str,
    out_path: Union[str, None] = None,
    model: str = "gpt-4",
    temperature: float = 0.1,
):
    ai = AI(
        model=model,
        temperature=temperature,
    )

    with open(messages_path) as f:
        messages = json.load(f)

    messages = ai.next(messages)

    if out_path:
        to_files(messages[-1]["content"], out_path)
        with open(pathlib.Path(out_path) / "all_output.txt", "w") as f:
            json.dump(messages[-1]["content"], f)


if __name__ == "__main__":
    app()
