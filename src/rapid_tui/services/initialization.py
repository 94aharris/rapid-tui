"""Initialization service for shared business logic."""

import logging
from pathlib import Path
from typing import List, Optional, Callable

from rapid_tui.models import (
    Language, Assistant, InitializationConfig,
    InitializationResult
)
from rapid_tui.utils.file_operations import TemplateManager


class InitializationService:
    """Service layer for RAPID framework initialization."""

    def __init__(self, project_path: Path, dry_run: bool = False, force: bool = False):
        """
        Initialize the service.

        Args:
            project_path: Target project directory
            dry_run: If True, simulate operations without actual changes
            force: If True, overwrite existing files
        """
        self.project_path = project_path
        self.dry_run = dry_run
        self.force = force
        self.logger = logging.getLogger(__name__)

    def initialize(
        self,
        language: Language,
        assistants: List[Assistant],
        verbose: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> InitializationResult:
        """
        Initialize RAPID framework in the project.

        Args:
            language: Selected programming language
            assistants: List of AI assistants to configure
            verbose: Enable verbose output
            progress_callback: Optional callback for progress updates

        Returns:
            InitializationResult with operation details
        """
        # Create configuration
        config = InitializationConfig(
            language=language,
            assistants=assistants,
            project_path=self.project_path
        )

        # Validate environment
        template_manager = TemplateManager(
            project_root=self.project_path,
            dry_run=self.dry_run
        )

        is_valid, issues = template_manager.validate_environment()
        if not is_valid and not self.force:
            return InitializationResult(
                success=False,
                operations=[],
                errors=issues
            )

        # Perform initialization
        result = template_manager.initialize_project(
            language=language,
            assistants=assistants,
            progress_callback=progress_callback
        )

        if verbose and result.operations:
            self.logger.info(f"Completed {len(result.operations)} operations")

        return result

    def get_status(self) -> dict:
        """
        Get current initialization status.

        Returns:
            Dictionary with status information
        """
        rapid_dir = self.project_path / ".rapid"

        status = {
            "initialized": rapid_dir.exists(),
            "project_path": str(self.project_path),
            "rapid_dir": str(rapid_dir) if rapid_dir.exists() else None,
        }

        if rapid_dir.exists():
            # Count resources
            agents_dir = rapid_dir / "agents"
            commands_dir = rapid_dir / "commands"

            status["agent_count"] = (
                sum(1 for _ in agents_dir.rglob("*.md"))
                if agents_dir.exists() else 0
            )
            status["command_count"] = (
                sum(1 for _ in commands_dir.rglob("*.md"))
                if commands_dir.exists() else 0
            )

            # Check for assistant directories
            assistant_dirs = []
            for dir_name in ["claude", "copilot"]:
                if (rapid_dir / dir_name).exists():
                    assistant_dirs.append(dir_name)
            status["assistant_dirs"] = assistant_dirs

        return status