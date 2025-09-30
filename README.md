# RAPID Framework

![simple_logo](imgs/rapid_transparent.png)

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/94aharris/rapid-tui)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## TL/DR

Structured AI-driven development framework with specialized agents and command-driven workflows.

**Languages:** `angular`, `python`, `generic`, `see-sharp`
**Assistants:** `claude` (claude-code), `copilot` (github-copilot), `rapid-only`

## File Synchronization

RAPID provides bidirectional synchronization between your central `.rapid/` directory (source of truth) and assistant-specific directories. This enables collaborative workflow development and consistent context across different AI tools.

### Update from .rapid/ (Default Direction)

```bash
# Sync all changes from .rapid/ to assistant directories
rapid update

# Update only Claude Code files
rapid update --agent claude

# Update only GitHub Copilot files
rapid update --agent copilot

# Force update even if target files are newer
rapid update --force
```

### Consolidate to .rapid/ (Reverse Direction)

```bash
# Consolidate all changes from assistant directories back to .rapid/
rapid update --reverse

# Consolidate only from Claude Code directory
rapid update --reverse --agent claude

# Consolidate only from GitHub Copilot directory
rapid update --reverse --agent copilot

# Force consolidation regardless of timestamps
rapid update --reverse --force
```

### File Synchronization Behavior

- **Default**: Only copies files where source is newer than target
- **Force Mode**: Overwrites target files regardless of timestamps
- **Dry Run**: Preview operations with `--dry-run` flag
- **Verbose**: See detailed operations with `--verbose` flag

### What Gets Synchronized

- **Instructions**: Language-specific coding guidelines (`.rapid/instructions/` ↔ assistant directories)
- **Agents**: Framework-specific AI agents (`.rapid/agents/` ↔ assistant directories)
- **Commands**: RAPID workflow slash commands (`.rapid/commands/` ↔ assistant directories)
- **Prompts**: Specialized prompt templates (`.rapid/prompts/` ↔ assistant directories)

### Typical Workflows

1. **Team Context Updates**: Update `.rapid/` files, then `rapid update` to distribute
2. **Individual Improvements**: Modify assistant files, then `rapid update --reverse` to share
3. **Conflict Resolution**: Use `--force` when you need to override timestamp checks
4. **Multi-Assistant Setup**: Sync specific agents when working with different AI tools development with specialized agents and command-driven workflows.

## Overview

The RAPID (Research - Align - Plan - Inspect - Develop) Framework is a systematic approach to agentic AI development that transforms feature requests and bug reports into production-ready code through a structured five-phase methodology. RAPID leverages specialized agents and command-driven workflows to ensure comprehensive requirements analysis, thorough planning, and quality implementation across any codebase.

Unlike traditional development approaches, RAPID emphasizes intentional context management and frequent compaction loops, enabling faster iteration cycles while maintaining code quality and architectural consistency. Each phase is orchestrated through custom commands that deploy specialized agents—from planning agents that transform requirements into technical specifications, to implementation agents that write production code following established best practices.

**RAPID is a FRAMEWORK not a set of tools:** Although this particular library is a TUI to help enable RAPID within various AI coding assistants, it is NOT required to be a RAPID developer. The framework is a way to approach AiDD (AI Driven Development), not this toolkit. A developer manually stepping through each stage and copying context between new sessions in any AI interface is also using RAPID.

## Key Distinguishers

RAPID differentiates itself from specification-driven methodologies like GitHub's spec-kit through several core innovations:

**Context-First Development**: While spec-kit emphasizes abstract specifications before implementation, RAPID prioritizes deep codebase context gathering. The Research phase systematically analyzes existing patterns, dependencies, and architectural decisions to inform development, ensuring new code integrates seamlessly with established systems.

**Interactive Alignment Loops**: RAPID's dedicated Align phase creates structured feedback sessions with stakeholders, resolving ambiguities through direct interaction rather than relying solely on upfront specification clarity. This reduces miscommunication and ensures shared understanding before implementation begins.

**Domain-Specific Optimization**: Unlike technology-agnostic approaches, RAPID deploys specialized agents optimized for specific frameworks and languages, following established naming conventions and architectural patterns, resulting in more idiomatic and maintainable code.

**Integrated Workflow Management**: RAPID includes built-in git worktree management and optional external task system integration, providing complete development lifecycle support from task retrieval through deployment, rather than focusing solely on the specification-to-code transformation.

**Intentional Context Compaction**: RAPID's emphasis on "frequent compaction loops" and systematic context management prevents information overload while maintaining comprehensive understanding throughout the development process.

