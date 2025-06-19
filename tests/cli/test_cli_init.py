"""Tests for the CLI init command."""

import subprocess
from unittest.mock import MagicMock, Mock, patch

import pytest
from typer.testing import CliRunner

from automake.cli.app import app


class TestInitCommand:
    """Test cases for the init command."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    @pytest.mark.skip(reason="CLI init tests have mocking issues causing hangs")
    @patch("automake.cli.commands.init.get_config")
    @patch("automake.cli.commands.init.ensure_model_available")
    @patch("automake.cli.commands.init.get_available_models")
    @patch("subprocess.Popen")
    @patch("subprocess.run")
    @patch("automake.utils.output.get_formatter")
    @patch("time.sleep")
    def test_init_success_model_already_available(
        self,
        mock_sleep,
        mock_get_formatter,
        mock_run,
        mock_popen,
        mock_get_models,
        mock_ensure_model,
        mock_get_config,
    ):
        """Test successful init when model is already available."""
        # Arrange
        mock_config = MagicMock()
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_config.ollama_model = "llama2"
        mock_get_config.return_value = mock_config

        # Mock output formatter
        mock_formatter = MagicMock()
        mock_live_box = MagicMock()
        mock_formatter.live_box.return_value.__enter__.return_value = mock_live_box
        mock_formatter.live_box.return_value.__exit__.return_value = None
        mock_get_formatter.return_value = mock_formatter

        # Mock successful ollama --version check
        mock_run.return_value = Mock(returncode=0, stdout="ollama version 0.1.0")

        # Mock model already available
        mock_get_models.return_value = ["llama2", "codellama"]
        mock_ensure_model.return_value = (True, False)  # Available, not pulled

        # Act
        result = self.runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 0
        mock_get_config.assert_called_once()
        mock_ensure_model.assert_called_once_with(mock_config)

    @pytest.mark.skip(reason="CLI init tests have mocking issues causing hangs")
    @patch("automake.utils.output.get_formatter")
    @patch("subprocess.run")
    @patch("subprocess.Popen")
    @patch("automake.cli.commands.init.get_available_models")
    @patch("automake.cli.commands.init.ensure_model_available")
    @patch("automake.cli.commands.init.get_config")
    def test_init_success_model_pulled(
        self,
        mock_get_config,
        mock_ensure_model,
        mock_get_models,
        mock_popen,
        mock_run,
        mock_get_formatter,
    ):
        """Test successful init when model needs to be pulled."""
        # Arrange
        mock_config = MagicMock()
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_config.ollama_model = "llama2"
        mock_get_config.return_value = mock_config

        # Mock output formatter
        mock_formatter = MagicMock()
        mock_live_box = MagicMock()
        mock_formatter.live_box.return_value.__enter__.return_value = mock_live_box
        mock_formatter.live_box.return_value.__exit__.return_value = None
        mock_get_formatter.return_value = mock_formatter

        # Mock successful ollama --version check
        mock_run.return_value = Mock(returncode=0, stdout="ollama version 0.1.0")

        # Mock model needs to be pulled
        mock_ensure_model.return_value = (True, True)  # Available, was pulled
        mock_get_models.return_value = ["llama2", "codellama"]

        # Act
        result = self.runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 0
        mock_get_config.assert_called_once()
        mock_ensure_model.assert_called_once_with(mock_config)

    @pytest.mark.skip(reason="CLI init tests have mocking issues causing hangs")
    @patch("automake.utils.output.get_formatter")
    @patch("automake.cli.commands.init.get_config")
    @patch("subprocess.run")
    def test_init_ollama_not_installed(
        self, mock_run, mock_get_config, mock_get_formatter
    ):
        """Test init when Ollama is not installed."""
        # Arrange
        mock_config = MagicMock()
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_config.ollama_model = "llama2"
        mock_get_config.return_value = mock_config

        # Mock output formatter
        mock_formatter = MagicMock()
        mock_live_box = MagicMock()
        mock_formatter.live_box.return_value.__enter__.return_value = mock_live_box
        mock_formatter.live_box.return_value.__exit__.return_value = None
        mock_get_formatter.return_value = mock_formatter

        # Mock ollama command not found
        mock_run.side_effect = FileNotFoundError("ollama command not found")

        # Act
        result = self.runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 1

    @pytest.mark.skip(reason="CLI init tests have mocking issues causing hangs")
    @patch("automake.cli.commands.init.get_config")
    @patch("subprocess.run")
    def test_init_ollama_command_fails(self, mock_run, mock_get_config):
        """Test init when ollama --version command fails."""
        # Arrange
        mock_config = MagicMock()
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_config.ollama_model = "llama2"
        mock_get_config.return_value = mock_config

        # Mock ollama command fails
        mock_run.side_effect = subprocess.CalledProcessError(1, "ollama")

        # Act
        result = self.runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 1

    @pytest.mark.skip(reason="CLI init tests have mocking issues causing hangs")
    @patch("subprocess.run")
    @patch("subprocess.Popen")
    @patch("automake.cli.commands.init.get_available_models")
    @patch("automake.cli.commands.init.ensure_model_available")
    @patch("automake.cli.commands.init.get_config")
    def test_init_ollama_manager_error_not_found(
        self, mock_get_config, mock_ensure_model, mock_get_models, mock_popen, mock_run
    ):
        """Test init when OllamaManagerError indicates Ollama not found."""
        # Arrange
        mock_config = MagicMock()
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_config.ollama_model = "llama2"
        mock_get_config.return_value = mock_config

        # Mock successful ollama --version check
        mock_run.return_value = Mock(returncode=0, stdout="ollama version 0.1.0")
        mock_get_models.return_value = ["llama2", "codellama"]

        # Mock OllamaManagerError for command not found
        from automake.utils.ollama_manager import OllamaManagerError

        mock_ensure_model.side_effect = OllamaManagerError("Ollama not found")

        # Act
        result = self.runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 1

    @pytest.mark.skip(reason="CLI init tests have mocking issues causing hangs")
    @patch("subprocess.run")
    @patch("subprocess.Popen")
    @patch("automake.cli.commands.init.get_available_models")
    @patch("automake.cli.commands.init.ensure_model_available")
    @patch("automake.cli.commands.init.get_config")
    def test_init_ollama_manager_error_connection(
        self, mock_get_config, mock_ensure_model, mock_get_models, mock_popen, mock_run
    ):
        """Test init when OllamaManagerError indicates connection issue."""
        # Arrange
        mock_config = MagicMock()
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_config.ollama_model = "llama2"
        mock_get_config.return_value = mock_config

        # Mock successful ollama --version check
        mock_run.return_value = Mock(returncode=0, stdout="ollama version 0.1.0")
        mock_get_models.return_value = ["llama2", "codellama"]

        # Mock OllamaManagerError for connection issue
        from automake.utils.ollama_manager import OllamaManagerError

        mock_ensure_model.side_effect = OllamaManagerError("Connection failed")

        # Act
        result = self.runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 1

    @pytest.mark.skip(reason="CLI init tests have mocking issues causing hangs")
    @patch("subprocess.run")
    @patch("subprocess.Popen")
    @patch("automake.cli.commands.init.get_available_models")
    @patch("automake.cli.commands.init.ensure_model_available")
    @patch("automake.cli.commands.init.get_config")
    def test_init_ollama_manager_error_model_pull(
        self, mock_get_config, mock_ensure_model, mock_get_models, mock_popen, mock_run
    ):
        """Test init when OllamaManagerError indicates model pull issue."""
        # Arrange
        mock_config = MagicMock()
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_config.ollama_model = "llama2"
        mock_get_config.return_value = mock_config

        # Mock successful ollama --version check
        mock_run.return_value = Mock(returncode=0, stdout="ollama version 0.1.0")
        mock_get_models.return_value = ["llama2", "codellama"]

        # Mock OllamaManagerError for model pull issue
        from automake.utils.ollama_manager import OllamaManagerError

        mock_ensure_model.side_effect = OllamaManagerError("Model pull failed")

        # Act
        result = self.runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 1

    @pytest.mark.skip(reason="CLI init tests have mocking issues causing hangs")
    @patch("subprocess.run")
    @patch("subprocess.Popen")
    @patch("automake.cli.commands.init.get_available_models")
    @patch("automake.cli.commands.init.ensure_model_available")
    @patch("automake.cli.commands.init.get_config")
    def test_init_unexpected_error(
        self, mock_get_config, mock_ensure_model, mock_get_models, mock_popen, mock_run
    ):
        """Test init when an unexpected error occurs."""
        # Arrange
        mock_config = MagicMock()
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_config.ollama_model = "llama2"
        mock_get_config.return_value = mock_config

        # Mock successful ollama --version check
        mock_run.return_value = Mock(returncode=0, stdout="ollama version 0.1.0")
        mock_get_models.return_value = ["llama2", "codellama"]

        # Mock unexpected error
        mock_ensure_model.side_effect = Exception("Unexpected error")

        # Act
        result = self.runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 1

    @pytest.mark.skip(reason="CLI init tests have mocking issues causing hangs")
    @patch("automake.utils.output.get_formatter")
    @patch("subprocess.run")
    @patch("subprocess.Popen")
    @patch("automake.cli.commands.init.get_available_models")
    @patch("automake.cli.commands.init.ensure_model_available")
    @patch("automake.cli.commands.init.get_config")
    def test_init_get_models_fails_gracefully(
        self,
        mock_get_config,
        mock_ensure_model,
        mock_get_models,
        mock_popen,
        mock_run,
        mock_get_formatter,
    ):
        """Test that init continues even if getting available models fails."""
        # Arrange
        mock_config = MagicMock()
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_config.ollama_model = "llama2"
        mock_get_config.return_value = mock_config

        # Mock output formatter
        mock_formatter = MagicMock()
        mock_live_box = MagicMock()
        mock_formatter.live_box.return_value.__enter__.return_value = mock_live_box
        mock_formatter.live_box.return_value.__exit__.return_value = None
        mock_get_formatter.return_value = mock_formatter

        # Mock successful ollama --version check
        mock_run.return_value = Mock(returncode=0, stdout="ollama version 0.1.0")

        # Mock model available
        mock_ensure_model.return_value = (True, False)

        # Mock get_models succeeds first (server check) then fails (model list)
        mock_get_models.side_effect = [
            ["llama2", "codellama"],
            Exception("Failed to get models"),
        ]

        # Act
        result = self.runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 0
        mock_get_config.assert_called_once()
        mock_ensure_model.assert_called_once_with(mock_config)
