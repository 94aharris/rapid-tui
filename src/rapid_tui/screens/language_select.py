"""Language selection screen for RAPID TUI."""

from textual.app import ComposeResult
from textual.widgets import Static, RadioSet, RadioButton, Button
from textual.containers import Horizontal, Vertical
from textual import on
from typing import Optional

from rapid_tui.screens.base import BaseScreen
from rapid_tui.models import Language


class LanguageSelectScreen(BaseScreen):
    """Screen for selecting programming language/framework."""

    # CSS is now in external styles.css file

    def __init__(self):
        """Initialize language selection screen."""
        super().__init__(name="language_select", title="Select Programming Language")
        self.selected_language: Optional[Language] = None

    def setup_content(self) -> None:
        """Setup the language selection interface."""
        content = self.query_one("#content")

        # Clear existing content by removing all children
        for child in list(content.children):
            child.remove()

        # Add description
        content.mount(
            Static(
                "Select the primary programming language/framework for your project:",
                classes="language-description",
            )
        )

        # Create language selection container
        language_container = Vertical(classes="language-container")

        # Create radio set for language selection
        radio_set = RadioSet(id="language_radio")

        # Containers must be mounted before adding children
        content.mount(language_container)
        language_container.mount(radio_set)

        for language in Language:
            label = language.display_name
            if not language.has_templates:
                label += " (⚠️ No templates available yet)"

            # Create radio button with label and set its ID for tracking
            radio_button = RadioButton(label, id=f"radio_{language.value}")
            radio_set.mount(radio_button)

        # Add buttons
        button_row = Horizontal(
            Button("Next", variant="primary", id="next_button"),
            Button("Cancel", variant="default", id="cancel_button"),
            classes="button-row",
        )

        content.mount(button_row)

    def set_initial_focus(self) -> None:
        """Set initial focus to the language radio set."""
        try:
            radio_set = self.query_one("#language_radio", RadioSet)
            radio_set.focus()
        except Exception:
            pass  # Focus fallback handled by Textual

    @on(RadioSet.Changed, "#language_radio")
    def handle_language_selection(self, event: RadioSet.Changed) -> None:
        """Handle language selection change."""
        if event.pressed is None:
            return
        try:
            # Extract language value from button ID (radio_{language_value})
            button_id = event.pressed.id
            if button_id and button_id.startswith("radio_"):
                language_value = button_id.replace("radio_", "")
                self.selected_language = Language(language_value)
                self.logger.info(
                    f"Language selected: {self.selected_language.display_name}"
                )

            # Show warning if no templates available
            if not self.selected_language.has_templates:
                self.show_warning(
                    f"Note: {self.selected_language.display_name} templates are not yet available. "
                    "Only command templates will be copied."
                )
            else:
                self.clear_messages()

        except ValueError as e:
            self.show_error(f"Invalid language selection: {e}")

    @on(Button.Pressed, "#next_button")
    def handle_next_button(self) -> None:
        """Handle next button press."""
        if self.validate_input():
            self.app.handle_language_selection(self.selected_language)

    @on(Button.Pressed, "#cancel_button")
    def handle_cancel_button(self) -> None:
        """Handle cancel button press."""
        self.app.exit()

    def validate_input(self) -> bool:
        """Validate that a language has been selected."""
        if self.selected_language is None:
            self.show_error("Please select a programming language")
            return False

        self.clear_messages()
        return True

    def get_result(self) -> Optional[Language]:
        """Get the selected language."""
        return self.selected_language
