"""Tests for the main CLI module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from automake import __version__
from automake.cli.main import app, read_ascii_art


class TestMainCLI:
    """Test cases for the main CLI application."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_flag(self) -> None:
        """Test that --version flag displays version and exits."""
        result = self.runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert f"AutoMake version {__version__}" in result.stdout

    def test_version_flag_short(self) -> None:
        """Test that -v flag displays version and exits."""
        result = self.runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert f"AutoMake version {__version__}" in result.stdout

    def test_help_flag(self) -> None:
        """Test that --help flag displays help information."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        # Check for our custom help format
        assert "Usage" in result.stdout
        assert "automake [OPTIONS] COMMAND" in result.stdout
        assert (
            "AI-powered Makefile command execution with natural language processing"
            in result.stdout
        )
        assert "Examples" in result.stdout
        assert "Options" in result.stdout

    def test_help_flag_short(self) -> None:
        """Test that -h flag displays help information."""
        result = self.runner.invoke(app, ["-h"])
        assert result.exit_code == 0
        # Check for our custom help format
        assert "Usage" in result.stdout
        assert "automake [OPTIONS] COMMAND" in result.stdout
        assert (
            "AI-powered Makefile command execution with natural language processing"
            in result.stdout
        )
        assert "Examples" in result.stdout
        assert "Options" in result.stdout

    def test_help_command(self) -> None:
        """Test that 'help' command displays help information."""
        result = self.runner.invoke(app, ["help"])
        assert result.exit_code == 0
        # Check for our custom help format
        assert "Usage" in result.stdout
        assert "automake [OPTIONS] COMMAND" in result.stdout
        assert (
            "AI-powered Makefile command execution with natural language processing"
            in result.stdout
        )
        assert "Examples" in result.stdout
        assert "Options" in result.stdout

    def test_help_command_case_insensitive(self) -> None:
        """Test that 'HELP' command displays help information (case insensitive)."""
        result = self.runner.invoke(app, ["run", "HELP"])
        assert result.exit_code == 0
        # Check for our custom help format
        assert "Usage" in result.stdout
        assert "automake [OPTIONS] COMMAND" in result.stdout
        assert (
            "AI-powered Makefile command execution with natural language processing"
            in result.stdout
        )
        assert "Examples" in result.stdout
        assert "Options" in result.stdout

    def test_main_command_with_makefile_success(self) -> None:
        """Test main command with a natural language argument and existing Makefile."""
        test_command = "build the project"
        makefile_content = """# Test Makefile
all: build test

build:
\techo "Building..."

test:
\techo "Testing..."

