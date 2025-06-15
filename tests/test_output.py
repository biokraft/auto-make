"""Tests for the output formatting module."""

import threading
import time
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console
from rich.text import Text

from automake.utils.output import (
    LiveBox,
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


class TestLiveBox:
    """Test cases for the LiveBox class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.output_buffer = StringIO()
        self.console = Console(file=self.output_buffer, width=80, legacy_windows=False)

    def test_init_default_parameters(self) -> None:
        """Test LiveBox initialization with default parameters."""
        live_box = LiveBox(self.console)

        assert live_box.console is self.console
        assert live_box.title == "Live Output"
        assert live_box.border_style == "blue"
        assert live_box.refresh_per_second == 4.0
        assert live_box.transient is True
        assert not live_box._is_active
        assert live_box._live is None

    def test_init_custom_parameters(self) -> None:
        """Test LiveBox initialization with custom parameters."""
        live_box = LiveBox(
            console=self.console,
            title="Custom Title",
            border_style="red",
            refresh_per_second=8.0,
            transient=False,
        )

        assert live_box.title == "Custom Title"
        assert live_box.border_style == "red"
        assert live_box.refresh_per_second == 8.0
        assert live_box.transient is False

    def test_update_with_string(self) -> None:
        """Test updating LiveBox content with a string."""
        live_box = LiveBox(self.console)
        live_box.update("Test content")

        # Content should be stored as Text object
        assert isinstance(live_box._content, Text)
        assert str(live_box._content) == "Test content"

    def test_update_with_text_object(self) -> None:
        """Test updating LiveBox content with a Text object."""
        live_box = LiveBox(self.console)
        text_content = Text("Styled text", style="bold")
        live_box.update(text_content)

        assert live_box._content is text_content

    def test_update_with_other_renderable(self) -> None:
        """Test updating LiveBox content with other renderable objects."""
        live_box = LiveBox(self.console)
        live_box.update(42)  # Number as renderable

        assert isinstance(live_box._content, Text)
        assert str(live_box._content) == "42"

    def test_append_text_basic(self) -> None:
        """Test appending text to LiveBox content."""
        live_box = LiveBox(self.console)
        live_box.update("Initial")
        live_box.append_text(" appended")

        assert str(live_box._content) == "Initial appended"

    def test_append_text_with_style(self) -> None:
        """Test appending styled text to LiveBox content."""
        live_box = LiveBox(self.console)
        live_box.update("Initial")
        live_box.append_text(" styled", style="bold")

        # Check that content contains both parts
        content_str = str(live_box._content)
        assert "Initial" in content_str
        assert "styled" in content_str

    def test_clear_content(self) -> None:
        """Test clearing LiveBox content."""
        live_box = LiveBox(self.console)
        live_box.update("Some content")
        live_box.clear()

        assert str(live_box._content) == ""

    def test_set_title(self) -> None:
        """Test updating LiveBox title."""
        live_box = LiveBox(self.console)
        live_box.set_title("New Title")

        assert live_box.title == "New Title"

    def test_context_manager(self) -> None:
        """Test LiveBox as context manager."""
        with (
            patch.object(LiveBox, "start") as mock_start,
            patch.object(LiveBox, "stop") as mock_stop,
        ):
            live_box = LiveBox(self.console)

            with live_box as box:
                assert box is live_box
                mock_start.assert_called_once()

            mock_stop.assert_called_once()

    def test_start_stop_lifecycle(self) -> None:
        """Test LiveBox start and stop lifecycle."""
        live_box = LiveBox(self.console)

        # Initially not active
        assert not live_box._is_active
        assert live_box._live is None

        # Start should activate
        live_box.start()
        assert live_box._is_active
        assert live_box._live is not None

        # Stop should deactivate
        live_box.stop()
        assert not live_box._is_active
        assert live_box._live is None

    def test_start_when_already_active(self) -> None:
        """Test starting LiveBox when already active does nothing."""
        live_box = LiveBox(self.console)
        live_box.start()
        first_live = live_box._live

        # Starting again should not change the live instance
        live_box.start()
        assert live_box._live is first_live

    def test_stop_when_not_active(self) -> None:
        """Test stopping LiveBox when not active does nothing."""
        live_box = LiveBox(self.console)

        # Should not raise an error
        live_box.stop()
        assert not live_box._is_active
        assert live_box._live is None

    def test_thread_safety_concurrent_updates(self) -> None:
        """Test thread safety with concurrent updates."""
        live_box = LiveBox(self.console)
        results = []
        errors = []

        def update_content(thread_id: int) -> None:
            try:
                for i in range(10):
                    live_box.update(f"Thread {thread_id} - Update {i}")
                    time.sleep(0.001)  # Small delay to encourage race conditions
                results.append(f"Thread {thread_id} completed")
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")

        # Create multiple threads updating concurrently
        threads = []
        for i in range(3):
            thread = threading.Thread(target=update_content, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5.0)

        # Should have no errors and all threads should complete
        assert len(errors) == 0
        assert len(results) == 3

    def test_thread_safety_concurrent_append(self) -> None:
        """Test thread safety with concurrent append operations."""
        live_box = LiveBox(self.console)
        live_box.update("Initial: ")

        results = []
        errors = []

        def append_content(thread_id: int) -> None:
            try:
                for i in range(5):
                    live_box.append_text(f"T{thread_id}:{i} ")
                    time.sleep(0.001)
                results.append(f"Thread {thread_id} completed")
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")

        # Create multiple threads appending concurrently
        threads = []
        for i in range(3):
            thread = threading.Thread(target=append_content, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5.0)

        # Should have no errors and all threads should complete
        assert len(errors) == 0
        assert len(results) == 3

        # Content should contain contributions from all threads
        final_content = str(live_box._content)
        assert "Initial:" in final_content
        for i in range(3):
            assert f"T{i}:" in final_content

    def test_update_when_active(self) -> None:
        """Test that updates trigger live refresh when active."""
        live_box = LiveBox(self.console)

        # Mock the live instance after it's created
        with patch.object(live_box, "_live", create=True) as mock_live:
            mock_live.update = MagicMock()
            live_box._is_active = True  # Simulate active state

            # Update should trigger live update
            live_box.update("New content")
            mock_live.update.assert_called_once()

    def test_update_when_inactive(self) -> None:
        """Test that updates don't trigger live refresh when inactive."""
        live_box = LiveBox(self.console)

        # Mock the live instance but keep it inactive
        with patch.object(live_box, "_live", create=True) as mock_live:
            mock_live.update = MagicMock()
            live_box._is_active = False  # Ensure inactive state

            # Update should not trigger live update
            live_box.update("New content")
            mock_live.update.assert_not_called()


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

    def test_create_live_box_default(self) -> None:
        """Test creating LiveBox with default parameters."""
        live_box = self.formatter.create_live_box()

        assert isinstance(live_box, LiveBox)
        assert live_box.console is self.console
        assert live_box.title == "Live Output"
        assert live_box.border_style == "dim"  # INFO message type
        assert live_box.refresh_per_second == 4.0
        assert live_box.transient is True

    def test_create_live_box_custom_parameters(self) -> None:
        """Test creating LiveBox with custom parameters."""
        live_box = self.formatter.create_live_box(
            title="Custom Title",
            message_type=MessageType.ERROR,
            refresh_per_second=8.0,
            transient=False,
        )

        assert live_box.title == "Custom Title"
        assert live_box.border_style == "red"  # ERROR message type
        assert live_box.refresh_per_second == 8.0
        assert live_box.transient is False

    def test_create_live_box_message_type_styling(self) -> None:
        """Test that different message types apply correct styling."""
        test_cases = [
            (MessageType.INFO, "dim"),
            (MessageType.SUCCESS, "green"),
            (MessageType.WARNING, "yellow"),
            (MessageType.ERROR, "red"),
            (MessageType.HINT, "dim"),
        ]

        for message_type, expected_border in test_cases:
            live_box = self.formatter.create_live_box(message_type=message_type)
            assert live_box.border_style == expected_border

    def test_live_box_context_manager(self) -> None:
        """Test OutputFormatter live_box context manager."""
        with (
            patch.object(LiveBox, "__enter__") as mock_enter,
            patch.object(LiveBox, "__exit__") as mock_exit,
        ):
            mock_live_box = MagicMock()
            mock_enter.return_value = mock_live_box

            with self.formatter.live_box("Test Title") as live_box:
                assert live_box is mock_live_box

            mock_enter.assert_called_once()
            mock_exit.assert_called_once()

    def test_live_box_context_manager_parameters(self) -> None:
        """Test live_box context manager with custom parameters."""
        with patch("automake.utils.output.formatter.LiveBox") as mock_live_box_class:
            mock_instance = MagicMock()
            mock_live_box_class.return_value = mock_instance
            mock_instance.__enter__.return_value = mock_instance

            with self.formatter.live_box(
                title="Custom Title",
                message_type=MessageType.SUCCESS,
                refresh_per_second=10.0,
                transient=False,
            ) as live_box:  # noqa: F841
                pass

            # Verify LiveBox was created with correct parameters
            mock_live_box_class.assert_called_once_with(
                console=self.console,
                title="Custom Title",
                border_style="green",
                refresh_per_second=10.0,
                transient=False,
            )

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
        """Test print_makefile_found method."""
        self.formatter.print_makefile_found("Makefile", "1024")
        output = self.console.file.getvalue()
        assert "Found Makefile (1024)" in output

    def test_print_targets_preview(self) -> None:
        """Test print_targets_preview method."""
        targets = ["build", "test", "clean"]
        self.formatter.print_targets_preview(targets, 5)
        output = self.console.file.getvalue()
        assert "Available targets: build, test, clean" in output

    def test_print_targets_preview_no_extra(self) -> None:
        """Test print_targets_preview with no extra targets."""
        targets = ["build", "test"]
        self.formatter.print_targets_preview(targets, 2)
        output = self.console.file.getvalue()
        assert "Available targets: build, test" in output

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
        self.formatter.print_simple("Test message", message_type, prefix=True)
        output = self.get_output()
        assert expected_emoji in output

    def test_ai_thinking_box_context_manager(self) -> None:
        """Test ai_thinking_box context manager."""
        with (
            patch.object(LiveBox, "__enter__") as mock_enter,
            patch.object(LiveBox, "__exit__") as mock_exit,
        ):
            mock_live_box = MagicMock()
            mock_enter.return_value = mock_live_box

            with self.formatter.ai_thinking_box("Custom Title") as live_box:
                assert live_box == mock_live_box

            mock_enter.assert_called_once()
            mock_exit.assert_called_once()

    def test_command_execution_box_context_manager(self) -> None:
        """Test command_execution_box context manager."""
        with (
            patch.object(LiveBox, "__enter__") as mock_enter,
            patch.object(LiveBox, "__exit__") as mock_exit,
        ):
            mock_live_box = MagicMock()
            mock_enter.return_value = mock_live_box

            with self.formatter.command_execution_box("test") as live_box:
                assert live_box == mock_live_box

            mock_enter.assert_called_once()
            mock_exit.assert_called_once()

    def test_model_streaming_box_context_manager(self) -> None:
        """Test model_streaming_box context manager."""
        with (
            patch.object(LiveBox, "__enter__") as mock_enter,
            patch.object(LiveBox, "__exit__") as mock_exit,
        ):
            mock_live_box = MagicMock()
            mock_enter.return_value = mock_live_box

            with self.formatter.model_streaming_box("AI Response") as live_box:
                assert live_box == mock_live_box

            mock_enter.assert_called_once()
            mock_exit.assert_called_once()

    @patch("time.sleep")
    def test_print_ai_reasoning_streaming(self, mock_sleep: MagicMock) -> None:
        """Test print_ai_reasoning_streaming method."""
        with patch.object(self.formatter, "live_box") as mock_live_box_context:
            mock_live_box = MagicMock()
            mock_live_box_context.return_value.__enter__.return_value = mock_live_box

            self.formatter.print_ai_reasoning_streaming("Test reasoning", 85)

            # Verify live_box was called with correct parameters
            mock_live_box_context.assert_called_once_with(
                "AI Reasoning (Confidence: 85%)", MessageType.INFO, transient=False
            )

            # Verify update was called for each word
            assert (
                mock_live_box.update.call_count >= 2
            )  # At least for "Test" and "Test reasoning"

    @patch("time.sleep")
    def test_print_command_chosen_animated(self, mock_sleep: MagicMock) -> None:
        """Test print_command_chosen_animated method."""
        with patch.object(self.formatter, "live_box") as mock_live_box_context:
            mock_live_box = MagicMock()
            mock_live_box_context.return_value.__enter__.return_value = mock_live_box

            self.formatter.print_command_chosen_animated("build", 90)

            # Verify live_box was called with correct parameters
            mock_live_box_context.assert_called_once_with(
                "Command Selected", MessageType.SUCCESS, transient=False
            )

            # Verify update was called multiple times for animation
            assert mock_live_box.update.call_count >= 3  # Multiple animation steps

    @patch("time.sleep")
    def test_print_command_chosen_animated_no_command(
        self, mock_sleep: MagicMock
    ) -> None:
        """Test print_command_chosen_animated with no command found."""
        with patch.object(self.formatter, "live_box") as mock_live_box_context:
            mock_live_box = MagicMock()
            mock_live_box_context.return_value.__enter__.return_value = mock_live_box

            self.formatter.print_command_chosen_animated(None, 30)

            # Verify live_box was called
            mock_live_box_context.assert_called_once()

            # Verify update was called with no command message
            mock_live_box.update.assert_called_with(
                "❌ No suitable command found (confidence: 30%)"
            )

    @patch("time.sleep")
    def test_animate_thinking_message(self, mock_sleep: MagicMock) -> None:
        """Test animate_thinking_message method."""
        mock_live_box = MagicMock()

        message = "🤔 Analyzing your command..."
        self.formatter.animate_thinking_message(mock_live_box, message, delay=0.1)

        # Verify that update was called multiple times (once per token)
        assert mock_live_box.update.call_count > 1

        # Verify that the final call contains the complete message
        final_call = mock_live_box.update.call_args_list[-1]
        assert message in final_call[0][0]

        # Verify sleep was called for animation timing
        assert mock_sleep.call_count > 0

    @patch("time.sleep")
    def test_animate_thinking_message_with_punctuation(
        self, mock_sleep: MagicMock
    ) -> None:
        """Test animate_thinking_message with punctuation and spaces."""
        mock_live_box = MagicMock()

        message = "Hello, world! How are you?"
        self.formatter.animate_thinking_message(mock_live_box, message, delay=0.05)

        # Should handle punctuation and spaces correctly
        assert mock_live_box.update.call_count > 5  # Multiple tokens

        # Check that intermediate calls build up the message
        calls = [call[0][0] for call in mock_live_box.update.call_args_list]

        # Each call should be a progressive build-up
        for i in range(1, len(calls)):
            assert len(calls[i]) >= len(calls[i - 1])

        # Final call should be the complete message
        assert calls[-1] == message


class TestLiveBoxIntegration:
    """Integration tests for LiveBox with real console output."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.output_buffer = StringIO()
        self.console = Console(file=self.output_buffer, width=80, legacy_windows=False)
        self.formatter = OutputFormatter(self.console)

    def test_live_box_streaming_simulation(self) -> None:
        """Test simulating streaming content to LiveBox."""
        with self.formatter.live_box("Streaming Test", MessageType.INFO) as live_box:
            # Simulate streaming tokens
            tokens = [
                "Hello",
                " ",
                "world",
                "!",
                " ",
                "This",
                " ",
                "is",
                " ",
                "streaming.",
            ]

            for token in tokens:
                live_box.append_text(token)
                time.sleep(0.01)  # Small delay to simulate real streaming

        # After context manager exits, we can't easily test the output
        # since it's transient, but we can verify no exceptions occurred
        assert True  # Test passes if no exceptions were raised

    def test_live_box_error_handling(self) -> None:
        """Test LiveBox handles errors gracefully."""
        live_box = self.formatter.create_live_box()

        # Test that operations don't fail when not started
        live_box.update("Test content")
        live_box.append_text(" more")
        live_box.clear()
        live_box.set_title("New Title")

        # Should not raise any exceptions
        assert True

    def test_live_box_with_different_content_types(self) -> None:
        """Test LiveBox with various content types."""
        live_box = self.formatter.create_live_box()

        # Test with different content types
        live_box.update("String content")
        live_box.update(Text("Rich text content", style="bold"))
        live_box.update(42)  # Number
        live_box.update(["list", "content"])  # List

        # Should handle all types without errors
        assert True

    def test_phase1_error_message_format_consistency(self) -> None:
        """Test Phase 1 error messages use consistent LiveBox format."""
        with self.formatter.live_box("Test Error", MessageType.ERROR) as error_box:
            error_box.update(
                "❌ This is a test error message\n\n"
                "💡 Hint: This is a helpful hint for the user"
            )

        # Verify the content was set correctly
        assert "❌" in str(error_box._content)
        assert "💡" in str(error_box._content)
        assert "test error message" in str(error_box._content)
        assert "helpful hint" in str(error_box._content)

    def test_phase1_success_message_format_consistency(self) -> None:
        """Test Phase 1 success messages use consistent LiveBox format."""
        with self.formatter.live_box(
            "Test Success", MessageType.SUCCESS
        ) as success_box:
            success_box.update("🎉 Operation completed successfully!")

        # Verify the content was set correctly
        assert "🎉" in str(success_box._content)
        assert "completed successfully" in str(success_box._content)

    def test_phase1_progress_message_format_consistency(self) -> None:
        """Test Phase 1 progress messages use consistent LiveBox format."""
        with self.formatter.live_box("Test Progress", MessageType.INFO) as progress_box:
            progress_box.update("🔧 Initializing system...")
            progress_box.update("🔍 Checking dependencies...")
            progress_box.update("✅ All checks passed")

        # Verify the final content
        assert "✅" in str(progress_box._content)
        assert "All checks passed" in str(progress_box._content)


class TestGlobalFormatter:
    """Test cases for global formatter functions."""

    def test_get_formatter_singleton(self) -> None:
        """Test that get_formatter returns the same instance."""
        formatter1 = get_formatter()
        formatter2 = get_formatter()
        assert formatter1 is formatter2

    def test_get_formatter_with_console(self) -> None:
        """Test get_formatter with custom console on first call."""
        # Reset global formatter
        import automake.utils.output.formatter

        automake.utils.output.formatter._global_formatter = None

        custom_console = Console()
        formatter = get_formatter(custom_console)
        assert formatter.console is custom_console

    @patch("automake.utils.output.formatter.get_formatter")
    def test_print_box_convenience_function(
        self, mock_get_formatter: MagicMock
    ) -> None:
        """Test print_box convenience function."""
        mock_formatter = MagicMock()
        mock_get_formatter.return_value = mock_formatter

        print_box("Test message", MessageType.INFO, "Test Title")
        mock_formatter.print_box.assert_called_once_with(
            "Test message", MessageType.INFO, "Test Title"
        )

    @patch("automake.utils.output.formatter.get_formatter")
    def test_print_error_box_convenience_function(
        self, mock_get_formatter: MagicMock
    ) -> None:
        """Test print_error_box convenience function."""
        mock_formatter = MagicMock()
        mock_get_formatter.return_value = mock_formatter

        print_error_box("Error message", "Hint message")
        mock_formatter.print_error_box.assert_called_once_with(
            "Error message", "Hint message"
        )

    @patch("automake.utils.output.formatter.get_formatter")
    def test_print_status_convenience_function(
        self, mock_get_formatter: MagicMock
    ) -> None:
        """Test print_status convenience function."""
        mock_formatter = MagicMock()
        mock_get_formatter.return_value = mock_formatter

        print_status("Status message", MessageType.WARNING, "Status Title")
        mock_formatter.print_status.assert_called_once_with(
            "Status message", MessageType.WARNING, "Status Title"
        )


class TestOutputFormatterIntegration:
    """Integration tests for OutputFormatter with real console."""

    def test_real_console_output(self) -> None:
        """Test OutputFormatter with real console (no mocking)."""
        formatter = OutputFormatter()

        # These should not raise exceptions
        formatter.print_box("Test message")
        formatter.print_simple("Simple message")
        formatter.print_command_received("test command")
        formatter.print_makefile_found("Makefile", "1024")
        formatter.print_targets_preview(["build", "test"], 2)
        formatter.print_error_box("Error message")
        formatter.print_status("Status message")

    def test_style_configurations_complete(self) -> None:
        """Test that all message types have complete style configurations."""
        formatter = OutputFormatter()

        required_keys = {"title", "title_color", "border_style", "emoji"}

        for message_type in MessageType:
            style_config = formatter._styles[message_type]
            assert set(style_config.keys()) == required_keys

    def test_print_ascii_art_with_content(self) -> None:
        """Test print_ascii_art with actual content."""
        formatter = OutputFormatter()
        art_content = "  ___  \n /   \\ \n \\___/ "

        # Should not raise an exception
        formatter.print_ascii_art(art_content)

    def test_print_ascii_art_empty_content(self) -> None:
        """Test print_ascii_art with empty content."""
        formatter = OutputFormatter()

        # Should handle empty content gracefully
        formatter.print_ascii_art("")
        formatter.print_ascii_art("   ")

    def test_print_rainbow_ascii_art_with_content(self) -> None:
        """Test print_rainbow_ascii_art with actual content."""
        formatter = OutputFormatter()
        art_content = "TEST"

        # Should not raise an exception (but will be very fast)
        formatter.print_rainbow_ascii_art(art_content, duration=0.1)

    def test_print_rainbow_ascii_art_empty_content(self) -> None:
        """Test print_rainbow_ascii_art with empty content."""
        formatter = OutputFormatter()

        # Should handle empty content gracefully
        formatter.print_rainbow_ascii_art("")
        formatter.print_rainbow_ascii_art("   ")
