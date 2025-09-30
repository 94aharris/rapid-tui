"""Main Typer CLI application for RAPID framework."""

import sys
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
import click

from rapid_tui.models import Language, Assistant
from rapid_tui.utils.logo import display_welcome_banner

app = typer.Typer(
    name="rapid",
    help="RAPID Framework initialization and management tool",
    rich_markup_mode="rich",
)

console = Console()

# Import commands to register them with the app
from rapid_tui.cli.commands import init, list, config, status


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    ui: bool = typer.Option(False, "--ui", hidden=True),  # Hidden but still functional
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Simulate operations without making changes"
    ),
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

    # Show logo and help when no command is provided
    if ctx.invoked_subcommand is None:
        display_welcome_banner(console)
        console.print()  # Add some spacing
        console.print(ctx.get_help())
        raise typer.Exit()


def cli():
    """CLI entry point."""
    app()


if __name__ == "__main__":
    cli()
