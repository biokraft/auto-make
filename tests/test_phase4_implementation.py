"""Tests for Phase 4 implementation - Non-Interactive Agent Mode.

This module tests the primary interface `automake "prompt"` and LiveBox streaming.
"""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from automake.cli.app import app


class TestPhase4Implementation:
    """Test Phase 4 - Non-Interactive Agent Mode implementation."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("automake.cli.app.ManagerAgentRunner")
    @patch("automake.cli.app.get_config")
    @patch("automake.cli.app.setup_logging")
    @patch("automake.cli.app.log_config_info")
    @patch("automake.cli.app.log_command_execution")
    @patch("automake.cli.app.get_formatter")
    def test_primary_interface_automake_prompt(
        self,
        mock_get_formatter,
        mock_log_command,
        mock_log_config,
        mock_setup_logging,
        mock_get_config,
        mock_manager_runner,
    ):
        """Test that `automake "prompt"` works as the primary interface."""
        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        # Mock output formatter and live box
        mock_formatter = Mock()
        mock_live_box = Mock()
        mock_live_box.__enter__ = Mock(return_value=mock_live_box)
        mock_live_box.__exit__ = Mock(return_value=None)
        mock_formatter.live_box.return_value = mock_live_box
        mock_get_formatter.return_value = mock_formatter

        # Mock manager runner
        mock_runner_instance = Mock()
        mock_runner_instance.initialize.return_value = False
        mock_manager_runner.return_value = mock_runner_instance

        # Mock the _run_non_interactive function
        with patch("automake.cli.app._run_non_interactive") as mock_run_non_interactive:
            result = self.runner.invoke(app, ["build the project"])

            # Verify the command executed successfully
            assert result.exit_code == 0

            # Verify the agent was initialized
            mock_manager_runner.assert_called_once_with(mock_config)
            mock_runner_instance.initialize.assert_called_once()

            # Verify _run_non_interactive was called with correct arguments
            mock_run_non_interactive.assert_called_once_with(
                mock_runner_instance, "build the project", mock_formatter
            )

            # Verify logging was set up
            mock_log_command.assert_called_once()
            assert "main: build the project" in str(mock_log_command.call_args)

    @patch("automake.cli.app.ManagerAgentRunner")
    @patch("automake.cli.app.get_config")
    @patch("automake.cli.app.setup_logging")
    @patch("automake.cli.app.get_formatter")
    def test_primary_interface_with_livebox_streaming(
        self,
        mock_get_formatter,
        mock_setup_logging,
        mock_get_config,
        mock_manager_runner,
    ):
        """Test that LiveBox is used for streaming output in primary interface."""
        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_setup_logging.return_value = Mock()

        # Mock output formatter and live box
        mock_formatter = Mock()
        mock_live_box = Mock()
        mock_live_box.__enter__ = Mock(return_value=mock_live_box)
        mock_live_box.__exit__ = Mock(return_value=None)
        mock_formatter.live_box.return_value = mock_live_box
        mock_get_formatter.return_value = mock_formatter

        # Mock manager runner
        mock_runner_instance = Mock()
        mock_runner_instance.initialize.return_value = True  # Ollama was started
        mock_manager_runner.return_value = mock_runner_instance

        with patch("automake.cli.app._run_non_interactive"):
            result = self.runner.invoke(app, ["list all python files"])

            assert result.exit_code == 0

            # Verify LiveBox was used for initialization
            mock_formatter.live_box.assert_called()
            call_args = mock_formatter.live_box.call_args_list

            # Should have been called for "Agent Initialization"
            assert any("Agent Initialization" in str(call) for call in call_args)

            # Verify LiveBox update was called
            mock_live_box.update.assert_called()
            update_calls = [call[0][0] for call in mock_live_box.update.call_args_list]

            # Should show initialization messages
            assert any("🤖 Initializing AI agent system" in msg for msg in update_calls)
            assert any(
                "Ollama server started automatically" in msg for msg in update_calls
            )

    def test_no_prompt_shows_welcome(self):
        """Test that running `automake` without arguments shows welcome message."""
        result = self.runner.invoke(app, [])
        assert result.exit_code == 0
        assert "Welcome" in result.output

    @patch("automake.cli.app.ManagerAgentRunner")
    @patch("automake.cli.app.get_config")
    @patch("automake.cli.app.get_formatter")
    def test_primary_interface_error_handling(
        self,
        mock_get_formatter,
        mock_get_config,
        mock_manager_runner,
    ):
        """Test error handling in primary interface."""
        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config

        # Mock output formatter and live box
        mock_formatter = Mock()
        mock_live_box = Mock()
        mock_live_box.__enter__ = Mock(return_value=mock_live_box)
        mock_live_box.__exit__ = Mock(return_value=None)
        mock_formatter.live_box.return_value = mock_live_box
        mock_get_formatter.return_value = mock_formatter

        # Mock manager runner to raise an exception
        mock_manager_runner.side_effect = Exception("Agent initialization failed")

        result = self.runner.invoke(app, ["test command"])

        # Should exit with error code
        assert result.exit_code == 1

        # Verify error LiveBox was used
        mock_formatter.live_box.assert_called()
        call_args = mock_formatter.live_box.call_args_list

        # Should have been called for error handling
        assert any("Agent Error" in str(call) for call in call_args)

    def test_subcommands_still_work(self):
        """Test that existing subcommands still work alongside primary interface."""
        # Test that help still works
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage" in result.output

        # Test that agent command still exists
        result = self.runner.invoke(app, ["agent", "--help"])
        assert result.exit_code == 0
        assert "Launch the AI agent" in result.output

        # Test that run command still exists
        result = self.runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "Execute natural language commands" in result.output

    def test_help_shows_primary_interface(self):
        """Test that help information shows the primary interface prominently."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0

        # Should show the new usage pattern
        assert 'automake "PROMPT"' in result.output or "PROMPT" in result.output

        # Should show examples of direct prompts
        assert "build the project" in result.output
        assert "list all python files" in result.output

    @patch("automake.cli.app.ManagerAgentRunner")
    @patch("automake.cli.app.get_config")
    @patch("automake.cli.app.setup_logging")
    @patch("automake.cli.app.get_formatter")
    def test_empty_prompt_handling(
        self,
        mock_get_formatter,
        mock_setup_logging,
        mock_get_config,
        mock_manager_runner,
    ):
        """Test handling of empty prompt."""
        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_setup_logging.return_value = Mock()

        mock_formatter = Mock()
        mock_live_box = Mock()
        mock_live_box.__enter__ = Mock(return_value=mock_live_box)
        mock_live_box.__exit__ = Mock(return_value=None)
        mock_formatter.live_box.return_value = mock_live_box
        mock_get_formatter.return_value = mock_formatter

        mock_runner_instance = Mock()
        mock_runner_instance.initialize.return_value = False
        mock_manager_runner.return_value = mock_runner_instance

        with patch("automake.cli.app._run_non_interactive") as mock_run_non_interactive:
            result = self.runner.invoke(app, [""])

            # Should still execute (empty string is a valid prompt)
            assert result.exit_code == 0
            mock_run_non_interactive.assert_called_once_with(
                mock_runner_instance, "", mock_formatter
            )

    def test_phase4_acceptance_criteria(self):
        """Test that Phase 4 acceptance criteria are met."""
        # 1. automake "prompt" should be the primary interface
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert 'automake "PROMPT"' in result.output or "PROMPT" in result.output

        # 2. Help should show primary examples
        assert "build the project" in result.output
        assert "list all python files" in result.output

        # 3. Agent output should be streamed (tested in other tests with LiveBox)
        # 4. Non-interactive mode should work (tested in other tests)

        # Verify the main interface accepts prompts
        with (
            patch("automake.cli.app.ManagerAgentRunner"),
            patch("automake.cli.app.get_config"),
            patch("automake.cli.app.get_formatter"),
            patch("automake.cli.app._run_non_interactive"),
        ):
            result = self.runner.invoke(app, ["test prompt"])
            # Should not show help, should try to execute
            assert "Welcome" not in result.output
