"""Strategic tests for RAPID TUI data models.

This module focuses on critical business logic testing while avoiding redundant,
verbose, or brittle test scenarios.
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from rapid_tui.models import (
    Assistant,
    AssistantConfig,
    CopyOperation,
    FileOperation,
    InitializationConfig,
    InitializationResult,
    Language,
    UpdateResult,
)


class TestLanguageEnum:
    """Test Language enum critical functionality."""

    def test_language_has_templates_see_sharp_false(self):
        """Test critical business rule: SEE_SHARP has no templates."""
        assert Language.SEE_SHARP.has_templates is False

    def test_language_has_templates_others_true(self):
        """Test that other languages have templates available."""
        languages_with_templates = [Language.PYTHON, Language.ANGULAR, Language.GENERIC]
        for language in languages_with_templates:
            assert language.has_templates is True

    def test_language_display_names_exist(self):
        """Test that all languages have display names."""
        for language in Language:
            assert language.display_name
            assert len(language.display_name) > 0


class TestAssistantEnum:
    """Test Assistant enum functionality."""

    def test_assistant_display_names_exist(self):
        """Test that all assistants have display names."""
        for assistant in Assistant:
            assert assistant.display_name
            assert len(assistant.display_name) > 0


class TestAssistantConfig:
    """Test AssistantConfig Pydantic model."""

    def test_assistant_config_path_resolution(self, tmp_path):
        """Test essential path resolution with project root."""
        config = AssistantConfig(
            name="Test Assistant",
            base_dir=".test",
            agents_path="agents",
            commands_path="commands",
        )

        agent_dir = config.get_agent_dir(tmp_path)
        commands_dir = config.get_commands_dir(tmp_path)

        assert agent_dir == tmp_path / ".test" / "agents"
        assert commands_dir == tmp_path / ".test" / "commands"

    def test_assistant_config_no_agents_path(self, tmp_path):
        """Test path resolution when agents_path is None."""
        config = AssistantConfig(
            name="Test Assistant",
            base_dir=".test",
            agents_path=None,
            commands_path="prompts",
        )

        agent_dir = config.get_agent_dir(tmp_path)
        commands_dir = config.get_commands_dir(tmp_path)

        assert agent_dir is None
        assert commands_dir == tmp_path / ".test" / "prompts"


class TestInitializationConfig:
    """Test InitializationConfig validation logic."""

    def test_initialization_config_validate_assistants_auto_includes_rapid(self):
        """Test critical business rule: RAPID_ONLY is always included."""
        config = InitializationConfig(
            language=Language.PYTHON,
            assistants=[Assistant.CLAUDE_CODE],
            project_path=Path.cwd(),
        )

        assert Assistant.RAPID_ONLY in config.assistants
        assert Assistant.CLAUDE_CODE in config.assistants

    def test_initialization_config_validate_assistants_empty_fails(self):
        """Test validation fails with empty assistants list."""
        with pytest.raises(ValidationError) as exc_info:
            InitializationConfig(
                language=Language.PYTHON, assistants=[], project_path=Path.cwd()
            )

        assert "At least one assistant must be selected" in str(exc_info.value)

    def test_initialization_config_validate_project_path_nonexistent(self, tmp_path):
        """Test validation fails with nonexistent project path."""
        nonexistent_path = tmp_path / "nonexistent"

        with pytest.raises(ValidationError) as exc_info:
            InitializationConfig(
                language=Language.PYTHON,
                assistants=[Assistant.CLAUDE_CODE],
                project_path=nonexistent_path,
            )

        assert "Project path does not exist" in str(exc_info.value)

    def test_initialization_config_validate_project_path_not_directory(self, tmp_path):
        """Test validation fails when project path is a file."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test")

        with pytest.raises(ValidationError) as exc_info:
            InitializationConfig(
                language=Language.PYTHON,
                assistants=[Assistant.CLAUDE_CODE],
                project_path=file_path,
            )

        assert "Project path is not a directory" in str(exc_info.value)


