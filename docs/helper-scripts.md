# RAPID Framework Helper Scripts Documentation

## Overview

**NOTE:** rapid scripts are not yet available, these are conceptual docs...

The RAPID Framework helper scripts are deterministic Python utilities designed to eliminate repetitive, error-prone operations that AI agents commonly struggle with during the development workflow. These scripts provide reliable, consistent interfaces for common tasks that would otherwise consume significant context and risk failure when performed through general-purpose commands.

## Background & Rationale

### The Problem

When AI agents work within the RAPID Framework workflow, they frequently:

- Waste context attempting complex git operations with varied syntax
- Lose track of file paths and naming conventions
- Repeatedly discover project structure information
- Make errors with path construction and file management
- Struggle with consistent data formatting between phases

### The Solution

Deterministic helper scripts provide:

- **Context Efficiency**: Single command replaces multiple discovery steps
- **Reliability**: Consistent error handling and validation
- **Standardization**: Enforces RAPID conventions automatically
- **Reusability**: Common operations abstracted for all agent types
- **Predictability**: JSON/structured output for easy parsing

## Script Architecture

### Location Structure

```
rapid-tui/
├── templates/
│   ├── scripts/           # Source scripts in main project
│   │   ├── worktree_manager.py
│   │   ├── context_manager.py
│   │   ├── task_retriever.py
│   │   ├── codebase_analyzer.py
│   │   └── progress_tracker.py
│   ├── commands/          # RAPID command templates
│   └── agents/            # Agent personality templates

target-project/
└── .rapid/
    ├── scripts/           # Deployed scripts
    ├── commands/          # Deployed commands
    └── branch-name/       # Branch-specific context
```

### Deployment

Scripts are deployed to target projects during `rapid-tui init` alongside commands and agents, ensuring they're available for all RAPID operations.

## Core Helper Scripts

### 1. worktree_manager.py - Git Worktree Operations

**Purpose**: Provides safe, consistent git worktree management with RAPID naming conventions.

**Core Functions**:

- Create worktrees with task-number prefixes
- Switch between worktrees safely
- List active worktrees with status
- Clean up completed worktrees

**Usage Examples**:

```bash
# Create a new worktree for task PROJ-123
python .rapid/scripts/worktree_manager.py create --task PROJ-123 --description "add-user-export"
# Output: {"status": "success", "worktree": "../PROJ-123-add-user-export", "branch": "feature/PROJ-123-add-user-export"}

# Switch to a different worktree
python .rapid/scripts/worktree_manager.py switch --name PROJ-123-add-user-export
# Output: {"status": "success", "previous": "main", "current": "PROJ-123-add-user-export"}

# List all worktrees
python .rapid/scripts/worktree_manager.py list
# Output: {"worktrees": [{"path": "../PROJ-123-add-user-export", "branch": "feature/PROJ-123-add-user-export", "status": "clean"}]}
```

**RAPID Integration**:

- Used by `/rapid-init` to create feature branches
- Referenced by agents when switching contexts between tasks
- Ensures consistent branch naming across all phases

### 2. context_manager.py - RAPID Context File Management

**Purpose**: Manages reading, writing, and updating RAPID context files with proper path resolution and validation.

**Core Functions**:

- Get current branch context directory
- Read/write research, planning, and development files
- Merge updates without overwriting
- Validate file structure and content

**Usage Examples**:

```bash
# Get current context directory
python .rapid/scripts/context_manager.py get-dir
# Output: {"directory": ".rapid/PROJ-123-add-user-export", "branch": "feature/PROJ-123-add-user-export"}

# Write research prompt
python .rapid/scripts/context_manager.py write --type research-prompt --content "Add export functionality with date filtering"
# Output: {"status": "success", "file": ".rapid/PROJ-123-add-user-export/research-prompt.md"}

# Read existing research
python .rapid/scripts/context_manager.py read --type research
# Output: {"content": "## Relevant Context\n...", "file": ".rapid/PROJ-123-add-user-export/research.md"}

# Append to existing file
python .rapid/scripts/context_manager.py append --type research --section "CLARIFYING QUESTIONS" --content "- Should export include archived items?"
# Output: {"status": "success", "file": ".rapid/PROJ-123-add-user-export/research.md", "section": "CLARIFYING QUESTIONS"}
```

**RAPID Integration**:

- Essential for all phases to maintain context
- Prevents agents from constructing incorrect paths
- Ensures consistent file formatting

### 3. task_retriever.py - External Task Integration

**Purpose**: Fetches and formats task information from external systems (Jira, GitHub Issues, Azure DevOps, etc.).

**Core Functions**:

- Retrieve task by ID from configured system
- Parse acceptance criteria and requirements
- Format for RAPID research prompts
- Cache task data locally

**Configuration** (`.rapid/config.yaml`):

```yaml
task_system:
  type: jira # or github, azure, linear
  url: https://company.atlassian.net
  project: PROJ
  auth_type: token # credentials stored securely
```

**Usage Examples**:

```bash
# Retrieve task details
python .rapid/scripts/task_retriever.py get --id PROJ-123
# Output: {
#   "id": "PROJ-123",
#   "title": "Add user export functionality",
#   "description": "Users need to export their data...",
#   "acceptance_criteria": ["Export includes all user fields", "Date range filtering works"],
#   "priority": "high",
#   "type": "feature"
# }

# Format as research prompt
python .rapid/scripts/task_retriever.py format --id PROJ-123 --template research
# Output: {"prompt": "PROJ-123: Add user export functionality\n\nAs a User I want to export my data..."}

# Cache task locally
python .rapid/scripts/task_retriever.py cache --id PROJ-123
# Output: {"status": "success", "cached": ".rapid/cache/PROJ-123.json"}
```

**RAPID Integration**:

