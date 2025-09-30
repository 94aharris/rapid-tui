"""Main Typer CLI application for RAPID framework."""

import typer
from rich.console import Console

from rapid_tui import __version__
from rapid_tui.utils.logo import display_welcome_banner

app = typer.Typer(
    name="rapid",
    help=f"RAPID Framework initialization and management tool (v{__version__})",
    rich_markup_mode="rich",
)

console = Console()


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(f"RAPID TUI v{__version__}")
        raise typer.Exit()


# Import commands to register them with the app


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    ui: bool = typer.Option(False, "--ui", hidden=True),  # Hidden but still functional
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Simulate operations without making changes"
    ),
):
    f"""
    RAPID Framework CLI - Initialize AI-driven development projects

    Version: {__version__}
    """  # noqa: B021
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
