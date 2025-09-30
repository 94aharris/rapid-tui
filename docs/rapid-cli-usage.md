# RAPID CLI Usage Guide

## Overview

RAPID now provides a powerful Command-Line Interface (CLI) powered by Typer, making it easier to integrate into CI/CD pipelines, scripts, and automated workflows. The traditional Textual-based TUI is still available via the `--ui` flag for users who prefer an interactive experience.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd rapid-tui

# Install using Poetry
poetry install

# Or install globally
pip install .
```

## Command Structure

The RAPID CLI follows a standard command structure:

```bash
rapid [GLOBAL OPTIONS] COMMAND [OPTIONS] [ARGUMENTS]
```

### Global Options

- `--ui` : Launch the interactive TUI mode instead of CLI
- `--verbose, -v` : Enable verbose output for debugging
- `--dry-run` : Simulate operations without making actual changes
- `--help` : Show help message

## Commands

### 1. Initialize Project (`init`)

Initialize RAPID framework in your project with templates and configurations.

#### Basic Usage

```bash
# Initialize with specific language and assistant
rapid init --language python --assistant claude-code

# Initialize with multiple assistants
rapid init -l python -a claude-code -a github-copilot

# Interactive mode (prompts for all options)
rapid init --interactive
rapid init -i

# Dry run to see what would be copied
rapid init --dry-run -l python -a claude-code

# Force overwrite existing files
rapid init --force -l python -a claude-code

# Specify custom project path
rapid init --path /path/to/project -l angular -a claude-code
```

#### Options

- `--language, -l` : Programming language (angular, python, generic, see-sharp)
- `--assistant, -a` : AI assistant(s) to configure (can specify multiple)
- `--interactive, -i` : Interactive mode for guided selection
- `--force, -f` : Overwrite existing files without prompting
- `--path, -p` : Project path (default: current directory)

#### Examples

```bash
# Python project with Claude Code
rapid init --language python --assistant claude-code

# Angular project with multiple assistants
rapid init -l angular -a claude-code -a github-copilot

# Interactive setup
rapid init -i

# Check what would be done without making changes
rapid init --dry-run -l python -a rapid-only
```

### 2. List Available Options (`list`)

Display available languages, assistants, or templates.

#### Usage

```bash
# List available languages
rapid list languages

# List available AI assistants
rapid list assistants

# List templates by language
rapid list templates
```

#### Output Examples

```
# rapid list languages
Available Languages
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Code      ┃ Display Name       ┃ Has Templates ┃ Status      ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ angular   │ Angular/TypeScript │ ✓             │ Available   │
│ python    │ Python             │ ✓             │ Available   │
│ generic   │ Generic/Other      │ ✓             │ Available   │
│ see-sharp │ C# (.NET)          │ ✗             │ Coming Soon │
└───────────┴────────────────────┴───────────────┴─────────────┘

# rapid list assistants
Available AI Assistants
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Code           ┃ Display Name    ┃ Description                         ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ claude-code    │ Claude Code     │ Anthropic's Claude AI coding assist │
│ github-copilot │ GitHub Copilot  │ GitHub's AI pair programmer         │
│ rapid-only     │ .rapid only     │ Basic RAPID framework files only    │
└────────────────┴─────────────────┴─────────────────────────────────────┘
```

### 3. Configuration Management (`config`)

Manage RAPID configuration settings and defaults.

#### Usage

```bash
# Show current configuration
rapid config --show
rapid config

# Set default language
rapid config --set-language python

# Set default assistants
rapid config --set-assistant claude-code --set-assistant rapid-only

# Use global config (in home directory)
rapid config --global --set-language python

# Reset configuration to defaults
rapid config --reset
```

#### Configuration File

RAPID looks for `.rapidrc.json` in the current directory or home directory:

```json
{
  "defaults": {
    "language": "python",
    "assistants": ["claude_code", "rapid_only"],
    "verbose": false
  }
}
```

### 4. Check Status (`status`)

Check the initialization status of RAPID framework in your project.

#### Usage

```bash
# Check status in current directory
rapid status

# Check status in specific directory
rapid status --path /path/to/project
```

#### Output Example

```
✓ RAPID framework is initialized

.rapid directory structure
├── agents/
│   └── 3 file(s)
├── commands/
│   └── 5 file(s)
└── rapid_tui.log

Installation Statistics
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Category         ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Agent Templates  │ 3     │
│ Command Template │ 5     │
│ Assistant Config │ claude│
│ Log Files        │ 1     │
└──────────────────┴───────┘

