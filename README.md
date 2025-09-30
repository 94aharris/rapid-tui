# RAPID Framework

![simple_logo](imgs/rapid_transparent.png)

## TL/DR

Structured agentic development with specialized agents and command-driven workflows.

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

**Centralized Context Management**: RAPID TUI enables teams to maintain AI workflow artifacts in a single `.rapid/` directory, then synchronize them across different AI coding assistants (Claude Code, GitHub Copilot, etc.). Teams update context documents and agent definitions once, and the TUI distributes them to assistant-specific folders, keeping workflows consistent across the team regardless of which AI tool individual developers prefer.

The framework addresses common development challenges including incomplete requirements gathering, insufficient codebase analysis, and lack of systematic planning by enforcing a disciplined workflow that captures context, validates understanding, and ensures alignment before implementation begins. This results in more predictable outcomes, reduced rework, and higher-quality code that integrates seamlessly with existing application architecture.

## Quick Start

### Installation

```bash
git clone <repository-url>
cd rapid-tui
poetry install
```

### Initialize Your Project

Navigate to your project and run:

```bash
cd /path/to/your/project

# Quick setup with CLI
rapid init --language python --assistant claude-code

# Or interactive mode for guided setup
rapid init -i

```

This will:

- Copy framework-specific agents to `.rapid/agents/`
- Copy RAPID command definitions to `.rapid/commands/`
- Set up your AI assistant directories (`.claude/`, `.github/`, etc.)

### Available Commands

```bash
# Initialize project
rapid init -l python -a claude-code    # Quick setup
rapid init --interactive                # Guided setup

# Check what's available
rapid list languages                    # Show supported languages
rapid list assistants                   # Show AI assistants

# Check status
rapid status                            # Verify installation
```

### Supported Options

**Languages:** `angular`, `python`, `generic`, `see-sharp`
**Assistants:** `claude-code`, `github-copilot`, `rapid-only`

## Init (Setup)

```bash
/rapid-init
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

## Research: Codebase Context Gathering

```bash
rapid-research
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

## Align: Interactive Clarification Session

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

## Plan: Technical Specification Generation

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

## Inspect: Plan Validation and Review

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

## Develop: Code Implementation

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
