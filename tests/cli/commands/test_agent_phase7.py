"""Tests for Phase 7 - Non-Interactive Mode Confirmation.

This module tests the confirmation functionality in non-interactive mode.
"""

from unittest.mock import Mock, patch

import pytest

from automake.agent.manager import ManagerAgentRunner
from automake.cli.commands.agent import _run_non_interactive
from automake.config import Config


class TestNonInteractiveConfirmation:
    """Test confirmation functionality in non-interactive mode."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config with confirmation enabled."""
        config = Mock(spec=Config)
        config.agent_require_confirmation = True
        return config

    @pytest.fixture
    def mock_config_no_confirmation(self):
        """Create a mock config with confirmation disabled."""
        config = Mock(spec=Config)
        config.agent_require_confirmation = False
        return config

    @pytest.fixture
    def mock_runner(self):
        """Create a mock agent runner."""
        runner = Mock(spec=ManagerAgentRunner)
        runner.agent = Mock()
        return runner

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

    def test_non_interactive_with_confirmation_enabled_prompts_user(
        self, mock_runner, mock_output, mock_config
    ):
        """Test that non-interactive mode prompts for confirmation when enabled."""
        # Mock the agent to return an action that needs confirmation
        mock_action = {"tool_name": "test_tool", "arguments": {"param": "value"}}
        mock_runner.run.return_value = [mock_action, "Final result"]

        # Mock the confirmation prompt
        with (
            patch("automake.cli.commands.agent.get_config", return_value=mock_config),
            patch("automake.cli.commands.agent.console") as mock_console,
            patch("automake.cli.commands.agent.Prompt") as mock_prompt,
        ):
            # User confirms the action
            mock_prompt.ask.return_value = "y"

            _run_non_interactive(mock_runner, "test prompt", mock_output)

            # Verify confirmation was requested
            mock_prompt.ask.assert_called_once()
            # Verify console displayed action details
            mock_console.print.assert_called()

    def test_non_interactive_with_confirmation_disabled_skips_prompt(
        self, mock_runner, mock_output, mock_config_no_confirmation
    ):
        """Test that non-interactive mode skips confirmation when disabled."""
        # Mock the agent to return an action
        mock_action = {"tool_name": "test_tool", "arguments": {"param": "value"}}
        mock_runner.run.return_value = [mock_action, "Final result"]

        with (
            patch(
                "automake.cli.commands.agent.get_config",
                return_value=mock_config_no_confirmation,
            ),
            patch("automake.cli.commands.agent.console"),
            patch("automake.cli.commands.agent.Prompt") as mock_prompt,
        ):
            _run_non_interactive(mock_runner, "test prompt", mock_output)

            # Verify no confirmation was requested
            mock_prompt.ask.assert_not_called()

    def test_non_interactive_user_cancels_action(
        self, mock_runner, mock_output, mock_config
    ):
        """Test that non-interactive mode handles user cancellation gracefully."""
        # Mock the agent to return an action that needs confirmation
        mock_action = {"tool_name": "test_tool", "arguments": {"param": "value"}}
        mock_runner.run.return_value = [mock_action, "Final result"]

        with (
            patch("automake.cli.commands.agent.get_config", return_value=mock_config),
            patch("automake.cli.commands.agent.console"),
            patch("automake.cli.commands.agent.Prompt") as mock_prompt,
        ):
            # User cancels the action
            mock_prompt.ask.return_value = "n"

            # Should raise typer.Exit(1) when user cancels
            with pytest.raises(Exception) as exc_info:
                _run_non_interactive(mock_runner, "test prompt", mock_output)

            # Verify it's a typer.Exit with code 1
            assert "Exit" in str(type(exc_info.value))
            assert "1" in str(exc_info.value)

    def test_non_interactive_handles_string_response(
        self, mock_runner, mock_output, mock_config
    ):
        """Test non-interactive mode handles string responses without confirmation."""
        # Mock the agent to return a simple string response
        mock_runner.run.return_value = "Simple text response"

        with (
            patch("automake.cli.commands.agent.get_config", return_value=mock_config),
            patch("automake.cli.commands.agent.console") as mock_console,
            patch("automake.cli.commands.agent.Prompt") as mock_prompt,
        ):
            _run_non_interactive(mock_runner, "test prompt", mock_output)

            # Verify no confirmation was requested for string response
            mock_prompt.ask.assert_not_called()
            # Verify result was printed
            mock_console.print.assert_called()

    def test_non_interactive_handles_mixed_response(
        self, mock_runner, mock_output, mock_config
    ):
        """Test that non-interactive mode handles mixed responses with confirmations."""
        # Mock the agent to return mixed response (action + text)
        mock_action = {"tool_name": "test_tool", "arguments": {"param": "value"}}
        mock_runner.run.return_value = [mock_action, "Text response", "Final result"]

        with (
            patch("automake.cli.commands.agent.get_config", return_value=mock_config),
            patch("automake.cli.commands.agent.console"),
            patch("automake.cli.commands.agent.Prompt") as mock_prompt,
        ):
            # User confirms the action
            mock_prompt.ask.return_value = "y"

            _run_non_interactive(mock_runner, "test prompt", mock_output)

            # Verify confirmation was requested only once (for the action)
            mock_prompt.ask.assert_called_once()
