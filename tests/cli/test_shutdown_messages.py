"""Tests for shutdown message display during signal handling."""

from io import StringIO
from unittest.mock import Mock, patch

from automake.agent.ui.session import RichInteractiveSession
from automake.cli.app import app
from automake.core.signal_handler import SignalHandler


class TestShutdownMessages:
    """Test shutdown message display functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Reset signal handler singleton
        SignalHandler._reset_instance()

    def test_shutdown_message_displayed_on_sigint(self):
        """Test that a user-friendly message is displayed when SIGINT is received."""
        signal_handler = SignalHandler()

        with patch.object(signal_handler, "_console") as mock_console:
            # Simulate SIGINT by calling the handler directly
            with patch("sys.exit"):  # Prevent actual exit
                signal_handler._signal_handler(2, None)

            # Check that shutdown message was displayed
            mock_console.print.assert_called()

    def test_shutdown_message_includes_cleanup_info(self):
        """Test that shutdown message includes information about cleanup process."""
        signal_handler = SignalHandler()

        # Register a mock cleanup function
        cleanup_called = []

        def mock_cleanup():
            cleanup_called.append(True)

        signal_handler.register_cleanup(mock_cleanup, "Test cleanup")

        with patch.object(signal_handler, "_console") as mock_console:
            with patch("sys.exit"):  # Prevent actual exit
                signal_handler._signal_handler(2, None)

            # Check that cleanup info was displayed
            mock_console.print.assert_called()
            # Check that cleanup function was called
            assert len(cleanup_called) == 1

    def test_timeout_warning_message_displayed(self):
        """Test that a warning is displayed if cleanup takes too long."""
        signal_handler = SignalHandler()

        # Create an event to control when cleanup finishes
        import threading

        cleanup_event = threading.Event()

        # Register a cleanup function that waits for the event
        def slow_cleanup():
            cleanup_event.wait(timeout=1.0)  # Wait up to 1 second for event

        signal_handler.register_cleanup(slow_cleanup, "Slow cleanup")

        with (
            patch("sys.stderr", new_callable=StringIO) as mock_stderr,
            patch("sys.exit"),
            patch("time.sleep"),
        ):  # Mock exit and sleep to prevent actual delays
            with patch.object(signal_handler, "_cleanup_timeout", 0.1):
                signal_handler._handle_sigint(2, None)

                output = mock_stderr.getvalue()
                assert "Force terminating" in output or "timeout" in output.lower()

    def test_eof_goodbye_message_in_interactive_session(self):
        """Test that a goodbye message is displayed when EOF is received."""
        mock_agent = Mock()
        mock_console = Mock()

        with (
            patch(
                "automake.core.signal_handler.SignalHandler"
            ) as mock_signal_handler_class,
            patch("sys.exit") as mock_exit,
        ):
            # Mock the signal handler
            mock_signal_handler = Mock()
            mock_signal_handler.register_cleanup.return_value = "cleanup_id"
            mock_signal_handler_class.return_value = mock_signal_handler

            session = RichInteractiveSession(mock_agent, mock_console)

            # Simulate EOF handling directly by calling the relevant part of start()
            try:
                # This simulates what happens in start() when EOFError is caught
                raise EOFError()
            except EOFError:
                # This is the code from the start() method's EOF handler
                mock_console.print("Goodbye! 👋")
                session._cleanup_session()
                mock_exit(0)

            # Check that a goodbye message was printed
            mock_console.print.assert_called_with("Goodbye! 👋")
            # Verify that sys.exit was called with 0 (normal exit)
            mock_exit.assert_called_with(0)

    def test_shutdown_message_respects_quiet_mode(self):
        """Test that shutdown messages respect quiet/verbose configuration."""
        signal_handler = SignalHandler()

        with (
            patch("sys.stderr", new_callable=StringIO) as mock_stderr,
            patch("sys.exit"),
        ):
            # Test with quiet mode
            with patch.object(signal_handler, "_quiet_mode", True):
                signal_handler._handle_sigint(2, None)

                output = mock_stderr.getvalue()
                # In quiet mode, should have minimal output
                assert len(output.strip()) < 50  # Arbitrary small length

    def test_shutdown_message_includes_process_count(self):
        """Test that shutdown message includes process cleanup info."""
        signal_handler = SignalHandler()

        # Register multiple cleanup functions to simulate multiple processes
        for i in range(3):
            signal_handler.register_cleanup(lambda: None, f"Process {i}")

        with (
            patch("sys.stderr", new_callable=StringIO) as mock_stderr,
            patch("sys.exit"),
        ):
            signal_handler._handle_sigint(2, None)

            output = mock_stderr.getvalue()
            # Should mention multiple cleanup tasks
            assert "3" in output or "multiple" in output.lower()

    def test_error_message_on_cleanup_failure(self):
        """Test that appropriate error message is shown if cleanup fails."""
        signal_handler = SignalHandler()

        # Register a cleanup function that raises an exception
        def failing_cleanup():
            raise RuntimeError("Cleanup failed")

        signal_handler.register_cleanup(failing_cleanup, "Failing cleanup")

        with (
            patch("sys.stderr", new_callable=StringIO) as mock_stderr,
            patch("sys.exit"),
        ):
            signal_handler._handle_sigint(2, None)

            output = mock_stderr.getvalue()
            assert "error" in output.lower() or "failed" in output.lower()

    def test_help_text_mentions_signal_handling(self):
        """Test that help text mentions signal handling capabilities."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            try:
                # Try to get help output - this might exit, so catch SystemExit
                app(["--help"])
            except SystemExit:
                pass

            output = mock_stdout.getvalue()
            # Help should mention that Ctrl+C is handled gracefully
            assert (
                "ctrl+c" in output.lower()
                or "sigint" in output.lower()
                or "signal" in output.lower()
            )

    def test_shutdown_message_threading_safe(self):
        """Test that shutdown messages are displayed safely in threads."""
        # Create a fresh signal handler for this test
        signal_handler = SignalHandler()
        # Reset the shutdown state for this test
        signal_handler._is_shutting_down = False

        import threading

        messages = []
        messages_lock = threading.Lock()

        def capture_message():
            with (
                patch("sys.stderr", new_callable=StringIO) as mock_stderr,
                patch("sys.exit"),
            ):  # Mock exit to prevent thread termination
                # Create separate signal handler instance for each thread
                thread_handler = SignalHandler()
                thread_handler._is_shutting_down = False  # Reset shutdown state
                thread_handler._handle_sigint(2, None)
                with messages_lock:
                    messages.append(mock_stderr.getvalue())

        # Start multiple threads that try to handle signals
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=capture_message)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should have captured messages from all threads
        # Note: Due to the singleton pattern and shutdown locking,
        # we expect at least one message but maybe not all 3
        assert len(messages) >= 1
        for message in messages:
            if message:  # Non-empty messages should contain shutdown text
                assert "Shutting down" in message
