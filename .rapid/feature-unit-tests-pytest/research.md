# RAPID CLI Framework Unit Tests Implementation Research

## Project Overview

The RAPID CLI framework is a command-line tool for initializing AI assistant configurations across different programming languages and frameworks. The core functionality handles template management, file operations, configuration validation, and project initialization workflows that support multiple AI assistants (Claude Code, GitHub Copilot, RAPID-only).

## Current Testing Infrastructure

### Existing Test Setup

- **pytest** configured with comprehensive options in `pyproject.toml`
- **pytest-cov** for coverage reporting with HTML output to `htmlcov/`
- **pytest-mock** for mocking capabilities
- Test configuration targets `src/rapid_tui` with `--cov-report=term-missing` and `--cov-report=html`
- Existing `tests/test_config.py` with comprehensive configuration testing (98 test methods)
- Empty `tests/test_models.py` file ready for expansion

### Test Configuration Analysis

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--tb=short",
    "--cov=src/rapid_tui",
    "--cov-report=term-missing",
    "--cov-report=html"
]
```

## Core Business Logic Analysis

### 1. Data Models (`src/rapid_tui/models.py`)

**Key Components Requiring Testing:**

- **Language Enum**: 4 variants (ANGULAR, PYTHON, GENERIC, SEE_SHARP)
  - `display_name` property mapping
  - `has_templates` property (SEE_SHARP returns False, others True)
- **Assistant Enum**: 3 variants (CLAUDE_CODE, GITHUB_COPILOT, RAPID_ONLY)
  - `display_name` property mapping
- **AssistantConfig Model**: Pydantic model with methods
  - `get_agent_dir()` method returns Optional[Path]
  - `get_commands_dir()` method returns Path
- **InitializationConfig Model**: Core validation logic
  - `validate_assistants()` class method ensures RAPID_ONLY inclusion
  - `validate_project_path()` validates path exists and is directory
- **CopyOperation Model**: File operation tracking
  - `relative_destination` property with error handling
- **InitializationResult Model**: Results aggregation
  - Complex `summary` property with multiple statistics
- **FileOperation & UpdateResult Models**: Similar patterns for updates

### 2. Configuration Management (`src/rapid_tui/config.py`)

**Key Components:**

- **Template Path Functions**:
  - `get_templates_dir()`, `get_agents_template_dir()`, `get_commands_template_dir()`
  - Path resolution relative to module location
- **Assistant Configuration Mapping**: `ASSISTANT_CONFIGS` dict
  - Claude Code: `.claude/agents`, `.claude/commands`
  - GitHub Copilot: `.github` (no agents), `.github/prompts`
  - RAPID Only: `.rapid/agents`, `.rapid/commands`
- **Template Mappings**: `TEMPLATE_MAPPINGS` by language
  - Python: `python-code-agent.md`, `python-planning-agent.md`
  - Angular/Generic: `rapid-code-agent.md`, `rapid-planning-agent.md`
  - SEE_SHARP: Empty arrays (no templates)
- **CLI Alias Resolution**: `resolve_agent_name()` function
  - Maps "claude" -> CLAUDE_CODE, "copilot" -> GITHUB_COPILOT, "all" -> None

### 3. File Operations (`src/rapid_tui/utils/file_operations.py`)

**TemplateManager Class - Key Methods:**

- **`initialize_project()`**: Main workflow orchestration
  - Progress callback handling
  - Language and assistant processing
  - Error collection and rollback logic
- **`copy_for_assistant()`**: Assistant-specific file copying
- **`_copy_agents()` & `_copy_commands()`**: Type-specific copying
- **`_copy_file()`**: Individual file copying with retry logic (MAX_RETRY_ATTEMPTS=3)
- **`_ensure_directory()`**: Directory creation with tracking
- **`_rollback()`**: Failure recovery mechanism
- **`validate_environment()`**: Pre-flight environment checks
  - Write permissions, disk space (10MB minimum), template directory existence

**Error Handling Patterns:**

- Retry logic with configurable attempts and delays
- Comprehensive error collection in CopyOperation records
- Rollback mechanism for failed operations
- Environment validation before operations

### 4. Service Layer

#### Initialization Service (`src/rapid_tui/services/initialization.py`)

- **`InitializationService`** class with dry_run and force options
- **`initialize()`** method: Main business logic entry point
- **`get_status()`** method: Current state inspection
- Environment validation delegation to TemplateManager
- Progress callback integration

#### Update Service (`src/rapid_tui/services/update.py`)

- **`UpdateService`** class for file synchronization
- **`sync_all_agents()`** & **`sync_agent()`**: Outbound synchronization
- **`consolidate_all_agents()`** & **`consolidate_agent()`**: Inbound synchronization
- **`_sync_directory_structure()`**: Recursive directory synchronization
- **`_compare_files()`**: Timestamp-based file comparison
- Rich Console integration for formatted output

### 5. CLI Interface (`src/rapid_tui/cli/`)

#### Main CLI (`src/rapid_tui/cli/main.py`)

- **Typer application** setup with version callback
- **Global options**: `--verbose`, `--dry-run`, `--ui` (hidden)
- **Context object** management for passing options
- **CLI/TUI delegation** logic

#### Init Command (`src/rapid_tui/cli/commands/init.py`)

- **Interactive mode** with rich table displays
- **Argument validation** for languages and assistants
- **Progress display** with Rich Progress component
- **Detailed result reporting** with operation summaries
- **Force and dry-run** support

### 6. TUI Application (`src/rapid_tui/app.py`)

- **RapidTUI** class extending Textual App
- **Environment validation** on mount
- **Screen navigation** management (language -> assistant -> confirmation)
- **Configuration state** management through InitializationConfig
- **Logging setup** with file and console handlers

## Testing Strategy Requirements

### High-Priority Testing Areas

#### 1. Data Model Validation Testing

- **Enum property methods** (display_name, has_templates)
- **Pydantic field validators** (assistants, project_path)
- **Computed properties** (relative_destination, summary statistics)
- **Edge cases**: Invalid paths, empty lists, malformed data

#### 2. Configuration System Testing

- **Path resolution** across different installation contexts
- **Assistant configuration** mapping completeness
- **Template mapping** validation for all languages
- **CLI alias resolution** with case sensitivity

#### 3. File Operations Testing

- **Template copying** with mocked filesystem
- **Error handling** and retry logic
- **Environment validation** (permissions, disk space)
- **Rollback mechanisms** on failures
- **Atomic operations** simulation

#### 4. Service Layer Testing

- **End-to-end workflows** with mocked dependencies
- **Error propagation** from file operations
- **Progress callback** integration
- **State management** and status reporting

#### 5. CLI Command Testing

- **Argument parsing** and validation
- **Interactive prompts** simulation
- **Output formatting** verification
- **Error handling** and exit codes

### Mock Strategy Implementation

**Filesystem Mocking:**

```python
# Mock pathlib.Path methods
# Mock shutil operations
# Mock os.stat and disk usage checks
# Mock file I/O operations
```

**Environment Mocking:**

```python
# Mock Path.exists(), Path.is_dir(), Path.mkdir()
# Mock file permissions and write access
# Mock template directory existence
# Mock logging and console output
```

**CLI Testing Patterns:**

```python
# Mock Typer context objects
# Mock Rich console output
# Mock interactive prompts (Prompt.ask, Confirm.ask)
# Mock progress callbacks
```

### Test File Structure Analysis

**Existing Test Coverage:**

- `tests/test_config.py`: Comprehensive (98 test methods)
  - Template path resolution ✓
  - Assistant configuration validation ✓
  - Language template mapping ✓
  - Agent name resolution ✓
  - Configuration constants ✓
  - Integration testing ✓

**Required New Test Files:**

- `tests/test_models.py`: Currently empty, needs full implementation
- `tests/test_file_operations.py`: New file for TemplateManager testing
- `tests/test_services_initialization.py`: New file for InitializationService
- `tests/test_services_update.py`: New file for UpdateService
- `tests/test_cli_main.py`: New file for main CLI application
- `tests/test_cli_commands.py`: New file for CLI command implementations
- `tests/test_app_cli_mode.py`: New file for app CLI delegation

### Coverage Targets

- **Models**: 95%+ (critical business logic)
- **File Operations**: 90%+ (complex error handling)
- **Services**: 90%+ (workflow orchestration)
- **CLI Commands**: 85%+ (user interface logic)
- **Overall Project**: 90%+

## Implementation Context

### Dependencies Available

- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking capabilities
- **pydantic**: Model validation (already in use)
- **pathlib**: Path operations (already in use)
- **typer**: CLI framework (already in use)
- **rich**: Console formatting (already in use)

### Project Structure

```
src/rapid_tui/
├── models.py          # Core data models
├── config.py          # Configuration management
├── app.py            # TUI/CLI delegation
├── cli/
│   ├── main.py       # Typer CLI app
│   └── commands/     # Individual commands
├── services/
│   ├── initialization.py  # Init business logic
│   └── update.py          # Sync business logic
└── utils/
    └── file_operations.py  # Template management

