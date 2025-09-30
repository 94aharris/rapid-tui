"""Main RAPID TUI application."""

import logging
import sys
from pathlib import Path

from textual.app import App
from textual.binding import Binding
from textual.screen import Screen

from rapid_tui.models import Assistant, InitializationConfig, Language
from rapid_tui.screens.assistant_select import AssistantSelectScreen
from rapid_tui.screens.confirmation import ConfirmationScreen
from rapid_tui.screens.language_select import LanguageSelectScreen


class RapidTUI(App):
    """Main TUI application for RAPID framework initialization."""

    # Load CSS from external file
    CSS_PATH = "styles.css"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("escape", "back", "Back"),
        Binding("ctrl+c", "quit", "Exit"),
    ]

    def __init__(self):
        """Initialize the RAPID TUI application."""
        super().__init__()
        self.config = InitializationConfig()
        self.screens: dict[str, type[Screen]] = {}
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup application logging."""
        log_dir = Path.cwd() / ".rapid"
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_dir / "rapid_tui.log"),
                logging.StreamHandler(),
            ],
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info("RAPID TUI started")

    def on_mount(self) -> None:
        """Initialize application on mount."""
        # Validate environment
        if not self._validate_environment():
            self.exit(message="Environment validation failed")
            return

        # Start with language selection
        self.push_screen(LanguageSelectScreen())

    def _validate_environment(self) -> bool:
        """Validate environment for running RAPID TUI."""
        current_dir = Path.cwd()

        # Check write permissions
        test_file = current_dir / ".rapid_test"
        try:
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            self.logger.error(f"No write permission in current directory: {e}")
            print(f"❌ Error: No write permission in current directory: {current_dir}")
            return False

        self.logger.info(f"Environment validated for: {current_dir}")
        return True

    def handle_language_selection(self, language: Language) -> None:
        """
        Handle language selection from language screen.

        Args:
            language: Selected programming language
        """
        self.config.language = language
        self.logger.info(f"Language selected: {language.display_name}")

        # Navigate to assistant selection
        assistant_screen = AssistantSelectScreen(language)
        self.push_screen(assistant_screen)

    def handle_assistant_selection(self, assistants: list[Assistant]) -> None:
        """
        Handle assistant selection from assistant screen.

        Args:
            assistants: List of selected assistants
        """
        self.config.assistants = assistants
        self.logger.info(f"Assistants selected: {[a.display_name for a in assistants]}")

        # Navigate to confirmation screen
        confirmation_screen = ConfirmationScreen(self.config)
        self.push_screen(confirmation_screen)

    def go_back(self) -> None:
        """Navigate to the previous screen."""
        if len(self.screen_stack) > 1:
            self.pop_screen()
            self.logger.info("Navigated back to previous screen")

    def action_back(self) -> None:
        """Handle back action."""
        self.go_back()

    def action_quit(self) -> None:
        """Handle quit action."""
        self.logger.info("Application quit by user")
        self.exit()

    def on_screen_suspend(self) -> None:
        """Handle screen suspend event."""
        self.logger.info("Screen suspended")

    def on_screen_resume(self) -> None:
        """Handle screen resume event."""
        self.logger.info("Screen resumed")


def main():
    """Universal entry point that delegates to CLI or TUI."""

    # Check if --ui flag is present (hidden but still functional)
    if "--ui" in sys.argv:
        # Remove --ui from args if present
        if "--ui" in sys.argv:
            sys.argv.remove("--ui")

        # Launch TUI mode
        try:
            app = RapidTUI()
            app.run()
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            logging.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)
    else:
        # Launch CLI mode (default)
        from rapid_tui.cli.main import cli

        cli()


if __name__ == "__main__":
    main()
