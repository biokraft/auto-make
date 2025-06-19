"""Tests for Phase 6: Intelligent Error Handling."""

import sys
from unittest.mock import Mock, patch

import click
import pytest
import typer
from typer.testing import CliRunner

from automake.cli.error_handler import (
    _create_error_correction_prompt,
    _extract_command_from_suggestion,
    _present_suggestion,
    _show_fallback_help,
    handle_cli_error,
)


class TestMainEntryPoint:
    """Test the main entry point error handling wrapper."""

    @patch("automake.__main__.app")
    def test_main_normal_execution(self, mock_app):
        """Test main function with normal execution."""
        from automake.__main__ import main

        mock_app.return_value = None

        main()

        mock_app.assert_called_once()

    @patch("automake.__main__.handle_cli_error")
    @patch("automake.__main__.app")
    def test_main_handles_click_usage_error(self, mock_app, mock_handle_error):
        """Test main function handles click usage errors."""
        from automake.__main__ import main

        error = click.exceptions.UsageError("Invalid option")
        mock_app.side_effect = error

        main()

        mock_handle_error.assert_called_once_with(error, sys.argv)

    @patch("automake.__main__.handle_cli_error")
    @patch("automake.__main__.app")
    def test_main_handles_click_exception(self, mock_app, mock_handle_error):
        """Test main function handles general click exceptions."""
        from automake.__main__ import main

        error = click.exceptions.ClickException("Click error")
        mock_app.side_effect = error

        main()

        mock_handle_error.assert_called_once_with(error, sys.argv)

    @patch("automake.__main__.app")
    def test_main_reraises_typer_exit(self, mock_app):
        """Test main function re-raises typer.Exit."""
        from automake.__main__ import main

        mock_app.side_effect = typer.Exit(1)

        with pytest.raises(typer.Exit):
            main()

    @patch("automake.__main__.typer.echo")
    @patch("automake.__main__.app")
    def test_main_handles_keyboard_interrupt(self, mock_app, mock_echo):
        """Test main function handles KeyboardInterrupt."""
        from automake.__main__ import main

        mock_app.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 130
        mock_echo.assert_called_with("\n👋 Goodbye!", err=True)

    @patch("automake.__main__.typer.echo")
    @patch("automake.__main__.app")
    def test_main_handles_unexpected_error(self, mock_app, mock_echo):
        """Test main function handles unexpected errors."""
        from automake.__main__ import main

        mock_app.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        mock_echo.assert_called_with(
            "❌ An unexpected error occurred: Unexpected error", err=True
        )

    @patch("automake.__main__.traceback.print_exc")
    @patch("automake.__main__.typer.echo")
    @patch("automake.__main__.app")
    def test_main_shows_debug_info_with_debug_flag(
        self, mock_app, mock_echo, mock_traceback
    ):
        """Test main function shows debug info when --debug flag is present."""
        from automake.__main__ import main

        mock_app.side_effect = RuntimeError("Unexpected error")

        # Mock sys.argv to include --debug
        with patch("automake.__main__.sys.argv", ["automake", "--debug", "test"]):
            with pytest.raises(SystemExit):
                main()

        mock_traceback.assert_called_once()


