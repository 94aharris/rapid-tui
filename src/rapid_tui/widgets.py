"""Custom styled widgets for RAPID TUI."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Container, Static


class StyledButton(Button):
    """A button with consistent styling."""

    DEFAULT_CLASSES = "styled-button"

    def __init__(self, label: str, variant: str = "primary", **kwargs):
        """Initialize styled button with variant support."""
        super().__init__(label, variant=variant, **kwargs)
        self.add_class(f"button-{variant}")


class Card(Vertical):
    """A card container with consistent styling."""

    DEFAULT_CLASSES = "card"

    def __init__(self, title: str = None, **kwargs):
        """Initialize card with optional title."""
        super().__init__(**kwargs)
        self.title = title

    def compose(self) -> ComposeResult:
        """Compose the card layout."""
        if self.title:
            yield Static(self.title, classes="card-title")
        yield Container(classes="card-content")


class InfoPanel(Vertical):
    """An info panel with icon and text."""

    DEFAULT_CLASSES = "info-panel"

    def __init__(self, message: str, icon: str = "ℹ️", variant: str = "info", **kwargs):
        """Initialize info panel."""
        super().__init__(**kwargs)
        self.message = message
        self.icon = icon
        self.add_class(f"info-panel-{variant}")

    def compose(self) -> ComposeResult:
        """Compose the info panel."""
        yield Horizontal(
            Static(self.icon, classes="info-icon"),
            Static(self.message, classes="info-text"),
            classes="info-content",
        )


class FormGroup(Vertical):
    """A form group container for better organization."""

    DEFAULT_CLASSES = "form-group"

    def __init__(self, label: str = None, **kwargs):
        """Initialize form group."""
        super().__init__(**kwargs)
        self.label = label

    def compose(self) -> ComposeResult:
        """Compose the form group."""
        if self.label:
            yield Static(self.label, classes="form-label")
        yield Container(classes="form-controls")
