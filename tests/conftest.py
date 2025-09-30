"""Pytest configuration and fixtures for RAPID TUI tests."""

from pathlib import Path

import pytest

from rapid_tui.models import Assistant, AssistantConfig, InitializationConfig, Language


@pytest.fixture
def sample_languages() -> list[Language]:
    """Provide all Language enum values for testing."""
    return list(Language)


@pytest.fixture
def sample_assistants() -> list[Assistant]:
    """Provide all Assistant enum values for testing."""
    return list(Assistant)


@pytest.fixture
def mock_project_structure(tmp_path: Path) -> Path:
    """Create a mock project directory structure for testing."""
    # Create template directories
    templates_dir = tmp_path / "templates"
    agents_dir = templates_dir / "agents"
    commands_dir = templates_dir / "commands"
    prompts_dir = templates_dir / "prompts"

    # Create language-specific agent templates
    (agents_dir / "python").mkdir(parents=True)
    (agents_dir / "python" / "python-code-agent.md").write_text("# Python Agent")
    (agents_dir / "python" / "python-planning-agent.md").write_text("# Python Planning")

    (agents_dir / "angular").mkdir(parents=True)
    (agents_dir / "angular" / "rapid-code-agent.md").write_text("# Angular Agent")

    (agents_dir / "generic").mkdir(parents=True)
    (agents_dir / "generic" / "rapid-code-agent.md").write_text("# Generic Agent")

    # Create command templates
    commands_dir.mkdir(parents=True)
    (commands_dir / "rapid-init.md").write_text("# Init Command")
    (commands_dir / "rapid-develop.md").write_text("# Develop Command")

    # Create prompt templates
    prompts_dir.mkdir(parents=True)
    (prompts_dir / "rapid-init.prompt.md").write_text("# Init Prompt")

    return tmp_path


@pytest.fixture
def mock_initialization_config(tmp_path: Path) -> InitializationConfig:
    """Create valid InitializationConfig for testing."""
    return InitializationConfig(
        language=Language.PYTHON,
        assistants=[Assistant.CLAUDE_CODE],
        project_path=tmp_path,
    )


@pytest.fixture
def sample_assistant_configs() -> dict[Assistant, AssistantConfig]:
    """Provide sample assistant configurations for testing."""
    return {
        Assistant.CLAUDE_CODE: AssistantConfig(
            name="Claude Code",
            base_dir=".claude",
            agents_path="agents",
            commands_path="commands",
            copy_agents=True,
            copy_commands=True,
        ),
        Assistant.GITHUB_COPILOT: AssistantConfig(
            name="GitHub Copilot",
            base_dir=".github",
            agents_path=None,
            commands_path="prompts",
            copy_agents=False,
            copy_commands=True,
        ),
        Assistant.RAPID_ONLY: AssistantConfig(
            name=".rapid only",
            base_dir=".rapid",
            agents_path="agents",
            commands_path="commands",
            copy_agents=True,
            copy_commands=True,
        ),
    }
