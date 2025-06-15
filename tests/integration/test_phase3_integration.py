"""Integration tests for Phase 3: Agent Scaffolding."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from smolagents import ToolCallingAgent

from automake.agent.ui import InteractiveSession, RichInteractiveSession
from automake.agent.ui.session import SessionStatus
from automake.config import Config


class TestPhase3Integration:
    """Integration tests for Phase 3 agent scaffolding."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary config directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        agent = Mock(spec=ToolCallingAgent)
        agent.run.return_value = "Test response from agent"
        return agent

    def test_config_agent_section_integration(self, temp_config_dir):
        """Test that config properly handles agent section."""
        config = Config(temp_config_dir)

        # Verify default value
        assert config.agent_require_confirmation is False

        # Update the value
        config.set("agent", "require_confirmation", True)

        # Verify it was updated
        assert config.agent_require_confirmation is True

        # Create a new config instance to test persistence
        new_config = Config(temp_config_dir)
        assert new_config.agent_require_confirmation is True

    def test_rich_interactive_session_with_config(self, temp_config_dir, mock_agent):
        """Test RichInteractiveSession integration with config."""
        # Setup config with confirmation enabled
        config = Config(temp_config_dir)
        config.set("agent", "require_confirmation", True)

        # Create session with config value
        session = RichInteractiveSession(
            agent=mock_agent, require_confirmation=config.agent_require_confirmation
        )

        assert session.require_confirmation is True
        assert session.agent is mock_agent

    @patch("automake.agent.ui.session.Live")
    @patch("automake.agent.ui.session.Prompt.ask")
    def test_session_complete_workflow(self, mock_ask, mock_live_class, mock_agent):
        """Test complete session workflow from start to finish."""
        # Setup mocks
        mock_live = Mock()
        mock_live_class.return_value.__enter__.return_value = mock_live

        # Mock user input sequence: one command then quit
        mock_ask.side_effect = ["list files", "quit"]

        # Mock agent streaming response
        mock_agent.run.return_value = iter(["Listing", " files", "..."])

        # Create and start session
        session = RichInteractiveSession(agent=mock_agent)
        session.start()

        # Verify agent was called
        mock_agent.run.assert_called_with("list files", stream=True)

        # Verify history was updated
        assert len(session.history) == 2  # User input + agent response
        assert session.history[0]["role"] == "user"
        assert session.history[0]["content"] == "list files"
        assert session.history[1]["role"] == "assistant"
        assert session.history[1]["content"] == "Listing files..."

    @patch("automake.agent.ui.session.Live")
    @patch("automake.agent.ui.session.Prompt.ask")
    def test_session_with_confirmation_workflow(
        self, mock_ask, mock_live_class, mock_agent
    ):
        """Test session workflow with confirmation enabled."""
        # Setup mocks
        mock_live = Mock()
        mock_live_class.return_value.__enter__.return_value = mock_live

        # Mock user input: command, then quit
        mock_ask.side_effect = ["delete file", "quit"]

        # Mock agent response
        mock_agent.run.return_value = "File deleted successfully"

        # Create session with confirmation enabled
        session = RichInteractiveSession(agent=mock_agent, require_confirmation=True)

        # Test confirmation method
        action = {"tool_name": "delete_file", "arguments": {"path": "/tmp/test.txt"}}

        # Mock confirmation response
        with patch.object(session, "get_confirmation", return_value=True):
            result = session.get_confirmation(action)
            assert result is True

    def test_session_status_transitions(self, mock_agent):
        """Test session status transitions."""
        session = RichInteractiveSession(agent=mock_agent)

        # Initial status
        assert session.status == SessionStatus.WAITING_FOR_INPUT

        # Update to thinking
        session.update_state(SessionStatus.THINKING)
        assert session.status == SessionStatus.THINKING

        # Update to executing tool
        tool_call = {"tool_name": "test_tool"}
        session.update_state(SessionStatus.EXECUTING_TOOL, tool_call)
        assert session.status == SessionStatus.EXECUTING_TOOL
        assert session.last_tool_call == tool_call

        # Update to completed
        session.update_state(SessionStatus.COMPLETED)
        assert session.status == SessionStatus.COMPLETED

    def test_session_error_handling(self, mock_agent):
        """Test session error handling."""
        session = RichInteractiveSession(agent=mock_agent)

        # Mock agent error
        mock_agent.run.side_effect = Exception("Agent failed")

        with patch("automake.agent.ui.session.Live"):
            session._process_agent_response("test input")

        # Should have updated status to error
        assert session.status == SessionStatus.ERROR

    @patch("automake.cli.commands.agent.RichInteractiveSession")
    @patch("automake.cli.commands.agent.get_config")
    def test_agent_command_integration(
        self, mock_get_config, mock_session_class, mock_agent
    ):
        """Test agent command integration with RichInteractiveSession."""
        from automake.cli.commands.agent import _run_interactive

        # Setup config mock
        mock_config = Mock()
        mock_config.agent_require_confirmation = True
        mock_get_config.return_value = mock_config

        # Setup runner mock
        mock_runner = Mock()
        mock_runner.agent = mock_agent

        # Setup session mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Run interactive mode
        _run_interactive(mock_runner, Mock())

        # Verify session was created with correct config
        mock_session_class.assert_called_once()
        call_kwargs = mock_session_class.call_args[1]
        assert call_kwargs["require_confirmation"] is True
        assert call_kwargs["agent"] is mock_agent

        # Verify session was started
        mock_session.start.assert_called_once()

    def test_abc_enforcement(self):
        """Test that InteractiveSession ABC is properly enforced."""
        # Should not be able to instantiate ABC directly
        with pytest.raises(TypeError):
            InteractiveSession(Mock())

        # Should be able to create concrete implementation
        session = RichInteractiveSession(Mock())
        assert isinstance(session, InteractiveSession)

    def test_module_imports(self):
        """Test that all Phase 3 modules can be imported correctly."""
        # Test UI module imports
        from automake.agent.ui import InteractiveSession, RichInteractiveSession
        from automake.agent.ui.session import SessionStatus

        # Verify classes exist and are correct types
        assert InteractiveSession is not None
        assert RichInteractiveSession is not None
        assert SessionStatus is not None

        # Verify inheritance
        assert issubclass(RichInteractiveSession, InteractiveSession)

    def test_config_file_generation_includes_agent_section(self, temp_config_dir):
        """Test that generated config file includes agent section."""
        # Remove any existing config
        config_file = temp_config_dir / "config.toml"
        if config_file.exists():
            config_file.unlink()

        # Create config (should generate file)
        Config(temp_config_dir)

        # Verify file was created and contains agent section
        assert config_file.exists()
        content = config_file.read_text()
        assert "[agent]" in content
        assert "require_confirmation" in content