class TestCopyOperation:
    """Test CopyOperation model and properties."""

    def test_copy_operation_relative_destination_success(self, tmp_path, mocker):
        """Test core relative path calculation."""
        # Mock Path.cwd() to return tmp_path
        mocker.patch("rapid_tui.models.Path.cwd", return_value=tmp_path)

        destination = tmp_path / "project" / ".claude" / "agent.md"
        operation = CopyOperation(
            source=Path("/templates/agent.md"),
            destination=destination,
            operation_type="agent",
            assistant=Assistant.CLAUDE_CODE,
        )

        relative_path = operation.relative_destination
        assert relative_path == "project/.claude/agent.md"


class TestInitializationResult:
    """Test InitializationResult aggregation logic."""

    def test_initialization_result_summary_statistics(self):
        """Test critical summary statistics generation."""
        operations = [
            CopyOperation(
                source=Path("/templates/agent1.md"),
                destination=Path("/project/.claude/agent1.md"),
                operation_type="agent",
                assistant=Assistant.CLAUDE_CODE,
            ),
            CopyOperation(
                source=Path("/templates/command1.md"),
                destination=Path("/project/.claude/command1.md"),
                operation_type="command",
                assistant=Assistant.CLAUDE_CODE,
            ),
            CopyOperation(
                source=Path("/templates/agent2.md"),
                destination=Path("/project/.rapid/agent2.md"),
                operation_type="agent",
                assistant=Assistant.RAPID_ONLY,
            ),
        ]

        result = InitializationResult(
            success=True,
            operations=operations,
            total_files_copied=3,
            total_directories_created=2,
            errors=[],
            warnings=["Test warning"],
        )

        summary = result.summary

        assert summary["success"] is True
        assert summary["files_copied"] == 3
        assert summary["directories_created"] == 2
        assert summary["errors_count"] == 0
        assert summary["warnings_count"] == 1
        assert summary["operations_by_type"]["agent"] == 2
        assert summary["operations_by_type"]["command"] == 1
        assert summary["operations_by_assistant"]["claude_code"] == 2
        assert summary["operations_by_assistant"]["rapid_only"] == 1

    def test_initialization_result_summary_with_failures(self):
        """Test summary generation with failures."""
        result = InitializationResult(
            success=False,
            operations=[],
            total_files_copied=0,
            errors=["Error 1", "Error 2"],
        )

        summary = result.summary

        assert summary["success"] is False
        assert summary["files_copied"] == 0
        assert summary["errors_count"] == 2
        assert summary["operations_by_type"]["agent"] == 0
        assert summary["operations_by_type"]["command"] == 0


class TestFileOperation:
    """Test FileOperation model."""

    def test_file_operation_relative_paths(self, tmp_path, mocker):
        """Test relative path properties work correctly."""
        # Mock Path.cwd() to return tmp_path
        mocker.patch("rapid_tui.models.Path.cwd", return_value=tmp_path)

        source = tmp_path / "source" / "file.md"
        target = tmp_path / "target" / "file.md"

        operation = FileOperation(
            source=source, target=target, operation="copy", reason="Test copy"
        )

        assert operation.relative_source == "source/file.md"
        assert operation.relative_target == "target/file.md"


class TestUpdateResult:
    """Test UpdateResult model."""

    def test_update_result_summary_statistics(self):
        """Test update result summary generation."""
        operations = [
            FileOperation(
                source=Path("/source/file1.md"),
                target=Path("/target/file1.md"),
                operation="copy",
                reason="Modified",
            ),
            FileOperation(
                source=Path("/source/file2.md"),
                target=Path("/target/file2.md"),
                operation="skip",
                reason="Identical",
            ),
        ]

        result = UpdateResult(
            success=True,
            operations=operations,
            files_copied=1,
            files_skipped=1,
            errors=[],
        )

        summary = result.summary

        assert summary["success"] is True
        assert summary["files_copied"] == 1
        assert summary["files_skipped"] == 1
        assert summary["total_operations"] == 2
        assert summary["errors_count"] == 0

    def test_update_result_summary_with_errors(self):
        """Test update result summary with errors."""
        result = UpdateResult(
            success=False,
            operations=[],
            files_copied=0,
            files_skipped=0,
            errors=["Permission denied", "File not found"],
        )

        summary = result.summary

        assert summary["success"] is False
        assert summary["files_copied"] == 0
        assert summary["total_operations"] == 0
        assert summary["errors_count"] == 2
