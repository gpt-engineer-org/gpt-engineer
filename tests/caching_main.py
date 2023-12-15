import typer

from gpt_engineer.applications.cli.main import main
from tests.caching_ai import CachingAI

# Entry point for the caching_main CLI application
main.__globals__["AI"] = CachingAI
app = typer.Typer()
app.command()(main)

if __name__ == "__main__":
    typer.run(main)

# Utilizes Typer for CLI interactions and sets up the main function for execution with a caching layer.
