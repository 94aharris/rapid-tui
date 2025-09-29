"""Base screen class for RAPID TUI screens."""

from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.containers import Container, Vertical
from textual.app import ComposeResult
from typing import Optional, Any
import logging


class BaseScreen(Screen):
    """Base class for all RAPID TUI screens."""

    # No inline CSS needed - using external styles.css

    def __init__(self, name: str = None, title: str = "RAPID TUI"):
        """
        Initialize base screen.

        Args:
            name: Screen name for navigation
            title: Screen title to display
        """
        super().__init__(name=name)
        self.title = title
        self.error_message: Optional[str] = None
        self.warning_message: Optional[str] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def compose(self) -> ComposeResult:
        """Compose the base layout."""
        yield Header()
        yield Container(
            Static(self.title, classes="screen-title"),
            Vertical(id="content", classes="content-container"),
            id="main-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Handle mount event."""
        self.logger.info(f"Screen mounted: {self.__class__.__name__}")
        self.setup_content()
        self.set_initial_focus()

    def set_initial_focus(self) -> None:
        """Set initial focus for the screen. Override in subclasses."""
        pass

    def setup_content(self) -> None:
        """Setup screen-specific content. Override in subclasses."""
        pass

    def show_error(self, message: str) -> None:
        """Display an error message."""
        self.error_message = message
        error_widget = Static(f"❌ {message}", classes="error-message")
        content = self.query_one("#content")
        content.mount(error_widget)
        self.logger.error(message)

    def show_warning(self, message: str) -> None:
        """Display a warning message."""
        self.warning_message = message
        warning_widget = Static(f"⚠️  {message}", classes="warning-message")
        content = self.query_one("#content")
        content.mount(warning_widget)
        self.logger.warning(message)

    def show_info(self, message: str) -> None:
        """Display an info message."""
        info_widget = Static(f"ℹ️  {message}", classes="info-message")
        content = self.query_one("#content")
        content.mount(info_widget)
        self.logger.info(message)

    def clear_messages(self) -> None:
        """Clear all messages."""
        content = self.query_one("#content")
        for widget in content.query(".error-message, .warning-message, .info-message"):
            widget.remove()

    def validate_input(self) -> bool:
        """
        Validate user input before proceeding.
        Override in subclasses.

        Returns:
            True if input is valid, False otherwise
        """
        return True

    def get_result(self) -> Any:
        """
        Get the result/selection from this screen.
        Override in subclasses.

        Returns:
            Screen-specific result data
        """
        return None

    def can_proceed(self) -> bool:
        """
        Check if user can proceed to next screen.

        Returns:
            True if can proceed, False otherwise
        """
        if not self.validate_input():
            return False
        return self.error_message is None