class TestErrorHandler:
    """Test the error handler functionality."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config."""
        config = Mock()
        config.ollama_base_url = "http://localhost:11434"
        config.ollama_model = "qwen3:0.6b"
        return config

    @pytest.fixture
    def mock_runner(self):
        """Create a mock ManagerAgentRunner."""
        runner = Mock()
        runner.initialize.return_value = False
        runner.run.return_value = 'Try using: automake "build the project"'
        return runner

    @patch("automake.cli.error_handler.get_formatter")
    @patch("automake.cli.error_handler.get_config")
    @patch("automake.cli.error_handler.setup_logging")
    @patch("automake.cli.error_handler.ManagerAgentRunner")
    @patch("automake.cli.error_handler._present_suggestion")
    def test_handle_cli_error_success(
        self,
        mock_present,
        mock_runner_class,
        mock_setup_logging,
        mock_get_config,
        mock_get_formatter,
        mock_config,
        mock_runner,
    ):
        """Test successful error handling."""
        mock_get_config.return_value = mock_config
        mock_runner_class.return_value = mock_runner
        mock_formatter = Mock()
        mock_get_formatter.return_value = mock_formatter

        # Mock the live_box context manager properly
        mock_live_box = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_live_box)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_formatter.live_box.return_value = mock_context_manager

        error = click.exceptions.UsageError("Invalid option --bad")
        argv = ["automake", "--bad", "test"]

        handle_cli_error(error, argv)

        mock_runner.initialize.assert_called_once()
        mock_runner.run.assert_called_once()
        mock_present.assert_called_once()

    @patch("automake.cli.error_handler.get_formatter")
    @patch("automake.cli.error_handler.get_config")
    @patch("automake.cli.error_handler.setup_logging")
    @patch("automake.cli.error_handler.ManagerAgentRunner")
    @patch("automake.cli.error_handler._show_fallback_help")
    def test_handle_cli_error_agent_failure(
        self,
        mock_fallback,
        mock_runner_class,
        mock_setup_logging,
        mock_get_config,
        mock_get_formatter,
        mock_config,
    ):
        """Test error handling when agent fails."""
        mock_get_config.return_value = mock_config
        mock_runner = Mock()
        mock_runner.initialize.return_value = False
        mock_runner.run.side_effect = Exception("Agent failed")
        mock_runner_class.return_value = mock_runner

        mock_formatter = Mock()
        mock_get_formatter.return_value = mock_formatter

        # Mock the live_box context manager properly
        mock_live_box = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_live_box)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_formatter.live_box.return_value = mock_context_manager

        error = click.exceptions.UsageError("Invalid option --bad")
        argv = ["automake", "--bad", "test"]

        handle_cli_error(error, argv)

        mock_fallback.assert_called_once()

    @patch("automake.cli.error_handler.get_formatter")
    @patch("automake.cli.error_handler.get_config")
    @patch("automake.cli.error_handler.setup_logging")
    @patch("automake.cli.error_handler.ManagerAgentRunner")
    def test_handle_cli_error_initialization_failure(
        self,
        mock_runner_class,
        mock_setup_logging,
        mock_get_config,
        mock_get_formatter,
        mock_config,
    ):
        """Test error handling when runner initialization fails."""
        mock_get_config.return_value = mock_config
        mock_runner_class.side_effect = Exception("Initialization failed")

        mock_formatter = Mock()
        mock_get_formatter.return_value = mock_formatter

        # Mock the live_box context manager properly
        mock_live_box = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_live_box)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_formatter.live_box.return_value = mock_context_manager

        error = click.exceptions.UsageError("Invalid option --bad")
        argv = ["automake", "--bad", "test"]

        with pytest.raises(SystemExit) as exc_info:
            handle_cli_error(error, argv)

        assert exc_info.value.code == 1


class TestErrorCorrectionPrompt:
    """Test error correction prompt generation."""

    def test_create_error_correction_prompt(self):
        """Test creating error correction prompt."""
        error_message = "No such option: --bad"
        original_command = "automake --bad test"

        prompt = _create_error_correction_prompt(error_message, original_command)

        assert "automake --bad test" in prompt
        assert "No such option: --bad" in prompt
        assert "natural language prompt" in prompt
        assert "automake agent" in prompt

    def test_create_error_correction_prompt_formatting(self):
        """Test prompt formatting includes all required elements."""
        error_message = "Invalid command"
        original_command = "automake invalid"

        prompt = _create_error_correction_prompt(error_message, original_command)

        # Check for key instruction elements
        assert "analyze this error" in prompt.lower()
        assert "suggest a corrected command" in prompt.lower()
        assert "briefly explain" in prompt.lower()
        assert "provide the exact corrected command" in prompt.lower()


class TestCommandExtraction:
    """Test command extraction from AI suggestions."""

    def test_extract_command_from_backticks(self):
        """Test extracting command from backticks."""
        suggestion = 'You should try `automake "build project"` instead.'

        result = _extract_command_from_suggestion(suggestion)

        assert result == 'automake "build project"'

    def test_extract_command_from_line_start(self):
        """Test extracting command that starts a line."""
        suggestion = """The error suggests you used an invalid option.

automake "build the project"

This should work better."""

        result = _extract_command_from_suggestion(suggestion)

        assert result == 'automake "build the project"'

    def test_extract_command_from_colon_format(self):
        """Test extracting command from colon format."""
        suggestion = "Corrected command: automake agent"

        result = _extract_command_from_suggestion(suggestion)

        assert result == "automake agent"

    def test_extract_command_no_match(self):
        """Test when no command can be extracted."""
        suggestion = "This is just explanatory text without any commands."

        result = _extract_command_from_suggestion(suggestion)

        assert result is None

    def test_extract_command_ignores_explanatory_text(self):
        """Test that explanatory text is ignored."""
        suggestion = """The problem is that you used an invalid option.

Try using: `automake "test command"`

This will work better."""

        result = _extract_command_from_suggestion(suggestion)

        assert result == 'automake "test command"'