**Centralized Context Management**: RAPID TUI enables teams to maintain AI workflow artifacts in a single `.rapid/` directory, then synchronize them bidirectionally across different AI coding assistants (Claude Code, GitHub Copilot, etc.). Teams can update context documents and agent definitions once in `.rapid/` and distribute them to assistant-specific folders, or consolidate changes made in assistant directories back to `.rapid/` for team sharing. The `rapid update` command supports both directions, keeping workflows consistent across the team regardless of which AI tool individual developers prefer while enabling collaborative workflow improvements.

The framework addresses common development challenges including incomplete requirements gathering, insufficient codebase analysis, and lack of systematic planning by enforcing a disciplined workflow that captures context, validates understanding, and ensures alignment before implementation begins. This results in more predictable outcomes, reduced rework, and higher-quality code that integrates seamlessly with existing application architecture.

## Quick Start

### Installation

#### From Source

```bash
git clone https://github.com/anthropics/rapid-tui.git
cd rapid-tui
poetry install
```

#### Using Poetry

```bash
# Add to your development dependencies
poetry add --group dev rapid-tui

# Or install globally
pipx install rapid-tui
```

### Initialize Your Project

Navigate to your project and run:

```bash
cd /path/to/your/project

# Quick setup with CLI
rapid init --language python --assistant claude

# Multiple assistants
rapid init --language python --assistant claude --assistant copilot

# Or interactive mode for guided setup
rapid init --interactive

```

This will:

- Create `.rapid/` directory structure for centralized context management
- Copy language-specific instruction templates to `.rapid/instructions/`
- Copy framework-specific agents to `.rapid/agents/`
- Copy RAPID command definitions to `.rapid/commands/`
- Copy prompt templates to `.rapid/prompts/`
- Set up your AI assistant directories (`.claude/`, `.github/`, etc.)
- Synchronize all templates to assistant-specific folders

### Available Commands

```bash
# Initialize project
rapid init -l python -a claude         # Quick setup
rapid init -l python -a claude -a copilot  # Multiple assistants
rapid init --interactive                # Guided setup
rapid init --force                      # Overwrite existing files

# Synchronize files between .rapid/ and assistant directories
rapid update                            # Update all assistants from .rapid/
rapid update --agent claude             # Update only Claude files
rapid update --agent all                # Update all configured agents
rapid update --reverse                  # Consolidate changes back to .rapid/
rapid update --reverse --agent copilot  # Consolidate only Copilot changes
rapid update --force                    # Force overwrite regardless of timestamps

# Check what's available
rapid list languages                    # Show supported languages
rapid list assistants                   # Show AI assistants
rapid list templates                    # Show available templates

# Check status and configuration
rapid status                            # Verify installation
rapid config                            # Manage configuration

# Get help
rapid --help                            # Main help
rapid init --help                       # Command-specific help
```

### Supported Options

**Languages:** `angular`, `python`, `generic`, `see-sharp`
**Assistants:** `claude` (claude-code), `copilot` (github-copilot), `rapid-only`

## Development and Testing

### Running Tests

RAPID TUI includes a comprehensive test suite using pytest:

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=rapid_tui --cov-report=html

# Run specific test file
poetry run pytest tests/test_cli_main.py

# Run tests in verbose mode
poetry run pytest -v

# Run tests and show stdout
poetry run pytest -s
```

### Test Structure

- `tests/test_cli_main.py` - CLI command tests
- `tests/test_config.py` - Configuration management tests
- `tests/test_services_initialization.py` - Initialization service tests
- `tests/test_services_update.py` - Update/sync service tests
- `tests/test_models.py` - Data model tests
- `tests/test_helpers.py` - Utility function tests

### Code Quality

```bash
# Format code with black
poetry run black .

# Lint with ruff
poetry run ruff check .

# Type checking with mypy
poetry run mypy src/rapid_tui
```

## Template Structure

After initialization, RAPID creates a structured template directory in `.rapid/` that serves as the central source of truth for all AI assistant configurations:

```
.rapid/
├── instructions/           # Language-specific development guidelines
│   ├── python.md          # Python coding standards and patterns
│   ├── angular.md         # Angular component and service patterns
│   ├── generic.md         # General development guidelines
│   └── see-sharp.md       # C# conventions and patterns
├── agents/                # Framework-specific AI agents
│   ├── python/
│   │   ├── python-planning-agent.md
│   │   └── python-code-agent.md
│   ├── angular/
│   │   ├── rapid-planning-agent.md
│   │   └── rapid-code-agent.md
│   └── generic/
│       ├── rapid-planning-agent.md
│       └── rapid-code-agent.md
├── commands/              # RAPID workflow slash commands
│   ├── rapid-init.md      # Project initialization command
│   ├── rapid-research.md  # Codebase research command
│   ├── rapid-align.md     # Requirements alignment command
│   ├── rapid-plan.md      # Technical planning command
│   ├── rapid-inspect.md   # Plan review command
│   └── rapid-develop.md   # Implementation command
└── prompts/               # Specialized prompt templates
    ├── rapid-init.prompt.md
    ├── rapid-research.prompt.md
    ├── rapid-align.prompt.md
    ├── rapid-plan.prompt.md
    ├── rapid-inspect.prompt.md
    └── rapid-develop.prompt.md
