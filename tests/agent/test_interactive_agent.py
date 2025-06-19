"""Tests for Phase 5: Interactive Agent Mode functionality.

This module tests the implementation of the interactive agent mode using the
RichInteractiveSession and the complete agent workflow.
"""

from unittest.mock import Mock, patch

import pytest
from rich.console import Console
from smolagents import ToolCallingAgent

from automake.agent.ui.session import (
    InteractiveSession,
    RichInteractiveSession,
    SessionStatus,
)


class TestInteractiveAgentMode:
    """Test suite for Phase 5 interactive agent mode."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock ToolCallingAgent for testing."""
        agent = Mock(spec=ToolCallingAgent)
        agent.run.return_value = "Test response from agent"
        return agent

    @pytest.fixture
    def mock_console(self):
        """Create a mock Console for testing."""
        return Mock(spec=Console)

    @pytest.fixture
    def rich_session(self, mock_agent, mock_console):
        """Create a RichInteractiveSession for testing."""
        return RichInteractiveSession(
            agent=mock_agent, console=mock_console, require_confirmation=False
        )

    def test_rich_interactive_session_initialization(self, mock_agent, mock_console):
        """Test that RichInteractiveSession initializes correctly."""
        session = RichInteractiveSession(
            agent=mock_agent, console=mock_console, require_confirmation=True
        )

        assert session.agent == mock_agent
        assert session.console == mock_console
        assert session.require_confirmation is True
        assert session.status == SessionStatus.WAITING_FOR_INPUT
        assert session.history == []
        assert session.last_tool_call is None

    def test_rich_interactive_session_is_interactive_session(self, rich_session):
        """Test that RichInteractiveSession implements InteractiveSession ABC."""
        assert isinstance(rich_session, InteractiveSession)

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_get_user_input(self, mock_prompt_ask, rich_session):
        """Test user input capture."""
        mock_prompt_ask.return_value = "test user input"

        result = rich_session.get_user_input()

        assert result == "test user input"
        mock_prompt_ask.assert_called_once_with("[bold cyan]You[/bold cyan]")

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_get_confirmation_yes(self, mock_prompt_ask, rich_session):
        """Test confirmation UI returns True for 'yes'."""
        mock_prompt_ask.return_value = "yes"
        action = {"tool_name": "test_tool", "arguments": {"arg1": "value1"}}

        result = rich_session.get_confirmation(action)

        assert result is True
        mock_prompt_ask.assert_called_once()

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_get_confirmation_no(self, mock_prompt_ask, rich_session):
        """Test confirmation UI returns False for 'no'."""
        mock_prompt_ask.return_value = "no"
        action = {"tool_name": "test_tool", "arguments": {"arg1": "value1"}}

        result = rich_session.get_confirmation(action)

        assert result is False

    def test_update_state_changes_status(self, rich_session):
        """Test that update_state changes the session status."""
        tool_call = {"tool_name": "test_tool"}

        rich_session.update_state(SessionStatus.EXECUTING_TOOL, tool_call)

        assert rich_session.status == SessionStatus.EXECUTING_TOOL
        assert rich_session.last_tool_call == tool_call

    def test_render_with_string_content(self, rich_session):
        """Test rendering with string content."""
        content = "Test content"

        # This should not raise an exception
        rich_session.render(content)

        # Verify the content was processed (we can't easily test the internal state)
        assert rich_session._current_content is not None

    @patch("automake.agent.ui.session.Live")
    @patch("automake.agent.ui.session.Prompt.ask")
    def test_process_agent_response_non_streaming(
        self, mock_prompt_ask, mock_live_class, rich_session
    ):
        """Test processing non-streaming agent response."""
        # Setup mocks
        mock_live = Mock()
        mock_live_class.return_value.__enter__.return_value = mock_live
        rich_session.agent.run.return_value = "Agent response"

        # Call the method
        rich_session._process_agent_response("test input")

        # Verify agent was called
        rich_session.agent.run.assert_called_once_with("test input", stream=True)

        # Verify history was updated
        assert len(rich_session.history) == 1
        assert rich_session.history[0]["role"] == "assistant"
        assert rich_session.history[0]["content"] == "Agent response"

    @patch("automake.agent.ui.session.Live")
    @patch("automake.agent.ui.session.Prompt.ask")
    def test_process_agent_response_streaming(
        self, mock_prompt_ask, mock_live_class, rich_session
    ):
        """Test processing streaming agent response."""
        # Setup mocks
        mock_live = Mock()
        mock_live_class.return_value.__enter__.return_value = mock_live
        rich_session.agent.run.return_value = iter(["chunk1", "chunk2", "chunk3"])

        # Call the method
        rich_session._process_agent_response("test input")

        # Verify agent was called
        rich_session.agent.run.assert_called_once_with("test input", stream=True)

        # Verify history was updated with accumulated response
        assert len(rich_session.history) == 1
        assert rich_session.history[0]["role"] == "assistant"
        assert rich_session.history[0]["content"] == "chunk1chunk2chunk3"

    @patch("automake.agent.ui.session.Live")
    @patch("automake.agent.ui.session.Prompt.ask")
    def test_process_agent_response_error_handling(
        self, mock_prompt_ask, mock_live_class, rich_session
    ):
        """Test error handling in agent response processing."""
        # Setup mocks
        mock_live = Mock()
        mock_live_class.return_value.__enter__.return_value = mock_live
        rich_session.agent.run.side_effect = Exception("Test error")

        # Call the method - should not raise
        rich_session._process_agent_response("test input")

        # Verify status was set to error
        assert rich_session.status == SessionStatus.ERROR

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_start_session_exit_commands(self, mock_prompt_ask, rich_session):
        """Test that start() handles exit commands correctly."""
        # Mock input sequence: normal input, then exit
        mock_prompt_ask.side_effect = ["exit"]

        # Mock the agent response processing
        with patch.object(rich_session, "_process_agent_response") as mock_process:
            rich_session.start()

            # Verify exit was handled and agent wasn't called
            mock_process.assert_not_called()

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_start_session_quit_commands(self, mock_prompt_ask, rich_session):
        """Test that start() handles quit commands correctly."""
        # Mock input sequence: quit command
        mock_prompt_ask.side_effect = ["quit"]

        # Mock the agent response processing
        with patch.object(rich_session, "_process_agent_response") as mock_process:
            rich_session.start()

            # Verify quit was handled and agent wasn't called
            mock_process.assert_not_called()

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_start_session_empty_input(self, mock_prompt_ask, rich_session):
        """Test that start() handles empty input correctly."""
        # Mock input sequence: empty input, then exit
        mock_prompt_ask.side_effect = ["", "exit"]

        # Mock the agent response processing
        with patch.object(rich_session, "_process_agent_response") as mock_process:
            rich_session.start()

            # Verify empty input was skipped and agent wasn't called
            mock_process.assert_not_called()

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_start_session_keyboard_interrupt(self, mock_prompt_ask, rich_session):
        """Test that start() handles KeyboardInterrupt correctly."""
        mock_prompt_ask.side_effect = KeyboardInterrupt()

        # Should handle the interrupt gracefully
        rich_session.start()

        # Verify console print was called for goodbye message
        rich_session.console.print.assert_called()

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_start_session_eof_error(self, mock_prompt_ask, rich_session):
        """Test that start() handles EOFError correctly."""
        mock_prompt_ask.side_effect = EOFError()

        # Should handle the EOF gracefully
        rich_session.start()

        # Verify console print was called for goodbye message
        rich_session.console.print.assert_called()

    def test_session_status_enum_values(self):
        """Test that SessionStatus enum has expected values."""
        assert SessionStatus.WAITING_FOR_INPUT.value == "waiting_for_input"
        assert SessionStatus.THINKING.value == "thinking"
        assert SessionStatus.EXECUTING_TOOL.value == "executing_tool"
        assert SessionStatus.COMPLETED.value == "completed"
        assert SessionStatus.ERROR.value == "error"

    def test_create_panel_method(self, rich_session):
        """Test that _create_panel creates a Panel correctly."""
        rich_session.render("Test content")
        panel = rich_session._create_panel()

        assert panel.title == "🤖 Agent"
        assert panel.title_align == "left"
        assert panel.border_style == "blue"


