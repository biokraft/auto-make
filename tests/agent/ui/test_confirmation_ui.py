"""Tests for enhanced confirmation UI in interactive sessions."""

from unittest.mock import Mock, patch

import pytest
from rich.console import Console

from automake.agent.ui.session import RichInteractiveSession


class TestConfirmationUI:
    """Test enhanced confirmation UI functionality."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent."""
        return Mock()

    @pytest.fixture
    def session(self, mock_agent):
        """Create a RichInteractiveSession for testing."""
        console = Console(file=Mock(), width=80)  # Mock file to prevent actual output
        return RichInteractiveSession(
            agent=mock_agent, console=console, require_confirmation=True
        )

    def test_get_confirmation_displays_tool_name(self, session):
        """Test that confirmation displays the tool name clearly."""
        action = {"tool_name": "run_command", "arguments": {"command": "ls -la"}}

        with patch("automake.agent.ui.session.Prompt.ask", return_value="y"):
            result = session.get_confirmation(action)
            assert result is True

    def test_get_confirmation_displays_arguments(self, session):
        """Test that confirmation displays tool arguments."""
        action = {
            "tool_name": "write_file",
            "arguments": {"filename": "test.py", "content": "print('hello world')"},
        }

        with patch("automake.agent.ui.session.Prompt.ask", return_value="y"):
            result = session.get_confirmation(action)
            assert result is True

    def test_get_confirmation_handles_no_arguments(self, session):
        """Test that confirmation works when no arguments are provided."""
        action = {"tool_name": "list_files"}

        with patch("automake.agent.ui.session.Prompt.ask", return_value="y"):
            result = session.get_confirmation(action)
            assert result is True

    def test_get_confirmation_returns_false_on_rejection(self, session):
        """Test that confirmation returns False when user rejects."""
        action = {
            "tool_name": "delete_file",
            "arguments": {"filename": "important.txt"},
        }

        with patch("automake.agent.ui.session.Prompt.ask", return_value="n"):
            result = session.get_confirmation(action)
            assert result is False

    def test_get_confirmation_accepts_various_yes_responses(self, session):
        """Test that confirmation accepts various forms of 'yes'."""
        action = {"tool_name": "test_tool"}

        for response in ["y", "yes", "Y", "YES"]:
            with patch("automake.agent.ui.session.Prompt.ask", return_value=response):
                result = session.get_confirmation(action)
                assert result is True

    def test_get_confirmation_accepts_various_no_responses(self, session):
        """Test that confirmation accepts various forms of 'no'."""
        action = {"tool_name": "test_tool"}

        for response in ["n", "no", "N", "NO"]:
            with patch("automake.agent.ui.session.Prompt.ask", return_value=response):
                result = session.get_confirmation(action)
                assert result is False

    def test_get_confirmation_formats_complex_arguments(self, session):
        """Test that confirmation properly formats complex argument structures."""
        action = {
            "tool_name": "complex_operation",
            "arguments": {
                "files": ["file1.py", "file2.py"],
                "options": {"recursive": True, "force": False},
                "count": 42,
            },
        }

        with patch("automake.agent.ui.session.Prompt.ask", return_value="y"):
            result = session.get_confirmation(action)
            assert result is True

    def test_get_confirmation_enhanced_display(self, session):
        """Test enhanced confirmation display shows formatted action details."""
        action = {
            "tool_name": "run_command",
            "arguments": {
                "command": "rm -rf /important/data",
                "working_dir": "/home/user",
            },
        }

        # Mock console.print to capture what gets displayed
        with (
            patch.object(session.console, "print") as mock_print,
            patch("automake.agent.ui.session.Prompt.ask", return_value="y"),
        ):
            result = session.get_confirmation(action)

            # Verify the result
            assert result is True

            # Verify console.print was called (twice: newline + panel)
            assert mock_print.call_count >= 2

            # The second call should be the panel with the action details
            panel_call = mock_print.call_args_list[1]
            panel_arg = panel_call[0][0]

            # Verify it's a Panel object
            from rich.panel import Panel

            assert isinstance(panel_arg, Panel)

            # Verify the panel contains the expected tool name in its content
            panel_content = str(panel_arg.renderable)
            assert "run_command" in panel_content
            assert "command" in panel_content
