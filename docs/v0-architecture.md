# RAPID v0 Architecture & Implementation Plan

## Executive Summary

RAPID v0 is a dual-interface application providing both a Typer-based Command-Line Interface (CLI) and a Textual-based Terminal User Interface (TUI) for initializing RAPID Framework workflows in software projects. The CLI mode is the default interface, offering scriptability and CI/CD integration, while the TUI mode (accessible via `--ui` flag) provides an interactive experience. Both interfaces share the same core functionality for copying framework-specific agent templates and command definitions to appropriate directories based on user-selected programming language and AI assistant preferences.

## Version 0 Scope

### Core Features
- Language selection (Angular, Python, Generic, See Sharp) - via CLI flags or TUI interface
- AI assistant selection (Claude Code, GitHub Copilot, .rapid only) - supports multiple selections
- Template distribution to assistant-specific directories
- Progress feedback and error handling
- CLI mode with commands: `init`, `list`, `config`, `status`
- TUI mode for interactive selection
- Configuration file support (`.rapidrc.json`)
- Dry-run mode for testing operations

### Out of Scope for v0
- Update command functionality
- Prompt format transformation between assistants
- Custom template directories
- Project validation beyond basic checks

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    RAPID Application                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────┐    ┌────────────────────────┐ │
│  │    CLI Interface     │    │    TUI Interface       │ │
│  │   (Typer-based)      │    │   (Textual-based)      │ │
│  │                      │    │                        │ │
│  │  Commands:           │    │  Screens:              │ │
│  │  - init              │    │  - Language Select     │ │
│  │  - list              │    │  - Assistant Select    │ │
│  │  - config            │    │  - Confirmation        │ │
│  │  - status            │    │                        │ │
│  └─────────────────────┘    └────────────────────────┘ │
│                   \              /                       │
│                    \            /                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │            Service Layer (Shared Logic)          │  │
│  │              InitializationService               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Models     │  │   Config     │  │   Utils      │ │
│  │  - Language  │  │  - Assistant │  │  - File Ops  │ │
│  │  - Assistant │  │    configs  │  │  - Template  │ │
│  │  - Config    │  │  - Paths     │  │    Manager   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  File System    │
                    │  - .rapid/      │
                    │  - .claude/     │
                    │  - .github/     │
                    │  - .rapidrc.json│
                    └─────────────────┘
```

## Directory Structure

### Source Code Organization

```
rapid-tui/
├── docs/
│   ├── v0-architecture.md          # This document
│   ├── typer-migration-implementation-plan.md
│   └── rapid-cli-usage.md          # CLI usage guide
├── src/
│   └── rapid_tui/
│       ├── __init__.py
│       ├── app.py                  # Universal entry point
│       ├── config.py               # Configuration and constants
│       ├── models.py               # Pydantic data models
│       ├── cli/                    # CLI interface (Typer)
│       │   ├── __init__.py
│       │   ├── main.py             # Main CLI application
│       │   └── commands/
│       │       ├── __init__.py
│       │       ├── init.py         # Initialize command
│       │       ├── list.py         # List command
│       │       ├── config.py       # Config command
│       │       └── status.py       # Status command
│       ├── services/               # Shared business logic
│       │   ├── __init__.py
│       │   └── initialization.py   # Initialization service
│       ├── screens/                # TUI interface (Textual)
│       │   ├── __init__.py
│       │   ├── base.py            # Base screen class
│       │   ├── language_select.py  # Language selection screen
│       │   ├── assistant_select.py # Assistant selection screen
│       │   └── confirmation.py     # Confirmation/result screen
│       └── utils/
│           ├── __init__.py
│           └── file_operations.py  # File management utilities
├── templates/                      # Source templates
│   ├── agents/
│   │   ├── angular/
│   │   ├── generic/
│   │   └── python/
│   └── commands/
└── tests/                          # Test suite
    ├── __init__.py
    ├── cli/
    │   └── test_commands.py
    ├── test_file_operations.py
    └── test_screens.py
```

### Target Directory Structure (Created by Application)

```
<user_project>/
├── .rapid/                         # Always created
│   ├── agents/
│   │   └── <language-specific>/
│   └── commands/
│       └── *.md
├── .claude/                        # If Claude Code selected
│   ├── agents/
│   │   └── <language-specific>/
│   └── commands/
│       └── *.md
└── .github/                        # If GitHub Copilot selected
    └── prompts/                    # Note: No subdirectory
        └── *.md                     # Commands directly here
