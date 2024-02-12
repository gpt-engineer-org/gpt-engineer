import typer

from gpt_engineer.applications.cli.main import main
from tests.caching_ai import CachingAI

main.__globals__["AI"] = CachingAI
app = typer.Typer()
app.command()(main)

if __name__ == "__main__":
    typer.run(main)