```

## AI Assistant Integration

RAPID templates are synchronized to assistant-specific directories:

- **Claude Code**: Files copied to `.claude/` directory
- **GitHub Copilot**: Files copied to `.github/` directory
- **All Assistants**: Core RAPID commands available as slash commands

The `rapid update` command keeps these synchronized bidirectionally.

---

# RAPID Workflow: AI Assistant Slash Commands

The following commands are installed in your AI assistants after running `rapid init`. These are **slash commands** used within your AI coding assistant, not CLI commands.

## /rapid-init (Setup)

```bash
/rapid-init [feature description]
```

### Overview:

The Init phase establishes the development workspace and creates a comprehensive research prompt. This phase handles task retrieval (if applicable), git worktree creation, and formulates a detailed feature prompt that guides the entire RAPID development cycle. The output is a validated research prompt stored for subsequent phases.

### Steps:

1. Retrieve task details if external task tracking is configured and a task identifier is provided
2. Create a new git worktree with a descriptive branch name
3. Switch to the newly created git worktree
4. Formulate a detailed feature prompt from user input and task description with comprehensive acceptance criteria
5. Validate the formulated prompt with the user to ensure accuracy and completeness
6. Store the validated prompt in `.rapid/branch-name/research-prompt.md` for use by subsequent phases

## /rapid-research: Codebase Context Gathering

```bash
/rapid-research
```

### Overview:

The Research phase conducts comprehensive codebase analysis to gather relevant context for feature implementation or bug remediation. This phase focuses on discovering existing patterns, dependencies, and architectural elements that will inform the development plan. The output is a consolidated research document with identified context and any clarifying questions that need resolution.

### Steps:

1. Read the research prompt from `.rapid/branch-name/research-prompt.md` and incorporate any additional user-provided information
2. Systematically research the existing codebase for context relevant to the specific feature or bug, focusing only on information useful for development planning
3. Analyze existing patterns, architectural elements, dependencies, and conventions that relate to the implementation requirements
4. Document all collected research findings in `.rapid/branch-name/research.md`
5. Identify any gaps or ambiguities that require clarification and add them to the CLARIFYING QUESTIONS section at the bottom of the research file
6. Report completion with the research file path and confirm readiness to proceed to the `/rapid-align` stage

## /rapid-align: Interactive Clarification Session

```bash
/rapid-align
```

### Overview:

The Align phase creates an interactive feedback loop with the user to resolve any ambiguities or gaps identified during the Research phase. This ensures that all stakeholders have a shared understanding of requirements before proceeding to planning. The phase focuses on clarifying questions, updating research documentation, and confirming readiness for the planning stage.

### Steps:

1. Read the research findings from `.rapid/branch-name/research.md` and incorporate any additional user-provided information
2. Review the CLARIFYING QUESTIONS section and engage the user in an interactive session to resolve each question
3. Wait for user responses and gather additional context or clarifications as needed
4. Update `.rapid/branch-name/research.md` by removing answered questions and incorporating the clarified information into the main research content
5. Confirm with the user that all questions have been addressed and requirements are clearly understood
6. Validate that the task is ready to proceed to the `/rapid-plan` stage with complete and unambiguous requirements

## /rapid-plan: Technical Specification Generation

```bash
/rapid-plan
```

### Overview:

The Plan phase leverages a specialized planning agent to transform the clarified research into a comprehensive technical implementation plan. This phase analyzes acceptance criteria, examines the codebase for architectural patterns, and generates detailed specifications that enable seamless execution by the development agent. The output is a thorough implementation roadmap ready for review and execution.

### Steps:

1. Read the finalized research from `.rapid/branch-name/research.md` and incorporate any additional user-provided information
2. Deploy the framework-specific planning agent to analyze the research and create a comprehensive code implementation plan
3. The planning agent conducts codebase discovery, identifies existing patterns, and maps requirements to technical specifications
4. Generate detailed specifications including necessary code structures, integration points, and configuration requirements
5. Store the comprehensive implementation plan in `.rapid/branch-name/plan.md`
6. Confirm completion of the planning phase and validate readiness to proceed to the `/rapid-inspect` stage

## /rapid-inspect: Plan Validation and Review

```bash
/rapid-inspect
```

### Overview:

The Inspect phase provides a final quality assurance checkpoint before implementation begins. This phase presents the generated plan to the user for review, validation, and any necessary adjustments. It ensures that the technical specifications align with expectations and requirements before committing to the development phase, preventing costly iterations during implementation.

### Steps:

1. Read the implementation plan from `.rapid/branch-name/plan.md` and incorporate any additional user-provided information
2. Present the complete plan to the user in a clear, reviewable format
3. Verify with the user that the plan accurately reflects requirements and expectations
4. Identify any adjustments, modifications, or concerns raised by the user during review
5. Update `.rapid/branch-name/plan.md` with any recommended changes or refinements as necessary
6. Confirm with the user that the plan is approved and ready for implementation, then validate readiness to proceed to the `/rapid-develop` stage

## /rapid-develop: Code Implementation

```bash
/rapid-develop
```

### Overview:

The Develop phase executes the approved implementation plan using a specialized development agent. This phase focuses exclusively on implementing production code changes, following framework best practices and existing codebase patterns. The development agent transforms the detailed plan into working code while maintaining code quality, type safety, and integration with the existing application architecture.

### Steps:

1. Read the approved implementation plan from `.rapid/branch-name/plan.md` and incorporate any additional user-provided information
2. Deploy the framework-specific development agent to implement the planned code changes according to the specifications
3. The development agent writes code following established project conventions, naming patterns, and architectural decisions
4. Ensure code compiles/runs without errors, follows language-specific type requirements, and integrates properly with existing dependencies
5. Verify that the implementation maintains backward compatibility and follows existing architectural patterns
6. Confirm completion of all planned implementation tasks with the user, providing summary of modified/created files and key changes implemented

## Appendix: Complete RAPID Workflow Example

Here's a full example of using RAPID with Claude Code to implement a new feature:

### 1. Initialize RAPID in Your Repository

```bash
# Navigate to your project
cd /path/to/your/project

