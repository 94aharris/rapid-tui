"""Strategic tests for update service.

This module focuses on synchronization logic and file comparison operations.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from rapid_tui.services.update import UpdateService
from rapid_tui.models import Assistant, UpdateResult, FileOperation
from tests.test_helpers import MockConsole


class TestUpdateService:
    """Test UpdateService core functionality."""

    def test_update_service_initialization(self, tmp_path):
        """Test UpdateService basic initialization."""
        service = UpdateService(tmp_path)

        assert service.project_root == tmp_path
        assert service.dry_run is False
        assert service.verbose is False

    def test_update_service_with_options(self, tmp_path):
        """Test UpdateService initialization with options."""
        service = UpdateService(tmp_path, dry_run=True, verbose=True)

        assert service.dry_run is True
        assert service.verbose is True


class TestUpdateServiceSync:
    """Test sync operations (rapid -> assistants)."""

    def test_sync_all_agents_success(self, tmp_path, mocker):
        """Test syncing to all configured assistants."""
        # Mock console to avoid output during tests
        mocker.patch("rapid_tui.services.update.Console", return_value=MockConsole())

        # Create .rapid directory structure
        rapid_dir = tmp_path / ".rapid"
        agents_dir = rapid_dir / "agents" / "python"
        commands_dir = rapid_dir / "commands"
        agents_dir.mkdir(parents=True)
        commands_dir.mkdir(parents=True)

        # Create source files
        (agents_dir / "agent.md").write_text("# Agent")
        (commands_dir / "command.md").write_text("# Command")

        service = UpdateService(tmp_path)

        # Mock individual sync operations
        mock_sync_agent = mocker.patch.object(service, "sync_agent")
        mock_sync_agent.return_value = UpdateResult(
            success=True, operations=[], files_copied=1, files_skipped=0, errors=[]
        )

        result = service.sync_all_agents()

        assert result.success is True
        # Should call sync_agent for Claude and Copilot, but not RAPID_ONLY
        assert mock_sync_agent.call_count == 2

    def test_sync_agent_claude_structure(self, tmp_path, mocker):
        """Test syncing to Claude assistant with agents and commands."""
        # Mock console and shutil
        mocker.patch("rapid_tui.services.update.Console", return_value=MockConsole())
        mock_shutil_copy2 = mocker.patch("rapid_tui.services.update.shutil.copy2")

        # Create .rapid directory structure
        rapid_dir = tmp_path / ".rapid"
        agents_dir = rapid_dir / "agents" / "python"
        commands_dir = rapid_dir / "commands"
        agents_dir.mkdir(parents=True)
        commands_dir.mkdir(parents=True)

        # Create source files with timestamps
        agent_file = agents_dir / "agent.md"
        command_file = commands_dir / "command.md"
        agent_file.write_text("# Agent")
        command_file.write_text("# Command")

        service = UpdateService(tmp_path)
        result = service.sync_agent(Assistant.CLAUDE_CODE)

        assert result.success is True
        assert result.files_copied > 0

    def test_sync_agent_copilot_structure(self, tmp_path, mocker):
        """Test syncing to Copilot assistant (commands only, no agents)."""
        mocker.patch("rapid_tui.services.update.Console", return_value=MockConsole())
        mock_shutil_copy2 = mocker.patch("rapid_tui.services.update.shutil.copy2")

        # Create .rapid directory with prompts (for Copilot)
        rapid_dir = tmp_path / ".rapid"
        prompts_dir = rapid_dir / "prompts"
        prompts_dir.mkdir(parents=True)

        (prompts_dir / "prompt.md").write_text("# Prompt")

        service = UpdateService(tmp_path)
        result = service.sync_agent(Assistant.GITHUB_COPILOT)

        # Should succeed and copy prompts (Copilot doesn't use agents)
        assert result.success is True

    def test_sync_agent_rapid_only_error(self, tmp_path):
        """Test that syncing to RAPID_ONLY returns error."""
        service = UpdateService(tmp_path)
        result = service.sync_agent(Assistant.RAPID_ONLY)

        assert result.success is False
        assert "Cannot sync to .rapid directory" in result.errors[0]

    def test_sync_agent_no_rapid_directory(self, tmp_path):
        """Test sync fails when .rapid directory doesn't exist."""
        service = UpdateService(tmp_path)
        result = service.sync_agent(Assistant.CLAUDE_CODE)

        assert result.success is False
        assert ".rapid directory not found" in result.errors[0]


