"""Tests for Phase 7 - Configuration Command Support.

This module tests the configuration command support for agent.require_confirmation.
"""

from unittest.mock import Mock, patch

import pytest

from automake.cli.commands.config import config_set_command
from automake.config import Config


class TestConfigCommandPhase7:
    """Test configuration command support for Phase 7."""

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
        config = Mock(spec=Config)
        config.set = Mock()
        return config

    def test_config_set_agent_require_confirmation_true(self, mock_config, mock_output):
        """Test setting agent.require_confirmation to true via config command."""
        with (
            patch("automake.cli.commands.config.get_config", return_value=mock_config),
            patch(
                "automake.cli.commands.config.get_formatter", return_value=mock_output
            ),
        ):
            config_set_command("agent.require_confirmation", "true")

            # Verify config.set was called with correct parameters
            mock_config.set.assert_called_once_with(
                "agent", "require_confirmation", True
            )

            # Verify success message was displayed
            mock_output.live_box.assert_called()

    def test_config_set_agent_require_confirmation_false(
        self, mock_config, mock_output
    ):
        """Test setting agent.require_confirmation to false via config command."""
        with (
            patch("automake.cli.commands.config.get_config", return_value=mock_config),
            patch(
                "automake.cli.commands.config.get_formatter", return_value=mock_output
            ),
        ):
            config_set_command("agent.require_confirmation", "false")

            # Verify config.set was called with correct parameters
            mock_config.set.assert_called_once_with(
                "agent", "require_confirmation", False
            )

    def test_config_set_validates_boolean_values(self, mock_config, mock_output):
        """Test that config set properly validates boolean values."""
        with (
            patch("automake.cli.commands.config.get_config", return_value=mock_config),
            patch(
                "automake.cli.commands.config.get_formatter", return_value=mock_output
            ),
        ):
            # Test various boolean representations
            config_set_command("agent.require_confirmation", "True")
            mock_config.set.assert_called_with("agent", "require_confirmation", True)

            mock_config.reset_mock()
            config_set_command("agent.require_confirmation", "FALSE")
            mock_config.set.assert_called_with("agent", "require_confirmation", False)

    def test_config_set_invalid_key_path_error(self, mock_output):
        """Test that invalid key paths raise appropriate errors."""
        with (
            patch(
                "automake.cli.commands.config.get_formatter", return_value=mock_output
            ),
            pytest.raises(Exception) as exc_info,
        ):
            config_set_command("agent", "true")  # Missing key after section

        # Verify it's a typer.Exit exception
        assert "Exit" in str(type(exc_info.value))

    def test_config_set_handles_config_errors(self, mock_config, mock_output):
        """Test that configuration errors are handled gracefully."""
        mock_config.set.side_effect = Exception("Config write error")

        with (
            patch("automake.cli.commands.config.get_config", return_value=mock_config),
            patch(
                "automake.cli.commands.config.get_formatter", return_value=mock_output
            ),
            pytest.raises(Exception) as exc_info,
        ):
            config_set_command("agent.require_confirmation", "true")

        # Verify it's a typer.Exit exception
        assert "Exit" in str(type(exc_info.value))
        # Verify error message was displayed
        mock_output.live_box.assert_called()

    def test_config_set_shows_specific_message_for_agent_confirmation(
        self, mock_config, mock_output
    ):
        """Test that setting agent confirmation shows a specific helpful message."""
        with (
            patch("automake.cli.commands.config.get_config", return_value=mock_config),
            patch(
                "automake.cli.commands.config.get_formatter", return_value=mock_output
            ),
        ):
            config_set_command("agent.require_confirmation", "false")

            # Check that the success message was shown
            mock_output.live_box.assert_called()
            live_box_calls = mock_output.live_box.call_args_list

            # Should be called with "Configuration Updated" message type
            assert any("Configuration Updated" in str(call) for call in live_box_calls)
