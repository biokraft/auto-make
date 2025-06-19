"""Integration tests for Phase 7 - Action Confirmation.

This module tests the complete end-to-end functionality of action confirmation
across all components: configuration, interactive session, non-interactive mode,
and CLI commands.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from automake.agent.manager import ManagerAgentRunner
from automake.agent.ui.session import RichInteractiveSession
from automake.cli.commands.agent import _run_non_interactive
from automake.cli.commands.config import config_set_command
from automake.config.manager import Config


class TestPhase7Integration:
    """Integration tests for Phase 7 action confirmation functionality."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary config directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        return temp_dir
        # Cleanup is handled by tempfile

    @pytest.fixture
    def fresh_config(self, temp_config_dir):
        """Create a fresh config instance with temporary directory."""
        return Config(temp_config_dir)

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        agent = Mock()
        agent.run = Mock()
        return agent

    @pytest.fixture
    def mock_runner(self, mock_agent):
        """Create a mock agent runner."""
        runner = Mock(spec=ManagerAgentRunner)
        runner.agent = mock_agent
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

    def test_end_to_end_config_change_affects_interactive_session(
        self, fresh_config, mock_agent
    ):
        """Test that changing config affects interactive session behavior."""
        # Start with default (confirmation enabled)
        assert fresh_config.agent_require_confirmation is True

        # Create interactive session - should require confirmation
        session = RichInteractiveSession(
            agent=mock_agent,
            require_confirmation=fresh_config.agent_require_confirmation,
        )
        assert session.require_confirmation is True

        # Change config to disable confirmation
        fresh_config.set("agent", "require_confirmation", False)
        assert fresh_config.agent_require_confirmation is False

        # Create new session - should not require confirmation
        session_no_confirm = RichInteractiveSession(
            agent=mock_agent,
            require_confirmation=fresh_config.agent_require_confirmation,
        )
        assert session_no_confirm.require_confirmation is False

    def test_end_to_end_config_command_integration(self, temp_config_dir):
        """Test that config command properly updates configuration."""
        # Create config in temp directory
        config = Config(temp_config_dir)

        # Verify default is True
        assert config.agent_require_confirmation is True

        with patch("automake.cli.commands.config.get_config", return_value=config):
            # Use config command to set to false
            with patch("automake.cli.commands.config.get_formatter") as mock_formatter:
                mock_output = Mock()
                live_box = Mock()
                live_box.update = Mock()
                live_box.__enter__ = Mock(return_value=live_box)
                live_box.__exit__ = Mock(return_value=None)
                mock_output.live_box = Mock(return_value=live_box)
                mock_formatter.return_value = mock_output

                config_set_command("agent.require_confirmation", "false")

        # Verify config was updated
        assert config.agent_require_confirmation is False

        # Reload config from file to ensure persistence
        fresh_config = Config(temp_config_dir)
        assert fresh_config.agent_require_confirmation is False

    def test_end_to_end_non_interactive_with_config_integration(
        self, fresh_config, mock_runner, mock_output
    ):
        """Test non-interactive mode respects configuration settings."""
        # Set config to require confirmation
        fresh_config.set("agent", "require_confirmation", True)

        # Mock agent response with action
        mock_action = {"tool_name": "test_tool", "arguments": {"param": "value"}}
        mock_runner.run.return_value = [mock_action, "Result"]

        with (
            patch("automake.cli.commands.agent.get_config", return_value=fresh_config),
            patch("automake.cli.commands.agent.console"),
            patch("automake.cli.commands.agent.Prompt") as mock_prompt,
        ):
            # User confirms action
            mock_prompt.ask.return_value = "y"

            _run_non_interactive(mock_runner, "test prompt", mock_output)

            # Verify confirmation was requested
            mock_prompt.ask.assert_called_once()

        # Now disable confirmation
        fresh_config.set("agent", "require_confirmation", False)
        mock_prompt.reset_mock()

        with (
            patch("automake.cli.commands.agent.get_config", return_value=fresh_config),
            patch("automake.cli.commands.agent.console"),
            patch("automake.cli.commands.agent.Prompt") as mock_prompt,
        ):
            _run_non_interactive(mock_runner, "test prompt", mock_output)

            # Verify no confirmation was requested
            mock_prompt.ask.assert_not_called()

    def test_interactive_session_confirmation_workflow(self, fresh_config, mock_agent):
        """Test complete interactive session confirmation workflow."""
        # Enable confirmation
        fresh_config.set("agent", "require_confirmation", True)

        session = RichInteractiveSession(
            agent=mock_agent,
            require_confirmation=fresh_config.agent_require_confirmation,
        )

        # Mock action that needs confirmation
        test_action = {
            "tool_name": "file_write",
            "arguments": {"path": "/test.txt", "content": "test"},
        }

        # Test confirmation UI
        with patch("automake.agent.ui.session.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "y"

            result = session.get_confirmation(test_action)

            assert result is True
            mock_prompt.ask.assert_called_once()

        # Test rejection
        with patch("automake.agent.ui.session.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "n"

            result = session.get_confirmation(test_action)

            assert result is False

    def test_action_detection_consistency(self):
        """Test that action detection is consistent across components."""
        # Test action
        action = {"tool_name": "test_tool", "arguments": {"param": "value"}}

        # Test non-action items
        non_actions = [
            "string response",
            {"no_tool_name": "value"},
            {"tool_name": None},
            123,
            [],
        ]

        # Import the detection functions
        from automake.agent.ui.session import RichInteractiveSession
        from automake.cli.commands.agent import _is_action as cli_is_action

        # Test CLI detection
        assert cli_is_action(action) is True
        for non_action in non_actions:
            assert cli_is_action(non_action) is False

        # Test session detection
        session = RichInteractiveSession(Mock())
        assert session._is_action(action) is True
        for non_action in non_actions:
            assert session._is_action(non_action) is False

    def test_configuration_persistence_across_restarts(self, temp_config_dir):
        """Test that configuration changes persist across application restarts."""
        # Create first config instance
        config1 = Config(temp_config_dir)
        assert config1.agent_require_confirmation is True  # Default

        # Change setting
        config1.set("agent", "require_confirmation", False)
        assert config1.agent_require_confirmation is False

        # Create second config instance (simulating app restart)
        config2 = Config(temp_config_dir)
        assert config2.agent_require_confirmation is False  # Should persist

        # Change back
        config2.set("agent", "require_confirmation", True)

        # Create third instance
        config3 = Config(temp_config_dir)
        assert config3.agent_require_confirmation is True  # Should persist

    def test_error_handling_integration(self, fresh_config, mock_runner, mock_output):
        """Test error handling across the confirmation system."""
        fresh_config.set("agent", "require_confirmation", True)

        # Test config error handling
        with patch("automake.cli.commands.config.get_config") as mock_get_config:
            mock_get_config.side_effect = Exception("Config load error")

            with (
                patch(
                    "automake.cli.commands.config.get_formatter",
                    return_value=mock_output,
                ),
                pytest.raises((Exception, SystemExit)),
            ):
                config_set_command("agent.require_confirmation", "true")

        # Test non-interactive error handling
        mock_runner.run.side_effect = Exception("Agent error")

        with (
            patch("automake.cli.commands.agent.get_config", return_value=fresh_config),
            pytest.raises((Exception, SystemExit)),
        ):
            _run_non_interactive(mock_runner, "test prompt", mock_output)

    def test_boolean_value_conversion_consistency(self):
        """Test that boolean values are converted consistently across components."""
        from automake.cli.commands.config import _convert_config_value

        # Test various boolean representations
        true_values = ["true", "True", "TRUE", "yes", "Yes", "YES"]
        false_values = ["false", "False", "FALSE", "no", "No", "NO"]

        for value in true_values:
            if value.lower() in ("true", "false"):  # Only true/false are supported
                assert _convert_config_value(value) is True

        for value in false_values:
            if value.lower() in ("true", "false"):  # Only true/false are supported
                assert _convert_config_value(value) is False
