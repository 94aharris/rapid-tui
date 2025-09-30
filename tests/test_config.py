"""Tests for rapid_tui.config module."""

import pytest
from pathlib import Path

from rapid_tui.config import (
    get_templates_dir,
    get_agents_template_dir,
    get_commands_template_dir,
    get_assistant_config,
    get_language_templates,
    resolve_agent_name,
    get_available_agent_names,
    ASSISTANT_CONFIGS,
    TEMPLATE_MAPPINGS,
    UI_THEME,
)
from rapid_tui.models import Assistant, Language, AssistantConfig


class TestTemplatePaths:
    """Test template directory path functions."""

    def test_get_templates_dir(self):
        """Test templates directory path is correct."""
        templates_dir = get_templates_dir()
        assert templates_dir.name == "templates"
        assert templates_dir.is_absolute()

    def test_get_agents_template_dir(self):
        """Test agents template directory path."""
        agents_dir = get_agents_template_dir()
        assert agents_dir.name == "agents"
        assert "templates" in str(agents_dir)

    def test_get_commands_template_dir(self):
        """Test commands template directory path."""
        commands_dir = get_commands_template_dir()
        assert commands_dir.name == "commands"
        assert "templates" in str(commands_dir)


class TestAssistantConfig:
    """Test assistant configuration functions."""

    def test_get_assistant_config_claude(self):
        """Test getting Claude Code assistant configuration."""
        config = get_assistant_config(Assistant.CLAUDE_CODE)

        assert isinstance(config, AssistantConfig)
        assert config.name == "Claude Code"
        assert config.base_dir == ".claude"
        assert config.agents_path == "agents"
        assert config.commands_path == "commands"
        assert config.copy_agents is True
        assert config.copy_commands is True

    def test_get_assistant_config_copilot(self):
        """Test getting GitHub Copilot assistant configuration."""
        config = get_assistant_config(Assistant.GITHUB_COPILOT)

        assert isinstance(config, AssistantConfig)
        assert config.name == "GitHub Copilot"
        assert config.base_dir == ".github"
        assert config.agents_path is None  # No agents for Copilot
        assert config.commands_path == "prompts"
        assert config.copy_agents is False
        assert config.copy_commands is True

    def test_get_assistant_config_rapid_only(self):
        """Test getting RAPID only assistant configuration."""
        config = get_assistant_config(Assistant.RAPID_ONLY)

        assert isinstance(config, AssistantConfig)
        assert config.name == ".rapid only"
        assert config.base_dir == ".rapid"
        assert config.agents_path == "agents"
        assert config.commands_path == "commands"
        assert config.copy_agents is True
        assert config.copy_commands is True

    def test_assistant_configs_completeness(self):
        """Test that all assistants have configurations."""
        for assistant in Assistant:
            config = get_assistant_config(assistant)
            assert config is not None
            assert isinstance(config, AssistantConfig)


class TestLanguageTemplates:
    """Test language template configuration."""

    def test_get_language_templates_python(self):
        """Test getting Python language templates."""
        templates = get_language_templates(Language.PYTHON)

        assert "agents" in templates
        assert "commands" in templates
        assert "python-code-agent.md" in templates["agents"]
        assert "python-planning-agent.md" in templates["agents"]
        assert templates["commands"] == []  # Use all commands

    def test_get_language_templates_angular(self):
        """Test getting Angular language templates."""
        templates = get_language_templates(Language.ANGULAR)

        assert "agents" in templates
        assert "commands" in templates
        assert "rapid-code-agent.md" in templates["agents"]
        assert "rapid-planning-agent.md" in templates["agents"]

    def test_get_language_templates_generic(self):
        """Test getting generic language templates."""
        templates = get_language_templates(Language.GENERIC)

        assert "agents" in templates
        assert "commands" in templates
        assert "rapid-code-agent.md" in templates["agents"]
        assert "rapid-planning-agent.md" in templates["agents"]

    def test_get_language_templates_see_sharp(self):
        """Test getting C# language templates (should be empty)."""
        templates = get_language_templates(Language.SEE_SHARP)

        assert "agents" in templates
        assert "commands" in templates
        assert templates["agents"] == []  # No templates available
        assert templates["commands"] == []  # Use all commands

    def test_get_language_templates_invalid(self):
        """Test getting templates for invalid language returns default empty structure."""
        templates = get_language_templates("invalid_language")  # type: ignore

        assert templates == {"agents": [], "commands": []}

    def test_template_mappings_completeness(self):
        """Test that all languages have template mappings."""
        for language in Language:
            templates = get_language_templates(language)
            assert isinstance(templates, dict)
            assert "agents" in templates
            assert "commands" in templates
            assert isinstance(templates["agents"], list)
            assert isinstance(templates["commands"], list)