class TestUpdateServiceConsolidate:
    """Test consolidate operations (assistants -> rapid)."""

    def test_consolidate_all_agents_success(self, tmp_path, mocker):
        """Test consolidating from all assistants back to .rapid."""
        mocker.patch("rapid_tui.services.update.Console", return_value=MockConsole())

        # Create .rapid directory
        rapid_dir = tmp_path / ".rapid"
        rapid_dir.mkdir()

        service = UpdateService(tmp_path)

        # Mock individual consolidate operations
        mock_consolidate_agent = mocker.patch.object(service, "consolidate_agent")
        mock_consolidate_agent.return_value = UpdateResult(
            success=True, operations=[], files_copied=1, files_skipped=0, errors=[]
        )

        result = service.consolidate_all_agents()

        assert result.success is True
        # Should call consolidate_agent for Claude and Copilot, but not RAPID_ONLY
        assert mock_consolidate_agent.call_count == 2

    def test_consolidate_agent_claude_to_rapid(self, tmp_path, mocker):
        """Test consolidating Claude files back to .rapid."""
        mocker.patch("rapid_tui.services.update.Console", return_value=MockConsole())
        mock_shutil_copy2 = mocker.patch("rapid_tui.services.update.shutil.copy2")

        # Create .rapid and .claude directories
        rapid_dir = tmp_path / ".rapid"
        claude_dir = tmp_path / ".claude"
        rapid_dir.mkdir()

        claude_agents_dir = claude_dir / "agents" / "python"
        claude_commands_dir = claude_dir / "commands"
        claude_agents_dir.mkdir(parents=True)
        claude_commands_dir.mkdir(parents=True)

        # Create source files in Claude structure
        (claude_agents_dir / "agent.md").write_text("# Updated Agent")
        (claude_commands_dir / "command.md").write_text("# Updated Command")

        service = UpdateService(tmp_path)
        result = service.consolidate_agent(Assistant.CLAUDE_CODE)

        assert result.success is True

    def test_consolidate_agent_rapid_only_error(self, tmp_path):
        """Test that consolidating from RAPID_ONLY returns error."""
        service = UpdateService(tmp_path)
        result = service.consolidate_agent(Assistant.RAPID_ONLY)

        assert result.success is False
        assert "Cannot consolidate from .rapid directory" in result.errors[0]


class TestUpdateServiceFileOperations:
    """Test file comparison and copying logic."""


    def test_compare_files_target_not_exists(self, tmp_path):
        """Test file comparison when target doesn't exist."""
        source_file = tmp_path / "source.md"
        target_file = tmp_path / "target.md"

        source_file.write_text("content")

        service = UpdateService(tmp_path)
        should_update = service._compare_files(source_file, target_file)

        assert should_update is True

    def test_sync_file_copy_operation(self, tmp_path, mocker):
        """Test individual file sync with copy operation."""
        mock_shutil_copy2 = mocker.patch("rapid_tui.services.update.shutil.copy2")
        mocker.patch("rapid_tui.services.update.Console", return_value=MockConsole())

        source_file = tmp_path / "source.md"
        target_file = tmp_path / "target.md"

        source_file.write_text("content")

        service = UpdateService(tmp_path)
        operation = service._sync_file(source_file, target_file, force=False)

        assert operation.operation == "copy"
        assert operation.success is True
        mock_shutil_copy2.assert_called_once_with(source_file, target_file)



    def test_sync_file_error_handling(self, tmp_path, mocker):
        """Test file sync error handling."""
        mock_shutil_copy2 = mocker.patch("rapid_tui.services.update.shutil.copy2")
        mock_shutil_copy2.side_effect = PermissionError("Access denied")

        source_file = tmp_path / "source.md"
        target_file = tmp_path / "target.md"

        source_file.write_text("content")

        service = UpdateService(tmp_path)
        operation = service._sync_file(source_file, target_file, force=False)

        assert operation.operation == "error"
        assert operation.success is False
        assert "Access denied" in operation.reason

    def test_sync_directory_structure_preserves_paths(self, tmp_path, mocker):
        """Test that directory sync preserves nested path structure."""
        mocker.patch("rapid_tui.services.update.Console", return_value=MockConsole())
        mock_shutil_copy2 = mocker.patch("rapid_tui.services.update.shutil.copy2")

        # Create nested source structure
        source_dir = tmp_path / "source"
        nested_dir = source_dir / "nested" / "deep"
        nested_dir.mkdir(parents=True)

        (nested_dir / "file.md").write_text("content")

        target_dir = tmp_path / "target"

        service = UpdateService(tmp_path)
        operations, errors = service._sync_directory_structure(
            source_dir, target_dir, force=False
        )

        assert len(operations) == 1
        assert len(errors) == 0

        # Verify the nested structure is preserved in target path
        operation = operations[0]
        expected_target = target_dir / "nested" / "deep" / "file.md"
        assert operation.target == expected_target


class TestUpdateServiceDisplay:
    """Test result display functionality."""

    def test_display_results_success(self, tmp_path, mocker):
        """Test display of successful update results."""
        mock_console = MockConsole()
        mocker.patch("rapid_tui.services.update.Console", return_value=mock_console)

        service = UpdateService(tmp_path)
        result = UpdateResult(
            success=True, operations=[], files_copied=5, files_skipped=2, errors=[]
        )

        service.display_results(result)

        # Check that success message was printed
        assert any("completed successfully" in msg for msg in mock_console.messages)

    def test_display_results_with_errors(self, tmp_path, mocker):
        """Test display of results with errors."""
        mock_console = MockConsole()
        mocker.patch("rapid_tui.services.update.Console", return_value=mock_console)

        service = UpdateService(tmp_path)
        result = UpdateResult(
            success=False,
            operations=[],
            files_copied=0,
            files_skipped=0,
            errors=["Test error"],
        )

        service.display_results(result)

        # Check that error message and error details were printed
        assert any("completed with errors" in msg for msg in mock_console.messages)
        assert any("Test error" in msg for msg in mock_console.messages)
