"""
This script cleans each subdirectory in the 'benchmark' folder,
removing all files and folders except those named 'prompt' or 'main_prompt'.
"""

import os
import shutil
from pathlib import Path
import typer

app = typer.Typer()

@app.command()
def clean(confirm: bool = typer.Option(False, help="Confirm cleanup without asking")):
    """
    Clean all benchmark folders by removing all contents
    except 'prompt' and 'main_prompt' files/folders.
    """
    benchmarks_dir = Path("benchmark")

    if not benchmarks_dir.exists():
        typer.echo("❌ 'benchmark' directory does not exist.")
        raise typer.Exit()

    for benchmark in benchmarks_dir.iterdir():
        if benchmark.is_dir():
            typer.echo(f"\n🧹 Cleaning '{benchmark}'")

            for item in benchmark.iterdir():
                if item.name in ["prompt", "main_prompt"]:
                    continue

                try:
                    if not confirm:
                        if not typer.confirm(f"Delete '{item}'?"):
                            continue

                    if item.is_dir():
                        shutil.rmtree(item)
                        typer.echo(f"✅ Deleted folder: {item}")
                    else:
                        item.unlink()
                        typer.echo(f"✅ Deleted file: {item}")

                except Exception as e:
                    typer.echo(f"⚠️ Error deleting {item}: {e}")

if __name__ == "__main__":
    app()
