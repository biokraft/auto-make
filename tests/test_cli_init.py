"""Tests for the CLI init command."""

from unittest.mock import Mock, patch

import pytest
import typer

from automake.cli.main import init
from automake.utils.ollama_manager import OllamaManagerError


class TestInitCommand:
    """Test cases for the init command."""

    @patch("automake.cli.main.get_available_models")
    @patch("automake.cli.main.ensure_model_available")
    @patch("automake.cli.main.get_config")
    @patch("subprocess.run")
    def test_init_success_model_already_available(
        self, mock_subprocess, mock_get_config, mock_ensure_model, mock_get_models
    ):
        """Test successful init when model is already available."""
        # Arrange
        mock_config = Mock()
        mock_config.ollama_model = "qwen3:0.6b"
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_get_config.return_value = mock_config

        # Mock successful ollama --version check
        mock_subprocess.return_value = Mock(returncode=0)

        # Mock model already available
        mock_ensure_model.return_value = (True, False)  # Available, not pulled
        mock_get_models.return_value = ["qwen3:0.6b", "llama2:7b"]

        # Act & Assert - should not raise
        init()

        mock_ensure_model.assert_called_once_with(mock_config)

    @patch("automake.cli.main.get_available_models")
    @patch("automake.cli.main.ensure_model_available")
    @patch("automake.cli.main.get_config")
    @patch("subprocess.run")
    def test_init_success_model_pulled(
        self, mock_subprocess, mock_get_config, mock_ensure_model, mock_get_models
    ):
        """Test successful init when model needs to be pulled."""
        # Arrange
        mock_config = Mock()
        mock_config.ollama_model = "qwen3:0.6b"
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_get_config.return_value = mock_config

        # Mock successful ollama --version check
        mock_subprocess.return_value = Mock(returncode=0)

        # Mock model needs to be pulled
        mock_ensure_model.return_value = (True, True)  # Available, was pulled
        mock_get_models.return_value = ["qwen3:0.6b"]

        # Act & Assert - should not raise
        init()

        mock_ensure_model.assert_called_once_with(mock_config)

    @patch("automake.cli.main.get_config")
    @patch("subprocess.run")
    def test_init_ollama_not_installed(self, mock_subprocess, mock_get_config):
        """Test init when Ollama is not installed."""
        # Arrange
        mock_config = Mock()
        mock_config.ollama_model = "qwen3:0.6b"
        mock_get_config.return_value = mock_config

        # Mock ollama command not found
        mock_subprocess.side_effect = FileNotFoundError("ollama command not found")

        # Act & Assert
        with pytest.raises(typer.Exit) as exc_info:
            init()

        assert exc_info.value.exit_code == 1

    @patch("automake.cli.main.get_config")
    @patch("subprocess.run")
    def test_init_ollama_command_fails(self, mock_subprocess, mock_get_config):
        """Test init when ollama --version command fails."""
        # Arrange
        mock_config = Mock()
        mock_config.ollama_model = "qwen3:0.6b"
        mock_get_config.return_value = mock_config

        # Mock ollama command returns non-zero exit code
        mock_subprocess.return_value = Mock(returncode=1)

        # Act & Assert
        with pytest.raises(typer.Exit) as exc_info:
            init()

        assert exc_info.value.exit_code == 1

    @patch("automake.cli.main.ensure_model_available")
    @patch("automake.cli.main.get_config")
    @patch("subprocess.run")
    def test_init_ollama_manager_error_not_found(
        self, mock_subprocess, mock_get_config, mock_ensure_model
    ):
        """Test init when OllamaManagerError indicates Ollama not found."""
        # Arrange
        mock_config = Mock()
        mock_config.ollama_model = "qwen3:0.6b"
        mock_get_config.return_value = mock_config

        # Mock successful ollama --version check
        mock_subprocess.return_value = Mock(returncode=0)

        # Mock OllamaManagerError for command not found
        mock_ensure_model.side_effect = OllamaManagerError("Ollama command not found")

        # Act & Assert
        with pytest.raises(typer.Exit) as exc_info:
            init()

        assert exc_info.value.exit_code == 1

    @patch("automake.cli.main.ensure_model_available")
    @patch("automake.cli.main.get_config")
    @patch("subprocess.run")
    def test_init_ollama_manager_error_connection(
        self, mock_subprocess, mock_get_config, mock_ensure_model
    ):
        """Test init when OllamaManagerError indicates connection issue."""
        # Arrange
        mock_config = Mock()
        mock_config.ollama_model = "qwen3:0.6b"
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_get_config.return_value = mock_config

        # Mock successful ollama --version check
        mock_subprocess.return_value = Mock(returncode=0)

        # Mock OllamaManagerError for connection issue
        mock_ensure_model.side_effect = OllamaManagerError("Connection refused")

        # Act & Assert
        with pytest.raises(typer.Exit) as exc_info:
            init()

        assert exc_info.value.exit_code == 1

    @patch("automake.cli.main.ensure_model_available")
    @patch("automake.cli.main.get_config")
    @patch("subprocess.run")
    def test_init_ollama_manager_error_model_pull(
        self, mock_subprocess, mock_get_config, mock_ensure_model
    ):
        """Test init when OllamaManagerError indicates model pull issue."""
        # Arrange
        mock_config = Mock()
        mock_config.ollama_model = "invalid-model"
        mock_get_config.return_value = mock_config

        # Mock successful ollama --version check
        mock_subprocess.return_value = Mock(returncode=0)

        # Mock OllamaManagerError for model pull issue
        mock_ensure_model.side_effect = OllamaManagerError(
            "Failed to pull model 'invalid-model'"
        )

        # Act & Assert
        with pytest.raises(typer.Exit) as exc_info:
            init()

        assert exc_info.value.exit_code == 1

    @patch("automake.cli.main.ensure_model_available")
    @patch("automake.cli.main.get_config")
    @patch("subprocess.run")
    def test_init_unexpected_error(
        self, mock_subprocess, mock_get_config, mock_ensure_model
    ):
        """Test init when an unexpected error occurs."""
        # Arrange
        mock_config = Mock()
        mock_config.ollama_model = "qwen3:0.6b"
        mock_get_config.return_value = mock_config

        # Mock successful ollama --version check
        mock_subprocess.return_value = Mock(returncode=0)

        # Mock unexpected error
        mock_ensure_model.side_effect = Exception("Unexpected error")

        # Act & Assert
        with pytest.raises(typer.Exit) as exc_info:
            init()

        assert exc_info.value.exit_code == 1

    @patch("automake.cli.main.get_available_models")
    @patch("automake.cli.main.ensure_model_available")
    @patch("automake.cli.main.get_config")
    @patch("subprocess.run")
    def test_init_get_models_fails_gracefully(
        self, mock_subprocess, mock_get_config, mock_ensure_model, mock_get_models
    ):
        """Test that init continues even if getting available models fails."""
        # Arrange
        mock_config = Mock()
        mock_config.ollama_model = "qwen3:0.6b"
        mock_get_config.return_value = mock_config

        # Mock successful ollama --version check
        mock_subprocess.return_value = Mock(returncode=0)

        # Mock model available
        mock_ensure_model.return_value = (True, False)

        # Mock get_models fails
        mock_get_models.side_effect = OllamaManagerError("Failed to get models")

        # Act & Assert - should not raise, should continue gracefully
        init()

        mock_ensure_model.assert_called_once_with(mock_config)
