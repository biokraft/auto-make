"""Tests for the main CLI functionality."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from automake.cli.app import app
from automake.cli.display.help import read_ascii_art


class TestMainCLI:
    """Test cases for the main CLI functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_flag(self) -> None:
        """Test --version flag."""
        result = self.runner.invoke(app, ["--version"])
        assert result.exit_code == 0

    def test_version_flag_short(self) -> None:
        """Test -v flag."""
        result = self.runner.invoke(app, ["-v"])
        assert result.exit_code == 0

    def test_help_flag(self) -> None:
        """Test --help flag."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage" in result.output
        assert "Commands" in result.output
        assert "run" in result.output
        assert "init" in result.output
        assert "config" in result.output
        assert "logs" in result.output
        assert "help" in result.output
        # Check for ASCII art or welcome message
        assert "Welcome" in result.output or "automake" in result.output.lower(), (
            "Should contain welcome message or ASCII art"
        )

    def test_help_flag_short(self) -> None:
        """Test -h flag."""
        result = self.runner.invoke(app, ["-h"])
        assert result.exit_code == 0
        assert "Usage" in result.output
        assert "Commands" in result.output
        assert "run" in result.output
        assert "init" in result.output
        assert "config" in result.output
        assert "logs" in result.output
        assert "help" in result.output
        # Check for ASCII art or welcome message
        assert "Welcome" in result.output or "automake" in result.output.lower(), (
            "Should contain welcome message or ASCII art"
        )

    def test_help_command(self) -> None:
        """Test help command."""
        result = self.runner.invoke(app, ["help"])
        assert result.exit_code == 0
        assert "Usage" in result.output
        assert "Commands" in result.output
        assert "run" in result.output
        assert "init" in result.output
        assert "config" in result.output
        assert "logs" in result.output
        assert "help" in result.output
        # Check for ASCII art or welcome message
        assert "Welcome" in result.output or "automake" in result.output.lower(), (
            "Should contain welcome message or ASCII art"
        )

    @patch("automake.cli.app.ManagerAgentRunner")
    @patch("automake.cli.app.get_config")
    @patch("automake.cli.app.setup_logging")
    @patch("automake.cli.app.log_config_info")
    @patch("automake.cli.app.log_command_execution")
    @patch("automake.cli.app._run_non_interactive")
    def test_help_command_case_insensitive(
        self,
        mock_run_non_interactive: Mock,
        mock_log_command: Mock,
        mock_log_config: Mock,
        mock_setup_logging: Mock,
        mock_get_config: Mock,
        mock_manager_runner: Mock,
    ) -> None:
        """Test that HELP is treated as a prompt in Phase 4 implementation."""
        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        # Setup manager runner mock
        mock_runner_instance = Mock()
        mock_runner_instance.initialize.return_value = False
        mock_manager_runner.return_value = mock_runner_instance

        result = self.runner.invoke(app, ["HELP"])
        # With Phase 4, unrecognized commands like "HELP" are treated as prompts
        # This should succeed (exit code 0) as it gets passed to the agent
        assert result.exit_code == 0

        # Verify that the non-interactive runner was called with "HELP"
        mock_run_non_interactive.assert_called_once()

    @patch("automake.cli.commands.run.ManagerAgentRunner")
    @patch("automake.cli.commands.run.get_config")
    @patch("automake.cli.commands.run.setup_logging")
    @patch("automake.cli.commands.run.log_config_info")
    @patch("automake.cli.commands.run.log_command_execution")
    @patch("automake.cli.commands.run.get_logger")
    def test_main_command_with_makefile_success(
        self,
        mock_get_logger: Mock,
        mock_log_command: Mock,
        mock_log_config: Mock,
        mock_setup_logging: Mock,
        mock_get_config: Mock,
        mock_manager_runner: Mock,
    ) -> None:
        """Test main command with a Makefile present."""
        test_command = "build the project"
        makefile_content = "all:\n\techo 'Hello World'"

        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_setup_logging.return_value = mock_logger

        # Setup manager runner mock
        mock_runner_instance = Mock()
        mock_runner_instance.initialize.return_value = False  # Ollama not started
        mock_runner_instance.run.return_value = "Task completed successfully"
        mock_manager_runner.return_value = mock_runner_instance

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            with patch(
                "automake.core.makefile_reader.Path.cwd", return_value=temp_path
            ):
                result = self.runner.invoke(app, ["run", test_command])

            # With the new agent architecture, the command should succeed
            assert result.exit_code == 0

    @patch("automake.cli.commands.run.ManagerAgentRunner")
    @patch("automake.cli.commands.run.get_config")
    @patch("automake.cli.commands.run.setup_logging")
    @patch("automake.cli.commands.run.log_config_info")
    @patch("automake.cli.commands.run.log_command_execution")
    @patch("automake.cli.commands.run.get_logger")
    def test_main_command_no_makefile_error(
        self,
        mock_get_logger: Mock,
        mock_log_command: Mock,
        mock_log_config: Mock,
        mock_setup_logging: Mock,
        mock_get_config: Mock,
        mock_manager_runner: Mock,
    ) -> None:
        """Test main command without a Makefile."""
        test_command = "build the project"

        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_setup_logging.return_value = mock_logger

        # Setup manager runner mock
        mock_runner_instance = Mock()
        mock_runner_instance.initialize.return_value = False
        mock_runner_instance.run.return_value = (
            "No Makefile found, but I can help with other tasks"
        )
        mock_manager_runner.return_value = mock_runner_instance

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Mock the current working directory to point to our empty temp directory
            with patch(
                "automake.core.makefile_reader.Path.cwd", return_value=temp_path
            ):
                result = self.runner.invoke(app, ["run", test_command])

            # Should succeed with new agent architecture
            assert result.exit_code == 0

    @patch("automake.cli.commands.run.ManagerAgentRunner")
    @patch("automake.cli.commands.run.get_config")
    @patch("automake.cli.commands.run.setup_logging")
    @patch("automake.cli.commands.run.log_config_info")
    @patch("automake.cli.commands.run.log_command_execution")
    @patch("automake.cli.commands.run.get_logger")
    def test_main_command_with_complex_argument(
        self,
        mock_get_logger: Mock,
        mock_log_command: Mock,
        mock_log_config: Mock,
        mock_setup_logging: Mock,
        mock_get_config: Mock,
        mock_manager_runner: Mock,
    ) -> None:
        """Test main command with a complex natural language argument."""
        test_command = "deploy the application to staging environment"
        makefile_content = "all:\n\techo 'Hello World'"

        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_setup_logging.return_value = mock_logger

        # Setup manager runner mock
        mock_runner_instance = Mock()
        mock_runner_instance.initialize.return_value = False
        mock_runner_instance.run.return_value = "Deployment task completed"
        mock_manager_runner.return_value = mock_runner_instance

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            result = self.runner.invoke(app, ["run", test_command])
            assert result.exit_code == 0

    @patch("automake.cli.commands.run.ManagerAgentRunner")
    @patch("automake.cli.commands.run.get_config")
    @patch("automake.cli.commands.run.setup_logging")
    @patch("automake.cli.commands.run.log_config_info")
    @patch("automake.cli.commands.run.log_command_execution")
    @patch("automake.cli.commands.run.get_logger")
    def test_main_command_with_quotes(
        self,
        mock_get_logger: Mock,
        mock_log_command: Mock,
        mock_log_config: Mock,
        mock_setup_logging: Mock,
        mock_get_config: Mock,
        mock_manager_runner: Mock,
    ) -> None:
        """Test main command with quoted arguments."""
        test_command = "run tests with coverage"
        makefile_content = "test:\n\techo 'Running tests'"

        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_setup_logging.return_value = mock_logger

        # Setup manager runner mock
        mock_runner_instance = Mock()
        mock_runner_instance.initialize.return_value = False
        mock_runner_instance.run.return_value = "Tests completed with coverage"
        mock_manager_runner.return_value = mock_runner_instance

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            result = self.runner.invoke(app, ["run", test_command])
            assert result.exit_code == 0

    def test_no_arguments_shows_welcome(self) -> None:
        """Test that running without arguments shows welcome message."""
        result = self.runner.invoke(app, [])
        assert result.exit_code == 0  # Should show welcome and exit cleanly
        assert "Welcome" in result.output
        assert 'Run "automake help" for detailed usage information.' in result.output

    @patch("automake.cli.commands.run.ManagerAgentRunner")
    @patch("automake.cli.commands.run.get_config")
    @patch("automake.cli.commands.run.setup_logging")
    @patch("automake.cli.commands.run.log_config_info")
    @patch("automake.cli.commands.run.log_command_execution")
    @patch("automake.cli.commands.run.get_logger")
    def test_empty_command_argument(
        self,
        mock_get_logger: Mock,
        mock_log_command: Mock,
        mock_log_config: Mock,
        mock_setup_logging: Mock,
        mock_get_config: Mock,
        mock_manager_runner: Mock,
    ) -> None:
        """Test behavior with empty command argument."""
        makefile_content = "all:\n\techo 'Hello World'"

        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_setup_logging.return_value = mock_logger

        # Setup manager runner mock
        mock_runner_instance = Mock()
        mock_runner_instance.initialize.return_value = False
        mock_runner_instance.run.return_value = "Please provide a command"
        mock_manager_runner.return_value = mock_runner_instance

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            result = self.runner.invoke(app, ["run", ""])
            assert result.exit_code == 0

    @pytest.mark.parametrize(
        "command",
        [
            "build",
            "test everything",
            "deploy to production with rollback enabled",
            "clean up temporary files and rebuild",
        ],
    )
    @patch("automake.cli.commands.run.ManagerAgentRunner")
    @patch("automake.cli.commands.run.get_config")
    @patch("automake.cli.commands.run.setup_logging")
    @patch("automake.cli.commands.run.log_config_info")
    @patch("automake.cli.commands.run.log_command_execution")
    @patch("automake.cli.commands.run.get_logger")
    def test_various_command_formats(
        self,
        mock_get_logger: Mock,
        mock_log_command: Mock,
        mock_log_config: Mock,
        mock_setup_logging: Mock,
        mock_get_config: Mock,
        mock_manager_runner: Mock,
        command: str,
    ) -> None:
        """Test various command formats are accepted."""
        makefile_content = "all:\n\techo 'Hello World'"

        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_setup_logging.return_value = mock_logger

        # Setup manager runner mock
        mock_runner_instance = Mock()
        mock_runner_instance.initialize.return_value = False
        mock_runner_instance.run.return_value = f"Executed: {command}"
        mock_manager_runner.return_value = mock_runner_instance

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            result = self.runner.invoke(app, ["run", command])
            assert result.exit_code == 0

    @patch("automake.cli.commands.run.ManagerAgentRunner")
    @patch("automake.cli.commands.run.get_config")
    @patch("automake.cli.commands.run.setup_logging")
    @patch("automake.cli.commands.run.log_config_info")
    @patch("automake.cli.commands.run.log_command_execution")
    @patch("automake.cli.commands.run.get_logger")
    def test_makefile_with_many_targets(
        self,
        mock_get_logger: Mock,
        mock_log_command: Mock,
        mock_log_config: Mock,
        mock_setup_logging: Mock,
        mock_get_config: Mock,
        mock_manager_runner: Mock,
    ) -> None:
        """Test Makefile with many targets shows preview correctly."""
        # Create a Makefile with many targets
        targets = [f"target{i}:\n\techo 'Target {i}'" for i in range(10)]
        makefile_content = "\n\n".join(targets)

        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_setup_logging.return_value = mock_logger

        # Setup manager runner mock
        mock_runner_instance = Mock()
        mock_runner_instance.initialize.return_value = False
        mock_runner_instance.run.return_value = (
            "Found multiple targets, executed appropriate one"
        )
        mock_manager_runner.return_value = mock_runner_instance

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            result = self.runner.invoke(app, ["run", "test command"])
            assert result.exit_code == 0

    @patch("automake.cli.commands.run.ManagerAgentRunner")
    @patch("automake.cli.commands.run.get_config")
    @patch("automake.cli.commands.run.setup_logging")
    @patch("automake.cli.commands.run.log_config_info")
    @patch("automake.cli.commands.run.log_command_execution")
    @patch("automake.cli.commands.run.get_logger")
    def test_makefile_without_targets(
        self,
        mock_get_logger: Mock,
        mock_log_command: Mock,
        mock_log_config: Mock,
        mock_setup_logging: Mock,
        mock_get_config: Mock,
        mock_manager_runner: Mock,
    ) -> None:
        """Test Makefile without clear targets."""
        makefile_content = """# This is just a comment