✓ No issues found
```

## TUI Mode

The original Textual-based TUI is still available for users who prefer an interactive interface:

```bash
# Launch TUI with the --ui flag
rapid --ui

# Or use the legacy command (backward compatibility)
rapid-tui
```

## Environment Variables

Configure RAPID behavior using environment variables:

```bash
# Set default language
export RAPID_DEFAULT_LANGUAGE=python

# Set default assistants (comma-separated)
export RAPID_DEFAULT_ASSISTANTS=claude-code,rapid-only

# Specify config file location
export RAPID_CONFIG_PATH=~/.config/rapid/config.json

# Disable colored output
export RAPID_NO_COLOR=1
```

## CI/CD Integration

The CLI mode is perfect for CI/CD pipelines and automation:

### GitHub Actions Example

```yaml
name: Initialize RAPID
on: [push]

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install RAPID
        run: pip install rapid-tui

      - name: Initialize RAPID Framework
        run: rapid init --language python --assistant claude-code --force
```

### Shell Script Example

```bash
#!/bin/bash

# Initialize RAPID for a Python project
rapid init \
  --language python \
  --assistant claude-code \
  --assistant github-copilot \
  --force

# Check initialization status
if rapid status; then
  echo "RAPID framework initialized successfully"
else
  echo "Failed to initialize RAPID framework"
  exit 1
fi
```

## Common Workflows

### 1. New Project Setup

```bash
# Create project directory
mkdir my-project && cd my-project

# Initialize git
git init

# Initialize RAPID interactively
rapid init -i

# Verify setup
rapid status
```

### 2. Batch Initialization

```bash
# Initialize multiple projects
for project in project1 project2 project3; do
  rapid init \
    --path "./$project" \
    --language python \
    --assistant claude-code \
    --force
done
```

### 3. Configuration Templates

Create a team configuration:

```bash
# Set team defaults
rapid config --global --set-language python
rapid config --global --set-assistant claude-code
rapid config --global --set-assistant rapid-only

# Team members can now use defaults
rapid init  # Uses configured defaults
```

## Troubleshooting

### Command Not Found

```bash
# Ensure rapid is in your PATH
poetry shell

# Or run with poetry
poetry run rapid --help
```

### Permission Denied

```bash
# Use --force to overwrite existing files
rapid init --force -l python -a claude-code

# Check directory permissions
ls -la .rapid/
```

### Validation Errors

```bash
# Check available options
rapid list languages
rapid list assistants

# Use interactive mode for guided setup
rapid init -i
```

## Tips and Best Practices

1. **Use Configuration Files**: Set defaults in `.rapidrc.json` to avoid repetitive typing
2. **Dry Run First**: Always test with `--dry-run` before making changes
3. **Version Control**: Add `.rapid/` to version control for team consistency
4. **CI/CD Integration**: Use CLI mode in pipelines for automated setup
5. **Interactive for New Users**: Recommend `-i` flag for first-time users

## Migration from TUI-Only

If you're upgrading from the TUI-only version:

```bash
# Old way (still works)
rapid-tui

# New way - CLI mode (default)
rapid init -l python -a claude-code

# New way - TUI mode
rapid --ui
```

## Command Reference

### Quick Reference Card

```bash
# Initialize
rapid init -l <lang> -a <assistant>     # Basic init
rapid init -i                            # Interactive
rapid init --dry-run                     # Preview changes

# List
rapid list languages                     # Show languages
rapid list assistants                    # Show assistants
rapid list templates                     # Show templates

# Configure
rapid config --show                      # Show config
rapid config --set-language <lang>       # Set default
rapid config --reset                     # Reset config

# Status
rapid status                             # Check status
rapid status --path <path>               # Check specific path

# TUI Mode
rapid --ui                               # Launch TUI
rapid-tui                                # Legacy command
```

## Support and Feedback

- **Documentation**: Check `/docs` directory for detailed guides
- **Issues**: Report bugs via GitHub Issues
- **Support**: Contact the RAPID team for assistance

## Conclusion

The new CLI interface makes RAPID more versatile and automation-friendly while maintaining the familiar TUI for interactive use. Choose the mode that best fits your workflow:

- **CLI Mode**: Scripts, CI/CD, automation, quick operations
- **TUI Mode**: Interactive exploration, visual feedback, guided setup

Both modes share the same underlying functionality, ensuring consistent results regardless of your chosen interface.