class TestInteractiveSessionABC:
    """Test the InteractiveSession abstract base class."""

    def test_interactive_session_is_abstract(self):
        """Test that InteractiveSession cannot be instantiated directly."""
        mock_agent = Mock(spec=ToolCallingAgent)

        with pytest.raises(TypeError):
            InteractiveSession(mock_agent)

    def test_interactive_session_abstract_methods(self):
        """Test that InteractiveSession defines the expected abstract methods."""
        # Get all abstract methods
        abstract_methods = InteractiveSession.__abstractmethods__

        expected_methods = {
            "start",
            "render",
            "get_user_input",
            "get_confirmation",
            "update_state",
        }

        assert abstract_methods == expected_methods


class TestPhase5Integration:
    """Integration tests for Phase 5 functionality."""

    @patch("automake.agent.ui.session.Live")
    @patch("automake.agent.ui.session.Prompt.ask")
    def test_full_interactive_session_workflow(self, mock_prompt_ask, mock_live_class):
        """Test a complete interactive session workflow."""
        # Setup
        mock_agent = Mock(spec=ToolCallingAgent)
        mock_agent.run.return_value = "Hello! I can help you with that."

        mock_console = Mock(spec=Console)
        mock_live = Mock()
        mock_live_class.return_value.__enter__.return_value = mock_live

        # Mock user input sequence: question, then exit
        mock_prompt_ask.side_effect = ["help me with something", "exit"]

        session = RichInteractiveSession(
            agent=mock_agent, console=mock_console, require_confirmation=False
        )

        # Run the session
        session.start()

        # Verify the workflow
        assert len(session.history) == 2  # User input + agent response
        assert session.history[0]["role"] == "user"
        assert session.history[0]["content"] == "help me with something"
        assert session.history[1]["role"] == "assistant"
        assert session.history[1]["content"] == "Hello! I can help you with that."

        # Verify agent was called correctly
        mock_agent.run.assert_called_once_with("help me with something", stream=True)

        # Verify console interactions
        assert mock_console.print.call_count >= 2  # Welcome message + goodbye
