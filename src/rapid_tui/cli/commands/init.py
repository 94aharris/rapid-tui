"""Initialize command for RAPID CLI."""

import sys
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint

from rapid_tui.models import Language, Assistant, InitializationConfig
from rapid_tui.services.initialization import InitializationService
from rapid_tui.cli.main import app

console = Console()


@app.command()
def init(
    ctx: typer.Context,
    language: Optional[str] = typer.Option(
        None, "--language", "-l",
        help="Programming language (angular, python, generic, see-sharp)"
    ),
    assistants: Optional[List[str]] = typer.Option(
        None, "--assistant", "-a",
        help="AI assistants to configure (can specify multiple)"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i",
        help="Interactive mode for selections"
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Overwrite existing files"
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p",
        help="Project path (default: current directory)"
    )
):
    """Initialize RAPID framework in your project."""

    verbose = ctx.obj.get("verbose", False)
    dry_run = ctx.obj.get("dry_run", False)

    project_path = path or Path.cwd()

    if not project_path.exists():
        console.print(f"[red]Error: Project path does not exist: {project_path}[/red]")
        raise typer.Exit(1)

    # Interactive mode or validate provided options
    selected_language = None
    selected_assistants = []

    if interactive or (not language and not assistants):
        selected_language, selected_assistants = _interactive_selection()
    else:
        # Validate language
        if language:
            try:
                selected_language = Language(language)
            except ValueError:
                console.print(f"[red]Error: Invalid language '{language}'[/red]")
                console.print("Valid options: angular, python, generic, see-sharp")
                raise typer.Exit(1)
        else:
            selected_language = _prompt_for_language()

        # Validate assistants
        if assistants:
            for assistant in assistants:
                try:
                    selected_assistants.append(Assistant(assistant.replace("-", "_")))
                except ValueError:
                    console.print(f"[red]Error: Invalid assistant '{assistant}'[/red]")
                    console.print("Valid options: claude-code, github-copilot, rapid-only")
                    raise typer.Exit(1)
        else:
            selected_assistants = _prompt_for_assistants()

    # Always include rapid_only if not present
    if Assistant.RAPID_ONLY not in selected_assistants:
        selected_assistants.append(Assistant.RAPID_ONLY)

    # Show summary
    _show_initialization_summary(selected_language, selected_assistants, project_path, dry_run)

    if not force:
        if not Confirm.ask("Proceed with initialization?"):
            console.print("[yellow]Initialization cancelled[/yellow]")
            raise typer.Exit(0)

    # Initialize with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task("Initializing RAPID framework...", total=None)

        service = InitializationService(project_path, dry_run=dry_run, force=force)
        result = service.initialize(
            language=selected_language,
            assistants=selected_assistants,
            verbose=verbose
        )

    # Show results
    if result.success:
        console.print("\n[green]✓ RAPID framework initialized successfully![/green]")
        console.print(f"  Files copied: {result.total_files_copied}")
        console.print(f"  Directories created: {result.total_directories_created}")

        if verbose:
            _show_detailed_results(result)
    else:
        console.print("\n[red]✗ Initialization failed[/red]")
        for error in result.errors:
            console.print(f"  [red]• {error}[/red]")
        raise typer.Exit(1)

    if result.warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in result.warnings:
            console.print(f"  [yellow]• {warning}[/yellow]")


def _interactive_selection():
    """Interactive mode for selecting language and assistants."""
    console.print("\n[bold]RAPID Framework Interactive Setup[/bold]\n")

    # Language selection
    language_table = Table(title="Available Languages")
    language_table.add_column("Code", style="cyan")
    language_table.add_column("Language", style="green")
    language_table.add_column("Templates", style="yellow")

    for lang in Language:
        has_templates = "✓" if lang.has_templates else "✗"
        language_table.add_row(lang.value, lang.display_name, has_templates)

    console.print(language_table)

    language_choice = Prompt.ask(
        "\nSelect language",
        choices=[lang.value for lang in Language],
        default="python"
    )
    selected_language = Language(language_choice)

    # Assistant selection
    assistant_table = Table(title="Available AI Assistants")
    assistant_table.add_column("Code", style="cyan")
    assistant_table.add_column("Assistant", style="green")

    for asst in Assistant:
        assistant_table.add_row(asst.value.replace("_", "-"), asst.display_name)

    console.print(assistant_table)

    console.print("\n[dim]You can select multiple assistants (space-separated)[/dim]")
    assistant_choices = Prompt.ask(
        "Select assistants",
        default="claude-code rapid-only"
    )

    selected_assistants = []
    for choice in assistant_choices.split():
        try:
            selected_assistants.append(Assistant(choice.replace("-", "_")))
        except ValueError:
            console.print(f"[yellow]Warning: Invalid assistant '{choice}' ignored[/yellow]")

    return selected_language, selected_assistants


def _prompt_for_language():
    """Prompt for language selection."""
    console.print("\n[yellow]No language specified[/yellow]")
    language_choice = Prompt.ask(
        "Select language",
        choices=[lang.value for lang in Language],
        default="python"
    )
    return Language(language_choice)


def _prompt_for_assistants():
    """Prompt for assistant selection."""
    console.print("\n[yellow]No assistants specified[/yellow]")
    console.print("[dim]Available: claude-code, github-copilot, rapid-only[/dim]")
    assistant_choices = Prompt.ask(
        "Select assistants (space-separated)",
        default="claude-code rapid-only"
    )

    selected = []
    for choice in assistant_choices.split():
        try:
            selected.append(Assistant(choice.replace("-", "_")))
        except ValueError:
            console.print(f"[yellow]Warning: Invalid assistant '{choice}' ignored[/yellow]")

    return selected


def _show_initialization_summary(language, assistants, path, dry_run):
    """Show summary before initialization."""
    table = Table(title="Initialization Summary")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Language", language.display_name)
    table.add_row("Assistants", ", ".join([a.display_name for a in assistants]))
    table.add_row("Project Path", str(path))
    table.add_row("Mode", "DRY RUN" if dry_run else "LIVE")

    console.print("\n")
    console.print(table)
    console.print("\n")


def _show_detailed_results(result):
    """Show detailed results in verbose mode."""
    console.print("\n[bold]Operation Details:[/bold]")

    for op in result.operations:
        if op.success:
            console.print(f"  [green]✓[/green] {op.relative_destination}")
        else:
            console.print(f"  [red]✗[/red] {op.relative_destination}: {op.error_message}")