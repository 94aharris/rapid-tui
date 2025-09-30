"""Tests for file operations and TemplateManager."""

import tempfile
from pathlib import Path

from rapid_tui.utils.file_operations import TemplateManager


class TestTemplateManagerFreshDirectory:
    """Test TemplateManager behavior in fresh directories."""

    def test_template_manager_handles_fresh_directory(self):
        """Test that TemplateManager can be instantiated in fresh directory without .rapid folder.

        This is a regression test for the bug where logger setup failed when the .rapid
        directory didn't exist during TemplateManager initialization.
        """
        import logging

        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Verify .rapid doesn't exist initially
            assert not (project_path / ".rapid").exists()

            # Clear any existing logger handlers to ensure fresh setup
            logger = logging.getLogger("rapid_tui.utils.file_operations")
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

            # This should not raise FileNotFoundError
            manager = TemplateManager(project_path)

            # Verify .rapid directory was created for logging
            assert (project_path / ".rapid").exists()
            assert (project_path / ".rapid" / "initialization.log").exists()

            # Verify manager is properly initialized
            assert manager.project_root == project_path
            assert manager.logger is not None

    def test_template_manager_dry_run_fresh_directory(self):
        """Test that TemplateManager dry run mode works in fresh directory."""
        import logging

        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Verify .rapid doesn't exist initially
            assert not (project_path / ".rapid").exists()

            # Clear any existing logger handlers to ensure fresh setup
            logger = logging.getLogger("rapid_tui.utils.file_operations")
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

            # Even in dry run mode, should create .rapid for logging
            manager = TemplateManager(project_path, dry_run=True)

            # Verify .rapid directory was created for logging even in dry run
            # (logging needs to work regardless of dry_run mode)
            assert (project_path / ".rapid").exists()
            assert (project_path / ".rapid" / "initialization.log").exists()
            assert manager.dry_run is True
