import json
import pathlib

from typing import Optional

import typer

from gpt_engineer.ai import GPT

app = typer.Typer()


@app.command()
def main(
    messages_path: str,
    out_path: Optional[str] = None,
    model: str = "gpt-4",
    temperature: float = 0.1,
):
    ai = GPT(
        model=model,
        temperature=temperature,
    )

    with open(messages_path) as f:
        messages = json.load(f)

    messages = ai.next(messages)

    if out_path:
        with open(pathlib.Path(out_path) / "all_output.txt", "w") as f:
            json.dump(messages.last_message_content(), f)


if __name__ == "__main__":
    app()