class TestAgentNameResolution:
    """Test agent name resolution functions."""

    def test_resolve_agent_name_claude(self):
        """Test resolving 'claude' to Claude Code assistant."""
        result = resolve_agent_name("claude")
        assert result == Assistant.CLAUDE_CODE

    def test_resolve_agent_name_copilot(self):
        """Test resolving 'copilot' to GitHub Copilot assistant."""
        result = resolve_agent_name("copilot")
        assert result == Assistant.GITHUB_COPILOT

    def test_resolve_agent_name_all(self):
        """Test resolving 'all' returns None (special case)."""
        result = resolve_agent_name("all")
        assert result is None

    def test_resolve_agent_name_case_insensitive(self):
        """Test agent name resolution is case insensitive."""
        assert resolve_agent_name("CLAUDE") == Assistant.CLAUDE_CODE
        assert resolve_agent_name("Copilot") == Assistant.GITHUB_COPILOT
        assert resolve_agent_name("ALL") is None

    def test_resolve_agent_name_invalid(self):
        """Test resolving invalid agent name returns None."""
        result = resolve_agent_name("invalid_agent")
        assert result is None

    def test_get_available_agent_names(self):
        """Test getting list of available agent names."""
        names = get_available_agent_names()

        assert isinstance(names, list)
        assert "claude" in names
        assert "copilot" in names
        assert "all" in names
        assert len(names) >= 3


class TestConfigurationConstants:
    """Test configuration constants and settings."""

    def test_ui_theme_structure(self):
        """Test UI theme configuration structure."""
        required_keys = ["primary", "secondary", "accent", "error", "warning", "info"]

        for key in required_keys:
            assert key in UI_THEME
            assert isinstance(UI_THEME[key], str)
            assert len(UI_THEME[key]) > 0


    def test_assistant_configs_structure(self):
        """Test ASSISTANT_CONFIGS has correct structure."""
        assert isinstance(ASSISTANT_CONFIGS, dict)

        for assistant, config in ASSISTANT_CONFIGS.items():
            assert isinstance(assistant, Assistant)
            assert isinstance(config, AssistantConfig)
            assert hasattr(config, "name")
            assert hasattr(config, "base_dir")
            assert hasattr(config, "commands_path")

    def test_template_mappings_structure(self):
        """Test TEMPLATE_MAPPINGS has correct structure."""
        assert isinstance(TEMPLATE_MAPPINGS, dict)

        for language, templates in TEMPLATE_MAPPINGS.items():
            assert isinstance(language, Language)
            assert isinstance(templates, dict)
            assert "agents" in templates
            assert "commands" in templates
            assert isinstance(templates["agents"], list)
            assert isinstance(templates["commands"], list)


class TestConfigurationIntegration:
    """Test integration between different configuration components."""

    def test_assistant_config_and_templates_alignment(self):
        """Test that assistant configs align with template expectations."""
        # Claude and RAPID_ONLY should both copy agents
        claude_config = get_assistant_config(Assistant.CLAUDE_CODE)
        rapid_config = get_assistant_config(Assistant.RAPID_ONLY)

        assert claude_config.copy_agents is True
        assert rapid_config.copy_agents is True
        assert claude_config.agents_path is not None
        assert rapid_config.agents_path is not None

        # GitHub Copilot should not copy agents
        copilot_config = get_assistant_config(Assistant.GITHUB_COPILOT)
        assert copilot_config.copy_agents is False
        assert copilot_config.agents_path is None

    def test_language_templates_and_enum_alignment(self):
        """Test that template mappings cover all language enum values."""
        for language in Language:
            templates = get_language_templates(language)
            assert templates is not None

            # Even if templates are empty (like See-Sharp), the structure should exist
            assert isinstance(templates, dict)
            assert "agents" in templates
            assert "commands" in templates

