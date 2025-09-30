"""Data models for RAPID TUI application."""

from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class Language(str, Enum):
    """Supported programming languages/frameworks."""

    ANGULAR = "angular"
    PYTHON = "python"
    GENERIC = "generic"
    SEE_SHARP = "see-sharp"

    @property
    def display_name(self) -> str:
        """Human-readable name for UI display."""
        return {
            self.ANGULAR: "Angular/TypeScript",
            self.PYTHON: "Python",
            self.GENERIC: "Generic/Other",
            self.SEE_SHARP: "C# (.NET)",
        }[self]

    @property
    def has_templates(self) -> bool:
        """Check if this language has available templates."""
        # See-Sharp currently has no templates
        return self != self.SEE_SHARP


class Assistant(str, Enum):
    """Supported AI assistants."""

    CLAUDE_CODE = "claude_code"
    GITHUB_COPILOT = "github_copilot"
    RAPID_ONLY = "rapid_only"

    @property
    def display_name(self) -> str:
        """Human-readable name for UI display."""
        return {
            self.CLAUDE_CODE: "Claude Code",
            self.GITHUB_COPILOT: "GitHub Copilot",
            self.RAPID_ONLY: ".rapid only",
        }[self]


class AssistantConfig(BaseModel):
    """Configuration for each assistant's file structure."""

    name: str
    base_dir: str
    agents_path: Optional[str] = None
    commands_path: str
    copy_agents: bool = True
    copy_commands: bool = True

    def get_agent_dir(self, project_root: Path) -> Optional[Path]:
        """Get full path to agent directory."""
        if not self.agents_path:
            return None
        return project_root / self.base_dir / self.agents_path

    def get_commands_dir(self, project_root: Path) -> Path:
        """Get full path to commands directory."""
        return project_root / self.base_dir / self.commands_path


class InitializationConfig(BaseModel):
    """User selections for initialization."""

    language: Optional[Language] = None
    assistants: List[Assistant] = Field(default_factory=list)
    project_path: Path = Field(default_factory=Path.cwd)

    @field_validator("assistants")
    @classmethod
    def validate_assistants(cls, v: List[Assistant]) -> List[Assistant]:
        """Ensure at least one assistant is selected."""
        if not v:
            raise ValueError("At least one assistant must be selected")
        # Always include RAPID_ONLY if not present
        if Assistant.RAPID_ONLY not in v:
            v.append(Assistant.RAPID_ONLY)
        return v

    @field_validator("project_path")
    @classmethod
    def validate_project_path(cls, v: Path) -> Path:
        """Validate project path exists and is a directory."""
        if not v.exists():
            raise ValueError(f"Project path does not exist: {v}")
        if not v.is_dir():
            raise ValueError(f"Project path is not a directory: {v}")
        return v


class CopyOperation(BaseModel):
    """Record of a file copy operation."""

    source: Path
    destination: Path
    operation_type: str  # "agent" or "command"
    assistant: Optional[Assistant] = None
    success: bool = True
    error_message: Optional[str] = None

    @property
    def relative_destination(self) -> str:
        """Get destination relative to project root."""
        try:
            cwd = Path.cwd()
            return str(self.destination.relative_to(cwd))
        except ValueError:
            return str(self.destination)


class InitializationResult(BaseModel):
    """Result of the initialization process."""

    success: bool
    operations: List[CopyOperation]
    total_files_copied: int = 0
    total_directories_created: int = 0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    @property
    def summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        return {
            "success": self.success,
            "files_copied": self.total_files_copied,
            "directories_created": self.total_directories_created,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "operations_by_type": {
                "agent": len(
                    [op for op in self.operations if op.operation_type == "agent"]
                ),
                "command": len(
                    [op for op in self.operations if op.operation_type == "command"]
                ),
            },
            "operations_by_assistant": {
                assistant.value: len(
                    [op for op in self.operations if op.assistant == assistant]
                )
                for assistant in Assistant
            },
        }


class FileOperation(BaseModel):
    """Record of a file synchronization operation."""

    source: Path
    target: Path
    operation: str  # "copy", "skip", "error"
    reason: str
    success: bool = True

    @property
    def relative_target(self) -> str:
        """Get target path relative to project root."""
        try:
            cwd = Path.cwd()
            return str(self.target.relative_to(cwd))
        except ValueError:
            return str(self.target)

    @property
    def relative_source(self) -> str:
        """Get source path relative to project root."""
        try:
            cwd = Path.cwd()
            return str(self.source.relative_to(cwd))
        except ValueError:
            return str(self.source)


class UpdateResult(BaseModel):
    """Result of update synchronization."""

    success: bool
    operations: List[FileOperation]
    files_copied: int = 0
    files_skipped: int = 0
    errors: List[str] = Field(default_factory=list)

    @property
    def summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        return {
            "success": self.success,
            "files_copied": self.files_copied,
            "files_skipped": self.files_skipped,
            "total_operations": len(self.operations),
            "errors_count": len(self.errors),
        }
