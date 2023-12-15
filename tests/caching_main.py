from tests.caching_ai import CachingAI
from gpt_engineer.applications.cli.main import main
import typer


main.__globals__["AI"] = CachingAI
app = typer.Typer()
app.command()(main)

if __name__ == "__main__":
    typer.run(main)
