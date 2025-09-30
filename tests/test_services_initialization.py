"""Strategic tests for initialization service.

This module focuses on core business logic and integration with TemplateManager.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from rapid_tui.services.initialization import InitializationService
from rapid_tui.models import Language, Assistant, InitializationResult
from tests.test_helpers import MockTemplateManager, create_mock_initialization_result


class TestInitializationService:
    """Test InitializationService business logic."""

    def test_initialization_service_basic_setup(self, tmp_path):
        """Test basic service initialization."""
        service = InitializationService(tmp_path)

        assert service.project_path == tmp_path
        assert service.dry_run is False
        assert service.force is False

    def test_initialization_service_with_options(self, tmp_path):
        """Test service initialization with dry_run and force options."""
        service = InitializationService(tmp_path, dry_run=True, force=True)

        assert service.dry_run is True
        assert service.force is True


class TestInitializationServiceIntegration:
    """Test service integration with TemplateManager."""

    def test_initialize_environment_validation_failure(self, tmp_path, mocker):
        """Test initialization handles environment validation failures."""
        mock_template_manager_class = mocker.patch(
            "rapid_tui.services.initialization.TemplateManager"
        )
        mock_template_manager = MockTemplateManager(success=False)
        mock_template_manager.validate_environment = Mock(
            return_value=(False, ["Test error"])
        )
        mock_template_manager_class.return_value = mock_template_manager

        service = InitializationService(tmp_path, force=False)
        result = service.initialize(
            language=Language.PYTHON, assistants=[Assistant.CLAUDE_CODE]
        )

        # Should fail without calling initialize_project when validation fails
        assert result.success is False
        assert "Test error" in result.errors
        assert mock_template_manager.call_count == 0  # Should not proceed


class TestInitializationServiceStatus:
    """Test status reporting functionality."""

    def test_get_status_not_initialized(self, tmp_path):
        """Test status when .rapid directory doesn't exist."""
        service = InitializationService(tmp_path)
        status = service.get_status()

        assert status["initialized"] is False
        assert status["project_path"] == str(tmp_path)
        assert status["rapid_dir"] is None

    def test_get_status_initialized_basic(self, tmp_path):
        """Test status when .rapid directory exists."""
        rapid_dir = tmp_path / ".rapid"
        rapid_dir.mkdir()

        service = InitializationService(tmp_path)
        status = service.get_status()

        assert status["initialized"] is True
        assert status["project_path"] == str(tmp_path)
        assert status["rapid_dir"] == str(rapid_dir)
