"""Tests for CLI config commands.

This module contains tests for the configuration-related CLI commands.
"""

from unittest.mock import Mock, patch

import pytest
import typer

from automake.cli.commands.config import (
    config_model_command,
    config_set_command,
    config_show_command,
)


class TestConfigCommands:
    """Test cases for configuration commands."""

    @pytest.fixture
    def mock_output(self):
        """Create a mock output formatter."""
        output = Mock()
        live_box = Mock()
        live_box.update = Mock()
        live_box.__enter__ = Mock(return_value=live_box)
        live_box.__exit__ = Mock(return_value=None)
        output.live_box = Mock(return_value=live_box)
        return output

    @pytest.fixture
    def mock_config(self):
        """Create a mock config instance."""
        config = Mock()
        config.get_all_sections.return_value = {
            "ollama": {"base_url": "http://localhost:11434", "model": "llama2:7b"}
        }
        return config

    @patch("automake.cli.commands.config.get_config")
    @patch("automake.cli.commands.config.get_formatter")
    def test_show_config_command(
        self, mock_get_formatter, mock_get_config, mock_output, mock_config
    ):
        """Test show config command."""
        mock_get_config.return_value = mock_config
        mock_get_formatter.return_value = mock_output

        config_show_command()

        mock_get_config.assert_called_once()
        mock_output.live_box.assert_called()

    @patch("automake.cli.commands.config.get_config")
    @patch("automake.cli.commands.config.get_formatter")
    def test_set_config_command(
        self, mock_get_formatter, mock_get_config, mock_output, mock_config
    ):
        """Test set config command."""
        mock_get_config.return_value = mock_config
        mock_get_formatter.return_value = mock_output

        config_set_command("ollama.model", "llama2:13b")

        mock_config.set.assert_called_once_with("ollama", "model", "llama2:13b")
        mock_output.live_box.assert_called()

    # New tests for model configuration command
    @patch("automake.cli.commands.config.ModelSelector")
    @patch("automake.cli.commands.config.get_config")
    @patch("automake.cli.commands.config.get_formatter")
    def test_config_model_command_success(
        self,
        mock_get_formatter,
        mock_get_config,
        mock_model_selector_class,
        mock_output,
    ):
        """Test successful model configuration."""
        # Setup mocks
        mock_config = Mock()
        mock_config.get.return_value = "llama2:7b"  # Current model
        mock_get_config.return_value = mock_config
        mock_get_formatter.return_value = mock_output

        mock_selector = Mock()
        mock_selector.select_model.return_value = "mistral:7b"
        mock_model_selector_class.return_value = mock_selector

        config_model_command()

        # Verify interactions
        mock_model_selector_class.assert_called_once_with(mock_config)
        mock_selector.select_model.assert_called_once()
        mock_config.set.assert_called_once_with("ollama", "model", "mistral:7b")
        mock_output.live_box.assert_called()

    @patch("automake.cli.commands.config.ModelSelector")
    @patch("automake.cli.commands.config.get_config")
    @patch("automake.cli.commands.config.get_formatter")
    def test_config_model_command_same_model_selected(
        self,
        mock_get_formatter,
        mock_get_config,
        mock_model_selector_class,
        mock_output,
    ):
        """Test when user selects the same model that's already configured."""
        # Setup mocks
        mock_config = Mock()
        mock_config.get.return_value = "llama2:7b"
        mock_get_config.return_value = mock_config
        mock_get_formatter.return_value = mock_output

        mock_selector = Mock()
        mock_selector.select_model.return_value = "llama2:7b"
        mock_model_selector_class.return_value = mock_selector

        config_model_command()

        # Verify config was not updated when same model selected
        mock_config.set.assert_not_called()
        mock_output.live_box.assert_called()

    @patch("automake.cli.commands.config.ModelSelector")
    @patch("automake.cli.commands.config.get_config")
    @patch("automake.cli.commands.config.get_formatter")
    def test_config_model_command_selection_cancelled(
        self,
        mock_get_formatter,
        mock_get_config,
        mock_model_selector_class,
        mock_output,
    ):
        """Test when user cancels model selection."""
        # Setup mocks
        mock_config = Mock()
        mock_config.get.return_value = "llama2:7b"
        mock_get_config.return_value = mock_config
        mock_get_formatter.return_value = mock_output

        mock_selector = Mock()
        mock_selector.select_model.side_effect = Exception(
            "Model selection cancelled by user"
        )
        mock_model_selector_class.return_value = mock_selector

        with pytest.raises(typer.Exit):
            config_model_command()

        # Verify config was not updated
        mock_config.set.assert_not_called()

    @patch("automake.cli.commands.config.ModelSelector")
    @patch("automake.cli.commands.config.get_config")
    @patch("automake.cli.commands.config.get_formatter")
    def test_config_model_command_config_load_error(
        self,
        mock_get_formatter,
        mock_get_config,
        mock_model_selector_class,
        mock_output,
    ):
        """Test handling of configuration load errors."""
        # Setup mocks
        mock_get_config.side_effect = Exception("Failed to load config")
        mock_get_formatter.return_value = mock_output

        with pytest.raises(typer.Exit):
            config_model_command()

        # Verify ModelSelector was not called
        mock_model_selector_class.assert_not_called()

    @patch("automake.cli.commands.config.ModelSelector")
    @patch("automake.cli.commands.config.get_config")
    @patch("automake.cli.commands.config.get_formatter")
    def test_config_model_command_config_save_error(
        self,
        mock_get_formatter,
        mock_get_config,
        mock_model_selector_class,
        mock_output,
    ):
        """Test handling of configuration save errors."""
        # Setup mocks
        mock_config = Mock()
        mock_config.get.return_value = "llama2:7b"
        mock_config.set.side_effect = Exception("Failed to save config")
        mock_get_config.return_value = mock_config
        mock_get_formatter.return_value = mock_output

        mock_selector = Mock()
        mock_selector.select_model.return_value = "mistral:7b"
        mock_model_selector_class.return_value = mock_selector

        with pytest.raises(typer.Exit):
            config_model_command()

    @patch("automake.cli.commands.config.ModelSelector")
    @patch("automake.cli.commands.config.get_config")
    @patch("automake.cli.commands.config.get_formatter")
    def test_config_model_command_no_current_model(
        self,
        mock_get_formatter,
        mock_get_config,
        mock_model_selector_class,
        mock_output,
    ):
        """Test when no model is currently configured."""
        # Setup mocks
        mock_config = Mock()
        mock_config.get.return_value = None
        mock_get_config.return_value = mock_config
        mock_get_formatter.return_value = mock_output

        mock_selector = Mock()
        mock_selector.select_model.return_value = "llama2:7b"
        mock_model_selector_class.return_value = mock_selector

        config_model_command()

    @patch("automake.cli.commands.config.ModelSelector")
    @patch("automake.cli.commands.config.get_config")
    @patch("automake.cli.commands.config.get_formatter")
    def test_config_model_command_displays_guidance(
        self,
        mock_get_formatter,
        mock_get_config,
        mock_model_selector_class,
        mock_output,
    ):
        """Test that the command displays helpful guidance to the user."""
        # Setup mocks
        mock_config = Mock()
        mock_config.get.return_value = "llama2:7b"
        mock_get_config.return_value = mock_config
        mock_get_formatter.return_value = mock_output

        mock_selector = Mock()
        mock_selector.select_model.return_value = "mistral:7b"
        mock_model_selector_class.return_value = mock_selector

        config_model_command()

        # Verify the command executed successfully
        mock_output.live_box.assert_called()
