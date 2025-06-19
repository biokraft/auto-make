"""Tests for integrating confirmation into agent execution flow."""

from unittest.mock import Mock, patch

import pytest
from rich.console import Console

from automake.agent.ui.session import RichInteractiveSession


class TestAgentConfirmationIntegration:
    """Test integration of confirmation into agent execution flow."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent that simulates smolagents behavior."""
        agent = Mock()

        # Mock agent.run() to return a generator that yields actions
        def mock_run(prompt, stream=True):
            # Simulate agent thinking and then taking an action
            yield "I need to run a command to help you."

            # Simulate an action that needs confirmation
            action = {"tool_name": "run_command", "arguments": {"command": "ls -la"}}
            yield action

            yield "Command executed successfully!"

        agent.run = Mock(side_effect=mock_run)
        return agent

    @pytest.fixture
    def session_with_confirmation(self, mock_agent):
        """Create a session with confirmation enabled."""
        console = Console(file=Mock(), width=80)
        return RichInteractiveSession(
            agent=mock_agent, console=console, require_confirmation=True
        )

    @pytest.fixture
    def session_without_confirmation(self, mock_agent):
        """Create a session with confirmation disabled."""
        console = Console(file=Mock(), width=80)
        return RichInteractiveSession(
            agent=mock_agent, console=console, require_confirmation=False
        )

    def test_confirmation_enabled_prompts_user(self, session_with_confirmation):
        """Test that when confirmation is enabled, user is prompted for actions."""
        with patch.object(
            session_with_confirmation, "get_confirmation", return_value=True
        ) as mock_confirm:
            session_with_confirmation._process_agent_response("test command")

            # Should have been called to confirm the action
            mock_confirm.assert_called_once()

            # Verify the action details were passed correctly
            call_args = mock_confirm.call_args[0][0]
            assert call_args["tool_name"] == "run_command"
            assert call_args["arguments"]["command"] == "ls -la"

    def test_confirmation_disabled_skips_prompt(self, session_without_confirmation):
        """Test that when confirmation is disabled, user is not prompted."""
        with patch.object(
            session_without_confirmation, "get_confirmation"
        ) as mock_confirm:
            session_without_confirmation._process_agent_response("test command")

            # Should not have been called
            mock_confirm.assert_not_called()

    def test_user_confirms_action_proceeds(self, session_with_confirmation):
        """Test that when user confirms, the action proceeds."""
        with patch.object(
            session_with_confirmation, "get_confirmation", return_value=True
        ):
            # Should complete without error
            session_with_confirmation._process_agent_response("test command")

    def test_user_rejects_action_cancelled(self, session_with_confirmation):
        """Test that when user rejects, the action is cancelled."""
        with patch.object(
            session_with_confirmation, "get_confirmation", return_value=False
        ):
            # Should handle cancellation gracefully
            session_with_confirmation._process_agent_response("test command")

            # Verify the session status reflects the cancellation
            # (This might need adjustment based on actual implementation)

    def test_non_action_items_skip_confirmation(self, session_with_confirmation):
        """Test that non-action items (like thoughts) skip confirmation."""

        # Create a mock agent that only returns thoughts
        def mock_run_thoughts_only(prompt, stream=True):
            yield "I'm thinking about this..."
            yield "Let me analyze the situation."
            yield "Here's my final response."

        session_with_confirmation.agent.run = Mock(side_effect=mock_run_thoughts_only)

        with patch.object(
            session_with_confirmation, "get_confirmation"
        ) as mock_confirm:
            session_with_confirmation._process_agent_response("test command")

            # Should not have been called for thoughts
            mock_confirm.assert_not_called()

    def test_multiple_actions_each_require_confirmation(
        self, session_with_confirmation
    ):
        """Test that multiple actions each require separate confirmation."""

        # Create a mock agent that returns multiple actions
        def mock_run_multiple_actions(prompt, stream=True):
            yield "I need to do several things."

            yield {"tool_name": "run_command", "arguments": {"command": "ls"}}

            yield "First command done, now the second."

            yield {
                "tool_name": "write_file",
                "arguments": {"filename": "test.txt", "content": "hello"},
            }

            yield "All done!"

        session_with_confirmation.agent.run = Mock(
            side_effect=mock_run_multiple_actions
        )

        with patch.object(
            session_with_confirmation, "get_confirmation", return_value=True
        ) as mock_confirm:
            session_with_confirmation._process_agent_response("test command")

            # Should have been called twice, once for each action
            assert mock_confirm.call_count == 2

            # Verify both actions were presented for confirmation
            call_args_list = [call[0][0] for call in mock_confirm.call_args_list]
            assert call_args_list[0]["tool_name"] == "run_command"
            assert call_args_list[1]["tool_name"] == "write_file"
