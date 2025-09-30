"""List command for RAPID CLI."""

import typer
from rich.console import Console
from rich.table import Table

from rapid_tui.cli.main import app
from rapid_tui.config import get_language_templates
from rapid_tui.models import Assistant, Language

console = Console()


@app.command(name="list")
def list_command(
    ctx: typer.Context,
    what: str = typer.Argument(
        ..., help="What to list: languages, assistants, templates"
    ),
):
    """List available options for RAPID framework."""

    if what.lower() == "languages":
        _list_languages()
    elif what.lower() == "assistants":
        _list_assistants()
    elif what.lower() == "templates":
        _list_templates()
    else:
        console.print(f"[red]Error: Unknown option '{what}'[/red]")
        console.print("Valid options: languages, assistants, templates")
        raise typer.Exit(1)


def _list_languages():
    """List available languages."""
    table = Table(title="Available Languages")
    table.add_column("Code", style="cyan", no_wrap=True)
    table.add_column("Display Name", style="green")
    table.add_column("Has Templates", style="yellow")
    table.add_column("Status", style="magenta")

    for lang in Language:
        has_templates = "✓" if lang.has_templates else "✗"
        status = "Available" if lang.has_templates else "Coming Soon"
        table.add_row(lang.value, lang.display_name, has_templates, status)

    console.print(table)
    console.print("\n[dim]Use with: rapid init --language <code>[/dim]")


def _list_assistants():
    """List available AI assistants."""
    table = Table(title="Available AI Assistants")
    table.add_column("Code", style="cyan", no_wrap=True)
    table.add_column("Display Name", style="green")
    table.add_column("Description", style="white")

    assistant_descriptions = {
        Assistant.CLAUDE_CODE: "Anthropic's Claude AI coding assistant",
        Assistant.GITHUB_COPILOT: "GitHub's AI pair programmer",
        Assistant.RAPID_ONLY: "Basic RAPID framework files only",
    }

    for asst in Assistant:
        code = asst.value.replace("_", "-")
        table.add_row(code, asst.display_name, assistant_descriptions[asst])

    console.print(table)
    console.print(
        "\n[dim]Use with: rapid init --assistant <code> (can specify multiple)[/dim]"
    )


def _list_templates():
    """List available templates per language."""
    console.print("[bold]Available Templates by Language[/bold]\n")

    for lang in Language:
        if lang.has_templates:
            console.print(f"[cyan]{lang.display_name}[/cyan]")

            templates = get_language_templates(lang)

            if templates.get("agents"):
                console.print("  [green]Agent Templates:[/green]")
                for agent in templates["agents"]:
                    console.print(f"    • {agent}")
            else:
                console.print("  [yellow]No agent templates available[/yellow]")

            console.print()
        else:
            console.print(f"[cyan]{lang.display_name}[/cyan]")
            console.print("  [yellow]Templates coming soon[/yellow]\n")
