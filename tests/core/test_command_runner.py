"""Tests for the Command Runner module."""

import subprocess
from unittest.mock import MagicMock, Mock, patch

import pytest

from automake.core.command_runner import CommandRunner, CommandRunnerError


class TestCommandRunner:
    """Test cases for the CommandRunner class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CommandRunner()

    @patch("subprocess.Popen")
    def test_run_success(self, mock_popen: MagicMock) -> None:
        """Test successful command execution."""
        # Mock process
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout.readline.side_effect = ["line1\n", "line2\n", ""]
        mock_process.wait.return_value = None
        mock_popen.return_value = mock_process

        result = self.runner.run("build", capture_output=True)

        # Verify the command was called correctly
        mock_popen.assert_called_once_with(
            "make build",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            preexec_fn=self.runner._create_process_group,
        )

        # Check result
        assert result == "line1\nline2"

    @patch("subprocess.Popen")
    def test_run_with_live_box(self, mock_popen: MagicMock) -> None:
        """Test command execution with LiveBox integration."""
        # Mock process
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout.readline.side_effect = ["Building...\n", "Done!\n", ""]
        mock_process.wait.return_value = None
        mock_popen.return_value = mock_process

        # Mock LiveBox
        mock_live_box = MagicMock()

        self.runner.run("build", live_box=mock_live_box)

        # Verify LiveBox was updated
        assert mock_live_box.update.call_count >= 2  # Initial + output updates

        # Check that the initial update starts with empty content
        initial_call = mock_live_box.update.call_args_list[0]
        assert initial_call[0][0] == ""

        # Check that the final update contains the command output
        final_call = mock_live_box.update.call_args_list[-1]
        assert "Building..." in final_call[0][0]
        assert "Done!" in final_call[0][0]

    @patch("subprocess.Popen")
    def test_run_failure(self, mock_popen: MagicMock) -> None:
        """Test command execution failure."""
        # Mock process that fails
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.stdout.readline.side_effect = ["error output\n", ""]
        mock_process.wait.return_value = None
        mock_popen.return_value = mock_process

        with pytest.raises(CommandRunnerError, match="Command 'test' failed"):
            self.runner.run("test")

    @patch("subprocess.Popen")
    def test_run_failure_with_live_box(self, mock_popen: MagicMock) -> None:
        """Test command execution failure with live box."""
        # Mock process that fails
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.stdout.readline.side_effect = ["error output\n", ""]
        mock_process.wait.return_value = None
        mock_popen.return_value = mock_process

        mock_live_box = MagicMock()

        with pytest.raises(CommandRunnerError, match="Command 'test' failed"):
            self.runner.run("test", live_box=mock_live_box)

    @patch("subprocess.Popen")
    def test_run_file_not_found_with_live_box(self, mock_popen: MagicMock) -> None:
        """Test command execution when make is not found, with LiveBox."""
        mock_popen.side_effect = FileNotFoundError()

        # Mock LiveBox
        mock_live_box = MagicMock()

        with pytest.raises(CommandRunnerError, match="`make` command not found"):
            self.runner.run("test", live_box=mock_live_box)

        # Verify LiveBox was updated with error
        error_call_found = False
        for call in mock_live_box.update.call_args_list:
            if "❌ Error:" in call[0][0] and "make` command not found" in call[0][0]:
                error_call_found = True
                break
        assert error_call_found, "LiveBox should show file not found error"

    @patch("subprocess.Popen")
    def test_run_unexpected_error_with_live_box(self, mock_popen: MagicMock) -> None:
        """Test command execution with unexpected error and LiveBox."""
        mock_popen.side_effect = RuntimeError("Unexpected error")

        # Mock LiveBox
        mock_live_box = MagicMock()

        with pytest.raises(CommandRunnerError, match="An unexpected error occurred"):
            self.runner.run("test", live_box=mock_live_box)

        # Verify LiveBox was updated with error
        error_call_found = False
        for call in mock_live_box.update.call_args_list:
            if "❌ Error:" in call[0][0] and "unexpected error" in call[0][0]:
                error_call_found = True
                break
        assert error_call_found, "LiveBox should show unexpected error"

    @patch("subprocess.Popen")
    def test_run_output_buffering_with_live_box(self, mock_popen: MagicMock) -> None:
        """Test that output is properly buffered and limited in LiveBox."""
        # Mock process with many lines of output
        mock_process = Mock()
        mock_process.returncode = 0
        # Generate 25 lines of output (more than the 20 line limit)
        output_lines = [f"Line {i}\n" for i in range(25)] + [""]
        mock_process.stdout.readline.side_effect = output_lines
        mock_process.wait.return_value = None
        mock_popen.return_value = mock_process

        # Mock LiveBox
        mock_live_box = MagicMock()

        self.runner.run("test", live_box=mock_live_box)

        # Check that LiveBox updates contain limited output
        # The last update should contain only the last 20 lines
        final_update = mock_live_box.update.call_args_list[-1][0][0]
        line_count = final_update.count("Line")
        assert line_count <= 20, "Output should be limited to 20 lines"

    @patch("subprocess.Popen")
    def test_run_file_not_found(self, mock_popen: MagicMock) -> None:
        """Test command execution when make is not found."""
        mock_popen.side_effect = FileNotFoundError()

        with pytest.raises(CommandRunnerError, match="`make` command not found"):
            self.runner.run("test")

    @patch("subprocess.Popen")
    def test_run_unexpected_error(self, mock_popen: MagicMock) -> None:
        """Test command execution with unexpected error."""
        mock_popen.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(CommandRunnerError, match="An unexpected error occurred"):
            self.runner.run("test")