```

## Data Models

### Core Enumerations

```python
from enum import Enum

class Language(str, Enum):
    """Supported programming languages/frameworks"""
    ANGULAR = "angular"
    PYTHON = "python"
    GENERIC = "generic"
    SEE_SHARP = "see-sharp"

class Assistant(str, Enum):
    """Supported AI assistants"""
    CLAUDE_CODE = "claude_code"
    GITHUB_COPILOT = "github_copilot"
    RAPID_ONLY = "rapid_only"
```

### Configuration Models

```python
from pydantic import BaseModel, Field
from pathlib import Path
from typing import List, Optional

class AssistantConfig(BaseModel):
    """Configuration for each assistant's file structure"""
    name: str
    base_dir: str
    agents_path: Optional[str] = None
    commands_path: str
    copy_agents: bool = True
    copy_commands: bool = True

class InitializationConfig(BaseModel):
    """User selections for initialization"""
    language: Language
    assistants: List[Assistant]
    project_path: Path = Field(default_factory=Path.cwd)

class CopyOperation(BaseModel):
    """Record of a file copy operation"""
    source: Path
    destination: Path
    operation_type: str  # "agent" or "command"
    assistant: Optional[Assistant] = None
    success: bool = True
    error_message: Optional[str] = None

class InitializationResult(BaseModel):
    """Result of the initialization process"""
    success: bool
    operations: List[CopyOperation]
    total_files_copied: int = 0
    errors: List[str] = Field(default_factory=list)
```

## Configuration Strategy

### Assistant-Specific Configurations

```python
# config.py
ASSISTANT_CONFIGS = {
    Assistant.CLAUDE_CODE: AssistantConfig(
        name="Claude Code",
        base_dir=".claude",
        agents_path="agents",
        commands_path="commands",
        copy_agents=True,
        copy_commands=True
    ),
    Assistant.GITHUB_COPILOT: AssistantConfig(
        name="GitHub Copilot",
        base_dir=".github",
        agents_path=None,  # No agents for Copilot
        commands_path="prompts",  # Direct path, no subdirectory
        copy_agents=False,
        copy_commands=True
    ),
    Assistant.RAPID_ONLY: AssistantConfig(
        name=".rapid only",
        base_dir=".rapid",
        agents_path="agents",
        commands_path="commands",
        copy_agents=True,
        copy_commands=True
    )
}

