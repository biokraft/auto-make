"""Tests for the interactive module."""

from unittest.mock import patch

from automake.core.interactive import select_command


@patch("questionary.select")
def test_select_command_selects_command(mock_select):
    """Test that a command is correctly selected."""
    mock_select.return_value.ask.return_value = "build"
    commands = ["build", "test"]
    result = select_command(commands)
    assert result == "build"
    mock_select.assert_called_once()


@patch("questionary.select")
def test_select_command_aborts(mock_select):
    """Test that aborting returns None."""
    mock_select.return_value.ask.return_value = "abort"
    commands = ["build", "test"]
    result = select_command(commands)
    assert result is None


@patch("questionary.select")
def test_select_command_no_selection(mock_select):
    """Test that making no selection (e.g., Ctrl+C) returns None."""
    mock_select.return_value.ask.return_value = None
    commands = ["build", "test"]
    result = select_command(commands)
    assert result is None


def test_select_command_no_commands():
    """Test that it returns None if no commands are provided."""
    result = select_command([])
    assert result is None


@patch("questionary.select", side_effect=KeyboardInterrupt)
def test_select_command_keyboard_interrupt(mock_select):
    """Test that KeyboardInterrupt is handled gracefully."""
    commands = ["build", "test"]
    result = select_command(commands)
    assert result is None