- Called by `/rapid-init` to populate initial context
- Provides consistent task information across phases
- Reduces manual copying of requirements

### 4. codebase_analyzer.py - Project Structure Discovery

**Purpose**: Analyzes project structure, frameworks, and tooling to provide consistent context for agents.

**Core Functions**:

- Detect framework and language
- Identify key directories and patterns
- List available scripts and commands
- Find test and lint configurations

**Usage Examples**:

```bash
# Analyze project structure
python .rapid/scripts/codebase_analyzer.py analyze
# Output: {
#   "language": "typescript",
#   "framework": "angular",
#   "version": "17.0.0",
#   "directories": {
#     "source": "src",
#     "tests": "src/app/**/*.spec.ts",
#     "assets": "src/assets"
#   },
#   "scripts": {
#     "build": "ng build",
#     "test": "ng test",
#     "lint": "ng lint"
#   },
#   "testing": {
#     "framework": "jest",
#     "config": "jest.config.js"
#   }
# }

# Get specific information
python .rapid/scripts/codebase_analyzer.py get --type scripts
# Output: {"scripts": {"build": "ng build", "test": "ng test", "lint": "ng lint"}}

# Find pattern locations
python .rapid/scripts/codebase_analyzer.py find --pattern service
# Output: {"pattern": "service", "locations": ["src/app/services", "src/app/core/services"]}
```

**RAPID Integration**:

- Used during research phase to understand project
- Helps select appropriate agent templates
- Provides consistent project context across phases

### 5. progress_tracker.py - Phase Progress Management

**Purpose**: Tracks RAPID workflow progress, validates phase prerequisites, and ensures proper phase transitions.

**Core Functions**:

- Track current phase status
- Validate prerequisites before phase entry
- Generate phase checklists
- Report completion metrics

**Usage Examples**:

```bash
# Get current status
python .rapid/scripts/progress_tracker.py status
# Output: {
#   "current_phase": "research",
#   "completed_phases": ["init"],
#   "pending_phases": ["align", "plan", "inspect", "develop"],
#   "branch": "feature/PROJ-123-add-user-export"
# }

# Validate phase transition
python .rapid/scripts/progress_tracker.py validate --phase align
# Output: {
#   "valid": true,
#   "prerequisites_met": ["research.md exists", "research-prompt.md exists"],
#   "warnings": []
# }

# Mark phase complete
python .rapid/scripts/progress_tracker.py complete --phase research
# Output: {
#   "status": "success",
#   "phase": "research",
#   "timestamp": "2024-01-15T10:30:00Z",
#   "next_phase": "align"
# }

# Get phase checklist
python .rapid/scripts/progress_tracker.py checklist --phase plan
# Output: {
#   "phase": "plan",
#   "required": [
#     "Review research.md",
#     "Identify implementation approach",
#     "Create task breakdown",
#     "Define test criteria"
#   ],
#   "optional": ["Consider performance impact", "Review similar implementations"]
# }
```

**RAPID Integration**:

- Enforces workflow discipline
- Prevents skipping critical steps
- Provides progress visibility
- Helps agents understand their current context

## Implementation Guidelines for Agents

When creating these scripts, ensure:

1. **Error Handling**: All scripts should handle errors gracefully and return structured error responses:

   ```python
   {"status": "error", "message": "Worktree already exists", "code": "WORKTREE_EXISTS"}
   ```

2. **JSON Output**: Default to JSON output for agent parsing:

   ```python
   import json
   result = {"status": "success", "data": {...}}
   print(json.dumps(result))
   ```

3. **Validation**: Validate inputs and state before operations:

   ```python
   if not os.path.exists(".rapid"):
       return {"status": "error", "message": "Not in a RAPID-enabled project"}
   ```

4. **Idempotency**: Operations should be safe to retry:

   ```python
   # Check if already exists before creating
   if worktree_exists(name):
       return {"status": "success", "message": "Already exists", "exists": True}
   ```

5. **Minimal Dependencies**: Use standard library where possible, document any required packages:
   ```python
   # Requires: pyyaml for config parsing
   import yaml  # Listed in .rapid/requirements.txt
   ```

## Script Development Template

```python
#!/usr/bin/env python3
"""
RAPID Framework Helper Script: [Script Name]
Purpose: [Brief description]
"""

import sys
import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='[Script description]')
    parser.add_argument('action', choices=['...'], help='Action to perform')
    parser.add_argument('--format', default='json', choices=['json', 'text'])

    args = parser.parse_args()

    try:
        # Validate RAPID environment
        if not Path('.rapid').exists():
            print(json.dumps({
                "status": "error",
                "message": "Not in a RAPID-enabled project"
            }))
            sys.exit(1)

        # Perform action
        result = perform_action(args)

        # Output result
        if args.format == 'json':
            print(json.dumps(result))
        else:
            print(format_text(result))

    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": str(e),
            "type": type(e).__name__
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Testing Scripts Locally

Before deployment, test scripts in isolation:

```bash
# Create test environment
mkdir test-project && cd test-project
git init
mkdir -p .rapid/scripts
cp ../rapid-tui/templates/scripts/*.py .rapid/scripts/

# Test each script
python .rapid/scripts/worktree_manager.py list
python .rapid/scripts/codebase_analyzer.py analyze
```

## Future Enhancements

Potential additional scripts for consideration:

- **dependency_checker.py**: Validate project dependencies and versions
- **test_runner.py**: Smart test execution based on changes
- **merge_assistant.py**: Help with merge conflict resolution
- **deployment_validator.py**: Pre-deployment checks
- **metrics_collector.py**: Track RAPID workflow efficiency

These scripts form the foundation of efficient, reliable AI-assisted development within the RAPID Framework, dramatically reducing context usage while improving success rates.
