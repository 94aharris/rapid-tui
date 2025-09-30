"""File operations and template management."""

import shutil
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from contextlib import contextmanager
import time

from rapid_tui.models import (
    Assistant, Language, CopyOperation,
    InitializationResult, AssistantConfig
)
from rapid_tui.config import (
    get_assistant_config, get_agents_template_dir,
    get_commands_template_dir, get_language_templates,
    COPY_BUFFER_SIZE, MAX_RETRY_ATTEMPTS, RETRY_DELAY
)


class TemplateManager:
    """Manages template copying with error handling and rollback."""

    def __init__(self, project_root: Path, dry_run: bool = False):
        """
        Initialize the template manager.

        Args:
            project_root: Target project directory
            dry_run: If True, simulate operations without actual copying
        """
        self.project_root = project_root
        self.dry_run = dry_run
        self.operations: List[CopyOperation] = []
        self.created_directories: List[Path] = []
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configure logging for file operations."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.FileHandler(
                self.project_root / ".rapid" / "initialization.log",
                mode='a'
            )
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def initialize_project(
        self,
        language: Language,
        assistants: List[Assistant],
        progress_callback: Optional[callable] = None
    ) -> InitializationResult:
        """
        Initialize project with selected templates.

        Args:
            language: Selected programming language
            assistants: List of AI assistants to configure
            progress_callback: Optional callback for progress updates

        Returns:
            InitializationResult with operation details
        """
        self.logger.info(f"Starting initialization for {language.value} with {[a.value for a in assistants]}")

        result = InitializationResult(
            success=True,
            operations=[],
            total_files_copied=0,
            total_directories_created=0
        )

        try:
            # Always ensure .rapid directory exists
            self._ensure_rapid_directory()

            # Process each assistant
            total_steps = len(assistants)
            for idx, assistant in enumerate(assistants):
                if progress_callback:
                    progress_callback(f"Configuring {assistant.display_name}", idx, total_steps)

                ops = self.copy_for_assistant(assistant, language)
                result.operations.extend(ops)

            # Calculate totals
            result.total_files_copied = len([op for op in result.operations if op.success])
            result.total_directories_created = len(self.created_directories)

            # Check for any failures
            failed_ops = [op for op in result.operations if not op.success]
            if failed_ops:
                result.success = False
                result.errors = [op.error_message for op in failed_ops if op.error_message]

            # Add warnings for See-Sharp if selected
            if language == Language.SEE_SHARP:
                result.warnings.append("C# templates are not yet available. Commands have been copied, but agent templates are pending.")

            if progress_callback:
                progress_callback("Initialization complete", total_steps, total_steps)

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            result.success = False
            result.errors.append(str(e))
            if not self.dry_run:
                self._rollback()

        return result

    def copy_for_assistant(
        self,
        assistant: Assistant,
        language: Language
    ) -> List[CopyOperation]:
        """
        Copy files according to assistant-specific structure.

        Args:
            assistant: The AI assistant to configure
            language: The programming language for agent templates

        Returns:
            List of copy operations performed
        """
        operations = []
        config = get_assistant_config(assistant)

        if not config:
            self.logger.error(f"No configuration found for {assistant.value}")
            return operations

        # Copy agents if applicable
        if config.copy_agents and config.agents_path:
            agent_ops = self._copy_agents(config, language, assistant)
            operations.extend(agent_ops)

        # Copy commands
        if config.copy_commands:
            command_ops = self._copy_commands(config, assistant)
            operations.extend(command_ops)

        # Copy instructions if applicable
        if config.copy_instructions:
            instruction_ops = self._copy_instructions(config, language, assistant)
            operations.extend(instruction_ops)

        return operations

    def _copy_agents(
        self,
        config: AssistantConfig,
        language: Language,
        assistant: Assistant
    ) -> List[CopyOperation]:
        """Copy agent templates to assistant directory."""
        operations = []

        # Get language-specific templates
        templates = get_language_templates(language)
        agent_files = templates.get("agents", [])

        if not agent_files and language != Language.SEE_SHARP:
            self.logger.warning(f"No agent templates found for {language.value}")
            return operations

        # Create target directory
        target_dir = config.get_agent_dir(self.project_root) / language.value
        self._ensure_directory(target_dir)

        # Copy each agent file
        source_dir = get_agents_template_dir() / language.value
        for filename in agent_files:
            source = source_dir / filename
            destination = target_dir / filename

            operation = self._copy_file(
                source, destination, "agent", assistant
            )
            operations.append(operation)

        return operations

    def _copy_commands(
        self,
        config: AssistantConfig,
        assistant: Assistant
    ) -> List[CopyOperation]:
        """Copy command templates to assistant directory.

        For GitHub Copilot, copies from templates/prompts to both .rapid/prompts and .github/prompts.
        For other assistants, copies from templates/commands to .rapid/commands and their respective directories.
        """
        operations = []

        # Determine source directory based on assistant
        if assistant == Assistant.GITHUB_COPILOT:
            from rapid_tui.config import get_prompts_template_dir
            source_dir = get_prompts_template_dir()
            rapid_subdir = "prompts"
        else:
            source_dir = get_commands_template_dir()
            rapid_subdir = "commands"

        command_files = list(source_dir.glob("*.md"))

        # Copy to .rapid/{commands|prompts} first
        rapid_target_dir = self.project_root / ".rapid" / rapid_subdir
        self._ensure_directory(rapid_target_dir)

        for source_file in command_files:
            # Copy to .rapid directory
            rapid_destination = rapid_target_dir / source_file.name
            operation = self._copy_file(
                source_file, rapid_destination, "command", assistant
            )
            operations.append(operation)

        # Copy to assistant directory
        target_dir = config.get_commands_dir(self.project_root)
        self._ensure_directory(target_dir)

        for source_file in command_files:
            destination = target_dir / source_file.name

            operation = self._copy_file(
                source_file, destination, "command", assistant
            )
            operations.append(operation)

        return operations

    def _copy_instructions(
        self,
        config: AssistantConfig,
        language: Language,
        assistant: Assistant,
    ) -> List[CopyOperation]:
        """Copy instruction template to .rapid/instructions/ and assistant directory.

        Args:
            config: Assistant configuration
            language: Selected language
            assistant: Target assistant

        Returns:
            List of copy operations performed
        """
        operations = []

        # Skip if assistant doesn't support instructions
        if not config.copy_instructions or not config.instructions_file:
            self.logger.debug(
                f"Skipping instruction copy for {assistant.value} "
                "(copy_instructions=False or no instructions_file configured)"
            )
            return operations

        # Get instruction template filename from TEMPLATE_MAPPINGS
        from rapid_tui.config import get_language_templates

        templates = get_language_templates(language)
        instruction_filename = templates.get("instructions")

        if not instruction_filename:
            self.logger.warning(
                f"No instruction template defined for language {language.value}"
            )
            return operations

        # Get template source path
        from rapid_tui.config import get_instructions_template_dir

        template_source = get_instructions_template_dir() / instruction_filename

        if not template_source.exists():
            self.logger.error(f"Instruction template not found: {template_source}")
            return operations

        # First, copy to .rapid/instructions/{language}.md
        rapid_instructions_dir = self.project_root / ".rapid" / "instructions"
        rapid_dest = rapid_instructions_dir / instruction_filename

        if not rapid_dest.exists() or self.dry_run:
            op = self._copy_file(
                source=template_source,
                destination=rapid_dest,
                operation_type="instruction",
                assistant=assistant,
            )
            operations.append(op)
            self.logger.info(
                f"Copied instruction template to .rapid/instructions/{instruction_filename}"
            )
        else:
            self.logger.debug(
                f"Instruction file already exists in .rapid/instructions/: {instruction_filename}"
            )

        # Second, copy to assistant directory (e.g., .claude/CLAUDE.md)
        assistant_dest = self.project_root / config.base_dir / config.instructions_file

        op = self._copy_file(
            source=template_source,
            destination=assistant_dest,
            operation_type="instruction",
            assistant=assistant,
        )
        operations.append(op)
        self.logger.info(
            f"Copied instruction template to {config.base_dir}/{config.instructions_file}"
        )

        return operations

    def _copy_file(
        self,
        source: Path,
        destination: Path,
        operation_type: str,
        assistant: Optional[Assistant] = None
    ) -> CopyOperation:
        """
        Copy a single file with retry logic.

        Args:
            source: Source file path
            destination: Destination file path
            operation_type: Type of operation (agent/command)
            assistant: Associated assistant

        Returns:
            CopyOperation record
        """
        operation = CopyOperation(
            source=source,
            destination=destination,
            operation_type=operation_type,
            assistant=assistant
        )

        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would copy {source} to {destination}")
            return operation

        if not source.exists():
            operation.success = False
            operation.error_message = f"Source file not found: {source}"
            self.logger.error(operation.error_message)
            return operation

        # Retry logic for file operations
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                if destination.exists():
                    self.logger.info(f"Overwriting existing file: {destination}")

                shutil.copy2(source, destination)
                self.logger.info(f"Copied {source.name} to {destination}")
                operation.success = True
                break

            except Exception as e:
                operation.success = False
                operation.error_message = str(e)

                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(RETRY_DELAY)
                else:
                    self.logger.error(f"Failed to copy after {MAX_RETRY_ATTEMPTS} attempts: {e}")

        self.operations.append(operation)
        return operation

    def _ensure_directory(self, path: Path) -> None:
        """Create directory if it doesn't exist."""
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would create directory: {path}")
            return

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            self.created_directories.append(path)
            self.logger.info(f"Created directory: {path}")

    def _ensure_rapid_directory(self) -> None:
        """Ensure .rapid directory structure exists."""
        rapid_dir = self.project_root / ".rapid"
        self._ensure_directory(rapid_dir)
        self._ensure_directory(rapid_dir / "agents")
        self._ensure_directory(rapid_dir / "commands")
        self._ensure_directory(rapid_dir / "prompts")
        self._ensure_directory(rapid_dir / "instructions")

    def _rollback(self) -> None:
        """Rollback operations on failure."""
        self.logger.info("Starting rollback due to error")

        # Remove copied files
        for operation in reversed(self.operations):
            if operation.success and operation.destination.exists():
                try:
                    operation.destination.unlink()
                    self.logger.info(f"Rolled back file: {operation.destination}")
                except Exception as e:
                    self.logger.error(f"Failed to rollback {operation.destination}: {e}")

        # Remove created directories (in reverse order)
        for directory in reversed(self.created_directories):
            try:
                if directory.exists() and not any(directory.iterdir()):
                    directory.rmdir()
                    self.logger.info(f"Removed directory: {directory}")
            except Exception as e:
                self.logger.error(f"Failed to remove directory {directory}: {e}")

    def validate_environment(self) -> Tuple[bool, List[str]]:
        """
        Validate the environment before operations.

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check project directory
        if not self.project_root.exists():
            issues.append(f"Project directory does not exist: {self.project_root}")

        if not self.project_root.is_dir():
            issues.append(f"Project path is not a directory: {self.project_root}")

        # Check write permissions
        test_file = self.project_root / ".rapid_test_write"
        try:
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            issues.append(f"No write permission in project directory: {e}")

        # Check disk space (simplified check)
        try:
            stat = shutil.disk_usage(self.project_root)
            free_mb = stat.free / (1024 * 1024)
            if free_mb < 10:  # Require at least 10MB free
                issues.append(f"Insufficient disk space: {free_mb:.1f}MB available")
        except Exception as e:
            issues.append(f"Could not check disk space: {e}")

        # Check template directory exists
        templates_dir = get_agents_template_dir()
        if not templates_dir.exists():
            issues.append(f"Templates directory not found: {templates_dir}")

        return len(issues) == 0, issues


@contextmanager
def temporary_directory(path: Path):
    """Context manager for temporary directory creation with cleanup."""
    created = False
    try:
        if not path.exists():
            path.mkdir(parents=True)
            created = True
        yield path
    finally:
        if created and path.exists():
            shutil.rmtree(path)