tests/
├── test_config.py        # ✓ Comprehensive existing
├── test_models.py        # ✗ Empty, needs implementation
└── [new test files]      # ✗ Need creation
```

### Error Patterns Found

- **Path validation**: Extensive use of Path.exists(), Path.is_dir()
- **File permissions**: Write access checking with test file creation
- **Retry logic**: MAX_RETRY_ATTEMPTS with RETRY_DELAY patterns
- **Rollback operations**: Reversed operation cleanup on failures
- **Environment checks**: Disk space, template directory validation

### Integration Points

- **TemplateManager ↔ InitializationService**: Primary integration
- **Services ↔ CLI Commands**: User interface to business logic
- **Models ↔ All Layers**: Data validation throughout
- **Config ↔ All Layers**: Configuration access patterns

## CLARIFYING QUESTIONS

1. **Test Environment Setup**: Should tests create temporary directories for filesystem operations, or is full mocking preferred?

2. **CLI Integration Testing**: What level of integration testing is desired for the full CLI workflow (init command from start to finish)?

3. **Cross-Platform Testing**: Should the test suite include specific Windows/macOS/Linux path handling scenarios?

4. **Performance Testing**: Are there performance benchmarks for file operations that should be validated in tests?

5. **Error Simulation**: Should tests include network/filesystem failure scenarios (permission denied, disk full, etc.)?

6. **TUI Testing**: The research focused on CLI and core logic - should Textual TUI components be included in this testing phase?