# Template paths
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
AGENTS_TEMPLATE_DIR = TEMPLATES_DIR / "agents"
COMMANDS_TEMPLATE_DIR = TEMPLATES_DIR / "commands"
```

## Core Components

### 1. Service Layer (NEW)

The `InitializationService` provides shared business logic for both interfaces.

```python
class InitializationService:
    """Service layer for RAPID framework initialization"""

    def __init__(self, project_path: Path, dry_run: bool = False, force: bool = False):
        self.project_path = project_path
        self.dry_run = dry_run
        self.force = force

    def initialize(
        self,
        language: Language,
        assistants: List[Assistant],
        verbose: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> InitializationResult:
        """Initialize RAPID framework in the project"""
        # Create TemplateManager
        # Validate environment
        # Perform initialization
        # Return results

    def get_status(self) -> dict:
        """Get current initialization status"""
        # Check .rapid directory
        # Count resources
        # Return status info
```

### 2. CLI Commands (NEW)

Each command is implemented as a separate module using Typer.

```python
# cli/commands/init.py
@app.command()
def init(
    ctx: typer.Context,
    language: Optional[str] = typer.Option(None, "--language", "-l"),
    assistants: Optional[List[str]] = typer.Option(None, "--assistant", "-a"),
    interactive: bool = typer.Option(False, "--interactive", "-i"),
    force: bool = typer.Option(False, "--force", "-f"),
    path: Optional[Path] = typer.Option(None, "--path", "-p")
):
    """Initialize RAPID framework in your project"""
    service = InitializationService(path or Path.cwd())
    # Validate inputs or prompt if interactive
    # Call service.initialize()
    # Display results
```

### 3. Template Manager

The `TemplateManager` class handles all file operations with flexibility for future enhancements.

```python
class TemplateManager:
    """Manages template copying with extensible design"""

    def __init__(self, project_root: Path, templates_root: Path):
        self.project_root = project_root
        self.templates_root = templates_root
        self.operations: List[CopyOperation] = []

    def copy_for_assistant(
        self,
        assistant: Assistant,
        language: Language
    ) -> List[CopyOperation]:
        """Copy files according to assistant-specific structure"""

    def _copy_agents(
        self,
        config: AssistantConfig,
        language: Language
    ) -> List[Path]:
        """Copy agent templates to assistant directory"""

    def _copy_commands(
        self,
        config: AssistantConfig
    ) -> List[Path]:
        """Copy command templates to assistant directory"""

    def validate_templates_exist(
        self,
        language: Language
    ) -> bool:
        """Verify required templates are available"""
```

### 4. Screen Components (TUI)

Each screen inherits from a base class and implements specific UI logic.

```python
class BaseScreen(Screen):
    """Base class for all screens"""

    def compose(self) -> ComposeResult:
        """Build the UI components"""
        pass

    def validate_input(self) -> bool:
        """Validate user input before proceeding"""
        pass

class LanguageSelectScreen(BaseScreen):
    """Language selection interface"""

    def on_mount(self) -> None:
        """Initialize with available languages"""

    def on_radio_set_changed(self, event) -> None:
        """Handle language selection"""

class AssistantSelectScreen(BaseScreen):
    """Assistant selection interface"""

    def on_mount(self) -> None:
        """Initialize with available assistants"""

    def on_checkbox_changed(self, event) -> None:
        """Handle assistant selection (multiple allowed)"""

class ConfirmationScreen(BaseScreen):
    """Display selections and confirm"""

    def show_summary(self) -> None:
        """Display what will be copied where"""

    def on_confirm(self) -> None:
        """Execute the initialization"""
```

### 5. Application Flow

```python
class RapidTUI(App):
    """Main TUI application"""

    CSS_PATH = "styles.css"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "back", "Back"),
    ]

    def __init__(self):
        super().__init__()
        self.config = InitializationConfig()
        self.current_screen = "language"

    async def on_mount(self) -> None:
        """Initialize application"""
        self.check_environment()
        self.push_screen(LanguageSelectScreen())

    async def execute_initialization(self) -> None:
        """Run the initialization process"""
        service = InitializationService(self.config.project_path)
        return service.initialize(
            language=self.config.language,
            assistants=self.config.assistants
        )
