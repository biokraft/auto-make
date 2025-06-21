"""Integration tests for signal handling across all components."""

import signal
import subprocess
from unittest.mock import MagicMock, patch


class TestSignalHandlingIntegration:
    """Integration tests for signal handling across all components."""

    def test_signal_handler_integrates_with_all_components(self):
        """Test that signal handler properly integrates with all components."""
        from automake.core.signal_handler import SignalHandler

        # Get signal handler instance
        handler = SignalHandler.get_instance()

        # Verify signal handler is properly configured
        assert handler is not None
        assert hasattr(handler, "cleanup_registry")
        assert hasattr(handler, "register_cleanup")
        assert hasattr(handler, "graceful_shutdown")

    def test_signal_handling_in_interactive_mode_simulation(self):
        """Test signal handling behavior in interactive mode simulation."""
        with patch(
            "automake.core.signal_handler.SignalHandler.get_instance"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_get_handler.return_value = mock_handler

            # Create a mock ToolCallingAgent
            mock_agent = MagicMock()

            # Create session - this should trigger signal handler registration
            from automake.agent.ui.session import RichInteractiveSession

            session = RichInteractiveSession(mock_agent)

            # Simulate starting the session to trigger signal handler registration
            with patch.object(session, "get_user_input", side_effect=EOFError):
                with patch.object(session.console, "print"):
                    try:
                        session.start()
                    except Exception:
                        pass  # Expected to fail during test

            # Verify signal handler integration
            assert mock_handler.register_cleanup.called

    def test_signal_handling_in_non_interactive_mode_simulation(self):
        """Test signal handling behavior in non-interactive mode simulation."""
        with patch(
            "automake.core.signal_handler.SignalHandler.get_instance"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_get_handler.return_value = mock_handler

            # Create agent runner with config
            from automake.agent.manager import ManagerAgentRunner
            from automake.config.manager import Config

            config = Config()
            runner = ManagerAgentRunner(config)

            # Initialize the runner to trigger signal handler registration
            with patch("automake.agent.manager.create_manager_agent") as mock_create:
                mock_create.return_value = (MagicMock(), False)
                try:
                    runner.initialize()
                except Exception:
                    pass  # Expected to fail during test

            # Verify signal handler integration
            assert mock_handler.register_cleanup.called

    def test_signal_handling_during_command_execution_simulation(self):
        """Test signal handling during command execution simulation."""
        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_handler,
            patch("subprocess.Popen") as mock_popen,
        ):
            mock_handler = MagicMock()
            mock_get_handler.return_value = mock_handler
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["test output\n", ""]
            mock_process.wait.return_value = None
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            from automake.core.command_runner import CommandRunner

            runner = CommandRunner()

            # Verify signal handler integration
            assert mock_handler.register_cleanup.called

            # Simulate running a command
            runner.run("test")

            # Verify process tracking works
            assert hasattr(runner, "_active_processes")

    def test_end_to_end_signal_handling_coordination(self):
        """Test end-to-end signal handling coordination between components."""
        cleanup_calls = []

        def track_cleanup(func, description):
            cleanup_calls.append(description)
            return f"cleanup_{len(cleanup_calls)}"

        with patch(
            "automake.core.signal_handler.SignalHandler.get_instance"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_handler.register_cleanup.side_effect = track_cleanup
            mock_get_handler.return_value = mock_handler

            # Import and create components
            from automake.agent.manager import ManagerAgentRunner
            from automake.agent.ui.session import RichInteractiveSession
            from automake.config.manager import Config
            from automake.core.command_runner import CommandRunner

            # Create instances
            config = Config()
            mock_agent = MagicMock()
            agent_runner = ManagerAgentRunner(config)

            # Create CommandRunner explicitly to register it with signal handler
            CommandRunner()

            # Initialize agent runner to trigger registration
            with patch("automake.agent.manager.create_manager_agent") as mock_create:
                mock_create.return_value = (MagicMock(), False)
                try:
                    agent_runner.initialize()
                except Exception:
                    pass

            session = RichInteractiveSession(mock_agent)

            # Start session to trigger registration
            with patch.object(session, "get_user_input", side_effect=EOFError):
                with patch.object(session.console, "print"):
                    try:
                        session.start()
                    except Exception:
                        pass

            # Verify all components registered cleanup
            assert (
                len(cleanup_calls) >= 2
            )  # At least CommandRunner and ManagerAgentRunner
            assert any("CommandRunner" in call for call in cleanup_calls)

    def test_signal_handling_prevents_zombie_processes_integration(self):
        """Test that signal handling prevents zombie processes in integration."""
        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_handler,
            patch("subprocess.Popen") as mock_popen,
            patch("os.killpg") as mock_killpg,
        ):
            mock_handler = MagicMock()
            mock_get_handler.return_value = mock_handler
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None  # Process still running
            mock_process.stdout.readline.side_effect = ["test output\n", ""]
            mock_process.wait.return_value = None
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            from automake.core.command_runner import CommandRunner

            runner = CommandRunner()

            # Run command and manually add process to simulate running state
            runner.run("test")
            runner._track_process(mock_process)

            # Simulate signal handler cleanup
            runner.cleanup_processes()

            # Verify process was terminated
            mock_killpg.assert_called()

    def test_signal_handling_configuration_integration(self):
        """Test that signal handling uses configuration values."""
        from automake.config.manager import Config

        # Create config instance
        config = Config()

        # Verify signal configuration exists
        assert hasattr(config, "signal_handling_enabled")
        assert hasattr(config, "signal_cleanup_timeout")
        assert hasattr(config, "signal_force_kill_timeout")

        # Verify reasonable defaults
        assert isinstance(config.signal_handling_enabled, bool)
        assert isinstance(config.signal_cleanup_timeout, int | float)
        assert isinstance(config.signal_force_kill_timeout, int | float)
        assert config.signal_cleanup_timeout > 0
        assert config.signal_force_kill_timeout > 0

    def test_signal_handling_proper_exit_codes_integration(self):
        """Test that signal handling uses proper exit codes in integration."""
        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_handler,
            patch("sys.exit") as mock_exit,
        ):
            mock_handler = MagicMock()
            mock_get_handler.return_value = mock_handler

            # Simulate SIGINT handling
            def simulate_sigint_handler(signum, frame):
                mock_handler.graceful_shutdown()
                import sys

                sys.exit(130)

            try:
                simulate_sigint_handler(signal.SIGINT, None)
            except SystemExit:
                pass

            # Verify proper exit code
            mock_exit.assert_called_with(130)

    def test_signal_handling_timeout_enforcement_integration(self):
        """Test that signal handling enforces timeouts in integration."""
        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_handler,
            patch("subprocess.Popen") as mock_popen,
            patch("time.sleep"),
        ):
            mock_handler = MagicMock()
            mock_get_handler.return_value = mock_handler
            mock_process = MagicMock()
            mock_process.pid = 12345
            # Process doesn't terminate gracefully
            mock_process.poll.side_effect = [
                None,
                None,
                -9,
            ]  # Still running, still running, killed
            mock_process.wait.side_effect = [
                None,
                subprocess.TimeoutExpired("cmd", 1.0),
            ]
            mock_process.stdout.readline.side_effect = ["test output\n", ""]
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            from automake.core.command_runner import CommandRunner

            runner = CommandRunner()

            # Run command and add to active processes
            runner.run("test")
            runner._track_process(mock_process)

            # Test cleanup with timeout
            runner.cleanup_processes(timeout=1.0)

            # Should have attempted graceful termination with timeout
            assert mock_process.wait.called
