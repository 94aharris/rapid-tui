"""Assistant selection screen for RAPID TUI."""

from textual import on
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Checkbox, Static

from rapid_tui.models import Assistant, Language
from rapid_tui.screens.base import BaseScreen


class AssistantSelectScreen(BaseScreen):
    """Screen for selecting AI assistants to configure."""

    # CSS is now in external styles.css file

    def __init__(self, language: Language):
        """
        Initialize assistant selection screen.

        Args:
            language: Previously selected programming language
        """
        super().__init__(name="assistant_select", title="Select AI Assistants")
        self.language = language
        self.selected_assistants: set[Assistant] = set()

    def setup_content(self) -> None:
        """Setup the assistant selection interface."""
        content = self.query_one("#content")
        # Remove all existing children
        for child in list(content.children):
            child.remove()

        # Add description
        desc_text = f"Select AI assistants to configure for {self.language.display_name} development:"
        content.mount(Static(desc_text, classes="assistant-description"))

        # Create assistant selection container and mount it first
        assistant_container = Vertical(classes="assistant-container")
        content.mount(assistant_container)

        # Add checkboxes for each assistant
        for assistant in Assistant:
            if assistant == Assistant.RAPID_ONLY:
                continue  # Skip RAPID_ONLY as it's always included

            checkbox = Checkbox(
                f"  {assistant.display_name}",
                value=False,
                id=f"assistant_{assistant.value}",
            )

            # Add description based on assistant
            info = self._get_assistant_info(assistant)
            info_widget = Static(info, classes="assistant-info") if info else None

            item_container = Vertical(classes="assistant-item")
            assistant_container.mount(item_container)

            # Now mount children to the item_container after it's been added
            item_container.mount(checkbox)
            if info_widget:
                item_container.mount(info_widget)

        # Add note about .rapid directory
        rapid_note = Static(
            "Note: The .rapid directory will always be created with full template structure",
            classes="rapid-note",
        )

        assistant_container.mount(rapid_note)

        # Add buttons
        button_row = Horizontal(
            Button("Previous", variant="default", id="prev_button"),
            Button("Next", variant="primary", id="next_button"),
            Button("Cancel", variant="default", id="cancel_button"),
            classes="button-row",
        )

        content.mount(button_row)

    def set_initial_focus(self) -> None:
        """Set initial focus to the first checkbox."""
        try:
            checkbox = self.query_one(Checkbox)
            checkbox.focus()
        except Exception:
            pass  # Focus fallback handled by Textual

    def _get_assistant_info(self, assistant: Assistant) -> str:
        """Get descriptive info for each assistant."""
        info_map = {
            Assistant.CLAUDE_CODE: "→ Creates .claude/agents/ and .claude/commands/",
            Assistant.GITHUB_COPILOT: "→ Creates .github/prompts/ (commands only, no agents)",
        }
        return info_map.get(assistant, "")

    @on(Checkbox.Changed)
    def handle_checkbox_change(self, event: Checkbox.Changed) -> None:
        """Handle checkbox state changes."""
        # Extract assistant from checkbox ID
        checkbox_id = event.checkbox.id
        if checkbox_id and checkbox_id.startswith("assistant_"):
            assistant_value = checkbox_id.replace("assistant_", "")

            try:
                assistant = Assistant(assistant_value)

                if event.value:
                    self.selected_assistants.add(assistant)
                    self.logger.info(f"Added assistant: {assistant.display_name}")
                else:
                    self.selected_assistants.discard(assistant)
                    self.logger.info(f"Removed assistant: {assistant.display_name}")

            except ValueError as e:
                self.show_error(f"Invalid assistant: {e}")

    @on(Button.Pressed, "#next_button")
    def handle_next_button(self) -> None:
        """Handle next button press."""
        if self.validate_input():
            # Always add RAPID_ONLY
            assistants = list(self.selected_assistants)
            if Assistant.RAPID_ONLY not in assistants:
                assistants.append(Assistant.RAPID_ONLY)
            self.app.handle_assistant_selection(assistants)

    @on(Button.Pressed, "#prev_button")
    def handle_prev_button(self) -> None:
        """Handle previous button press."""
        self.app.go_back()

    @on(Button.Pressed, "#cancel_button")
    def handle_cancel_button(self) -> None:
        """Handle cancel button press."""
        self.app.exit()

    def validate_input(self) -> bool:
        """Validate assistant selection."""
        # At least one assistant should be selected (besides RAPID_ONLY)
        if not self.selected_assistants:
            # It's okay to proceed with just RAPID_ONLY
            self.show_info("Only .rapid directory will be created")
            return True

        return True

    def get_result(self) -> list[Assistant]:
        """Get the selected assistants."""
        assistants = list(self.selected_assistants)
        if Assistant.RAPID_ONLY not in assistants:
            assistants.append(Assistant.RAPID_ONLY)
        return assistants
