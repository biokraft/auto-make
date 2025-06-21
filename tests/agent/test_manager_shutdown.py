"""Tests for agent manager shutdown functionality."""

import threading
import time
from unittest.mock import MagicMock, patch

from automake.agent.manager import ManagerAgentRunner
from automake.config import Config


class TestManagerAgentShutdown:
    """Test cases for ManagerAgentRunner shutdown functionality."""

    def test_manager_agent_has_shutdown_method(self):
        """Test that ManagerAgentRunner has a shutdown method."""
        config = Config()
        runner = ManagerAgentRunner(config)

        # Should have a shutdown method
        assert hasattr(runner, "shutdown")
        assert callable(runner.shutdown)

    def test_shutdown_method_cleans_up_resources(self):
        """Test that shutdown method cleans up agent resources."""
        config = Config()
        runner = ManagerAgentRunner(config)

        # Mock some resources that need cleanup
        runner._cleanup_functions = []
        cleanup_mock = MagicMock()
        runner._cleanup_functions.append(cleanup_mock)

        # Call shutdown
        runner.shutdown()

        # Verify cleanup was called
        cleanup_mock.assert_called_once()

    def test_shutdown_handles_uninitialized_agent(self):
        """Test that shutdown works even if agent is not initialized."""
        config = Config()
        runner = ManagerAgentRunner(config)

        # Should not raise exception even if agent is None
        runner.shutdown()  # Should not raise

    @patch("automake.agent.manager.create_manager_agent")
    def test_shutdown_after_initialization(self, mock_create_agent):
        """Test shutdown after agent has been initialized."""
        config = Config()
        runner = ManagerAgentRunner(config)

        # Mock agent creation
        mock_agent = MagicMock()
        mock_create_agent.return_value = (mock_agent, False)

        # Initialize the agent
        runner.initialize()

        # Shutdown should work
        runner.shutdown()

        # Agent should be set to None after shutdown
        assert runner.agent is None

    def test_shutdown_terminates_child_processes(self):
        """Test that shutdown terminates any child processes."""
        config = Config()
        runner = ManagerAgentRunner(config)

        # Mock child processes
        mock_process1 = MagicMock()
        mock_process2 = MagicMock()
        runner._child_processes = [mock_process1, mock_process2]

        # Call shutdown
        runner.shutdown()

        # Verify processes were terminated
        mock_process1.terminate.assert_called_once()
        mock_process2.terminate.assert_called_once()

    def test_shutdown_with_timeout(self):
        """Test that shutdown respects timeout for child processes."""
        config = Config()
        runner = ManagerAgentRunner(config)

        # Mock a process that doesn't terminate quickly
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process still running
        runner._child_processes = [mock_process]

        start_time = time.time()
        runner.shutdown(timeout=0.1)
        end_time = time.time()

        # Should have called terminate and then kill
        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()

        # Should respect timeout
        assert end_time - start_time < 0.2

    def test_shutdown_is_thread_safe(self):
        """Test that shutdown can be called safely from multiple threads."""
        config = Config()
        runner = ManagerAgentRunner(config)

        shutdown_calls = []

        def thread_shutdown(thread_id):
            runner.shutdown()
            shutdown_calls.append(thread_id)

        # Start multiple threads calling shutdown
        threads = []
        for i in range(5):
            thread = threading.Thread(target=thread_shutdown, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All threads should have completed without error
        assert len(shutdown_calls) == 5

    def test_shutdown_cleans_temporary_files(self):
        """Test that shutdown cleans up temporary files."""
        config = Config()
        runner = ManagerAgentRunner(config)

        # Mock temporary files
        temp_file1 = "/tmp/automake_temp_1"
        temp_file2 = "/tmp/automake_temp_2"
        runner._temp_files = [temp_file1, temp_file2]

        with patch("os.path.exists") as mock_exists, patch("os.unlink") as mock_unlink:
            mock_exists.return_value = True

            runner.shutdown()

            # Should have attempted to remove temp files
            assert mock_unlink.call_count == 2

    def test_shutdown_registers_with_signal_handler(self):
        """Test that ManagerAgentRunner registers shutdown with signal handler."""
        config = Config()

        with (
            patch(
                "automake.core.signal_handler.SignalHandler.get_instance"
            ) as mock_get_handler,
            patch("automake.agent.manager.create_manager_agent") as mock_create_agent,
        ):
            mock_handler = MagicMock()
            mock_get_handler.return_value = mock_handler
            mock_create_agent.return_value = (MagicMock(), False)

            runner = ManagerAgentRunner(config)

            # Mock the shutdown method before initialization
            with patch.object(runner, "shutdown") as mock_shutdown:
                runner.initialize()

                # Should have registered cleanup function with signal handler
                mock_handler.register_cleanup.assert_called()

                # Get the registered cleanup function
                cleanup_call = mock_handler.register_cleanup.call_args
                cleanup_func = cleanup_call[0][0]
                cleanup_desc = cleanup_call[0][1]

                assert "agent manager" in cleanup_desc.lower()

                # Calling the cleanup function should trigger shutdown
                cleanup_func()
                mock_shutdown.assert_called_once()
