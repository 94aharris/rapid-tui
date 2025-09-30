"""Configuration command for RAPID CLI."""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from rapid_tui.cli.main import app
from rapid_tui.models import Assistant, Language

console = Console()

CONFIG_FILE_NAME = ".rapidrc.json"


@app.command()
def config(
    ctx: typer.Context,
    show: Annotated[
        bool, typer.Option("--show", help="Show current configuration")
    ] = False,
    set_language: Annotated[
        str | None, typer.Option("--set-language", help="Set default language")
    ] = None,
    set_assistants: Annotated[
        list[str] | None, typer.Option("--set-assistant", help="Set default assistants")
    ] = None,
    global_config: Annotated[
        bool, typer.Option("--global", help="Use global config instead of local")
    ] = False,
    reset: Annotated[
        bool, typer.Option("--reset", help="Reset configuration to defaults")
    ] = False,
):
    """Manage RAPID configuration."""

    config_path = _get_config_path(global_config)

    if reset:
        _reset_config(config_path)
        return

    if show:
        _show_config(config_path)
        return

    if set_language or set_assistants:
        _update_config(config_path, set_language, set_assistants)
        return

    # If no options, show current config
    _show_config(config_path)


def _get_config_path(global_config: bool) -> Path:
    """Get configuration file path."""
    if global_config:
        return Path.home() / CONFIG_FILE_NAME
    else:
        return Path.cwd() / CONFIG_FILE_NAME


def _load_config(config_path: Path) -> dict:
    """Load configuration from file."""
    if not config_path.exists():
        return {
            "defaults": {
                "language": "python",
                "assistants": ["claude_code", "rapid_only"],
                "verbose": False,
            }
        }

    try:
        with open(config_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        console.print(f"[red]Error: Invalid JSON in {config_path}[/red]")
        return {}


def _save_config(config_path: Path, config: dict):
    """Save configuration to file."""
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    console.print(f"[green]Configuration saved to {config_path}[/green]")


def _show_config(config_path: Path):
    """Show current configuration."""
    config = _load_config(config_path)

    table = Table(title=f"RAPID Configuration ({config_path.name})")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    if "defaults" in config:
        defaults = config["defaults"]
        table.add_row("Default Language", defaults.get("language", "not set"))

        assistants = defaults.get("assistants", [])
        if assistants:
            assistants_str = ", ".join([a.replace("_", "-") for a in assistants])
        else:
            assistants_str = "not set"
        table.add_row("Default Assistants", assistants_str)

        table.add_row("Verbose", str(defaults.get("verbose", False)))

    console.print(table)

    if not config_path.exists():
        console.print(
            "\n[dim]Note: Using default configuration (file does not exist)[/dim]"
        )


def _update_config(
    config_path: Path, language: str | None, assistants: list[str] | None
):
    """Update configuration settings."""
    config = _load_config(config_path)

    if "defaults" not in config:
        config["defaults"] = {}

    updated = False

    if language:
        # Validate language
        try:
            lang = Language(language)
            config["defaults"]["language"] = lang.value
            console.print(
                f"[green]Default language set to: {lang.display_name}[/green]"
            )
            updated = True
        except ValueError:
            console.print(f"[red]Error: Invalid language '{language}'[/red]")
            console.print("Valid options: angular, python, generic, see-sharp")
            raise typer.Exit(1) from None

    if assistants:
        # Validate assistants
        valid_assistants = []
        for assistant in assistants:
            try:
                asst = Assistant(assistant.replace("-", "_"))
                valid_assistants.append(asst.value)
            except ValueError:
                console.print(f"[red]Error: Invalid assistant '{assistant}'[/red]")
                console.print("Valid options: claude-code, github-copilot, rapid-only")
                raise typer.Exit(1) from None

        config["defaults"]["assistants"] = valid_assistants
        console.print(
            f"[green]Default assistants set to: {', '.join(assistants)}[/green]"
        )
        updated = True

    if updated:
        _save_config(config_path, config)


def _reset_config(config_path: Path):
    """Reset configuration to defaults."""
    if config_path.exists():
        config_path.unlink()
        console.print(f"[yellow]Configuration reset ({config_path} deleted)[/yellow]")
    else:
        console.print("[yellow]No configuration file to reset[/yellow]")
