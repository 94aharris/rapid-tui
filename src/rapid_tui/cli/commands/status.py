"""Status command for RAPID CLI."""

from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from rapid_tui.cli.main import app

console = Console()


@app.command()
def status(
    ctx: typer.Context,
    path: Annotated[
        Path | None,
        typer.Option("--path", "-p", help="Project path (default: current directory)"),
    ] = None,
):
    """Check RAPID framework initialization status in current project."""

    project_path = path or Path.cwd()
    rapid_dir = project_path / ".rapid"

    if not rapid_dir.exists():
        console.print(
            "[yellow]⚠ RAPID framework not initialized in this project[/yellow]"
        )
        console.print("\nRun [cyan]rapid init[/cyan] to initialize RAPID framework")
        raise typer.Exit(1)

    console.print("[green]✓ RAPID framework is initialized[/green]\n")

    # Check directory structure
    _show_directory_structure(rapid_dir)

    # Show statistics
    _show_statistics(rapid_dir)

    # Check for updates or issues
    _check_health(rapid_dir)


def _show_directory_structure(rapid_dir: Path):
    """Show the .rapid directory structure."""
    tree = Tree("[bold].rapid[/bold] directory structure")

    for item in sorted(rapid_dir.iterdir()):
        if item.is_dir():
            branch = tree.add(f"[cyan]{item.name}/[/cyan]")
            file_count = sum(1 for _ in item.rglob("*") if _.is_file())
            if file_count > 0:
                branch.add(f"[dim]{file_count} file(s)[/dim]")
        else:
            tree.add(f"[white]{item.name}[/white]")

    console.print(tree)
    console.print()


def _show_statistics(rapid_dir: Path):
    """Show statistics about the RAPID installation."""
    table = Table(title="Installation Statistics")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")

    # Count agents
    agents_dir = rapid_dir / "agents"
    agent_count = sum(1 for _ in agents_dir.rglob("*.md")) if agents_dir.exists() else 0
    table.add_row("Agent Templates", str(agent_count))

    # Count commands
    commands_dir = rapid_dir / "commands"
    command_count = (
        sum(1 for _ in commands_dir.rglob("*.md")) if commands_dir.exists() else 0
    )
    table.add_row("Command Templates", str(command_count))

    # Check for assistant-specific directories
    assistant_dirs = []
    for possible_dir in ["claude", "copilot"]:
        if (rapid_dir / possible_dir).exists():
            assistant_dirs.append(possible_dir)

    if assistant_dirs:
        table.add_row("Assistant Configs", ", ".join(assistant_dirs))
    else:
        table.add_row("Assistant Configs", "None")

    # Check for log files
    log_files = list(rapid_dir.glob("*.log"))
    table.add_row("Log Files", str(len(log_files)))

    console.print(table)
    console.print()


def _check_health(rapid_dir: Path):
    """Check for potential issues or updates."""
    issues = []
    suggestions = []

    # Check if directories are empty
    agents_dir = rapid_dir / "agents"
    if agents_dir.exists() and not any(agents_dir.iterdir()):
        issues.append("Agents directory is empty")
        suggestions.append("Run [cyan]rapid init[/cyan] to add agent templates")

    commands_dir = rapid_dir / "commands"
    if commands_dir.exists() and not any(commands_dir.iterdir()):
        issues.append("Commands directory is empty")
        suggestions.append("Run [cyan]rapid init[/cyan] to add command templates")

    # Check for old log files
    log_files = list(rapid_dir.glob("*.log"))
    for log_file in log_files:
        stat = log_file.stat()
        age_days = (datetime.now().timestamp() - stat.st_mtime) / 86400
        if age_days > 30:
            suggestions.append(
                f"Old log file: {log_file.name} ({int(age_days)} days old)"
            )

    # Display health check results
    if issues:
        console.print("[yellow]⚠ Issues Found:[/yellow]")
        for issue in issues:
            console.print(f"  • {issue}")
        console.print()

    if suggestions:
        console.print("[blue]ℹ Suggestions:[/blue]")
        for suggestion in suggestions:
            console.print(f"  • {suggestion}")
    else:
        console.print("[green]✓ No issues found[/green]")
