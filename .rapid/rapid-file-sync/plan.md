# RAPID Update Command - Implementation Plan

## Executive Summary

Implementation of `rapid update` CLI command to synchronize files from `.rapid/` (source of truth) to assistant-specific directories (`.claude/` and `.github/prompts/`). This command enables bi-directional synchronization with conflict resolution and supports selective agent updating.

## Requirements Analysis

### Functional Requirements

1. **File Synchronization**: Copy files from `.rapid/` to assistant directories
2. **Selective Updates**: Allow updating specific assistants with `--agent` parameter
3. **Conflict Resolution**: Skip files where target is newer than source (default behavior)
4. **Force Update**: `--force` flag to overwrite regardless of timestamps
5. **Dry Run Support**: `--dry-run` flag to preview operations
6. **Validation**: Validate agent names and show available options on error

### Technical Requirements

1. **CLI Integration**: Follow existing Typer command patterns
2. **Error Handling**: Graceful error handling with rich console output
3. **Performance**: Efficient file comparison using modification times
4. **Safety**: No backup required (rely on version control)
5. **Logging**: No persistent logging for update operations

## Current State Analysis

### Existing Infrastructure

- **CLI Framework**: Typer with Rich console integration
- **File Operations**: `TemplateManager` class with comprehensive file handling
- **Configuration**: `ASSISTANT_CONFIGS` dictionary with assistant mappings
- **Models**: Well-defined data models for operations and results
- **Directory Structure**: `.rapid/` source directory with organized subdirectories

### Reusable Components

- **TemplateManager**: Can be adapted for reverse synchronization
- **Assistant Configuration**: Existing mappings can be leveraged
- **Rich Console**: Formatting patterns for consistent output
- **Context Pattern**: Global options (verbose, dry-run) handling

## Implementation Gap Analysis

### Current State

- Initialization system copies FROM templates TO assistant directories
- TemplateManager handles source → target copying with rollback
- Commands follow established patterns with context objects

### Desired State

- Update system copies FROM `.rapid/` TO assistant directories
- File comparison logic for selective updating
- Agent-specific filtering capabilities
- Simplified operation model (no rollback needed)

### Implementation Gap

1. **New Command Module**: `src/rapid_tui/cli/commands/update.py`
2. **Synchronization Service**: New service layer for update operations
3. **File Comparison Logic**: Timestamp-based comparison utilities
4. **Agent Validation**: Input validation with error feedback

## Technical Specification

### 1. Command Module Structure

**File**: `src/rapid_tui/cli/commands/update.py`

```python
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rapid_tui.cli.main import app
from rapid_tui.models import Assistant
from rapid_tui.services.update import UpdateService

@app.command()
def update(
    ctx: typer.Context,
    agent: Optional[str] = typer.Option(
        None, "--agent", "-a",
        help="Update specific agent (claude, copilot, all)"
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Force update even if target files are newer"
    ),
) -> None:
    """Synchronize files from .rapid/ to assistant directories."""
```

### 2. Update Service Layer

**File**: `src/rapid_tui/services/update.py`

```python
class UpdateService:
    """Service for handling file synchronization operations."""

    def __init__(self, project_root: Path, dry_run: bool = False, verbose: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.verbose = verbose
        self.console = Console()

    def sync_all_agents(self, force: bool = False) -> UpdateResult:
        """Sync files to all configured assistants."""

    def sync_agent(self, agent_name: str, force: bool = False) -> UpdateResult:
        """Sync files to specific assistant."""

    def _compare_files(self, source: Path, target: Path) -> bool:
        """Compare file timestamps to determine if update is needed."""

    def _sync_directory_structure(self, source_dir: Path, target_dir: Path, force: bool) -> List[FileOperation]:
        """Recursively sync directory structure preserving nested paths."""
```

### 3. Data Models Extension

**File**: `src/rapid_tui/models.py` (additions)