# Initialize RAPID for a Python project with Claude Code
rapid init --language python --assistant claude

# Verify initialization
rapid status
```

### 2. Start Feature Development

```bash
# In Claude Code, start with the init phase
/rapid-init

# Provide your feature request when prompted:
# "Add user authentication with JWT tokens including login, logout, and token refresh endpoints"
# This creates a new git worktree and research prompt
```

```bash
# Change to the appropriate worktree
cd <worktree_path>
```

### 3. Research the Codebase

```bash
# Research existing patterns and gather context
/rapid-research

# The agent will analyze your codebase for:
# - Existing authentication patterns
# - Database models and schemas
# - API endpoint conventions
# - Dependency management
# Output saved to .rapid/branch-name/research.md
```

### 4. Align on Requirements

```bash
# Resolve any questions and clarify requirements
/rapid-align

# Answer clarifying questions like:
# - "Should we use Redis for token blacklisting?"
# - "What should the token expiration time be?"
# - "Do you need role-based access control?"
```

### 5. Generate Technical Plan

```bash
# Create detailed implementation plan
/rapid-plan

# The planning agent generates:
# - API endpoint specifications
# - Database schema changes
# - Authentication flow diagrams
# - Integration points
# Output saved to .rapid/branch-name/plan.md
```

### 6. Review and Inspect Plan

```bash
# Review the generated plan before implementation
/rapid-inspect

# Review the plan and provide feedback:
# - Confirm API endpoint paths
# - Validate security considerations
# - Approve database changes
```

### 7. Implement the Feature

```bash
# Execute the approved plan
/rapid-develop

# The development agent will:
# - Create authentication middleware
# - Implement JWT token generation/validation
# - Add login/logout endpoints
# - Set up token refresh mechanism
# - Write necessary tests
```

### 8. Complete the Workflow

After development, you can:

- Review the implemented changes
- Run tests to verify functionality
- Commit changes to your feature branch
- Create a pull request for review

### Tips for Claude Code Users

1. **Keep context focused**: RAPID manages context automatically between phases
2. **Trust the process**: Let each phase complete before moving to the next
3. **Review outputs**: Check the `.rapid/branch-name/` files to understand what's being passed between phases
4. **Iterate if needed**: You can re-run any phase if adjustments are needed

This structured approach ensures consistent, high-quality implementations that align with your codebase patterns and requirements.
