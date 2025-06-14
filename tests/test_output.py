"""Tests for the output formatting module."""

from io import StringIO
from unittest.mock import patch

import pytest
from rich.console import Console

from automake.utils.output import (
    MessageType,
    OutputFormatter,
    get_formatter,
    print_box,
    print_error_box,
    print_status,
)


class TestMessageType:
    """Test cases for the MessageType enum."""

    def test_message_type_values(self) -> None:
        """Test that MessageType enum has expected values."""
        assert MessageType.INFO.value == "info"
        assert MessageType.SUCCESS.value == "success"
        assert MessageType.WARNING.value == "warning"
        assert MessageType.ERROR.value == "error"
        assert MessageType.HINT.value == "hint"


class TestOutputFormatter:
    """Test cases for the OutputFormatter class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Use StringIO to capture console output
        self.output_buffer = StringIO()
        self.console = Console(file=self.output_buffer, width=80, legacy_windows=False)
        self.formatter = OutputFormatter(self.console)

    def get_output(self) -> str:
        """Get the captured console output."""
        return self.output_buffer.getvalue()

    def test_init_with_console(self) -> None:
        """Test OutputFormatter initialization with provided console."""
        formatter = OutputFormatter(self.console)
        assert formatter.console is self.console

    def test_init_without_console(self) -> None:
        """Test OutputFormatter initialization without console creates new one."""
        formatter = OutputFormatter()
        assert formatter.console is not None
        assert isinstance(formatter.console, Console)

    def test_print_box_default(self) -> None:
        """Test print_box with default parameters."""
        self.formatter.print_box("Test message")
        output = self.get_output()

        assert "Test message" in output
        assert "─ Info " in output

    def test_print_box_error_type(self) -> None:
        """Test print_box with error message type."""
        self.formatter.print_box("Error occurred", MessageType.ERROR)
        output = self.get_output()

        assert "Error occurred" in output
        assert "─ Error " in output

    def test_print_box_custom_title(self) -> None:
        """Test print_box with custom title."""
        self.formatter.print_box("Custom message", MessageType.INFO, "Custom Title")
        output = self.get_output()

        assert "Custom message" in output
        assert "─ Custom Title " in output

    def test_print_simple_with_prefix(self) -> None:
        """Test print_simple with emoji prefix."""
        self.formatter.print_simple("Test message", MessageType.SUCCESS, prefix=True)
        output = self.get_output()

        assert "✅ Test message" in output

    def test_print_simple_without_prefix(self) -> None:
        """Test print_simple without emoji prefix."""
        self.formatter.print_simple("Test message", MessageType.SUCCESS, prefix=False)
        output = self.get_output()

        assert "Test message" in output
        assert "✅" not in output

    def test_print_simple_error_styling(self) -> None:
        """Test print_simple applies red styling for errors."""
        self.formatter.print_simple("Error message", MessageType.ERROR)
        output = self.get_output()

        # Rich markup should be present in the output
        assert "❌ Error message" in output

    def test_print_command_received(self) -> None:
        """Test print_command_received formats command correctly."""
        self.formatter.print_command_received("build project")
        output = self.get_output()

        assert "build project" in output
        assert "─ Command Received " in output

    def test_print_makefile_found(self) -> None:
        """Test print_makefile_found formats makefile info correctly."""
        self.formatter.print_makefile_found("Makefile", "1024")
        output = self.get_output()

        assert "Found Makefile:" in output
        assert "Makefile" in output
        assert "(1024 bytes)" in output
        assert "─ Success " in output

    def test_print_targets_preview(self) -> None:
        """Test print_targets_preview formats targets correctly."""
        targets = ["build", "test", "clean"]
        self.formatter.print_targets_preview(targets, 5)
        output = self.get_output()

        assert "─ Available Targets " in output
        assert "• build" in output
        assert "• test" in output
        assert "• clean" in output
        assert "and 2 more targets" in output

    def test_print_targets_preview_no_extra(self) -> None:
        """Test print_targets_preview when no extra targets."""
        targets = ["build", "test"]
        self.formatter.print_targets_preview(targets, 2)
        output = self.get_output()

        assert "─ Available Targets " in output
        assert "• build" in output
        assert "• test" in output
        assert "more targets" not in output

    def test_print_error_box_with_hint(self) -> None:
        """Test print_error_box with hint message."""
        self.formatter.print_error_box("Something went wrong", "Try this solution")
        output = self.get_output()

        assert "Something went wrong" in output
        assert "─ Error " in output
        assert "💡 Try this solution" in output

    def test_print_error_box_without_hint(self) -> None:
        """Test print_error_box without hint message."""
        self.formatter.print_error_box("Something went wrong")
        output = self.get_output()

        assert "Something went wrong" in output
        assert "─ Error " in output

    def test_print_status_info(self) -> None:
        """Test print_status with info type."""
        self.formatter.print_status("Processing...", MessageType.INFO)
        output = self.get_output()

        assert "Processing..." in output
        assert "─ Info " in output

    def test_print_status_warning(self) -> None:
        """Test print_status with warning type."""
        self.formatter.print_status("Be careful", MessageType.WARNING)
        output = self.get_output()

        assert "Be careful" in output
        assert "─ Warning " in output

    def test_print_status_with_custom_title(self) -> None:
        """Test print_status with custom title."""
        self.formatter.print_status(
            "Processing data...", MessageType.INFO, "Custom Title"
        )
        output = self.get_output()

        assert "Processing data..." in output
        assert "─ Custom Title " in output

    @pytest.mark.parametrize(
        ("message_type", "expected_emoji"),
        [
            (MessageType.INFO, "ℹ️"),
            (MessageType.SUCCESS, "✅"),
            (MessageType.WARNING, "⚠️"),
            (MessageType.ERROR, "❌"),
            (MessageType.HINT, "💡"),
        ],
    )
    def test_message_type_emojis(
        self, message_type: MessageType, expected_emoji: str
    ) -> None:
        """Test that each message type uses the correct emoji."""
        self.formatter.print_simple("Test", message_type, prefix=True)
        output = self.get_output()

        assert expected_emoji in output


class TestGlobalFormatter:
    """Test cases for global formatter functions."""

    def test_get_formatter_singleton(self) -> None:
        """Test that get_formatter returns the same instance."""
        formatter1 = get_formatter()
        formatter2 = get_formatter()

        assert formatter1 is formatter2

    def test_get_formatter_with_console(self) -> None:
        """Test get_formatter with custom console."""
        console = Console()

        # Reset global formatter to test fresh initialization
        import automake.utils.output

        automake.utils.output._global_formatter = None

        formatter = get_formatter(console)
        assert formatter.console is console

    def test_print_box_convenience_function(self) -> None:
        """Test print_box convenience function."""
        with patch("automake.utils.output.get_formatter") as mock_get_formatter:
            mock_formatter = mock_get_formatter.return_value

            print_box("Test message", MessageType.ERROR, "Custom Title")

            mock_formatter.print_box.assert_called_once_with(
                "Test message", MessageType.ERROR, "Custom Title"
            )

    def test_print_error_box_convenience_function(self) -> None:
        """Test print_error_box convenience function."""
        with patch("automake.utils.output.get_formatter") as mock_get_formatter:
            mock_formatter = mock_get_formatter.return_value

            print_error_box("Error message", "Hint message")

            mock_formatter.print_error_box.assert_called_once_with(
                "Error message", "Hint message"
            )

    def test_print_status_convenience_function(self) -> None:
        """Test print_status convenience function."""
        with patch("automake.utils.output.get_formatter") as mock_get_formatter:
            mock_formatter = mock_get_formatter.return_value

            print_status("Status message", MessageType.WARNING, "Custom")

            mock_formatter.print_status.assert_called_once_with(
                "Status message", MessageType.WARNING, "Custom"
            )


class TestOutputFormatterIntegration:
    """Integration tests for OutputFormatter with real console output."""

    def test_real_console_output(self) -> None:
        """Test that formatter works with real console (no exceptions)."""
        formatter = OutputFormatter()

        # These should not raise exceptions
        formatter.print_box("Test message")
        formatter.print_simple("Simple message")
        formatter.print_command_received("test command")
        formatter.print_makefile_found("Makefile", "1024")
        formatter.print_targets_preview(["build", "test"], 2)
        formatter.print_error_box("Error", "Hint")
        formatter.print_status("Status")

    def test_style_configurations_complete(self) -> None:
        """Test that all message types have complete style configurations."""
        formatter = OutputFormatter()

        required_keys = {"title", "title_color", "border_style", "emoji"}

        for message_type in MessageType:
            style_config = formatter._styles[message_type]
            assert set(style_config.keys()) == required_keys

            # Ensure all values are non-empty strings
            for _key, value in style_config.items():
                assert isinstance(value, str)
                assert len(value) > 0

    def test_print_ascii_art_with_content(self) -> None:
        """Test print_ascii_art with content."""
        formatter = OutputFormatter()
        art_content = "ASCII ART\nLINE 2"

        # Should not raise any exceptions
        formatter.print_ascii_art(art_content)

    def test_print_ascii_art_empty_content(self) -> None:
        """Test print_ascii_art with empty content."""
        formatter = OutputFormatter()

        # Should not print anything for empty content
        formatter.print_ascii_art("")
        formatter.print_ascii_art("   ")  # Only whitespace

    def test_print_rainbow_ascii_art_with_content(self) -> None:
        """Test print_rainbow_ascii_art with content."""
        formatter = OutputFormatter()
        art_content = "ASCII ART\nLINE 2"

        # Should not raise any exceptions (using very short duration for testing)
        formatter.print_rainbow_ascii_art(art_content, duration=0.1)

    def test_print_rainbow_ascii_art_empty_content(self) -> None:
        """Test print_rainbow_ascii_art with empty content."""
        formatter = OutputFormatter()

        # Should not print anything for empty content
        formatter.print_rainbow_ascii_art("")
        formatter.print_rainbow_ascii_art("   ")  # Only whitespace
