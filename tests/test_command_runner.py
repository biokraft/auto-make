"""Tests for the Command Runner module."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from automake.core.command_runner import CommandRunner, CommandRunnerError


@patch("subprocess.Popen")
def test_command_runner_success(mock_popen):
    """Test successful command execution."""
    # Mock Popen to simulate a successful command run
    process_mock = MagicMock()
    process_mock.returncode = 0
    process_mock.stdout.readline.side_effect = ["output\n", ""]
    process_mock.stderr.read.return_value = ""
    mock_popen.return_value = process_mock

    runner = CommandRunner()
    runner.run("test")

    mock_popen.assert_called_with(
        "make test",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    process_mock.wait.assert_called_once()


@patch("subprocess.Popen")
def test_command_runner_failure(mock_popen):
    """Test that CommandRunnerError is raised on command failure."""
    process_mock = MagicMock()
    process_mock.returncode = 1
    process_mock.stdout.readline.return_value = ""
    process_mock.stderr.read.return_value = "error details"
    mock_popen.return_value = process_mock

    runner = CommandRunner()
    with pytest.raises(CommandRunnerError, match="failed with exit code 1"):
        runner.run("fail")


@patch("subprocess.Popen")
def test_command_runner_capture_output(mock_popen):
    """Test that output is captured correctly."""
    process_mock = MagicMock()
    process_mock.returncode = 0
    process_mock.stdout.readline.side_effect = ["line 1\n", "line 2\n", ""]
    mock_popen.return_value = process_mock

    runner = CommandRunner()
    output = runner.run("test", capture_output=True)
    assert output == "line 1\nline 2\n"


def test_command_runner_make_not_found():
    """Test that an error is raised if `make` is not found."""
    with patch("subprocess.Popen", side_effect=FileNotFoundError):
        runner = CommandRunner()
        with pytest.raises(CommandRunnerError, match="`make` command not found"):
            runner.run("test")
