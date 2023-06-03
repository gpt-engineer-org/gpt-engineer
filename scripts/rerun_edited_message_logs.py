import json
import pathlib

import typer

from ..ai import AI
from ..chat_to_files import to_files

app = typer.Typer()


@app.command()
def chat(
    messages_path: str,
    out_path: str | None = None,
    model: str = "gpt-4",
    temperature: float = 0.1,
    max_tokens: int = 4096,
):

    ai = AI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
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