```python
class FileOperation(BaseModel):
    """Record of a file synchronization operation."""
    source: Path
    target: Path
    operation: str  # "copy", "skip", "error"
    reason: str
    success: bool = True

class UpdateResult(BaseModel):
    """Result of update synchronization."""
    success: bool
    operations: List[FileOperation]
    files_copied: int = 0
    files_skipped: int = 0
    errors: List[str] = Field(default_factory=list)
```

### 4. Agent Name Mapping

**File**: `src/rapid_tui/config.py` (additions)

```python
# Agent name aliases for CLI usage
AGENT_ALIASES = {
    "claude": Assistant.CLAUDE_CODE,
    "copilot": Assistant.GITHUB_COPILOT,
    "all": None  # Special case for all agents
}

def resolve_agent_name(agent_input: str) -> Optional[Assistant]:
    """Resolve user input to Assistant enum."""
    return AGENT_ALIASES.get(agent_input.lower())

def get_available_agent_names() -> List[str]:
    """Get list of valid agent names for error messages."""
    return list(AGENT_ALIASES.keys())
```

## Implementation Roadmap

### Phase 1: Core Command Structure

**Files to Create/Modify:**

1. `src/rapid_tui/cli/commands/update.py` - Main command implementation
2. `src/rapid_tui/cli/commands/__init__.py` - Import update command

**Key Features:**

- Command registration with Typer
- Parameter validation and help text
- Context object integration (dry-run, verbose)
- Basic error handling structure

### Phase 2: Update Service Layer

**Files to Create/Modify:**

1. `src/rapid_tui/services/update.py` - Core synchronization logic
2. `src/rapid_tui/models.py` - Add FileOperation and UpdateResult models

**Key Features:**

- File timestamp comparison logic
- Directory traversal and structure preservation
- Agent-specific directory mapping
- Operation result tracking

### Phase 3: Integration and Validation

**Files to Create/Modify:**

1. `src/rapid_tui/config.py` - Add agent name mapping utilities
2. Command integration testing

**Key Features:**

- Agent name validation and error messages
- Rich console output formatting
- Integration with existing assistant configurations
- Comprehensive error handling

### Phase 4: Output and User Experience

**Enhancements:**

- Rich table formatting for operation summaries
- Colored output for different operation types
- Verbose mode detailed logging
- User-friendly error messages

## Directory Synchronization Logic

### Source Structure (`.rapid/`)

```
.rapid/
├── agents/
│   └── python/
│       ├── python-code-agent.md
│       └── python-planning-agent.md
├── commands/
│   ├── rapid-align.md
│   ├── rapid-develop.md
│   └── [other commands]
└── prompts/
    ├── rapid-align.prompt.md
    └── [other prompts]
```

### Target Mapping

1. **Claude Agent**:

   - `.rapid/agents/` → `.claude/agents/`
   - `.rapid/commands/` → `.claude/commands/`

2. **GitHub Copilot**:
   - `.rapid/prompts/` → `.github/prompts/`
   - (No agent files for Copilot)

### File Comparison Algorithm

1. **Default Behavior**: Compare `source.stat().st_mtime` vs `target.stat().st_mtime`
2. **Skip Logic**: If `target_mtime > source_mtime`, skip copy
3. **Force Mode**: Copy regardless of timestamps
4. **Missing Target**: Always copy if target doesn't exist

## Error Handling Strategy

### Input Validation

- **Invalid Agent Names**: Display available options and exit with code 1
- **Missing .rapid Directory**: Clear error message with initialization guidance
- **Permission Errors**: Graceful handling with specific error messages

### Operation Errors

- **File Access Issues**: Skip file with warning, continue with others
- **Directory Creation Failures**: Stop operation, report error
- **Disk Space Issues**: Pre-check and warn if insufficient space

### Error Output Format