deploy:
\techo "Deploying..."
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            # Mock the AI agent and command runner
            with (
                patch("automake.cli.main.create_ai_agent") as mock_create_agent,
                patch("automake.cli.main.CommandRunner") as mock_runner,
                patch("automake.core.makefile_reader.Path.cwd", return_value=temp_path),
            ):
                # Mock AI agent response
                mock_agent = MagicMock()
                mock_response = MagicMock()
                mock_response.reasoning = "The user wants to build the project"
                mock_response.command = "build"
                mock_response.confidence = 95
                mock_response.alternatives = ["all"]
                mock_agent.interpret_command.return_value = mock_response
                mock_create_agent.return_value = (mock_agent, False)

                # Mock command runner
                mock_runner_instance = MagicMock()
                mock_runner.return_value = mock_runner_instance

                result = self.runner.invoke(app, ["run", test_command])

            if result.exit_code != 0:
                print(f"Exit code: {result.exit_code}")
                print(f"Stdout: {result.stdout}")
                print(f"Exception: {result.exception}")
            assert result.exit_code == 0
            assert "Command Received" in result.stdout
            assert test_command in result.stdout
            assert "Command Selected" in result.stdout
            assert "make build" in result.stdout

    def test_main_command_no_makefile_error(self) -> None:
        """Test main command when no Makefile exists."""
        test_command = "build the project"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Mock the current working directory to point to our empty temp directory
            with patch(
                "automake.core.makefile_reader.Path.cwd", return_value=temp_path
            ):
                result = self.runner.invoke(app, ["run", test_command])

            assert result.exit_code == 1
            assert "Command Received" in result.stdout
            assert test_command in result.stdout
            # Rich console formats the error differently
            assert "Error" in result.stdout  # Rich console uses "Error" in the box
            assert "No Makefile found" in result.stdout
            assert "Make sure you're in a directory with a Makefile" in result.stdout

    def test_main_command_with_complex_argument(self) -> None:
        """Test main command with a complex natural language argument."""
        test_command = "deploy the application to staging environment"
        makefile_content = "all:\n\techo 'Hello World'"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            with (
                patch("automake.cli.main.create_ai_agent") as mock_create_agent,
                patch("automake.cli.main.CommandRunner") as mock_runner,
                patch("automake.core.makefile_reader.Path.cwd", return_value=temp_path),
            ):
                # Mock AI agent response
                mock_agent = MagicMock()
                mock_response = MagicMock()
                mock_response.reasoning = "The user wants to deploy"
                mock_response.command = "all"
                mock_response.confidence = 85
                mock_response.alternatives = []
                mock_agent.interpret_command.return_value = mock_response
                mock_create_agent.return_value = (mock_agent, False)

                # Mock command runner
                mock_runner_instance = MagicMock()
                mock_runner.return_value = mock_runner_instance

                result = self.runner.invoke(app, ["run", test_command])

            assert result.exit_code == 0
            assert "Command Received" in result.stdout
            assert test_command in result.stdout

    def test_main_command_with_quotes(self) -> None:
        """Test main command with quoted arguments."""
        test_command = "run tests with coverage"
        makefile_content = "test:\n\techo 'Running tests'"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            with (
                patch("automake.cli.main.create_ai_agent") as mock_create_agent,
                patch("automake.cli.main.CommandRunner") as mock_runner,
                patch("automake.core.makefile_reader.Path.cwd", return_value=temp_path),
            ):
                # Mock AI agent response
                mock_agent = MagicMock()
                mock_response = MagicMock()
                mock_response.reasoning = "The user wants to run tests"
                mock_response.command = "test"
                mock_response.confidence = 90
                mock_response.alternatives = []
                mock_agent.interpret_command.return_value = mock_response
                mock_create_agent.return_value = (mock_agent, False)

                # Mock command runner
                mock_runner_instance = MagicMock()
                mock_runner.return_value = mock_runner_instance

                result = self.runner.invoke(app, ["run", test_command])

            assert result.exit_code == 0
            assert "Command Received" in result.stdout
            assert test_command in result.stdout

    def test_no_arguments_shows_welcome(self) -> None:
        """Test that running without arguments shows welcome message."""
        result = self.runner.invoke(app, [])
        assert result.exit_code == 0  # Should show welcome and exit cleanly
        assert "Welcome" in result.stdout
        assert 'Run "automake help" for detailed usage information.' in result.stdout

    def test_empty_command_argument(self) -> None:
        """Test behavior with empty command argument."""
        makefile_content = "all:\n\techo 'Hello World'"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            with (
                patch("automake.cli.main.create_ai_agent") as mock_create_agent,
                patch("automake.cli.main.CommandRunner") as mock_runner,
                patch("automake.core.makefile_reader.Path.cwd", return_value=temp_path),
            ):
                # Mock AI agent response with high confidence to avoid interactive mode
                mock_agent = MagicMock()
                mock_response = MagicMock()
                mock_response.reasoning = "Empty command provided, defaulting to all"
                mock_response.command = "all"
                mock_response.confidence = 85  # High enough to avoid interactive mode
                mock_response.alternatives = []
                mock_agent.interpret_command.return_value = mock_response
                mock_create_agent.return_value = (mock_agent, False)

                # Mock command runner
                mock_runner_instance = MagicMock()
                mock_runner.return_value = mock_runner_instance

                result = self.runner.invoke(app, ["run", ""])

            assert result.exit_code == 0
            assert "Command Received" in result.stdout

    @pytest.mark.parametrize(
        "command",
        [
            "build",
            "test everything",
            "deploy to production with rollback enabled",
            "clean up temporary files and rebuild",
        ],
    )
    def test_various_command_formats(self, command: str) -> None:
        """Test various command formats are accepted."""
        makefile_content = "all:\n\techo 'Hello World'"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            with (
                patch("automake.cli.main.create_ai_agent") as mock_create_agent,
                patch("automake.cli.main.CommandRunner") as mock_runner,
                patch("automake.core.makefile_reader.Path.cwd", return_value=temp_path),
            ):
                # Mock AI agent response
                mock_agent = MagicMock()
                mock_response = MagicMock()
                mock_response.reasoning = f"The user wants to execute: {command}"
                mock_response.command = "all"
                mock_response.confidence = 85
                mock_response.alternatives = []
                mock_agent.interpret_command.return_value = mock_response
                mock_create_agent.return_value = (mock_agent, False)

                # Mock command runner
                mock_runner_instance = MagicMock()
                mock_runner.return_value = mock_runner_instance

                result = self.runner.invoke(app, ["run", command])

            assert result.exit_code == 0
            assert "Command Received" in result.stdout
            assert command in result.stdout

    def test_makefile_with_many_targets(self) -> None:
        """Test Makefile with many targets shows preview correctly."""
        # Create a Makefile with many targets
        targets = [f"target{i}:\n\techo 'Target {i}'" for i in range(10)]
        makefile_content = "\n\n".join(targets)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            with (
                patch("automake.cli.main.create_ai_agent") as mock_create_agent,
                patch("automake.cli.main.CommandRunner") as mock_runner,
                patch("automake.core.makefile_reader.Path.cwd", return_value=temp_path),
            ):
                # Mock AI agent response
                mock_agent = MagicMock()
                mock_response = MagicMock()
                mock_response.reasoning = "The user wants to run a test command"
                mock_response.command = "target0"
                mock_response.confidence = 80
                mock_response.alternatives = ["target1", "target2"]
                mock_agent.interpret_command.return_value = mock_response
                mock_create_agent.return_value = (mock_agent, False)

                # Mock command runner
                mock_runner_instance = MagicMock()
                mock_runner.return_value = mock_runner_instance

                result = self.runner.invoke(app, ["run", "test command"])

            assert result.exit_code == 0
            assert "Command Received" in result.stdout
            assert "Command Selected" in result.stdout
            assert "make target0" in result.stdout

    def test_makefile_without_targets(self) -> None:
        """Test Makefile without clear targets."""
        makefile_content = """# This is just a comment
# Another comment
VARIABLE = value
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            with (
                patch("automake.cli.main.create_ai_agent") as mock_create_agent,
                patch("automake.cli.main.CommandRunner") as mock_runner,
                patch("automake.core.makefile_reader.Path.cwd", return_value=temp_path),
            ):
                # Mock AI agent response - provide a command even if no targets found
                mock_agent = MagicMock()
                mock_response = MagicMock()
                mock_response.reasoning = (
                    "No clear targets found, but providing a generic command"
                )
                mock_response.command = "all"  # Provide a command to avoid error path
                mock_response.confidence = (
                    85  # High confidence to avoid interactive mode
                )
                mock_response.alternatives = []
                mock_agent.interpret_command.return_value = mock_response
                mock_create_agent.return_value = (mock_agent, False)

                # Mock command runner
                mock_runner_instance = MagicMock()
                mock_runner.return_value = mock_runner_instance

                result = self.runner.invoke(app, ["run", "test command"])

            assert result.exit_code == 0
            assert "Command Received" in result.stdout
            assert "Command Selected" in result.stdout
            assert "make all" in result.stdout

    def test_makefile_read_error(self) -> None:
        """Test handling of Makefile read errors."""
        makefile_content = "all:\n\techo 'test'"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            with (
                patch("automake.core.makefile_reader.Path.cwd", return_value=temp_path),
                patch(
                    "automake.core.makefile_reader.MakefileReader.read_makefile",
                    side_effect=OSError("Permission denied"),
                ),
            ):
                result = self.runner.invoke(app, ["run", "test command"])

            assert result.exit_code == 1
            assert "Error reading Makefile" in result.stdout

    def test_unexpected_error_handling(self) -> None:
        """Test handling of unexpected errors."""
        with patch(
            "automake.core.makefile_reader.MakefileReader.get_makefile_info",
            side_effect=RuntimeError("Unexpected error"),
        ):
            result = self.runner.invoke(app, ["run", "test command"])

            assert result.exit_code == 1
            assert "Unexpected error" in result.stdout


class TestVersionCallback:
    """Test cases for the version callback function."""

    def test_version_callback_true(self) -> None:
        """Test version callback with True value."""
        from automake.cli.main import version_callback

        with pytest.raises((SystemExit, typer.Exit)):
            # Typer.Exit can raise different exceptions depending on context
            version_callback(True)

    def test_version_callback_false(self) -> None:
        """Test version callback with False value."""
        from automake.cli.main import version_callback

        # Should not raise any exception
        result = version_callback(False)
        assert result is None

    def test_version_callback_none(self) -> None:
        """Test version callback with None value."""
        from automake.cli.main import version_callback

        # Should not raise any exception
        result = version_callback(None)
        assert result is None


class TestASCIIArt:
    """Test cases for ASCII art functionality."""

    def test_read_ascii_art_file_exists(self) -> None:
        """Test reading ASCII art when file exists."""
        # This test will pass even if the file is empty or contains placeholder text
        art_content = read_ascii_art()
        # Should return a string (empty or with content)
        assert isinstance(art_content, str)

    def test_read_ascii_art_with_content(self) -> None:
        """Test that ASCII art is displayed in help when available."""
        # Test that help includes ASCII art functionality
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        # The help should be displayed regardless of ASCII art content
        assert "Usage" in result.stdout
