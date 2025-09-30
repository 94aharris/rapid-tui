"""Test helper functions and mock patterns for RAPID TUI tests."""

from unittest.mock import Mock

from rapid_tui.models import (
    InitializationResult,
)


def create_mock_initialization_result(
    success: bool = True,
    files_copied: int = 3,
    errors: list[str] = None,
) -> InitializationResult:
    """Create mock InitializationResult for testing."""
    return InitializationResult(
        success=success,
        operations=[],
        total_files_copied=files_copied,
        total_directories_created=2,
        errors=errors or ([] if success else ["Mock error"]),
        warnings=[],
    )


class MockTemplateManager:
    """Mock TemplateManager for service testing."""

    def __init__(self, success: bool = True, should_validate: bool = True):
        self.success = success
        self.should_validate = should_validate
        self._call_count = 0

    def initialize_project(self, **kwargs) -> InitializationResult:
        """Mock initialize_project method."""
        self._call_count += 1

        return create_mock_initialization_result(
            success=self.success, files_copied=5 if self.success else 0
        )

    def validate_environment(self) -> bool:
        """Mock validate_environment method."""
        return self.should_validate

    @property
    def call_count(self) -> int:
        """Get number of times initialize_project was called."""
        return self._call_count


class MockConsole:
    """Mock Rich Console for testing."""

    def __init__(self):
        self.messages = []
        self.printed_objects = []

    def print(self, *args, **kwargs):
        """Mock print method."""
        self.messages.append(str(args[0]) if args else "")
        if args:
            self.printed_objects.append(args[0])

    def clear(self):
        """Mock clear method."""
        pass

    def status(self, message: str):
        """Mock status context manager."""
        return MockStatus(message)


class MockStatus:
    """Mock Rich Status context manager."""

    def __init__(self, message: str):
        self.message = message

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def create_mock_typer_context(
    verbose: bool = False, dry_run: bool = False, **extra_params
) -> Mock:
    """Create mock Typer context object."""
    ctx = Mock()
    ctx.obj = {"verbose": verbose, "dry_run": dry_run, **extra_params}
    return ctx