```

## Implementation Phases

### Phase 1: Foundation (Completed)
1. Created project structure and base files
2. Implemented data models (models.py)
3. Created configuration module (config.py)

### Phase 2: File Operations (Completed)
1. Implemented TemplateManager class
2. Added copy operations for agents and commands
3. Created validation methods
4. Implemented error handling

### Phase 3: User Interface - TUI (Completed)
1. Created base screen class
2. Implemented language selection screen
3. Implemented assistant selection screen
4. Created confirmation screen
5. Added progress indicators

### Phase 4: CLI Interface (Completed)
1. Implemented Typer CLI structure
2. Created init, list, config, status commands
3. Added interactive prompts
4. Integrated rich formatting

### Phase 5: Service Layer & Integration (Completed)
1. Created InitializationService for shared logic
2. Updated entry point for dual-mode support
3. Connected both interfaces to service layer
4. Maintained backward compatibility

### Phase 6: Testing & Polish (In Progress)
1. Unit tests for CLI commands
2. Unit tests for file operations
3. Integration tests for full flow
4. Error scenario testing
5. UI refinements

## Error Handling Strategy

### Validation Points
1. **Environment Check**: Ensure not running in rapid-tui directory
2. **Template Availability**: Verify templates exist before copying
3. **Write Permissions**: Check target directories are writable
4. **Space Availability**: Ensure sufficient disk space

### Error Recovery
- Display clear error messages in both CLI and TUI
- Allow retry for transient failures
- Rollback partial operations on failure
- Log errors to `.rapid/initialization.log`
- Dry-run mode for testing without changes

## Future Extensibility

### Designed Extension Points

1. **Prompt Format Transformation**
   - `transform_prompt_format()` method placeholder
   - Separate transformation rules per assistant
   - Configurable transformation pipelines

2. **Additional Assistants**
   - Add new entries to `ASSISTANT_CONFIGS`
   - No changes to core logic required
   - Assistant-specific behaviors via configuration

3. **Custom Templates**
   - Support for project-specific templates
   - Template inheritance/override mechanism
   - Dynamic template discovery

4. **Update Command**
   - Diff detection for existing files
   - Merge strategies for conflicts
   - Backup before update

## Testing Strategy

### Unit Tests
- Test each CLI command independently
- Test each screen component independently
- Mock file operations for UI tests
- Test data model validation
- Test configuration loading

### Integration Tests
- Full initialization flow (CLI and TUI)
- Multiple assistant selection
- Error recovery scenarios
- Edge cases (empty templates, permissions)
- Configuration file handling

### Manual Testing Checklist
- [x] CLI init command with flags
- [x] CLI interactive mode
- [x] CLI list commands
- [x] CLI config management
- [x] CLI status checking
- [x] TUI language selection navigation
- [x] TUI assistant multi-selection
- [x] TUI confirmation screen accuracy
- [x] File copying verification
- [x] Error message clarity
- [x] Keyboard navigation
- [x] Terminal resize handling

## Dependencies

### Required Packages
- `textual>=6.1.0`: TUI framework
- `typer[all]>=0.9.0`: CLI framework with rich formatting
- `rich>=13.0.0`: Rich terminal formatting
- `pydantic>=2.11.9`: Data validation
- `pathlib`: File system operations (stdlib)
- `shutil`: File copying (stdlib)
- `typing`: Type hints (stdlib)

### Development Dependencies
- `pytest>=8.4.2`: Testing framework
- `pytest-asyncio`: Async test support
- `pytest-mock`: Mocking utilities

## Entry Point

```python
# src/rapid_tui/app.py
def main():
    """Universal entry point that delegates to CLI or TUI"""
    import sys

    # Check if --ui flag is present or called as rapid-tui
    if "--ui" in sys.argv or sys.argv[0].endswith("rapid-tui"):
        # Launch TUI mode
        from rapid_tui.app import RapidTUI
        app = RapidTUI()
        app.run()
    else:
        # Launch CLI mode (default)
        from rapid_tui.cli.main import cli
        cli()

if __name__ == "__main__":
    main()
```

## Command Line Interface

### CLI Mode (Default)
```bash
# Initialize with specific options
$ rapid init --language python --assistant claude-code

# Interactive initialization
$ rapid init --interactive

# List available options
$ rapid list languages
$ rapid list assistants
$ rapid list templates

# Manage configuration
$ rapid config --show
$ rapid config --set-language python

# Check status
$ rapid status

# Dry run mode
$ rapid init --dry-run -l python -a claude-code
```

### TUI Mode
```bash
# Launch TUI with --ui flag
$ rapid --ui

# Or use legacy command (backward compatibility)
$ rapid-tui
```

### Future Commands
```bash
# Update existing setup (not implemented in v0)
$ rapid update
```

## Success Criteria

### v0 Completion Checklist

#### CLI Mode
- [x] CLI commands implemented (`init`, `list`, `config`, `status`)
- [x] Support for command-line flags and options
- [x] Interactive prompts when options not provided
- [x] Configuration file support (`.rapidrc.json`)
- [x] Dry-run mode for testing
- [x] Rich formatted output with tables and colors
- [x] Verbose mode for debugging
- [x] CI/CD friendly (scriptable, non-interactive)

#### TUI Mode
- [x] User can select language from list
- [x] User can select one or more assistants
- [x] Graceful exit with Escape/Q keys
- [x] Confirmation before copying files
- [x] Progress indicators during operations

#### Shared Functionality
- [x] Templates copy to correct directories
- [x] `.rapid/` directory always created
- [x] `.claude/` structure correct when selected
- [x] `.github/prompts/` structure correct when selected
- [x] Clear error messages for failures
- [x] Success message with file count
- [x] Service layer for shared business logic
- [x] Consistent behavior across interfaces

## Conclusion

This architecture provides a solid foundation for RAPID v0 with dual interfaces catering to different user preferences and workflows. The CLI mode enables automation, scripting, and CI/CD integration, while the TUI mode offers an interactive experience for users who prefer guided selection. The shared service layer ensures consistency between interfaces, and the modular design allows for easy testing, maintenance, and extension as requirements evolve. The focus on configuration-driven behavior ensures that changes to assistant structures or new features can be added with minimal code changes to either interface.
