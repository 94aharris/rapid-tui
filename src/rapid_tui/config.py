"""Configuration and constants for RAPID TUI."""

from pathlib import Path
from typing import Dict, Optional, List
import logging
from rapid_tui.models import Assistant, AssistantConfig, Language


# Logging configuration
LOG_FILE = ".rapid/initialization.log"
LOG_LEVEL = logging.INFO

# Assistant-specific configurations
ASSISTANT_CONFIGS: Dict[Assistant, AssistantConfig] = {
    Assistant.CLAUDE_CODE: AssistantConfig(
        name="Claude Code",
        base_dir=".claude",
        agents_path="agents",
        commands_path="commands",
        instructions_file="CLAUDE.md",  # NEW
        copy_agents=True,
        copy_commands=True,
        copy_instructions=True,  # NEW
    ),
    Assistant.GITHUB_COPILOT: AssistantConfig(
        name="GitHub Copilot",
        base_dir=".github",
        agents_path=None,  # No agents for Copilot
        commands_path="prompts",  # Direct path, no subdirectory
        instructions_file="copilot-instructions.md",  # NEW
        copy_agents=False,
        copy_commands=True,
        copy_instructions=True,  # NEW
    ),
    Assistant.RAPID_ONLY: AssistantConfig(
        name=".rapid only",
        base_dir=".rapid",
        agents_path="agents",
        commands_path="commands",
        instructions_file=None,  # NEW - no separate instruction file
        copy_agents=True,
        copy_commands=True,
        copy_instructions=False,  # NEW
    ),
}


# Template paths
def get_templates_dir() -> Path:
    """Get the templates directory path."""
    return Path(__file__).parent.parent.parent / "templates"


def get_agents_template_dir() -> Path:
    """Get the agents template directory."""
    return get_templates_dir() / "agents"


def get_commands_template_dir() -> Path:
    """Get the commands template directory."""
    return get_templates_dir() / "commands"


def get_prompts_template_dir() -> Path:
    """Get the prompts template directory."""
    return get_templates_dir() / "prompts"


def get_instructions_template_dir() -> Path:
    """Get the path to the instructions template directory.

    Returns:
        Path: The path to templates/instructions directory
    """
    return get_templates_dir() / "instructions"


# UI Configuration
UI_THEME = {
    "primary": "cyan",
    "secondary": "bright_blue",
    "accent": "green",
    "error": "red",
    "warning": "yellow",
    "info": "blue",
}

# File operation settings
COPY_BUFFER_SIZE = 1024 * 1024  # 1MB chunks for file copying
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 0.5  # seconds

# Validation settings
MIN_DISK_SPACE_MB = 10  # Minimum free disk space required

# Template mappings
TEMPLATE_MAPPINGS = {
    Language.ANGULAR: {
        "agents": ["rapid-code-agent.md", "rapid-planning-agent.md"],
        "commands": [],  # Use all commands
        "instructions": "angular.md",  # NEW
    },
    Language.PYTHON: {
        "agents": ["python-code-agent.md", "python-planning-agent.md"],
        "commands": [],  # Use all commands
        "instructions": "python.md",  # NEW
    },
    Language.GENERIC: {
        "agents": ["rapid-code-agent.md", "rapid-planning-agent.md"],
        "commands": [],  # Use all commands
        "instructions": "generic.md",  # NEW
    },
    Language.SEE_SHARP: {
        "agents": [],  # No templates available yet
        "commands": [],  # Use all commands
        "instructions": "see-sharp.md",  # NEW
    },
}


def get_assistant_config(assistant: Assistant) -> AssistantConfig:
    """Get configuration for a specific assistant."""
    return ASSISTANT_CONFIGS.get(assistant)


def get_language_templates(language: Language) -> Dict[str, list]:
    """Get template files for a specific language."""
    return TEMPLATE_MAPPINGS.get(language, {"agents": [], "commands": []})


# Agent name aliases for CLI usage
AGENT_ALIASES = {
    "claude": Assistant.CLAUDE_CODE,
    "copilot": Assistant.GITHUB_COPILOT,
    "all": None,  # Special case for all agents
}


def resolve_agent_name(agent_input: str) -> Optional[Assistant]:
    """Resolve user input to Assistant enum."""
    return AGENT_ALIASES.get(agent_input.lower())


def get_available_agent_names() -> List[str]:
    """Get list of valid agent names for error messages."""
    return list(AGENT_ALIASES.keys())
