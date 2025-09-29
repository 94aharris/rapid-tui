"""Simplified language selection screen using custom widgets."""

from textual.app import ComposeResult
from textual.widgets import RadioSet, RadioButton
from textual import on
from typing import Optional

from rapid_tui.screens.base import BaseScreen
from rapid_tui.models import Language
from rapid_tui.widgets import Card, StyledButton, InfoPanel, FormGroup


class LanguageSelectScreenV2(BaseScreen):
    """Simplified language selection screen with custom widgets."""

    def __init__(self):
        """Initialize language selection screen."""
        super().__init__(name="language_select", title="Select Programming Language")
        self.selected_language: Optional[Language] = None

    def compose(self) -> ComposeResult:
        """Compose the screen using custom widgets."""
        # Use the parent's compose for header/footer
        yield from super().compose()

    def setup_content(self) -> None:
        """Setup using simplified custom widgets."""
        content = self.query_one("#content")

        # Clear existing content
        for child in list(content.children):
            child.remove()

        # Create a card for the language selection
        card = Card(title="Select Programming Language", classes="language-card")
        content.mount(card)

        # Get the card content container
        card_content = card.query_one(".card-content")

        # Create form group for radio buttons
        form_group = FormGroup(label="Choose your primary language:")
        card_content.mount(form_group)

        # Get the form controls container
        form_controls = form_group.query_one(".form-controls")

        # Create radio set
        radio_set = RadioSet(id="language_radio")
        form_controls.mount(radio_set)

        # Add radio buttons for each language
        for language in Language:
            label = language.display_name
            if not language.has_templates:
                label += " (No templates yet)"

            radio_button = RadioButton(label, id=f"radio_{language.value}")
            radio_set.mount(radio_button)

        # Add info panel if needed
        info = InfoPanel(
            "Select the primary programming language for your project",
            icon="💡",
            variant="info"
        )
        card_content.mount(info)

        # Add action buttons
        button_container = card_content.mount(Container(classes="button-row"))
        button_container.mount(StyledButton("Next", variant="primary", id="next_button"))
        button_container.mount(StyledButton("Cancel", variant="default", id="cancel_button"))

    @on(RadioSet.Changed, "#language_radio")
    def handle_language_selection(self, event: RadioSet.Changed) -> None:
        """Handle language selection change."""
        if event.pressed is None:
            return

        button_id = event.pressed.id
        if button_id and button_id.startswith("radio_"):
            language_value = button_id.replace("radio_", "")
            self.selected_language = Language(language_value)

            # Show warning if no templates
            if not self.selected_language.has_templates:
                self.show_warning(f"Note: {self.selected_language.display_name} templates are not yet available.")
            else:
                self.clear_messages()

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
        return True