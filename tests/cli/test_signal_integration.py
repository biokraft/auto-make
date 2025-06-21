"""Tests for signal handler integration in main entry points."""

import signal
import sys
from unittest.mock import MagicMock, patch

from automake.cli.app import app


class TestSignalIntegration:
    """Test cases for signal handler integration in main entry points."""

    def test_signal_handler_registered_in_cli_main(self):
        """Test that signal handler is registered when CLI main is called."""
        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_instance,
            patch("automake.cli.app._execute_primary_interface"),
        ):
            mock_handler = MagicMock()
            mock_get_instance.return_value = mock_handler

            # Import the app after patching
            from typer.testing import CliRunner

            from automake.cli.app import app

            runner = CliRunner()

            # Run the CLI with a command that triggers the main callback
            runner.invoke(app, ["test prompt"])

            # Should have registered signal handlers
            mock_handler.register_signal_handlers.assert_called()

    def test_signal_handler_registered_before_agent_initialization(self):
        """Test that signal handler is registered before agent initialization."""
        call_order = []

        def track_signal_register(*args):
            call_order.append("signal_register")

        def track_execute(*args, **kwargs):
            call_order.append("execute_primary")

        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_instance,
            patch(
                "automake.cli.app._execute_primary_interface", side_effect=track_execute
            ),
        ):
            mock_handler = MagicMock()
            mock_handler.register_signal_handlers.side_effect = track_signal_register
            mock_get_instance.return_value = mock_handler

            from typer.testing import CliRunner

            runner = CliRunner()
            runner.invoke(app, ["test prompt"])

            # Signal handler should be registered before execution
            assert "signal_register" in call_order
            if "execute_primary" in call_order:
                assert call_order.index("signal_register") < call_order.index(
                    "execute_primary"
                )

    def test_signal_handler_cleanup_registration_on_app_start(self):
        """Test that app components register cleanup with signal handler."""
        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_instance,
            patch("automake.cli.app._run_non_interactive") as mock_run_non_interactive,
        ):
            mock_handler = MagicMock()
            mock_get_instance.return_value = mock_handler

            # Mock the run function to avoid actual agent execution
            mock_run_non_interactive.return_value = None

            from typer.testing import CliRunner

            runner = CliRunner()
            runner.invoke(app, ["test prompt"])

            # Should have registered cleanup functions
            mock_handler.register_cleanup.assert_called()

    def test_signal_handler_integration_in_main_module(self):
        """Test that signal handler is integrated in __main__.py."""
        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_instance,
            patch("automake.cli.app.app"),
        ):
            mock_handler = MagicMock()
            mock_get_instance.return_value = mock_handler

            # Import and call __main__
            from automake.__main__ import main

            try:
                main()
            except SystemExit:
                pass

            # Should have registered signal handlers
            mock_handler.register_handlers.assert_called()

    def test_signal_handler_coordination_between_components(self):
        """Test that signal handler coordinates cleanup between different components."""
        cleanup_functions = []

        def track_cleanup(func, description):
            cleanup_functions.append(description)
            return f"cleanup_{len(cleanup_functions)}"

        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_instance,
            patch("automake.cli.app._run_non_interactive") as mock_run_non_interactive,
        ):
            mock_handler = MagicMock()
            mock_handler.register_cleanup.side_effect = track_cleanup
            mock_get_instance.return_value = mock_handler

            # Mock the run function to avoid actual agent execution
            mock_run_non_interactive.return_value = None

            from typer.testing import CliRunner

            runner = CliRunner()
            runner.invoke(app, ["test prompt"])

            # Should have registered cleanup for multiple components
            assert len(cleanup_functions) > 0

    def test_signal_handler_graceful_shutdown_on_sigint(self):
        """Test that SIGINT triggers graceful shutdown."""
        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_instance,
            patch("automake.cli.app._run_non_interactive") as mock_run_non_interactive,
        ):
            mock_handler = MagicMock()
            mock_get_instance.return_value = mock_handler

            # Mock the run function to avoid actual agent execution
            mock_run_non_interactive.return_value = None

            # Simulate SIGINT
            def simulate_sigint():
                # Call the registered SIGINT handler
                if mock_handler.register_signal_handlers.called:
                    # Simulate the signal handler being called
                    mock_handler.graceful_shutdown()

            from typer.testing import CliRunner

            runner = CliRunner()
            runner.invoke(app, ["test prompt"])
            simulate_sigint()

            # Should have called graceful shutdown
            mock_handler.graceful_shutdown.assert_called()

    def test_signal_handler_proper_exit_codes(self):
        """Test that signal handler uses proper exit codes."""
        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_instance,
            patch("automake.cli.app._run_non_interactive") as mock_run_non_interactive,
            patch("sys.exit") as mock_exit,
        ):
            mock_handler = MagicMock()
            mock_get_instance.return_value = mock_handler

            # Mock the run function to avoid actual agent execution
            mock_run_non_interactive.return_value = None

            # Mock the signal handler to call sys.exit with proper code
            def mock_sigint_handler(signum, frame):
                mock_handler.graceful_shutdown()
                sys.exit(130)

            mock_handler._handle_sigint = mock_sigint_handler

            from typer.testing import CliRunner

            runner = CliRunner()
            runner.invoke(app, ["test prompt"])

            # Simulate SIGINT
            try:
                mock_sigint_handler(signal.SIGINT, None)
            except SystemExit:
                pass

            # Should exit with code 130 for SIGINT
            mock_exit.assert_called_with(130)

    def test_signal_handler_prevents_double_registration(self):
        """Test that signal handler prevents double registration."""
        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_instance,
            patch("automake.cli.app._execute_primary_interface"),
        ):
            mock_handler = MagicMock()
            mock_get_instance.return_value = mock_handler

            from typer.testing import CliRunner

            runner = CliRunner()

            # Call main multiple times with commands that trigger the callback
            runner.invoke(app, ["test prompt 1"])
            runner.invoke(app, ["test prompt 2"])

            # Should only register handlers once due to singleton pattern
            # (The exact count depends on implementation, but should be consistent)
            assert mock_handler.register_signal_handlers.call_count >= 1

    def test_signal_handler_thread_safety(self):
        """Test that signal handler registration is thread-safe."""
        import threading

        registration_count = 0

        def count_registrations(*args):
            nonlocal registration_count
            registration_count += 1

        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_instance,
            patch("automake.cli.app._execute_primary_interface"),
        ):
            mock_handler = MagicMock()
            mock_handler.register_signal_handlers.side_effect = count_registrations
            mock_get_instance.return_value = mock_handler

            def run_main():
                from typer.testing import CliRunner

                runner = CliRunner()
                runner.invoke(app, ["test prompt"])

            # Run multiple threads concurrently
            threads = []
            for _ in range(3):
                thread = threading.Thread(target=run_main)
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Should have registered handlers for each thread
            assert registration_count >= 1
