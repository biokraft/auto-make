"""Tests for the updated agent command with Phase 3 scaffolding."""

from unittest.mock import MagicMock, Mock, patch

import pytest
import typer

from automake.agent.manager import ManagerAgentRunner
from automake.cli.commands.agent import (
    _run_interactive,
    _run_non_interactive,
    agent_command,
)
from automake.config import Config


class TestAgentCommandPhase3:
    """Test the updated agent command with RichInteractiveSession."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing."""
        config = Mock(spec=Config)
        config.agent_require_confirmation = False
        return config

    @pytest.fixture
    def mock_runner(self):
        """Create a mock ManagerAgentRunner for testing."""
        runner = Mock(spec=ManagerAgentRunner)
        runner.initialize.return_value = False  # Ollama was not started
        runner.agent = Mock()
        return runner

    @patch("automake.cli.commands.agent.get_config")
    @patch("automake.cli.commands.agent.setup_logging")
    @patch("automake.cli.commands.agent.ManagerAgentRunner")
    @patch("automake.cli.commands.agent.get_formatter")
    def test_agent_command_non_interactive(
        self, mock_get_formatter, mock_runner_class, mock_setup_logging, mock_get_config
    ):
        """Test agent command in non-interactive mode."""
        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        mock_runner = Mock()
        mock_runner.initialize.return_value = False
        mock_runner.run.return_value = "Test response"
        mock_runner_class.return_value = mock_runner

        mock_formatter = Mock()
        mock_live_box = Mock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_live_box
        mock_context_manager.__exit__.return_value = None
        mock_formatter.live_box.return_value = mock_context_manager
        mock_get_formatter.return_value = mock_formatter

        # Run the command
        agent_command("test prompt")

        # Verify initialization
        mock_runner_class.assert_called_once_with(mock_config)
        mock_runner.initialize.assert_called_once()

        # Verify non-interactive execution
        mock_runner.run.assert_called_once_with("test prompt")

    @patch("automake.cli.commands.agent.get_config")
    @patch("automake.cli.commands.agent.setup_logging")
    @patch("automake.cli.commands.agent.ManagerAgentRunner")
    @patch("automake.cli.commands.agent.get_formatter")
    @patch("automake.cli.commands.agent._run_interactive")
    def test_agent_command_interactive(
        self,
        mock_run_interactive,
        mock_get_formatter,
        mock_runner_class,
        mock_setup_logging,
        mock_get_config,
    ):
        """Test agent command in interactive mode."""
        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        mock_runner = Mock()
        mock_runner.initialize.return_value = True  # Ollama was started
        mock_runner_class.return_value = mock_runner

        mock_formatter = Mock()
        mock_live_box = Mock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_live_box
        mock_context_manager.__exit__.return_value = None
        mock_formatter.live_box.return_value = mock_context_manager
        mock_get_formatter.return_value = mock_formatter

        # Run the command without prompt (interactive mode)
        agent_command(None)

        # Verify initialization
        mock_runner_class.assert_called_once_with(mock_config)
        mock_runner.initialize.assert_called_once()

        # Verify interactive mode was called
        mock_run_interactive.assert_called_once_with(mock_runner, mock_formatter)

        # Verify Ollama startup message
        mock_live_box.update.assert_any_call(
            "🤖 AI agent system initialized\n✅ Ollama server started automatically"
        )

    @patch("automake.cli.commands.agent.get_config")
    @patch("automake.cli.commands.agent.setup_logging")
    @patch("automake.cli.commands.agent.ManagerAgentRunner")
    @patch("automake.cli.commands.agent.get_formatter")
    def test_agent_command_initialization_error(
        self, mock_get_formatter, mock_runner_class, mock_setup_logging, mock_get_config
    ):
        """Test agent command with initialization error."""
        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        mock_runner = Mock()
        mock_runner.initialize.side_effect = Exception("Initialization failed")
        mock_runner_class.return_value = mock_runner

        mock_formatter = Mock()
        mock_live_box = Mock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_live_box
        mock_context_manager.__exit__.return_value = None
        mock_formatter.live_box.return_value = mock_context_manager
        mock_get_formatter.return_value = mock_formatter

        # Run the command and expect it to raise typer.Exit
        with pytest.raises(typer.Exit) as exc_info:
            agent_command("test prompt")

        assert exc_info.value.exit_code == 1
        mock_live_box.update.assert_any_call(
            "❌ Failed to initialize agent: Initialization failed"
        )

    @patch("automake.cli.commands.agent.RichInteractiveSession")
    @patch("automake.cli.commands.agent.get_config")
    def test_run_interactive_with_rich_session(
        self, mock_get_config, mock_session_class
    ):
        """Test _run_interactive uses RichInteractiveSession."""
        # Setup mocks
        mock_config = Mock()
        mock_config.agent_require_confirmation = True
        mock_get_config.return_value = mock_config

        mock_runner = Mock()
        mock_runner.agent = Mock()

        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Run interactive mode
        _run_interactive(mock_runner, Mock())

        # Verify RichInteractiveSession was created with correct parameters
        mock_session_class.assert_called_once()
        call_args = mock_session_class.call_args
        assert call_args[1]["agent"] is mock_runner.agent
        assert call_args[1]["require_confirmation"] is True

        # Verify session was started
        mock_session.start.assert_called_once()

    @patch("automake.cli.commands.agent.RichInteractiveSession")
    @patch("automake.cli.commands.agent.get_config")
    def test_run_interactive_session_error(self, mock_get_config, mock_session_class):
        """Test _run_interactive handles session errors."""
        # Setup mocks
        mock_config = Mock()
        mock_config.agent_require_confirmation = False
        mock_get_config.return_value = mock_config

        mock_runner = Mock()
        mock_runner.agent = Mock()

        mock_session = Mock()
        mock_session.start.side_effect = Exception("Session failed")
        mock_session_class.return_value = mock_session

        # Run interactive mode and expect it to raise typer.Exit
        with pytest.raises(typer.Exit) as exc_info:
            _run_interactive(mock_runner, Mock())

        assert exc_info.value.exit_code == 1

    def test_run_non_interactive_success(self, mock_runner):
        """Test _run_non_interactive with successful execution."""
        mock_runner.run.return_value = "Task completed successfully"

        mock_output = Mock()
        mock_live_box = Mock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_live_box
        mock_context_manager.__exit__.return_value = None
        mock_output.live_box.return_value = mock_context_manager

        with patch("automake.cli.commands.agent.console") as mock_console:
            _run_non_interactive(mock_runner, "test prompt", mock_output)

        # Verify agent was called
        mock_runner.run.assert_called_once_with("test prompt")

        # Verify output was displayed
        mock_console.print.assert_any_call("\n[bold green]Agent Response:[/bold green]")
        mock_console.print.assert_any_call("Task completed successfully")

    def test_run_non_interactive_error(self, mock_runner):
        """Test _run_non_interactive with execution error."""
        mock_runner.run.side_effect = Exception("Execution failed")

        mock_output = Mock()
        mock_live_box = Mock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_live_box
        mock_context_manager.__exit__.return_value = None
        mock_output.live_box.return_value = mock_context_manager

        with pytest.raises(typer.Exit) as exc_info:
            _run_non_interactive(mock_runner, "test prompt", mock_output)

        assert exc_info.value.exit_code == 1
        mock_live_box.update.assert_any_call(
            "❌ Agent execution failed: Execution failed"
        )
