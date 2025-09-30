# RAPID Update Command - Research Context

## Feature Overview

Implementation of `rapid update` CLI command that synchronizes files from the `.rapid/` folder (source of truth) to appropriate agent target folders (`.claude/` and `.github/prompts/`).

## Existing Codebase Analysis

### 1. CLI Architecture (src/rapid_tui/cli/)

**Main CLI Structure (`src/rapid_tui/cli/main.py`):**

- Uses Typer framework for CLI commands
- Rich console for formatted output
- Global options: `--verbose`, `--dry-run`, `--version`
- Context object pattern for passing options to subcommands
- Commands are imported from `rapid_tui.cli.commands` module

**Command Patterns (`src/rapid_tui/cli/commands/`):**

- Each command is a separate module (init.py, status.py, config.py, list.py)
- All commands decorated with `@app.command()`
- Consistent error handling with typer.Exit()
- Rich console formatting throughout
- Context object access via `ctx.obj.get("verbose", False)`

### 2. File Operations Infrastructure

**Template Manager (`src/rapid_tui/utils/file_operations.py`):**

- Comprehensive file copying with retry logic and rollback
- Dry-run support built-in
- Progress callback support
- Error handling with detailed logging
- Directory creation with tracking for rollback
- File validation and environment checks

**Key Features Available:**

- `TemplateManager` class with project_root and dry_run initialization
- `_copy_file()` method with retry logic and operation tracking
- `_ensure_directory()` method for safe directory creation
- `validate_environment()` method for pre-operation checks
- Rollback functionality via `_rollback()` method

### 3. Configuration System

**Assistant Configuration (`src/rapid_tui/config.py`):**

- `ASSISTANT_CONFIGS` dictionary mapping Assistant enum to AssistantConfig
- Current mappings:
  - `CLAUDE_CODE`: `.claude/` with `agents/` and `commands/` subdirs
  - `GITHUB_COPILOT`: `.github/` with `prompts/` subdir only (no agents)
  - `RAPID_ONLY`: `.rapid/` with `agents/` and `commands/` subdirs

**AssistantConfig Model (`src/rapid_tui/models.py`):**

- `base_dir`: Root directory name
- `agents_path`: Subdirectory for agent files (optional)
- `commands_path`: Subdirectory for command files
- `copy_agents` / `copy_commands`: Boolean flags
- Helper methods: `get_agent_dir()`, `get_commands_dir()`

### 4. Models and Data Structures

**Relevant Models:**

- `Assistant` enum: CLAUDE_CODE, GITHUB_COPILOT, RAPID_ONLY
- `Language` enum: ANGULAR, PYTHON, GENERIC, SEE_SHARP
- `CopyOperation` class: Tracks individual file operations
- `InitializationResult` class: Aggregates operation results

### 5. Existing Directory Structure Analysis

**Current State:**

- `.rapid/` folder exists with:
  - `agents/python/` (python-code-agent.md, python-planning-agent.md)
  - `commands/` (rapid-\*.md files)
  - `prompts/` (rapid-\*.prompt.md files)
- `.claude/` exists with `agents/` and `commands/` subdirectories
- `.github/` exists with `prompts/` subdirectory

**Template Sources:**

- Templates directory: `/templates/` contains source templates
- Agent templates: `/templates/agents/{language}/`
- Command templates: `/templates/commands/`
- Prompt templates: `/templates/prompts/`

### 6. Similar Implementation Patterns

**Initialization Service (`src/rapid_tui/services/initialization.py`):**

- Service layer pattern for business logic
- Uses TemplateManager for file operations
- Progress callback integration
- Validation before operations
- Comprehensive result reporting

**Status Command (`src/rapid_tui/cli/commands/status.py`):**

- Directory structure analysis
- File counting and statistics
- Health checks and issue detection
- Rich table and tree formatting

## Implementation Strategy

### 1. Command Structure

Based on existing patterns, the update command should:

- Follow same decorator pattern: `@app.command()`
- Accept context object for global options
- Use Rich console for output formatting
- Support all standard CLI options (--verbose, --dry-run)

### 2. Agent Mapping Strategy

Leverage existing `ASSISTANT_CONFIGS` but extend for update-specific mapping:

- `.rapid/agents/` → `.claude/agents/` (for claude agent)
- `.rapid/commands/` → `.claude/commands/` (for claude agent)
- `.rapid/prompts/` → `.github/prompts/` (for github agent)

### 3. File Synchronization Logic

Reuse TemplateManager patterns with modifications:

- Source: `.rapid/` subdirectories
- Targets: Agent-specific directories
- Comparison: File modification time or checksum
- Safety: Backup option before overwrite

### 4. Progress and Output

Follow existing Rich formatting patterns:

- Progress spinners for long operations
- Tables for summary statistics
- Colored output for success/error states
- Verbose mode for detailed operation logs

## Key Dependencies and Imports

**Required Imports:**

```python
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from pathlib import Path
from typing import Optional, List
import hashlib
import time
```

**Internal Dependencies:**

- `rapid_tui.cli.main.app` for command registration
- `rapid_tui.models.Assistant` for agent enumeration
- `rapid_tui.config.ASSISTANT_CONFIGS` for directory mappings
- `rapid_tui.utils.file_operations.TemplateManager` for file operations

## File Comparison Strategy

### Options for File Change Detection:

1. **Modification Time**: Compare `stat.st_mtime` (fastest)
2. **File Size + mtime**: Two-level check for better accuracy
3. **Checksum**: MD5/SHA hash comparison (most accurate, slower)
4. **Force Mode**: Always overwrite regardless of changes

### Finalized Approach:

- Default: mtime comparison (skip if target newer than source)
- `--force` flag: Skip comparison, always copy
- No backup creation (rely on version control)
- No progress reporting or logging needed

## Error Handling Patterns

Based on existing code and clarified requirements:

- Use typer.Exit(1) for fatal errors
- Rich console for error display with colors
- No logging for update operations
- Graceful handling of permission errors
- Agent name validation: show available options and exit on invalid names

## Testing Considerations

**Unit Test Areas:**

- Agent name validation
- File synchronization logic
- Directory creation
- Error scenarios (missing files, permissions)
- Dry-run mode verification
- Backup functionality

**Integration Test Scenarios:**

- End-to-end synchronization with all agents
- Mixed scenarios (some files newer, some older)
- Error recovery and rollback
- Command-line option combinations

## CLARIFIED DESIGN DECISIONS

Based on user feedback, the following design decisions have been finalized:

1. **No Backup Strategy**: No file backups will be created as version control provides sufficient safety.

2. **Conflict Resolution**: If target file is newer than source, skip by default. Only overwrite with explicit `--force` flag.

3. **Directory Structure**: Preserve full nested directory structure during synchronization.

   - Example: `.rapid/agents/python/file.md` → `.claude/agents/python/file.md`

4. **Progress Reporting**: No progress reporting needed due to expected small file counts.

5. **Logging**: No logging for update operations to keep it lightweight.

6. **Agent Validation**: Invalid agent names show available options and exit with error.
