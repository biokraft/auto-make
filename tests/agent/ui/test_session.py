"""Tests for the interactive session scaffolding."""

from unittest.mock import Mock, patch

import pytest
from rich.console import Console
from smolagents import ToolCallingAgent

from automake.agent.ui.session import (
    InteractiveSession,
    RichInteractiveSession,
    SessionStatus,
)


class TestInteractiveSession:
    """Test the InteractiveSession ABC."""

    def test_abstract_base_class(self):
        """Test that InteractiveSession is an abstract base class."""
        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            InteractiveSession(Mock())

    def test_initialization(self):
        """Test that concrete implementations can be initialized."""
        mock_agent = Mock(spec=ToolCallingAgent)

        # Create a minimal concrete implementation for testing
        class TestSession(InteractiveSession):
            def start(self):
                pass

            def render(self, content):
                pass

            def get_user_input(self):
                return ""

            def get_confirmation(self, action):
                return True

            def update_state(self, new_status, tool_call=None):
                pass

        session = TestSession(mock_agent)

        assert session.agent is mock_agent
        assert session.history == []
        assert session.status == SessionStatus.WAITING_FOR_INPUT
        assert session.last_tool_call is None


class TestRichInteractiveSession:
    """Test the RichInteractiveSession implementation."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        return Mock(spec=ToolCallingAgent)

    @pytest.fixture
    def mock_console(self):
        """Create a mock console for testing."""
        return Mock(spec=Console)

    @pytest.fixture
    def session(self, mock_agent, mock_console):
        """Create a RichInteractiveSession for testing."""
        return RichInteractiveSession(
            agent=mock_agent, console=mock_console, require_confirmation=False
        )

    def test_initialization(self, mock_agent, mock_console):
        """Test RichInteractiveSession initialization."""
        session = RichInteractiveSession(
            agent=mock_agent, console=mock_console, require_confirmation=True
        )

        assert session.agent is mock_agent
        assert session.console is mock_console
        assert session.require_confirmation is True
        assert session.history == []
        assert session.status == SessionStatus.WAITING_FOR_INPUT
        assert session._live is None

    def test_initialization_with_defaults(self, mock_agent):
        """Test RichInteractiveSession initialization with default console."""
        session = RichInteractiveSession(agent=mock_agent)

        assert session.agent is mock_agent
        assert isinstance(session.console, Console)
        assert session.require_confirmation is False

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_get_user_input(self, mock_ask, session):
        """Test getting user input."""
        mock_ask.return_value = "test input"

        result = session.get_user_input()

        assert result == "test input"
        mock_ask.assert_called_once_with("[bold cyan]You[/bold cyan]")

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_get_confirmation_yes(self, mock_ask, session):
        """Test confirmation with yes response."""
        mock_ask.return_value = "y"
        action = {"tool_name": "test_tool", "arguments": {"arg1": "value1"}}

        result = session.get_confirmation(action)

        assert result is True
        session.console.print.assert_called()

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_get_confirmation_no(self, mock_ask, session):
        """Test confirmation with no response."""
        mock_ask.return_value = "n"
        action = {"tool_name": "test_tool"}

        result = session.get_confirmation(action)

        assert result is False

    def test_update_state(self, session):
        """Test updating session state."""
        tool_call = {"tool_name": "test_tool"}

        session.update_state(SessionStatus.EXECUTING_TOOL, tool_call)

        assert session.status == SessionStatus.EXECUTING_TOOL
        assert session.last_tool_call == tool_call

    def test_render_with_live_display(self, session):
        """Test rendering with active live display."""
        mock_live = Mock()
        session._live = mock_live

        session.render("test content")

        mock_live.update.assert_called_once()

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_start_session_exit_command(self, mock_ask, session):
        """Test starting session and exiting with quit command."""
        mock_ask.return_value = "quit"

        # Mock the problematic _process_agent_response method
        session._process_agent_response = Mock()

        session.start()

        session.console.print.assert_any_call("\n[yellow]👋 Goodbye![/yellow]")

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_start_session_keyboard_interrupt(self, mock_ask, session):
        """Test starting session with keyboard interrupt."""
        mock_ask.side_effect = KeyboardInterrupt()

        # Mock the problematic _process_agent_response method
        session._process_agent_response = Mock()

        session.start()

        session.console.print.assert_any_call(
            "\n[yellow]👋 Session interrupted. Goodbye![/yellow]"
        )

    @patch("automake.agent.ui.session.Prompt.ask")
    def test_start_session_eof_error(self, mock_ask, session):
        """Test starting session with EOF error."""
        mock_ask.side_effect = EOFError()

        # Mock the problematic _process_agent_response method
        session._process_agent_response = Mock()

        session.start()

        session.console.print.assert_any_call(
            "\n[yellow]👋 Session ended. Goodbye![/yellow]"
        )

    def test_render_string_content_updates_current_content(self, session):
        """Test that render method updates current content with string."""
        session.render("test content")
        assert session._current_content.plain == "test content"

    def test_render_with_text_object(self, session):
        """Test that render method handles Text objects."""
        from rich.text import Text

        text_obj = Text("rich text content")
        session.render(text_obj)
        assert session._current_content.plain == "rich text content"

    def test_update_state_changes_status(self, session):
        """Test that update_state changes the session status."""
        session.update_state(SessionStatus.THINKING)
        assert session.status == SessionStatus.THINKING

    def test_update_state_with_tool_call(self, session):
        """Test that update_state stores tool call information."""
        tool_call = {"tool_name": "test_tool", "args": {"param": "value"}}
        session.update_state(SessionStatus.EXECUTING_TOOL, tool_call)
        assert session.status == SessionStatus.EXECUTING_TOOL
        assert session.last_tool_call == tool_call

    def test_create_panel(self, session):
        """Test creating a panel for display."""
        session._current_content = session._current_content.from_markup("test content")

        panel = session._create_panel()

        assert panel.title == "🤖 Agent"
        assert panel.border_style == "blue"


class TestSessionStatus:
    """Test the SessionStatus enum."""

    def test_status_values(self):
        """Test that all expected status values exist."""
        assert SessionStatus.WAITING_FOR_INPUT.value == "waiting_for_input"
        assert SessionStatus.THINKING.value == "thinking"
        assert SessionStatus.EXECUTING_TOOL.value == "executing_tool"
        assert SessionStatus.COMPLETED.value == "completed"
        assert SessionStatus.ERROR.value == "error"
