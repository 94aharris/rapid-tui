"""Confirmation and progress screen for RAPID TUI."""

from textual.app import ComposeResult
from textual.widgets import Static, Button, ProgressBar, DataTable, RichLog
from textual.containers import Horizontal, Vertical, Container
from textual import work
from textual.message import Message
from textual import on
from typing import List, Optional
from pathlib import Path
import asyncio

from rapid_tui.screens.base import BaseScreen
from rapid_tui.models import (
    Language,
    Assistant,
    InitializationConfig,
    InitializationResult,
)
from rapid_tui.utils.file_operations import TemplateManager


class ProgressUpdate(Message):
    """Message for progress updates from worker thread."""

    def __init__(self, message: str, progress: int, total: int):
        self.message = message
        self.progress = progress
        self.total = total
        super().__init__()


class ConfirmationScreen(BaseScreen):
    """Screen for confirming selections and showing progress."""

    # CSS is now in external styles.css file

    def __init__(self, config: InitializationConfig):
        """
        Initialize confirmation screen.

        Args:
            config: The initialization configuration to confirm
        """
        super().__init__(name="confirmation", title="Confirm Initialization")
        self.config = config
        self.template_manager = TemplateManager(config.project_path)
        self.result: Optional[InitializationResult] = None
        self.progress_bar: Optional[ProgressBar] = None
        self.progress_label: Optional[Static] = None
        self.log_widget: Optional[RichLog] = None

    def setup_content(self) -> None:
        """Setup the confirmation interface."""
        content = self.query_one("#content")
        # Clear existing content by removing all children
        for child in list(content.children):
            child.remove()

        # Create summary container
        summary_container = Vertical(classes="summary-container")

        summary_container.mount(
            Static("Initialization Summary", classes="summary-title")
        )

        # Show configuration details
        self._add_summary_item(
            summary_container, "Project", str(self.config.project_path)
        )
        self._add_summary_item(
            summary_container, "Language", self.config.language.display_name
        )

        assistants_text = ", ".join([a.display_name for a in self.config.assistants])
        self._add_summary_item(summary_container, "Assistants", assistants_text)

        # Estimate file operations
        estimated = self._estimate_operations()
        self._add_summary_item(
            summary_container, "Estimated Files", f"~{estimated} files"
        )

        # Show directory structure preview
        preview = self._generate_directory_preview()
        summary_container.mount(
            Static("Directory Structure Preview:", classes="summary-label")
        )
        summary_container.mount(Static(preview, classes="summary-item"))

        content.mount(summary_container)

        # Add confirmation buttons
        button_row = Horizontal(
            Button("Previous", variant="default", id="prev_button"),
            Button("Initialize", variant="success", id="init_button"),
            Button("Cancel", variant="default", id="cancel_button"),
            classes="button-row",
        )

        content.mount(button_row)

    def set_initial_focus(self) -> None:
        """Set initial focus to the initialize button."""
        try:
            init_button = self.query_one("#init_button", Button)
            init_button.focus()
        except Exception:
            pass  # Focus fallback handled by Textual

    def _add_summary_item(self, container: Container, label: str, value: str) -> None:
        """Add a summary item to the container."""
        item = Horizontal(
            Static(f"{label}:", classes="summary-label"),
            Static(value),
            classes="summary-item",
        )
        container.mount(item)

    def _estimate_operations(self) -> int:
        """Estimate the number of file operations."""
        count = 0

        # Commands (6 files per assistant that copies commands)
        for assistant in self.config.assistants:
            if (
                assistant != Assistant.GITHUB_COPILOT
                and assistant != Assistant.RAPID_ONLY
            ):
                count += 6  # Number of command files

        # Agents (2 files per assistant that copies agents, if not SEE_SHARP)
        if self.config.language != Language.SEE_SHARP:
            for assistant in self.config.assistants:
                if assistant != Assistant.GITHUB_COPILOT:
                    count += 2  # Number of agent files

        return count

    def _generate_directory_preview(self) -> str:
        """Generate a preview of the directory structure to be created."""
        lines = []

        for assistant in self.config.assistants:
            if assistant == Assistant.CLAUDE_CODE:
                lines.append(".claude/")
                lines.append("  ├── agents/")
                lines.append(f"  │   └── {self.config.language.value}/")
                lines.append("  └── commands/")

            elif assistant == Assistant.GITHUB_COPILOT:
                lines.append(".github/")
                lines.append("  └── prompts/  (commands only)")

            elif assistant == Assistant.RAPID_ONLY:
                lines.append(".rapid/")
                lines.append("  ├── agents/")
                lines.append(f"  │   └── {self.config.language.value}/")
                lines.append("  └── commands/")

        return "\n".join(lines)

    @on(Button.Pressed, "#init_button")
    def handle_init_button(self) -> None:
        """Handle initialize button press."""
        self.start_initialization()

    @on(Button.Pressed, "#prev_button")
    def handle_prev_button(self) -> None:
        """Handle previous button press."""
        self.app.go_back()

    @on(Button.Pressed, "#cancel_button")
    def handle_cancel_button(self) -> None:
        """Handle cancel button press."""
        self.app.exit()

    @on(Button.Pressed, "#finish_button")
    def handle_finish_button(self) -> None:
        """Handle finish button press."""
        self.app.exit()

    def start_initialization(self) -> None:
        """Start the initialization process."""
        # Replace confirmation UI with progress UI
        content = self.query_one("#content")
        # Clear existing content by removing all children
        for child in list(content.children):
            child.remove()

        # Create progress container
        progress_container = Vertical(classes="progress-container")

        self.progress_label = Static(
            "Starting initialization...", classes="progress-label"
        )
        self.progress_bar = ProgressBar(total=100, show_eta=False)

        progress_container.mount(self.progress_label)
        progress_container.mount(self.progress_bar)

        # Create log widget for detailed output
        self.log_widget = RichLog(classes="result-log", wrap=True, markup=True)
        progress_container.mount(self.log_widget)

        content.mount(progress_container)

        # Start the initialization worker
        self.run_initialization()

    @work(exclusive=True, thread=True)
    def run_initialization(self) -> None:
        """Run the initialization process as a worker."""

        def progress_callback(message: str, current: int, total: int):
            """Update progress from worker thread."""
            # Post message to main thread instead of direct update
            self.post_message(ProgressUpdate(message, current, total))

        try:
            # Validate environment first
            valid, issues = self.template_manager.validate_environment()
            if not valid:
                for issue in issues:
                    # Post message to update UI from main thread
                    self.post_message(ProgressUpdate(f"❌ {issue}", 0, 100))
                # Use call_from_thread to safely update UI
                self.call_from_thread(self.show_error, "Environment validation failed")
                return

            # Run initialization
            self.result = self.template_manager.initialize_project(
                language=self.config.language,
                assistants=self.config.assistants,
                progress_callback=progress_callback,
            )

            # Show results from main thread
            self.call_from_thread(self.show_results)

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            # Post error message to main thread
            self.post_message(ProgressUpdate(f"❌ Error: {e}", 0, 100))
            self.call_from_thread(self.show_error, f"Initialization failed: {e}")

    def show_results(self) -> None:
        """Display initialization results."""
        if not self.result:
            return

        content = self.query_one("#content")
        # Clear existing content by removing all children
        for child in list(content.children):
            child.remove()

        # Create result container
        result_container = Vertical(classes="result-container")

        if self.result.success:
            result_container.mount(
                Static("✅ Initialization Successful!", classes="summary-title")
            )

            # Show summary statistics
            summary = self.result.summary
            self._add_summary_item(
                result_container, "Files Copied", str(summary["files_copied"])
            )
            self._add_summary_item(
                result_container,
                "Directories Created",
                str(summary["directories_created"]),
            )

            # Show file operations in a table
            table = DataTable(classes="files-table")
            table.add_columns("File", "Destination", "Status")

            for op in self.result.operations[:10]:  # Show first 10 operations
                status = "✅" if op.success else "❌"
                table.add_row(op.source.name, op.relative_destination, status)

            if len(self.result.operations) > 10:
                table.add_row(
                    "...", f"({len(self.result.operations) - 10} more)", "..."
                )

            result_container.mount(table)

        else:
            result_container.mount(
                Static("❌ Initialization Failed", classes="summary-title")
            )

            # Show errors
            for error in self.result.errors:
                result_container.mount(Static(f"• {error}", classes="error-message"))

        # Show warnings if any
        for warning in self.result.warnings:
            result_container.mount(Static(f"⚠️  {warning}", classes="warning-message"))

        # Add finish button
        button_row = Horizontal(
            Button("Finish", variant="primary", id="finish_button"),
            classes="button-row",
        )

        content.mount(result_container)
        content.mount(button_row)

    def on_progress_update(self, message: ProgressUpdate) -> None:
        """Handle progress updates from worker thread."""
        if self.progress_label:
            self.progress_label.update(message.message)
        if self.progress_bar and message.total > 0:
            progress = int((message.progress / message.total) * 100)
            self.progress_bar.update(progress=progress)
        if self.log_widget:
            self.log_widget.write(f"[cyan]{message.message}[/cyan]")
