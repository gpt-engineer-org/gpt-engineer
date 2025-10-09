import os
import platform
import subprocess
import sys

from importlib.metadata import distributions

from controller import Controller
from model import Game
from rich.console import Console
from rich.table import Table
from view import View

# Sensitive environment variables to mask
SENSITIVE_KEYS = ["OPENAI_API_KEY", "API_KEY", "SECRET", "TOKEN"]


def get_command_version(command):
    """Run a command and return its version, or 'Not found'."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split("\n")[0]
        return "Not found"
    except Exception:
        return "Not found"


def get_env_variables():
    """Return filtered environment variables with sensitive ones masked."""
    filtered = {}
    for key, value in os.environ.items():
        if key in SENSITIVE_KEYS:
            filtered[key] = "*****"
        elif key in ["PATH", "PYTHONPATH", "VIRTUAL_ENV"]:
            filtered[key] = value
    return filtered


def get_installed_packages():
    """Return a dict of installed Python packages and versions."""
    packages = {}
    for dist in distributions():
        name = dist.metadata["Name"]
        version = dist.version
        if name:
            packages[name] = version
    return packages


def sysinfo():
    info = {
        "gpt_engineer_version": "0.3.1",  # Change if your package version differs
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "pip_version": get_command_version("pip --version"),
        "git_version": get_command_version("git --version"),
        "node_version": get_command_version("node --version"),
        "env_variables": get_env_variables(),
        "installed_packages": get_installed_packages(),
    }

    # Pretty print using Rich
    console = Console()
    console.print("\n[bold cyan]=== System Information ===[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    # Top-level info
    for key in [
        "gpt_engineer_version",
        "os",
        "os_version",
        "architecture",
        "python_version",
        "pip_version",
        "git_version",
        "node_version",
    ]:
        table.add_row(key, str(info[key]))

    console.print(table)

    # Environment variables
    console.print("\n[bold cyan]Environment Variables:[/bold cyan]")
    for k, v in info["env_variables"].items():
        console.print(f"{k}: {v}")

    # Installed packages (optional: print first 30 only)
    console.print("\n[bold cyan]Installed Packages (first 30 shown):[/bold cyan]")
    for i, (pkg, ver) in enumerate(info["installed_packages"].items()):
        if i >= 30:
            console.print(f"... ({len(info['installed_packages'])-30} more packages)")
            break
        console.print(f"{pkg}: {ver}")


def main():
    # Check if --sysinfo argument is provided
    if "--sysinfo" in sys.argv:
        sysinfo()
        return

    # Regular game loop
    game = Game()
    view = View(game)
    controller = Controller(game, view)

    while game.is_running:
        controller.handle_input()
        game.update()
        view.render()


if __name__ == "__main__":
    main()
