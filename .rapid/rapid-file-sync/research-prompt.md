# RAPID Update Command - .rapid/ Folder Synchronization Feature

**Feature Description:**
As a developer using the RAPID framework, I want a CLI command `rapid update` that synchronizes files from the `.rapid/` folder (source of truth) to the appropriate agent target folders (`.claude/` and `.github/prompts/`), allowing me to manage all agent configurations, commands, and prompts centrally.

The `rapid update` command should check the `.rapid/` folder structure and synchronize its contents to specified target agent folders based on the agent(s) specified or sync all agents if none are specified. This establishes the `.rapid/` folder as the authoritative source for all agent instructions, commands, and prompts.

## Current Structure Analysis

**Source: `.rapid/` folder contains:**

- `.rapid/agents/python/` (python-code-agent.md, python-planning-agent.md)
- `.rapid/commands/` (rapid-\*.md files)
- `.rapid/prompts/` (rapid-\*.prompt.md files)

**Target Agent Folders:**

- `.claude/agents/python/` and `.claude/commands/` (Claude AI agent files)
- `.github/prompts/` (GitHub Copilot prompt files)

## Acceptance Criteria

### 1. CLI Command Structure

- `rapid update` - synchronizes to all agent folders (.claude and .github)
- `rapid update --agent claude` - synchronizes only to .claude folder
- `rapid update --agent github` - synchronizes only to .github/prompts folder
- `rapid update --agent claude,github` - synchronizes to specified agents
- `rapid update --dry-run` - shows what would be synchronized without making changes

### 2. Synchronization Logic

- Files in `.rapid/agents/` and `.rapid/commands/` sync to `.claude/agents/` and `.claude/commands/`
- Files in `.rapid/prompts/` sync to `.github/prompts/`
- Only copy files that are newer or different (compare checksums/modification time)
- Preserve file permissions and timestamps
- Handle nested directory structures appropriately

### 3. Agent Mapping

- `claude` agent: `.rapid/agents/` → `.claude/agents/`, `.rapid/commands/` → `.claude/commands/`
- `github` agent: `.rapid/prompts/` → `.github/prompts/`
- Support for future agents can be easily added to the mapping

### 4. Validation and Safety

- Validate that `.rapid/` folder exists before operation
- Create target directories if they don't exist
- Backup existing files before overwriting (optional flag `--backup`)
- Verify file integrity after copying
- Provide detailed output of what was synchronized

### 5. Command Options

- `--agent AGENT` - Specify one or more agents (claude, github)
- `--dry-run` - Preview changes without making them
- `--force` - Overwrite files even if source is not newer
- `--backup` - Create backup of existing files before overwriting
- `--verbose` - Show detailed operation information

### 6. Output and Reporting

- Show summary of files synchronized per agent
- Report any conflicts or errors
- Display statistics (files copied, directories created, conflicts resolved)
- Use rich formatting for clear, colored output consistent with existing CLI

### 7. Error Handling

- Handle missing source files gracefully
- Report permission errors clearly
- Validate agent names against supported agents (claude, github)
- Provide helpful error messages with suggested fixes

## Implementation Requirements

- Create new command file `src/rapid_tui/cli/commands/update.py`
- Add file synchronization utilities to handle the copying logic with agent mapping
- Integrate with existing CLI structure and use consistent styling/patterns
- Support all existing CLI flags (--verbose, --dry-run) for consistency
- Add appropriate unit tests for the synchronization logic and agent mapping

## Success Criteria

The feature will be considered complete when:

1. The `rapid update` command successfully synchronizes files from `.rapid/` to target agent folders
2. All command-line options work as specified
3. Proper error handling and validation is implemented
4. Rich console output provides clear feedback to users
5. The command integrates seamlessly with the existing CLI structure
6. Unit tests cover the synchronization logic and edge cases
