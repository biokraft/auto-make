"""Tests for animated interactive session functionality."""

from unittest.mock import Mock, patch

from rich.console import Console
from smolagents import ToolCallingAgent

from automake.agent.ui.session import RichInteractiveSession


class TestAnimatedInteractiveSession:
    """Test animated interactive session functionality."""

    def test_animation_methods_exist(self):
        """Test that the RichInteractiveSession has the new animation methods."""
        console = Mock(spec=Console)
        agent = Mock(spec=ToolCallingAgent)
        session = RichInteractiveSession(agent=agent, console=console)

        # Should have all three new animation methods
        assert hasattr(session, "display_thinking_animation")
        assert callable(session.display_thinking_animation)
        assert hasattr(session, "display_streaming_response")
        assert callable(session.display_streaming_response)
        assert hasattr(session, "display_animated_response")
        assert callable(session.display_animated_response)

    def test_display_thinking_animation_method_exists(self):
        """Test that RichInteractiveSession has display_thinking_animation method."""
        console = Mock(spec=Console)
        agent = Mock(spec=ToolCallingAgent)
        session = RichInteractiveSession(agent=agent, console=console)

        # Should have display_thinking_animation method
        assert hasattr(session, "display_thinking_animation")
        assert callable(session.display_thinking_animation)

    @patch("automake.agent.ui.session.get_formatter")
    def test_display_thinking_animation_with_livebox(self, mock_get_formatter):
        """Test display_thinking_animation uses LiveBox with animation."""
        # Setup mock formatter with live box capabilities
        mock_formatter = Mock()
        mock_live_box = Mock()
        mock_formatter.create_live_box.return_value = mock_live_box
        mock_get_formatter.return_value = mock_formatter

        console = Mock(spec=Console)
        agent = Mock(spec=ToolCallingAgent)
        session = RichInteractiveSession(agent=agent, console=console)

        # Call display_thinking_animation
        session.display_thinking_animation("Processing your request...")

        # Should create a live box
        mock_formatter.create_live_box.assert_called_once_with(
            title="AI Processing", refresh_per_second=4.0, transient=False
        )

        # Should call animate_text on the live box
        mock_live_box.animate_text.assert_called_once_with("Processing your request...")

    def test_display_streaming_response_method_exists(self):
        """Test that RichInteractiveSession has display_streaming_response method."""
        console = Mock(spec=Console)
        agent = Mock(spec=ToolCallingAgent)
        session = RichInteractiveSession(agent=agent, console=console)

        # Should have display_streaming_response method
        assert hasattr(session, "display_streaming_response")
        assert callable(session.display_streaming_response)

    @patch("automake.agent.ui.session.get_formatter")
    def test_display_streaming_response_with_animation(self, mock_get_formatter):
        """Test display_streaming_response uses animation for streaming content."""
        # Setup mock formatter
        mock_formatter = Mock()
        mock_live_box = Mock()
        mock_formatter.create_live_box.return_value = mock_live_box
        mock_get_formatter.return_value = mock_formatter

        console = Mock(spec=Console)
        agent = Mock(spec=ToolCallingAgent)
        session = RichInteractiveSession(agent=agent, console=console)

        # Simulate streaming response
        response_chunks = ["Hello", " world", "!", " How", " are", " you?"]

        # Call display_streaming_response
        session.display_streaming_response(response_chunks, title="AI Response")

        # Should create a live box
        mock_formatter.create_live_box.assert_called_once_with(
            title="AI Response", refresh_per_second=8.0, transient=False
        )

        # Should animate the complete response
        expected_full_response = "".join(response_chunks)
        mock_live_box.animate_text.assert_called_once_with(expected_full_response)

    def test_display_animated_response_method_exists(self):
        """Test that RichInteractiveSession has display_animated_response method."""
        console = Mock(spec=Console)
        agent = Mock(spec=ToolCallingAgent)
        session = RichInteractiveSession(agent=agent, console=console)

        # Should have display_animated_response method
        assert hasattr(session, "display_animated_response")
        assert callable(session.display_animated_response)

    @patch("automake.agent.ui.session.get_formatter")
    def test_display_animated_response_uses_animation(self, mock_get_formatter):
        """Test display_animated_response uses animation for responses."""
        # Setup mock formatter
        mock_formatter = Mock()
        mock_get_formatter.return_value = mock_formatter

        console = Mock(spec=Console)
        agent = Mock(spec=ToolCallingAgent)
        session = RichInteractiveSession(agent=agent, console=console)

        # Call display_animated_response
        session.display_animated_response(
            "Test response from agent", title="Agent Response"
        )

        # Should call print_box with animation (through formatter)
        mock_formatter.print_box.assert_called_once_with(
            "Test response from agent", title="Agent Response"
        )

    @patch("automake.agent.ui.session.get_formatter")
    def test_animated_methods_error_handling(self, mock_get_formatter):
        """Test that animated methods handle errors gracefully."""
        # Setup mock formatter that raises exception
        mock_formatter = Mock()
        mock_formatter.create_live_box.side_effect = Exception("LiveBox error")
        mock_get_formatter.return_value = mock_formatter

        console = Mock(spec=Console)
        agent = Mock(spec=ToolCallingAgent)
        session = RichInteractiveSession(agent=agent, console=console)

        # Should not raise exception
        session.display_thinking_animation("Test message")

        # Should fallback to regular display
        mock_formatter.print_box.assert_called_once()

    def test_animation_preserves_existing_functionality(self):
        """Test that animation doesn't break existing session functionality."""
        console = Mock(spec=Console)
        agent = Mock(spec=ToolCallingAgent)
        session = RichInteractiveSession(agent=agent, console=console)

        # Test existing methods still exist and work
        assert hasattr(session, "start")
        assert hasattr(session, "render")
        assert hasattr(session, "get_user_input")
        assert hasattr(session, "get_confirmation")
        assert hasattr(session, "update_state")

        # All should be callable
        assert callable(session.start)
        assert callable(session.render)
        assert callable(session.get_user_input)
        assert callable(session.get_confirmation)
        assert callable(session.update_state)
