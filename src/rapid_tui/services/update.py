"""Update service for RAPID framework synchronization."""

import shutil
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.table import Table

from rapid_tui.models import Assistant, FileOperation, UpdateResult
from rapid_tui.config import ASSISTANT_CONFIGS


class UpdateService:
    """Service for handling file synchronization operations."""

    def __init__(
        self, project_root: Path, dry_run: bool = False, verbose: bool = False
    ):
        self.project_root = project_root
        self.dry_run = dry_run
        self.verbose = verbose
        self.console = Console()

    def sync_all_agents(self, force: bool = False) -> UpdateResult:
        """Sync files to all configured assistants."""
        all_operations = []
        all_errors = []
        total_copied = 0
        total_skipped = 0

        # Skip RAPID_ONLY as it's the source, not a target
        agents_to_sync = [
            assistant
            for assistant in ASSISTANT_CONFIGS.keys()
            if assistant != Assistant.RAPID_ONLY
        ]

        for assistant in agents_to_sync:
            if self.verbose:
                self.console.print(f"Syncing to {assistant.display_name}...")

            result = self.sync_agent(assistant, force)
            all_operations.extend(result.operations)
            all_errors.extend(result.errors)
            total_copied += result.files_copied
            total_skipped += result.files_skipped

        return UpdateResult(
            success=len(all_errors) == 0,
            operations=all_operations,
            files_copied=total_copied,
            files_skipped=total_skipped,
            errors=all_errors,
        )

    def sync_agent(self, assistant: Assistant, force: bool = False) -> UpdateResult:
        """Sync files to specific assistant."""
        if assistant == Assistant.RAPID_ONLY:
            return UpdateResult(
                success=False,
                operations=[],
                errors=["Cannot sync to .rapid directory - it's the source"],
            )

        rapid_dir = self.project_root / ".rapid"
        if not rapid_dir.exists():
            return UpdateResult(
                success=False,
                operations=[],
                errors=[".rapid directory not found. Run 'rapid init' first."],
            )

        config = ASSISTANT_CONFIGS[assistant]
        operations = []
        errors = []

        # Sync agents directory if applicable
        if config.copy_agents and config.agents_path:
            agents_ops, agents_errors = self._sync_directory_structure(
                source_dir=rapid_dir / "agents",
                target_dir=self.project_root / config.base_dir / config.agents_path,
                force=force,
            )
            operations.extend(agents_ops)
            errors.extend(agents_errors)

        # Sync commands/prompts directory
        if config.copy_commands:
            # For Claude, sync to commands; for Copilot, sync prompts to prompts
            source_subdir = (
                "prompts" if assistant == Assistant.GITHUB_COPILOT else "commands"
            )
            commands_ops, commands_errors = self._sync_directory_structure(
                source_dir=rapid_dir / source_subdir,
                target_dir=self.project_root / config.base_dir / config.commands_path,
                force=force,
            )
            operations.extend(commands_ops)
            errors.extend(commands_errors)

        files_copied = len(
            [op for op in operations if op.operation == "copy" and op.success]
        )
        files_skipped = len([op for op in operations if op.operation == "skip"])

        return UpdateResult(
            success=len(errors) == 0,
            operations=operations,
            files_copied=files_copied,
            files_skipped=files_skipped,
            errors=errors,
        )

    def _sync_directory_structure(
        self, source_dir: Path, target_dir: Path, force: bool
    ) -> tuple[List[FileOperation], List[str]]:
        """Recursively sync directory structure preserving nested paths."""
        operations = []
        errors = []

        if not source_dir.exists():
            if self.verbose:
                self.console.print(f"Source directory not found: {source_dir}")
            return operations, errors

        # Ensure target directory exists
        if not self.dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)

        # Walk through all files in source directory
        for source_file in source_dir.rglob("*"):
            if source_file.is_file():
                # Calculate relative path from source_dir to maintain structure
                relative_path = source_file.relative_to(source_dir)
                target_file = target_dir / relative_path

                operation = self._sync_file(source_file, target_file, force)
                operations.append(operation)

                if not operation.success:
                    errors.append(
                        f"Failed to sync {operation.relative_source}: {operation.reason}"
                    )

        return operations, errors

    def _sync_file(self, source: Path, target: Path, force: bool) -> FileOperation:
        """Sync a single file with timestamp comparison."""
        try:
            # Check if update is needed
            should_copy = (
                force or not target.exists() or self._compare_files(source, target)
            )

            if not should_copy:
                return FileOperation(
                    source=source,
                    target=target,
                    operation="skip",
                    reason="Target file is newer or same age as source",
                    success=True,
                )

            # Ensure target directory exists
            if not self.dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

            if self.verbose:
                self.console.print(f"  ✓ Copied {source.name}")

            return FileOperation(
                source=source,
                target=target,
                operation="copy",
                reason="File copied successfully",
                success=True,
            )

        except Exception as e:
            return FileOperation(
                source=source,
                target=target,
                operation="error",
                reason=str(e),
                success=False,
            )

    def _compare_files(self, source: Path, target: Path) -> bool:
        """Compare file timestamps to determine if update is needed."""
        if not target.exists():
            return True

        source_mtime = source.stat().st_mtime
        target_mtime = target.stat().st_mtime

        # Return True if source is newer than target
        return source_mtime > target_mtime

    def consolidate_all_agents(self, force: bool = False) -> UpdateResult:
        """Consolidate files from all assistant directories back to .rapid/."""
        all_operations = []
        all_errors = []
        total_copied = 0
        total_skipped = 0

        rapid_dir = self.project_root / ".rapid"
        if not rapid_dir.exists():
            return UpdateResult(
                success=False,
                operations=[],
                errors=[".rapid directory not found. Run 'rapid init' first."],
            )

        # Skip RAPID_ONLY as it's the target, not a source
        agents_to_consolidate = [
            assistant
            for assistant in ASSISTANT_CONFIGS.keys()
            if assistant != Assistant.RAPID_ONLY
        ]

        for assistant in agents_to_consolidate:
            if self.verbose:
                self.console.print(f"Consolidating from {assistant.display_name}...")

            result = self.consolidate_agent(assistant, force)
            all_operations.extend(result.operations)
            all_errors.extend(result.errors)
            total_copied += result.files_copied
            total_skipped += result.files_skipped

        return UpdateResult(
            success=len(all_errors) == 0,
            operations=all_operations,
            files_copied=total_copied,
            files_skipped=total_skipped,
            errors=all_errors,
        )

    def consolidate_agent(
        self, assistant: Assistant, force: bool = False
    ) -> UpdateResult:
        """Consolidate files from specific assistant back to .rapid/."""
        if assistant == Assistant.RAPID_ONLY:
            return UpdateResult(
                success=False,
                operations=[],
                errors=["Cannot consolidate from .rapid directory - it's the target"],
            )

        rapid_dir = self.project_root / ".rapid"
        if not rapid_dir.exists():
            return UpdateResult(
                success=False,
                operations=[],
                errors=[".rapid directory not found. Run 'rapid init' first."],
            )

        config = ASSISTANT_CONFIGS[assistant]
        operations = []
        errors = []

        # Consolidate agents directory if applicable
        if config.copy_agents and config.agents_path:
            assistant_agents_dir = (
                self.project_root / config.base_dir / config.agents_path
            )
            if assistant_agents_dir.exists():
                agents_ops, agents_errors = self._sync_directory_structure(
                    source_dir=assistant_agents_dir,
                    target_dir=rapid_dir / "agents",
                    force=force,
                )
                operations.extend(agents_ops)
                errors.extend(agents_errors)

        # Consolidate commands/prompts directory
        if config.copy_commands:
            assistant_commands_dir = (
                self.project_root / config.base_dir / config.commands_path
            )
            if assistant_commands_dir.exists():
                # For Claude, consolidate from commands; for Copilot, consolidate from prompts
                target_subdir = (
                    "prompts" if assistant == Assistant.GITHUB_COPILOT else "commands"
                )
                commands_ops, commands_errors = self._sync_directory_structure(
                    source_dir=assistant_commands_dir,
                    target_dir=rapid_dir / target_subdir,
                    force=force,
                )
                operations.extend(commands_ops)
                errors.extend(commands_errors)

        files_copied = len(
            [op for op in operations if op.operation == "copy" and op.success]
        )
        files_skipped = len([op for op in operations if op.operation == "skip"])

        return UpdateResult(
            success=len(errors) == 0,
            operations=operations,
            files_copied=files_copied,
            files_skipped=files_skipped,
            errors=errors,
        )

    def display_results(self, result: UpdateResult, reverse: bool = False) -> None:
        """Display update results in a formatted table."""
        operation_name = "Consolidation" if reverse else "Update"

        if result.success:
            self.console.print(
                f"\n[green]✓ {operation_name} completed successfully![/green]"
            )
        else:
            self.console.print(f"\n[red]✗ {operation_name} completed with errors[/red]")

        # Summary stats
        self.console.print(f"  Files copied: {result.files_copied}")
        self.console.print(f"  Files skipped: {result.files_skipped}")

        if result.errors:
            self.console.print(f"\n[red]Errors ({len(result.errors)}):[/red]")
            for error in result.errors:
                self.console.print(f"  [red]• {error}[/red]")

        # Detailed operations in verbose mode
        if self.verbose and result.operations:
            self.console.print(f"\n[bold]{operation_name} Details:[/bold]")

            table = Table()
            table.add_column("Operation", style="cyan")
            table.add_column("Source", style="dim")
            table.add_column("Target", style="green")
            table.add_column("Status", style="yellow")

            for op in result.operations:
                status_color = "green" if op.success else "red"
                status_symbol = "✓" if op.success else "✗"
                status = (
                    f"[{status_color}]{status_symbol}[/{status_color}] {op.operation}"
                )

                table.add_row(status, op.relative_source, op.relative_target, op.reason)

            self.console.print(table)