```
❌ Error: Invalid agent name 'invalid-name'
   Available agents: claude, copilot, all

❌ Error: .rapid directory not found
   Run 'rapid init' to initialize the project
```

## Success Metrics and Testing

### Unit Test Coverage

1. **File Comparison Logic**: Test timestamp comparison edge cases
2. **Agent Name Validation**: Test all valid/invalid name scenarios
3. **Directory Traversal**: Test nested structure preservation
4. **Error Conditions**: Test missing files, permission errors

### Integration Test Scenarios

1. **Full Sync**: Update all agents with mixed file states
2. **Selective Sync**: Update single agent
3. **Force Mode**: Override newer target files
4. **Dry Run**: Verify no actual file modifications

### Performance Considerations

- **File Count**: Optimized for expected small file counts (< 100 files)
- **Directory Depth**: Efficient recursive traversal
- **Comparison Speed**: Fast timestamp-only comparison
- **Memory Usage**: Minimal operation tracking overhead

## Security and Safety

### File System Safety

- **No Backup Creation**: Relies on version control for safety
- **Path Validation**: Prevent directory traversal attacks
- **Permission Checks**: Validate write access before operations
- **Atomic Operations**: Use atomic file operations where possible

### Data Integrity

- **Timestamp Preservation**: Maintain original modification times
- **Content Verification**: No checksum verification needed (timestamp sufficient)
- **Rollback Strategy**: Not implemented (version control provides safety)

## Integration Points

### CLI Framework Integration

- **Command Registration**: Automatic registration via import in `__init__.py`
- **Context Sharing**: Access to global flags (verbose, dry-run)
- **Console Output**: Consistent Rich formatting patterns
- **Error Codes**: Standard exit codes for automation compatibility

### Existing Service Integration

- **Assistant Configuration**: Reuse `ASSISTANT_CONFIGS` mappings
- **File Operations**: Leverage patterns from `TemplateManager`
- **Model Consistency**: Follow existing model patterns and validation

### Configuration System

- **Agent Mappings**: Extend existing configuration with CLI aliases
- **Path Resolution**: Reuse existing path resolution utilities
- **Validation**: Consistent validation patterns across commands

## Implementation Dependencies

### Required Python Packages

- **typer**: Already integrated for CLI framework
- **rich**: Already integrated for console output
- **pathlib**: Standard library for path operations
- **pydantic**: Already integrated for data models

### Internal Dependencies

- `rapid_tui.cli.main.app`: Command registration
- `rapid_tui.models`: Data model definitions
- `rapid_tui.config`: Configuration and assistant mappings
- `rapid_tui.utils.file_operations`: File operation patterns

### File System Requirements

- **Source Directory**: `.rapid/` must exist with expected structure
- **Target Directories**: Will be created if missing
- **Permissions**: Write access to project root and subdirectories
- **Disk Space**: Minimal additional space (files are typically small)

## Success Criteria

### Functional Success

- ✅ Successfully sync files from `.rapid/` to assistant directories
- ✅ Preserve nested directory structure in target locations
- ✅ Skip files when target is newer (default behavior)
- ✅ Force overwrite with `--force` flag
- ✅ Support dry-run mode for safe preview
- ✅ Validate agent names with helpful error messages

### Technical Success

- ✅ Integrate seamlessly with existing CLI framework
- ✅ Follow established code patterns and conventions
- ✅ Handle all error conditions gracefully
- ✅ Provide clear, user-friendly output
- ✅ Maintain good performance for expected file counts
- ✅ Comprehensive test coverage for all scenarios

### User Experience Success

- ✅ Intuitive command-line interface
- ✅ Clear documentation and help text
- ✅ Consistent behavior with other rapid commands
- ✅ Helpful error messages with actionable guidance
- ✅ Appropriate output verbosity levels

This comprehensive implementation plan provides all necessary specifications for implementing the `rapid update` command following Python development best practices and maintaining consistency with the existing RAPID framework architecture.
