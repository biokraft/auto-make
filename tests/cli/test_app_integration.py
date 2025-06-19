"""Tests for CLI app integration.

This module tests the integration of commands with the main CLI application.
"""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from automake.cli.app import app


class TestCLIAppIntegration:
    """Test cases for CLI app integration."""

    def test_config_model_command_registered(self):
        """Test that config model command is properly registered."""
        runner = CliRunner()

        # Test that the command is available in help
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "model" in result.stdout

    @patch("automake.cli.commands.config.ModelSelector")
    @patch("automake.cli.commands.config.get_config")
    @patch("automake.cli.commands.config.get_formatter")
    def test_config_model_command_execution(
        self, mock_get_formatter, mock_get_config, mock_model_selector_class
    ):
        """Test that config model command executes correctly through CLI."""
        # Setup mocks
        mock_output = Mock()
        live_box = Mock()
        live_box.update = Mock()
        live_box.__enter__ = Mock(return_value=live_box)
        live_box.__exit__ = Mock(return_value=None)
        mock_output.live_box = Mock(return_value=live_box)
        mock_get_formatter.return_value = mock_output

        mock_config = Mock()
        mock_config.get.return_value = "llama2:7b"
        mock_get_config.return_value = mock_config

        mock_selector = Mock()
        mock_selector.select_model.return_value = "mistral:7b"
        mock_model_selector_class.return_value = mock_selector

        runner = CliRunner()
        result = runner.invoke(app, ["config", "model"])

        assert result.exit_code == 0
        mock_model_selector_class.assert_called_once()
        mock_selector.select_model.assert_called_once()
        mock_config.set.assert_called_once_with("ollama", "model", "mistral:7b")

    def test_config_help_shows_model_command(self):
        """Test that config help shows the model command."""
        runner = CliRunner()
        result = runner.invoke(app, ["config", "--help"])

        assert result.exit_code == 0
        assert "model" in result.stdout
        assert "Interactive model configuration" in result.stdout

    @patch("automake.cli.commands.config.ModelSelector")
    @patch("automake.cli.commands.config.get_config")
    @patch("automake.cli.commands.config.get_formatter")
    def test_complete_model_configuration_flow(
        self, mock_get_formatter, mock_get_config, mock_selector_class
    ):
        """Test the complete model configuration flow."""
        # Setup mocks
        mock_output = Mock()
        live_box = Mock()
        live_box.update = Mock()
        live_box.__enter__ = Mock(return_value=live_box)
        live_box.__exit__ = Mock(return_value=None)
        mock_output.live_box = Mock(return_value=live_box)
        mock_get_formatter.return_value = mock_output

        mock_config = Mock()
        mock_config.get.return_value = "current_model:7b"
        mock_get_config.return_value = mock_config

        mock_selector = Mock()
        mock_selector_class.return_value = mock_selector
        mock_selector.select_model.return_value = "new_model:3b"

        # Test successful configuration
        runner = CliRunner()
        result = runner.invoke(app, ["config", "model"])

        # Verify
        assert result.exit_code == 0
        mock_selector_class.assert_called_once_with(mock_config)
        mock_selector.select_model.assert_called_once()
        mock_config.set.assert_called_once_with("ollama", "model", "new_model:3b")

    @patch("automake.cli.commands.config.ModelSelector")
    @patch("automake.cli.commands.config.get_config")
    @patch("automake.cli.commands.config.get_formatter")
    def test_model_configuration_with_ollama_not_running(
        self, mock_get_formatter, mock_get_config, mock_selector_class
    ):
        """Test model configuration when Ollama is not running."""
        from automake.utils.model_selector import ModelSelectorError

        # Setup mocks
        mock_output = Mock()
        live_box = Mock()
        live_box.update = Mock()
        live_box.__enter__ = Mock(return_value=live_box)
        live_box.__exit__ = Mock(return_value=None)
        mock_output.live_box = Mock(return_value=live_box)
        mock_get_formatter.return_value = mock_output

        mock_config = Mock()
        mock_config.get.return_value = "current_model:7b"
        mock_get_config.return_value = mock_config

        mock_selector = Mock()
        mock_selector_class.return_value = mock_selector
        mock_selector.select_model.side_effect = ModelSelectorError(
            "Failed to retrieve local models: Connection refused"
        )

        # Test error handling
        runner = CliRunner()
        result = runner.invoke(app, ["config", "model"])

        # Verify error handling
        assert result.exit_code == 1

    @patch("automake.cli.commands.config.ModelSelector")
    @patch("automake.cli.commands.config.get_config")
    @patch("automake.cli.commands.config.get_formatter")
    def test_model_configuration_user_cancellation(
        self, mock_get_formatter, mock_get_config, mock_selector_class
    ):
        """Test model configuration when user cancels selection."""
        # Setup mocks
        mock_output = Mock()
        live_box = Mock()
        live_box.update = Mock()
        live_box.__enter__ = Mock(return_value=live_box)
        live_box.__exit__ = Mock(return_value=None)
        mock_output.live_box = Mock(return_value=live_box)
        mock_get_formatter.return_value = mock_output

        mock_config = Mock()
        mock_config.get.return_value = "current_model:7b"
        mock_get_config.return_value = mock_config

        mock_selector = Mock()
        mock_selector_class.return_value = mock_selector
        mock_selector.select_model.return_value = None  # User cancelled

        # Test cancellation handling
        runner = CliRunner()
        result = runner.invoke(app, ["config", "model"])

        # Verify cancellation handling
        assert result.exit_code == 0
