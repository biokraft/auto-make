"""Tests for signal handling functionality."""

import signal
import threading
import time
from unittest.mock import MagicMock, patch

from automake.core.signal_handler import SignalHandler


class TestSignalHandler:
    """Test cases for the SignalHandler class."""

    def setup_method(self):
        """Reset SignalHandler before each test."""
        SignalHandler._reset_instance()

    def test_signal_handler_initialization(self):
        """Test that SignalHandler can be initialized."""
        # This test will fail initially since SignalHandler doesn't exist
        handler = SignalHandler()
        assert handler is not None
        assert hasattr(handler, "cleanup_registry")
        assert hasattr(handler, "shutdown_timeout")

    def test_signal_handler_registers_sigint(self):
        """Test that SignalHandler registers SIGINT handler."""
        with patch("signal.signal") as mock_signal:
            handler = SignalHandler()
            handler.register_handlers()

            # Verify SIGINT handler was registered
            mock_signal.assert_called_with(signal.SIGINT, handler._handle_sigint)

    def test_cleanup_registry_add_and_remove(self):
        """Test adding and removing cleanup functions."""
        handler = SignalHandler()

        cleanup_func = MagicMock()
        cleanup_id = handler.register_cleanup(cleanup_func, "test cleanup")

        assert cleanup_id in handler.cleanup_registry
        assert handler.cleanup_registry[cleanup_id]["func"] == cleanup_func
        assert handler.cleanup_registry[cleanup_id]["description"] == "test cleanup"

        # Test removal
        handler.unregister_cleanup(cleanup_id)
        assert cleanup_id not in handler.cleanup_registry

    def test_graceful_shutdown_calls_cleanup_functions(self):
        """Test that graceful shutdown calls all registered cleanup functions."""
        handler = SignalHandler()

        cleanup_func1 = MagicMock()
        cleanup_func2 = MagicMock()

        handler.register_cleanup(cleanup_func1, "cleanup 1")
        handler.register_cleanup(cleanup_func2, "cleanup 2")

        # Trigger graceful shutdown
        handler.graceful_shutdown()

        # Verify both cleanup functions were called
        cleanup_func1.assert_called_once()
        cleanup_func2.assert_called_once()

    def test_graceful_shutdown_handles_cleanup_exceptions(self):
        """Test that graceful shutdown continues even if cleanup functions fail."""
        handler = SignalHandler()

        failing_cleanup = MagicMock(side_effect=Exception("Cleanup failed"))
        working_cleanup = MagicMock()

        handler.register_cleanup(failing_cleanup, "failing cleanup")
        handler.register_cleanup(working_cleanup, "working cleanup")

        # Should not raise exception despite failing cleanup
        handler.graceful_shutdown()

        # Both should have been called
        failing_cleanup.assert_called_once()
        working_cleanup.assert_called_once()

    def test_signal_handler_sets_proper_exit_code(self):
        """Test that signal handler sets exit code 130 for SIGINT."""
        handler = SignalHandler()

        with patch("sys.exit") as mock_exit:
            # Simulate SIGINT
            handler._handle_sigint(signal.SIGINT, None)

            # Should exit with code 130 (128 + SIGINT)
            mock_exit.assert_called_with(130)

    def test_signal_handler_timeout_handling(self):
        """Test that signal handler enforces timeout for cleanup."""
        handler = SignalHandler(shutdown_timeout=0.1)  # Very short timeout

        # Create a cleanup function that takes too long
        slow_cleanup = MagicMock(side_effect=lambda: time.sleep(0.2))
        handler.register_cleanup(slow_cleanup, "slow cleanup")

        with patch("sys.exit") as mock_exit:
            handler.graceful_shutdown()

            # Give a moment for the timeout thread to trigger
            time.sleep(0.15)

            # Should have called exit with code 130
            mock_exit.assert_called_with(130)

    def test_signal_handler_singleton_pattern(self):
        """Test that SignalHandler follows singleton pattern."""
        handler1 = SignalHandler.get_instance()
        handler2 = SignalHandler.get_instance()

        assert handler1 is handler2

    def test_signal_handler_thread_safety(self):
        """Test that signal handler is thread-safe."""
        handler = SignalHandler()
        cleanup_calls = []

        def thread_cleanup(thread_id):
            cleanup_calls.append(thread_id)

        # Register cleanup functions from multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=lambda tid=i: handler.register_cleanup(
                    lambda: thread_cleanup(tid), f"cleanup {tid}"
                )
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Trigger shutdown
        handler.graceful_shutdown()

        # All cleanup functions should have been called
        assert len(cleanup_calls) == 5
        assert set(cleanup_calls) == {0, 1, 2, 3, 4}
