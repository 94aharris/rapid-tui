"""Main Typer CLI application for RAPID framework."""

import sys
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from rapid_tui.models import Language, Assistant

app = typer.Typer(
    name="rapid",
    help="RAPID Framework initialization and management tool",
    no_args_is_help=True,
    rich_markup_mode="rich"
)

console = Console()

# Import commands to register them with the app
from rapid_tui.cli.commands import init, list, config, status


@app.callback()
def main(
    ctx: typer.Context,
    ui: bool = typer.Option(False, "--ui", hidden=True),  # Hidden but still functional
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate operations without making changes")
):
    """
    RAPID Framework CLI - Initialize AI-driven development projects
    """
    ctx.ensure_object(dict)
    ctx.obj["ui"] = ui
    ctx.obj["verbose"] = verbose
    ctx.obj["dry_run"] = dry_run

    if ui:
        from rapid_tui.app import RapidTUI
        app = RapidTUI()
        app.run()
        raise typer.Exit()


def cli():
    """CLI entry point."""
    app()


if __name__ == "__main__":
    cli()