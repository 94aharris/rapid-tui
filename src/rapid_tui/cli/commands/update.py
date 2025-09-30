"""Update command for RAPID CLI."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from rapid_tui.cli.main import app
from rapid_tui.models import Assistant
from rapid_tui.services.update import UpdateService
from rapid_tui.config import resolve_agent_name, get_available_agent_names

console = Console()


@app.command()
def update(
    ctx: typer.Context,
    agent: Optional[str] = typer.Option(
        None, "--agent", "-a", help="Update specific agent (claude, copilot, all)"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force update even if target files are newer"
    ),
    reverse: bool = typer.Option(
        False,
        "--reverse",
        "-r",
        help="Consolidate changes from assistant directories back to .rapid/",
    ),
) -> None:
    """Synchronize files between .rapid/ and assistant directories.

    By default, syncs FROM .rapid/ TO assistant directories (.claude/, .github/).
    Use --reverse to consolidate changes FROM assistant directories TO .rapid/.

    Only updates files where the source is newer than the target unless --force is used.

    Examples:
        rapid update                        # Update all agents from .rapid/
        rapid update --agent claude         # Update only Claude from .rapid/
        rapid update --reverse              # Consolidate all changes to .rapid/
        rapid update --reverse --agent claude # Consolidate only Claude changes
        rapid update --force --reverse      # Force consolidate all changes
    """
    verbose = ctx.obj.get("verbose", False)
    dry_run = ctx.obj.get("dry_run", False)

    project_root = Path.cwd()

    # Check if .rapid directory exists
    rapid_dir = project_root / ".rapid"
    if not rapid_dir.exists():
        console.print("[red]Error: .rapid directory not found[/red]")
        console.print("Run 'rapid init' to initialize the project first.")
        raise typer.Exit(1)

    # Validate agent parameter if provided
    target_agent = None
    if agent:
        if agent.lower() == "all":
            target_agent = None  # Will sync all agents
        else:
            target_agent = resolve_agent_name(agent)
            if target_agent is None:
                console.print(f"[red]Error: Invalid agent name '{agent}'[/red]")
                console.print(
                    f"Available agents: {', '.join(get_available_agent_names())}"
                )
                raise typer.Exit(1)

    # Show operation summary
    _show_update_summary(target_agent, force, dry_run, verbose, reverse)

    # Initialize service and perform update
    service = UpdateService(project_root, dry_run=dry_run, verbose=verbose)

    if reverse:
        # Consolidate changes from assistant directories to .rapid/
        if target_agent is None:
            # Consolidate from all agents
            result = service.consolidate_all_agents(force=force)
        else:
            # Consolidate from specific agent
            result = service.consolidate_agent(target_agent, force=force)
    else:
        # Normal sync from .rapid/ to assistant directories
        if target_agent is None:
            # Update all agents
            result = service.sync_all_agents(force=force)
        else:
            # Update specific agent
            result = service.sync_agent(target_agent, force=force)

    # Display results
    service.display_results(result, reverse=reverse)

    # Exit with appropriate code
    if not result.success:
        raise typer.Exit(1)


def _show_update_summary(
    agent: Optional[Assistant], force: bool, dry_run: bool, verbose: bool, reverse: bool
):
    """Show summary of update operation before execution."""
    if dry_run or verbose:
        operation_name = "Consolidation" if reverse else "Update"
        table = Table(title=f"{operation_name} Summary")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        target_name = agent.display_name if agent else "All agents"
        direction = "FROM agents TO .rapid/" if reverse else "FROM .rapid/ TO agents"

        table.add_row("Target", target_name)
        table.add_row("Direction", direction)
        table.add_row("Force update", "Yes" if force else "No")
        table.add_row("Mode", "DRY RUN" if dry_run else "LIVE")

        console.print("\n")
        console.print(table)
        console.print("\n")


def _show_available_agents():
    """Display table of available agents for user reference."""
    table = Table(title="Available Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("CLI Alias", style="yellow")

    # Only show agents that can be updated (not RAPID_ONLY)
    updateable_agents = [
        (Assistant.CLAUDE_CODE, "claude"),
        (Assistant.GITHUB_COPILOT, "copilot"),
    ]

    for assistant, alias in updateable_agents:
        table.add_row(
            assistant.display_name, f"Update {assistant.display_name} files", alias
        )

    table.add_row("All Agents", "Update all configured agents", "all")

    console.print(table)
