"""Tests for the main CLI module."""

import pytest
import typer
from typer.testing import CliRunner

from automake import __version__
from automake.main import app


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
        # Check for the help text that's actually displayed
        assert (
            "AI-powered Makefile command execution" in result.stdout
            or "automake" in result.stdout
        )
        assert "COMMAND" in result.stdout

    def test_main_command_with_argument(self) -> None:
        """Test main command with a natural language argument."""
        test_command = "build the project"
        result = self.runner.invoke(app, [test_command])

        assert result.exit_code == 0
        assert f"🤖 AutoMake received command: {test_command}" in result.stdout
        assert "⚠️  AI integration not yet implemented" in result.stdout
        assert "📋 This will be implemented in Phase 6" in result.stdout

    def test_main_command_with_complex_argument(self) -> None:
        """Test main command with a complex natural language argument."""
        test_command = "deploy the application to staging environment"
        result = self.runner.invoke(app, [test_command])

        assert result.exit_code == 0
        assert f"🤖 AutoMake received command: {test_command}" in result.stdout

    def test_main_command_with_quotes(self) -> None:
        """Test main command with quoted arguments."""
        test_command = "run tests with coverage"
        result = self.runner.invoke(app, [test_command])

        assert result.exit_code == 0
        assert f"🤖 AutoMake received command: {test_command}" in result.stdout

    def test_no_arguments_shows_help(self) -> None:
        """Test that running without arguments shows help."""
        result = self.runner.invoke(app, [])
        assert result.exit_code != 0  # Should fail without required argument
        # Check both stdout and stderr for error messages
        output = result.stdout + result.stderr
        assert "Missing argument" in output or "Usage:" in output or "Error" in output

    def test_empty_command_argument(self) -> None:
        """Test behavior with empty command argument."""
        result = self.runner.invoke(app, [""])
        assert result.exit_code == 0
        assert "🤖 AutoMake received command:" in result.stdout

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
        result = self.runner.invoke(app, [command])
        assert result.exit_code == 0
        assert f"🤖 AutoMake received command: {command}" in result.stdout


class TestVersionCallback:
    """Test cases for the version callback function."""

    def test_version_callback_true(self) -> None:
        """Test version callback with True value."""
        from automake.main import version_callback

        with pytest.raises((SystemExit, typer.Exit)):
            # Typer.Exit can raise different exceptions depending on context
            version_callback(True)

    def test_version_callback_false(self) -> None:
        """Test version callback with False value."""
        from automake.main import version_callback

        # Should not raise any exception
        result = version_callback(False)
        assert result is None

    def test_version_callback_none(self) -> None:
        """Test version callback with None value."""
        from automake.main import version_callback

        # Should not raise any exception
        result = version_callback(None)
        assert result is None
