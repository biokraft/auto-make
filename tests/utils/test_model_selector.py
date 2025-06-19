"""Tests for model selector functionality.

This module tests the ModelSelector class which provides interactive
model selection capabilities for AutoMake.
"""

from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError, Timeout

from automake.utils.model_selector import ModelSelector, ModelSelectorError


class TestModelSelector:
    """Test cases for ModelSelector class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.selector = ModelSelector(self.mock_config)

    def test_init_with_config(self):
        """Test ModelSelector initialization with config."""
        assert self.selector.config == self.mock_config

    @patch("automake.utils.model_selector.get_available_models")
    def test_get_local_models_success(self, mock_get_available_models):
        """Test successful retrieval of local models."""
        # Setup mock
        mock_get_available_models.return_value = ["llama2:7b", "mistral:7b"]

        # Test
        result = self.selector.get_local_models()

        # Verify
        assert result == ["llama2:7b", "mistral:7b"]
        mock_get_available_models.assert_called_once()

    @patch("automake.utils.model_selector.get_available_models")
    def test_get_local_models_failure(self, mock_get_available_models):
        """Test handling of Ollama manager failure."""
        # Setup mock to raise exception
        mock_get_available_models.side_effect = Exception("Connection failed")

        # Test
        with pytest.raises(ModelSelectorError, match="Failed to retrieve local models"):
            self.selector.get_local_models()

    @patch("automake.utils.model_selector.questionary.select")
    @patch("automake.utils.model_selector.get_available_models")
    def test_select_model_from_local_list(self, mock_get_available_models, mock_select):
        """Test selecting a model from local list."""
        # Setup mocks
        mock_get_available_models.return_value = ["llama2:7b", "mistral:7b"]
        mock_select.return_value.ask.return_value = "llama2:7b"

        # Test
        result = self.selector.select_model()

        # Verify
        assert result == "llama2:7b"
        mock_select.assert_called_once()

    @patch("automake.utils.model_selector.questionary.select")
    @patch("automake.utils.model_selector.get_available_models")
    def test_select_model_search_option(self, mock_get_available_models, mock_select):
        """Test selecting the search option."""
        # Setup mocks
        mock_get_available_models.return_value = ["llama2:7b"]
        mock_select.return_value.ask.return_value = "Search for a new model online..."

        with patch.object(
            self.selector, "search_online_models", return_value="new_model:latest"
        ) as mock_search:
            # Test
            result = self.selector.select_model()

            # Verify
            assert result == "new_model:latest"
            mock_search.assert_called_once()

    @patch("automake.utils.model_selector.questionary.text")
    @patch("automake.utils.model_selector.questionary.select")
    def test_search_online_models_manual_input(self, mock_select, mock_text):
        """Test manual model input in online search."""
        # Setup mocks - first select manual entry, then return custom model
        mock_select.return_value.ask.return_value = "✏️ Enter model name manually..."
        mock_text.return_value.ask.return_value = "custom_model:latest"

        # Test
        result = self.selector.search_online_models()

        # Verify
        assert result == "custom_model:latest"

    @patch("automake.utils.model_selector.questionary.select")
    @patch("automake.utils.model_selector.get_available_models")
    def test_select_model_no_local_models(self, mock_get_available_models, mock_select):
        """Test behavior when no local models are available."""
        # Setup mocks
        mock_get_available_models.return_value = []
        mock_select.return_value.ask.return_value = "Search for a new model online..."

        with patch.object(
            self.selector, "search_online_models", return_value="new_model:latest"
        ) as mock_search:
            # Test
            result = self.selector.select_model()

            # Verify
            assert result == "new_model:latest"
            mock_search.assert_called_once()

    @patch("automake.utils.model_selector.questionary.select")
    @patch("automake.utils.model_selector.get_available_models")
    def test_select_model_keyboard_interrupt(
        self, mock_get_available_models, mock_select
    ):
        """Test handling of keyboard interrupt during model selection."""
        # Setup mocks
        mock_get_available_models.return_value = ["llama2:7b"]
        mock_select.return_value.ask.side_effect = KeyboardInterrupt()

        # Test
        with pytest.raises(ModelSelectorError, match="Model selection cancelled"):
            self.selector.select_model()

    @patch("automake.utils.model_selector.questionary.select")
    def test_search_online_models_with_popular_suggestions(self, mock_select):
        """Test online search shows popular model suggestions."""
        # Setup mock
        mock_select.return_value.ask.return_value = (
            "llama3.2:3b - Compact and efficient 3B parameter model"
        )

        # Test
        result = self.selector.search_online_models()

        # Verify
        assert result == "llama3.2:3b"
        mock_select.assert_called_once()

        # Check that popular models are in the choices
        call_args = mock_select.call_args
        choices = call_args[1]["choices"]
        choice_values = [
            choice.value if hasattr(choice, "value") else choice for choice in choices
        ]

        # Should contain popular models and manual entry option
        assert any("llama3.2:3b" in str(choice) for choice in choice_values)
        assert any(
            "Enter model name manually" in str(choice) for choice in choice_values
        )

    @patch("automake.utils.model_selector.questionary.text")
    @patch("automake.utils.model_selector.questionary.select")
    def test_search_online_models_manual_entry_option(self, mock_select, mock_text):
        """Test selecting manual entry option in online search."""
        # Setup mocks
        mock_select.return_value.ask.return_value = "✏️ Enter model name manually..."
        mock_text.return_value.ask.return_value = "custom:model"

        # Test
        result = self.selector.search_online_models()

        # Verify
        assert result == "custom:model"
        mock_select.assert_called_once()
        mock_text.assert_called_once()

    @patch("automake.utils.model_selector.questionary.select")
    def test_search_online_models_keyboard_interrupt(self, mock_select):
        """Test handling of keyboard interrupt during online search."""
        # Setup mock
        mock_select.return_value.ask.side_effect = KeyboardInterrupt()

        # Test
        result = self.selector.search_online_models()

        # Verify
        assert result is None

    def test_get_popular_models_list(self):
        """Test getting list of popular models."""
        models = self.selector.get_popular_models()

        # Verify
        assert isinstance(models, list)
        assert len(models) > 0
        assert "llama3.2:3b" in models
        assert "mistral:7b" in models

    def test_format_model_info(self):
        """Test formatting model information for display."""
        # Test with description
        result = self.selector._format_model_info("llama3.2:3b", "Test description")
        assert result == "llama3.2:3b - Test description"

        # Test without description
        result = self.selector._format_model_info("model:tag", None)
        assert result == "model:tag"

    # Additional Error Handling Tests

    @patch("automake.utils.model_selector.get_available_models")
    def test_get_local_models_ollama_not_running(self, mock_get_available_models):
        """Test handling when Ollama service is not running."""
        # Setup mock to simulate Ollama not running
        mock_get_available_models.side_effect = ConnectionError("Connection refused")

        # Test
        with pytest.raises(ModelSelectorError, match="Failed to retrieve local models"):
            self.selector.get_local_models()

    @patch("automake.utils.model_selector.get_available_models")
    def test_get_local_models_timeout(self, mock_get_available_models):
        """Test handling of timeout when getting local models."""
        # Setup mock to simulate timeout
        mock_get_available_models.side_effect = Timeout("Request timed out")

        # Test
        with pytest.raises(ModelSelectorError, match="Failed to retrieve local models"):
            self.selector.get_local_models()

    @patch("automake.utils.model_selector.get_available_models")
    def test_get_local_models_empty_response(self, mock_get_available_models):
        """Test handling when Ollama returns empty model list."""
        # Setup mock
        mock_get_available_models.return_value = []

        # Test
        result = self.selector.get_local_models()

        # Verify - should return empty list, not raise error
        assert result == []

    @patch("automake.utils.model_selector.questionary.text")
    @patch("automake.utils.model_selector.questionary.select")
    def test_search_online_models_empty_manual_input(self, mock_select, mock_text):
        """Test handling of empty manual input."""
        # Setup mocks - first select manual entry, then return empty string
        mock_select.return_value.ask.return_value = "✏️ Enter model name manually..."
        mock_text.return_value.ask.return_value = ""

        # Test
        result = self.selector.search_online_models()

        # Verify - should return None for empty input
        assert result is None

    @patch("automake.utils.model_selector.questionary.text")
    @patch("automake.utils.model_selector.questionary.select")
    def test_search_online_models_whitespace_input(self, mock_select, mock_text):
        """Test handling of whitespace-only manual input."""
        # Setup mocks - first select manual entry, then return whitespace
        mock_select.return_value.ask.return_value = "✏️ Enter model name manually..."
        mock_text.return_value.ask.return_value = "   \t\n   "

        # Test
        result = self.selector.search_online_models()

        # Verify - should return None for whitespace-only input
        assert result is None

    @patch("automake.utils.model_selector.questionary.select")
    @patch("automake.utils.model_selector.get_available_models")
    def test_select_model_none_selection(self, mock_get_available_models, mock_select):
        """Test handling when user cancels selection."""
        # Setup mocks
        mock_get_available_models.return_value = ["llama2:7b"]
        mock_select.return_value.ask.return_value = None

        # Test
        result = self.selector.select_model()

        # Verify
        assert result is None

    @patch("automake.utils.model_selector.get_available_models")
    def test_get_local_models_permission_error(self, mock_get_available_models):
        """Test handling of permission errors when accessing Ollama."""
        # Setup mock to simulate permission error
        mock_get_available_models.side_effect = PermissionError("Permission denied")

        # Test
        with pytest.raises(ModelSelectorError, match="Failed to retrieve local models"):
            self.selector.get_local_models()

    @patch("automake.utils.model_selector.questionary.select")
    def test_search_online_models_invalid_selection(self, mock_select):
        """Test handling of unexpected selection values."""
        # Setup mock to return unexpected value
        mock_select.return_value.ask.return_value = "unexpected_value"

        # Test - should not crash, should return None or handle gracefully
        result = self.selector.search_online_models()

        # Verify - the method should handle unexpected values gracefully
        assert result is None or isinstance(result, str)

    def test_update_config_success(self):
        """Test successful configuration update."""
        # Mock the config.set method
        with patch.object(self.selector.config, "set") as mock_set:
            self.selector.update_config("llama3.2:3b")

            mock_set.assert_called_once_with("ollama", "model", "llama3.2:3b")

    def test_update_config_failure(self):
        """Test handling of configuration update failure."""
        # Mock the config.set method to raise an exception
        with patch.object(
            self.selector.config, "set", side_effect=Exception("Config error")
        ):
            with pytest.raises(
                ModelSelectorError, match="Failed to update configuration: Config error"
            ):
                self.selector.update_config("llama3.2:3b")
