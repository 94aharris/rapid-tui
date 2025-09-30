"""Logo display utility for RAPID CLI."""

from pathlib import Path

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def get_logo_path() -> Path:
    """Get the path to the logo file."""
    # Try multiple possible locations for the logo
    current_file = Path(__file__)

    # Look for logo relative to the package
    possible_paths = [
        current_file.parent.parent.parent.parent
        / "imgs"
        / "logo.txt",  # From src/rapid_tui/utils
        Path.cwd() / "imgs" / "logo.txt",  # From current working directory
        Path.home() / ".rapid" / "logo.txt",  # From user home directory
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


def load_logo() -> str:
    """Load the logo text from file."""
    logo_path = get_logo_path()

    if not logo_path or not logo_path.exists():
        return None

    try:
        with open(logo_path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def display_logo(
    console: Console = None, color: str = "cyan", show_panel: bool = False
):
    """Display the RAPID logo in the console.

    Args:
        console: Rich console instance (creates new if None)
        color: Color for the logo text
        show_panel: Whether to wrap logo in a panel
    """
    if console is None:
        console = Console()

    logo_text = load_logo()

    if not logo_text:
        return

    styled_logo = Text(logo_text, style=color)

    if show_panel:
        logo_panel = Panel(
            Align.center(styled_logo), border_style=color, padding=(0, 2)
        )
        console.print(logo_panel)
    else:
        console.print(Align.center(styled_logo))


def display_welcome_banner(console: Console = None):
    """Display a welcome banner with logo and title."""
    if console is None:
        console = Console()

    # Display the logo
    display_logo(console, color="cyan")

    # Add a welcome message
    welcome_text = Text("\nRAPID Framework CLI", style="bold white")
    subtitle = Text("Initialize AI-driven development projects\n", style="dim")

    console.print(Align.center(welcome_text))
    console.print(Align.center(subtitle))