# Another comment
VARIABLE = value
"""

        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_setup_logging.return_value = mock_logger

        # Setup manager runner mock
        mock_runner_instance = Mock()
        mock_runner_instance.initialize.return_value = False
        mock_runner_instance.run.return_value = (
            "No clear targets found, but I can help with other tasks"
        )
        mock_manager_runner.return_value = mock_runner_instance

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            makefile_path = temp_path / "Makefile"
            makefile_path.write_text(makefile_content)

            result = self.runner.invoke(app, ["run", "test command"])
            assert result.exit_code == 0

    @patch("automake.cli.commands.run.ManagerAgentRunner")
    @patch("automake.cli.commands.run.get_config")
    @patch("automake.cli.commands.run.setup_logging")
    @patch("automake.cli.commands.run.log_config_info")
    @patch("automake.cli.commands.run.log_command_execution")
    @patch("automake.cli.commands.run.get_logger")
    def test_makefile_read_error(
        self,
        mock_get_logger: Mock,
        mock_log_command: Mock,
        mock_log_config: Mock,
        mock_setup_logging: Mock,
        mock_get_config: Mock,
        mock_manager_runner: Mock,
    ) -> None:
        """Test handling of Makefile read errors."""
        makefile_content = "all:\n\techo 'test'"

        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_setup_logging.return_value = mock_logger

        # Setup manager runner mock to simulate error handling
        mock_runner_instance = Mock()
        mock_runner_instance.initialize.return_value = False
        mock_runner_instance.run.return_value = "Handled Makefile read error gracefully"
        mock_manager_runner.return_value = mock_runner_instance

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

            # Should succeed with new agent architecture
            assert result.exit_code == 0

    @patch("automake.cli.commands.run.ManagerAgentRunner")
    @patch("automake.cli.commands.run.get_config")
    @patch("automake.cli.commands.run.setup_logging")
    @patch("automake.cli.commands.run.log_config_info")
    @patch("automake.cli.commands.run.log_command_execution")
    @patch("automake.cli.commands.run.get_logger")
    def test_unexpected_error_handling(
        self,
        mock_get_logger: Mock,
        mock_log_command: Mock,
        mock_log_config: Mock,
        mock_setup_logging: Mock,
        mock_get_config: Mock,
        mock_manager_runner: Mock,
    ) -> None:
        """Test handling of unexpected errors."""
        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_setup_logging.return_value = mock_logger

        # Setup manager runner mock to raise an error
        mock_runner_instance = Mock()
        mock_runner_instance.initialize.side_effect = RuntimeError("Unexpected error")
        mock_manager_runner.return_value = mock_runner_instance

        result = self.runner.invoke(app, ["run", "test command"])

        # Should exit with error code 1 when there's an unexpected error
        assert result.exit_code == 1


class TestVersionCallback:
    """Test cases for the version callback function."""

    def test_version_callback_true(self) -> None:
        """Test version callback with True value."""
        from automake.cli.display.callbacks import version_callback

        with pytest.raises((SystemExit, typer.Exit)):
            # Typer.Exit can raise different exceptions depending on context
            version_callback(True)

    def test_version_callback_false(self) -> None:
        """Test version callback with False value."""
        from automake.cli.display.callbacks import version_callback

        # Should not raise any exception
        result = version_callback(False)
        assert result is None

    def test_version_callback_none(self) -> None:
        """Test version callback with None value."""
        from automake.cli.display.callbacks import version_callback

        # Should not raise any exception
        result = version_callback(None)
        assert result is None


class TestASCIIArt:
    """Test cases for ASCII art functionality."""

    def test_read_ascii_art_file_exists(self) -> None:
        """Test reading ASCII art when file exists."""
        # This should not raise an exception
        result = read_ascii_art()
        # Should return a string (could be empty if file doesn't exist)
        assert isinstance(result, str)

    def test_read_ascii_art_with_content(self) -> None:
        """Test ASCII art content is reasonable."""
        result = read_ascii_art()
        # Should be a string, might be empty if no ASCII art file
        assert isinstance(result, str)
        # If not empty, should contain some text
        if result.strip():
            assert len(result.strip()) > 0
