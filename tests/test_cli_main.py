"""Strategic tests for CLI main functionality.

This module focuses on essential CLI logic, version display, and context management.
"""

import pytest
from unittest.mock import Mock

import typer

from rapid_tui.cli.main import app, version_callback, main, cli
from rapid_tui import __version__


class TestVersionCallback:
    """Test version display functionality."""

    def test_version_callback_displays_version_and_exits(self, mocker):
        """Test version callback displays version and exits."""
        mock_console = mocker.patch("rapid_tui.cli.main.console")

        with pytest.raises(typer.Exit):
            version_callback(True)

        mock_console.print.assert_called_once_with(f"RAPID TUI v{__version__}")

    def test_version_callback_no_action_when_false(self, mocker):
        """Test version callback does nothing when value is False."""
        mock_console = mocker.patch("rapid_tui.cli.main.console")

        # Should not raise or print anything
        result = version_callback(False)
        assert result is None
        mock_console.print.assert_not_called()


class TestContextManagement:
    """Test context object handling."""

    def test_main_callback_sets_context_object(self, mocker):
        """Test that main callback properly sets context object."""
        # Mock dependencies to avoid actual execution
        mocker.patch("rapid_tui.cli.main.display_welcome_banner")

        # Create mock context
        ctx = Mock()
        ctx.ensure_object.return_value = {}
        ctx.invoked_subcommand = "init"  # Prevent help display
        ctx.obj = {}

        # Test with various options
        main(ctx, version=None, ui=False, verbose=True, dry_run=True)

        assert ctx.obj["ui"] is False
        assert ctx.obj["verbose"] is True
        assert ctx.obj["dry_run"] is True

    def test_main_callback_default_options(self, mocker):
        """Test main callback with default options."""
        mocker.patch("rapid_tui.cli.main.display_welcome_banner")

        ctx = Mock()
        ctx.ensure_object.return_value = {}
        ctx.invoked_subcommand = "init"
        ctx.obj = {}

        main(ctx, version=None, ui=False, verbose=False, dry_run=False)

        assert ctx.obj["ui"] is False
        assert ctx.obj["verbose"] is False
        assert ctx.obj["dry_run"] is False


class TestCLIEntryPoint:
    """Test CLI entry point functionality."""

    def test_cli_function_calls_app(self, mocker):
        """Test that cli() function calls the Typer app."""
        mock_app = mocker.patch("rapid_tui.cli.main.app")

        cli()

        mock_app.assert_called_once()