class TestSuggestionPresentation:
    """Test suggestion presentation and confirmation."""

    @patch("automake.cli.error_handler.console")
    @patch("automake.cli.error_handler.Confirm.ask")
    @patch("automake.cli.error_handler._execute_corrected_command")
    @patch("automake.cli.error_handler.get_logger")
    def test_present_suggestion_with_confirmation(
        self, mock_get_logger, mock_execute, mock_confirm, mock_console
    ):
        """Test presenting suggestion with user confirmation."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        suggestion = 'Try: `automake "build project"`'
        original_command = "automake --invalid"
        output = Mock()

        mock_confirm.return_value = True

        _present_suggestion(suggestion, original_command, output)

        mock_execute.assert_called_once_with('automake "build project"', output)

    @patch("automake.cli.error_handler.console")
    @patch("automake.cli.error_handler.Confirm.ask")
    @patch("automake.cli.error_handler._execute_corrected_command")
    def test_present_suggestion_without_confirmation(
        self, mock_execute, mock_confirm, mock_console
    ):
        """Test presenting suggestion when user declines."""
        suggestion = 'Try: `automake "build project"`'
        original_command = "automake --invalid"
        output = Mock()

        mock_confirm.return_value = False

        _present_suggestion(suggestion, original_command, output)

        mock_execute.assert_not_called()

    @patch("automake.cli.error_handler.console")
    def test_present_suggestion_no_command_extracted(self, mock_console):
        """Test presenting suggestion when no command can be extracted."""
        suggestion = "This is just explanatory text."
        original_command = "automake --invalid"
        output = Mock()

        _present_suggestion(suggestion, original_command, output)

        # Should print the suggestion but not ask for confirmation
        mock_console.print.assert_called()

    @patch("automake.cli.error_handler.console")
    @patch("automake.cli.error_handler.Confirm.ask")
    @patch("automake.cli.error_handler._execute_corrected_command")
    @patch("automake.cli.error_handler.get_logger")
    def test_present_suggestion_execution_failure(
        self, mock_get_logger, mock_execute, mock_confirm, mock_console
    ):
        """Test handling execution failure."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        suggestion = "Try: `automake help`"
        original_command = "automake --invalid"
        output = Mock()

        mock_confirm.return_value = True
        mock_execute.side_effect = Exception("Execution failed")

        with pytest.raises(SystemExit) as exc_info:
            _present_suggestion(suggestion, original_command, output)

        assert exc_info.value.code == 1


class TestFallbackHelp:
    """Test fallback help functionality."""

    @patch("automake.cli.error_handler.console")
    def test_show_fallback_help_basic(self, mock_console):
        """Test basic fallback help display."""
        error_message = "Invalid command"
        original_command = "automake invalid"

        _show_fallback_help(error_message, original_command)

        # Verify that help commands are displayed
        mock_console.print.assert_called()
        calls = [call[0][0] for call in mock_console.print.call_args_list]
        help_text = " ".join(calls)

        assert 'automake "build the project"' in help_text
        assert "automake agent" in help_text
        assert "automake help" in help_text
        assert "automake init" in help_text

    @patch("automake.cli.error_handler.console")
    def test_show_fallback_help_with_option_error(self, mock_console):
        """Test fallback help with option-specific guidance."""
        error_message = "no such option: --invalid"
        original_command = "automake --invalid test"

        _show_fallback_help(error_message, original_command)

        # Verify that option-specific help is shown
        calls = [call[0][0] for call in mock_console.print.call_args_list]
        help_text = " ".join(calls)

        assert "invalid option" in help_text.lower()
        assert "natural language" in help_text.lower()


class TestIntegration:
    """Integration tests for Phase 6 error handling."""

    def test_cli_runner_integration(self):
        """Test that the CLI runner properly integrates with error handling."""
        from automake.cli.app import app

        runner = CliRunner()

        # Test with an invalid option - this should trigger error handling
        # Note: In actual usage, this would be handled by the main wrapper
        result = runner.invoke(app, ["--invalid-option"])

        # The CLI should handle this gracefully
        assert result.exit_code != 0

    @patch("automake.cli.error_handler.ManagerAgentRunner")
    @patch("automake.cli.error_handler.get_config")
    def test_error_handler_with_real_error(self, mock_get_config, mock_runner_class):
        """Test error handler with a real CLI error."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config

        mock_runner = Mock()
        mock_runner.initialize.return_value = False
        mock_runner.run.return_value = "Try: automake help"
        mock_runner_class.return_value = mock_runner

        error = click.exceptions.UsageError("No such option: --invalid")
        argv = ["automake", "--invalid", "test"]

        with patch("automake.cli.error_handler.get_formatter") as mock_formatter:
            mock_live_box = Mock()
            mock_formatter.return_value.live_box.return_value.__enter__.return_value = (
                mock_live_box
            )

            with patch(
                "automake.cli.error_handler._present_suggestion"
            ) as mock_present:
                handle_cli_error(error, argv)

                mock_present.assert_called_once()
                args = mock_present.call_args[0]
                assert "Try: automake help" in args[0]  # suggestion
                assert "automake --invalid test" in args[1]  # original command
