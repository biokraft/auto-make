"""Performance and reliability tests for signal handling."""

import signal
import threading
import time
from unittest.mock import MagicMock, patch


class TestSignalHandlingPerformance:
    """Test signal handling performance and reliability."""

    def setup_method(self):
        """Reset SignalHandler before each test."""
        from automake.core.signal_handler import SignalHandler

        SignalHandler._reset_instance()

    def test_signal_handling_under_high_load(self):
        """Test that signal handling works correctly under high load."""
        from automake.core.command_runner import CommandRunner
        from automake.core.signal_handler import SignalHandler

        # Reset signal handler for clean test
        SignalHandler._instance = None
        handler = SignalHandler.get_instance()

        # Create multiple command runners to simulate high load
        runners = []
        for _i in range(10):
            runner = CommandRunner()
            runners.append(runner)

        # Simulate high load by registering many cleanup functions
        cleanup_calls = []

        def mock_cleanup(name):
            def cleanup_func():
                cleanup_calls.append(name)
                # Simulate some work
                time.sleep(0.01)

            return cleanup_func

        # Register cleanup functions
        for i, _runner in enumerate(runners):
            handler.register_cleanup(mock_cleanup(f"runner_{i}"), f"CommandRunner {i}")

        # Simulate signal handling
        start_time = time.time()
        handler.graceful_shutdown()
        end_time = time.time()

        # Verify all cleanups were called
        assert len(cleanup_calls) == 10

        # Verify it completed within reasonable time (should be < 1 second)
        assert end_time - start_time < 1.0

        # Reset for other tests
        SignalHandler._instance = None

    def test_signal_handling_with_multiple_concurrent_processes(self):
        """Test signal handling with multiple concurrent processes."""
        from automake.core.command_runner import CommandRunner
        from automake.core.signal_handler import SignalHandler

        # Reset signal handler for clean test
        SignalHandler._instance = None
        handler = SignalHandler.get_instance()

        with patch("subprocess.Popen") as mock_popen, patch("os.killpg") as mock_killpg:
            # Create multiple mock processes
            mock_processes = []
            for i in range(5):
                mock_process = MagicMock()
                mock_process.pid = 12345 + i
                mock_process.poll.return_value = None  # Still running
                mock_process.stdout.readline.side_effect = ["output\n", ""]
                mock_process.wait.return_value = None
                mock_process.returncode = 0
                mock_processes.append(mock_process)

            mock_popen.side_effect = mock_processes

            # Create command runners and start processes
            runners = []
            for i in range(5):
                runner = CommandRunner()
                runner.run(f"sleep {i}")
                # Manually track processes to simulate concurrent execution
                runner._track_process(mock_processes[i])
                runners.append(runner)

            # Simulate signal handling
            start_time = time.time()
            handler.graceful_shutdown()
            end_time = time.time()

            # Verify all processes were signaled
            assert mock_killpg.call_count >= 5

            # Verify it completed within reasonable time
            assert end_time - start_time < 2.0

            # Reset for other tests
            SignalHandler._instance = None

    def test_signal_handling_cleanup_timeout_enforcement(self):
        """Test that cleanup timeout is properly enforced."""
        from automake.config.manager import Config
        from automake.core.signal_handler import SignalHandler

        # Reset signal handler for clean test
        SignalHandler._instance = None
        handler = SignalHandler.get_instance()

        # Create config with short timeout
        config = Config()

        # Register a cleanup function that takes too long
        slow_cleanup_called = False

        def slow_cleanup():
            nonlocal slow_cleanup_called
            slow_cleanup_called = True
            time.sleep(2.0)  # Takes longer than timeout

        handler.register_cleanup(slow_cleanup, "Slow cleanup")

        # Simulate signal handling with timeout
        start_time = time.time()
        handler.graceful_shutdown()
        end_time = time.time()

        # Verify cleanup was called
        assert slow_cleanup_called

        # Verify it didn't wait for the full slow cleanup
        # Should complete within timeout + small buffer
        assert end_time - start_time < config.signal_cleanup_timeout + 0.5

        # Reset for other tests
        SignalHandler._instance = None

    def test_signal_handling_edge_case_rapid_signals(self):
        """Test signal handling with rapid signal sending."""
        from automake.core.signal_handler import SignalHandler

        # Reset signal handler for clean test
        SignalHandler._instance = None
        handler = SignalHandler.get_instance()

        # Track shutdown calls with proper flag handling
        shutdown_calls = []
        original_graceful_shutdown = handler._graceful_shutdown

        def mock_shutdown():
            shutdown_calls.append(time.time())
            # Call the original method to set the shutdown flag properly
            original_graceful_shutdown()

        with (
            patch.object(handler, "_graceful_shutdown", side_effect=mock_shutdown),
            patch("sys.exit") as mock_exit,
        ):
            # Simulate rapid signal sending
            for _ in range(3):
                handler._signal_handler(signal.SIGINT, None)
                time.sleep(0.01)  # Small delay between signals

        # Should have only triggered shutdown once due to shutdown_in_progress flag
        assert len(shutdown_calls) == 1

        # Should have called sys.exit with code 130
        mock_exit.assert_called_with(130)

        # Reset for other tests
        SignalHandler._instance = None

    def test_signal_handling_memory_efficiency(self):
        """Test that signal handling doesn't leak memory with many registrations."""
        from automake.core.signal_handler import SignalHandler

        # Reset signal handler for clean test
        SignalHandler._instance = None
        handler = SignalHandler.get_instance()

        # Register many cleanup functions
        cleanup_ids = []
        for i in range(100):

            def cleanup_func():
                pass

            cleanup_id = handler.register_cleanup(cleanup_func, f"Cleanup {i}")
            cleanup_ids.append(cleanup_id)

        # Verify all were registered
        assert len(handler.cleanup_registry) == 100

        # Unregister half of them
        for i in range(0, 100, 2):
            handler.unregister_cleanup(cleanup_ids[i])

        # Verify registry was cleaned up
        assert len(handler.cleanup_registry) == 50

        # Reset for other tests
        SignalHandler._instance = None

    def test_signal_handling_thread_safety(self):
        """Test that signal handling is thread-safe."""
        from automake.core.signal_handler import SignalHandler

        # Reset signal handler for clean test
        SignalHandler._instance = None
        handler = SignalHandler.get_instance()

        # Track registrations from different threads
        registration_results = []

        def register_cleanup(thread_id):
            def cleanup_func():
                pass

            cleanup_id = handler.register_cleanup(cleanup_func, f"Thread {thread_id}")
            registration_results.append((thread_id, cleanup_id))

        # Start multiple threads registering cleanup functions
        threads = []
        for i in range(10):
            thread = threading.Thread(target=register_cleanup, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all registrations succeeded
        assert len(registration_results) == 10
        assert len(handler.cleanup_registry) == 10

        # Verify all cleanup IDs are unique
        cleanup_ids = [result[1] for result in registration_results]
        assert len(set(cleanup_ids)) == 10

        # Reset for other tests
        SignalHandler._instance = None

    def test_signal_handling_resource_cleanup_completeness(self):
        """Test that all registered resources are properly cleaned up."""
        from automake.agent.manager import ManagerAgentRunner
        from automake.config.manager import Config
        from automake.core.command_runner import CommandRunner
        from automake.core.signal_handler import SignalHandler

        # Reset signal handler for clean test
        SignalHandler._instance = None
        handler = SignalHandler.get_instance()

        # Track cleanup execution by patching cleanup methods before creating
        cleanup_executions = []

        def track_command_cleanup():
            cleanup_executions.append("CommandRunner")

        def track_agent_cleanup():
            cleanup_executions.append("ManagerAgentRunner")

        # Patch the cleanup methods before creating the components
        with (
            patch(
                "automake.core.command_runner.CommandRunner.cleanup_processes",
                side_effect=track_command_cleanup,
            ),
            patch(
                "automake.agent.manager.ManagerAgentRunner.shutdown",
                side_effect=track_agent_cleanup,
            ),
            patch("automake.agent.manager.create_manager_agent") as mock_create,
        ):
            mock_create.return_value = (MagicMock(), False)

            # Create components - they will register their patched cleanup methods
            config = Config()
            agent_runner = ManagerAgentRunner(config)

            # Create CommandRunner explicitly to register it with signal handler
            CommandRunner()

            try:
                agent_runner.initialize()
            except Exception:
                pass  # Expected to fail in test environment

            # Verify components registered cleanup
            # CommandRunner and ManagerAgentRunner
            assert len(handler.cleanup_registry) >= 2

            # Simulate signal handling
            handler.graceful_shutdown()

            # Verify cleanup was executed
            assert "CommandRunner" in cleanup_executions
            assert "ManagerAgentRunner" in cleanup_executions

        # Reset for other tests
        SignalHandler._instance = None
