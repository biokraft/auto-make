"""Tests for enhanced process management with signal handling."""

import signal
import subprocess
from unittest.mock import MagicMock, call, patch

from automake.core.command_runner import CommandRunner


class TestProcessManagement:
    """Test cases for enhanced process management with signal handling."""

    def test_command_runner_uses_process_groups(self):
        """Test that command runner creates process groups for child processes."""
        runner = CommandRunner()

        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["test output\n", ""]
            mock_process.wait.return_value = None
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            runner.run("echo test")

            # Should have called Popen with preexec_fn to set process group
            mock_popen.assert_called_once()
            call_kwargs = mock_popen.call_args.kwargs
            assert "preexec_fn" in call_kwargs
            # The preexec_fn should set a new process group
            assert call_kwargs["preexec_fn"] is not None

    def test_command_runner_tracks_child_processes(self):
        """Test that command runner tracks child processes for cleanup."""
        runner = CommandRunner()

        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.stdout.readline.side_effect = ["test output\n", ""]
            mock_process.wait.return_value = None
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            runner.run("echo test")

            # Should track the process for cleanup initially, but untrack after
            assert hasattr(runner, "_active_processes")
            # Process should be untracked after successful completion
            assert 12345 not in [p.pid for p in runner._active_processes]

    def test_command_runner_cleanup_terminates_processes(self):
        """Test that cleanup properly terminates child processes."""
        runner = CommandRunner()

        with patch("subprocess.Popen") as mock_popen, patch("os.killpg") as mock_killpg:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None  # Process still running
            mock_process.stdout.readline.side_effect = ["test output\n", ""]
            mock_process.wait.return_value = None
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            # Manually add process to active list to simulate running process
            runner.run("sleep 10")
            # Add the process back to simulate it's still running
            runner._track_process(mock_process)

            runner.cleanup_processes()

            # Should have attempted to kill the process group
            mock_killpg.assert_called()

    def test_command_runner_timeout_based_force_termination(self):
        """Test that command runner uses timeout-based force termination."""
        runner = CommandRunner()

        with (
            patch("subprocess.Popen") as mock_popen,
            patch("os.killpg") as mock_killpg,
            patch("time.sleep"),
        ):
            mock_process = MagicMock()
            mock_process.pid = 12345
            # First poll returns None (running), second returns None (still running)
            # Third poll should return exit code (terminated)
            mock_process.poll.side_effect = [None, None, -15]
            mock_process.stdout.readline.side_effect = ["test output\n", ""]
            # Normal wait should succeed, but cleanup wait should timeout
            mock_process.wait.side_effect = [
                None,
                subprocess.TimeoutExpired("cmd", 1.0),
                None,
            ]
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            runner.run("sleep 10")
            # Add the process back to simulate it's still running
            runner._track_process(mock_process)

            runner.cleanup_processes(timeout=1.0)

            # Should have tried SIGTERM first, then SIGKILL
            expected_calls = [call(12345, signal.SIGTERM), call(12345, signal.SIGKILL)]
            mock_killpg.assert_has_calls(expected_calls)

    def test_command_runner_prevents_zombie_processes(self):
        """Test that command runner prevents zombie processes."""
        runner = CommandRunner()

        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.poll.return_value = 0  # Process finished
            mock_process.stdout.readline.side_effect = ["test output\n", ""]
            mock_process.wait.return_value = None
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            runner.run("echo test")
            # Add the process back to simulate cleanup scenario
            runner._track_process(mock_process)

            runner.cleanup_processes()

            # Should have waited for process to complete
            mock_process.wait.assert_called()

    def test_command_runner_signal_propagation(self):
        """Test that command runner propagates signals to child processes."""
        runner = CommandRunner()

        with patch("subprocess.Popen") as mock_popen, patch("os.killpg") as mock_killpg:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None  # Process still running
            mock_process.stdout.readline.side_effect = ["test output\n", ""]
            mock_process.wait.return_value = None
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            runner.run("sleep 10")
            # Add the process back to simulate it's still running
            runner._track_process(mock_process)

            runner.send_signal_to_processes(signal.SIGINT)

            # Should have sent signal to process group
            mock_killpg.assert_called_with(12345, signal.SIGINT)

    def test_command_runner_handles_process_group_errors(self):
        """Test that command runner handles process group errors gracefully."""
        runner = CommandRunner()

        with (
            patch("subprocess.Popen") as mock_popen,
            patch(
                "os.killpg", side_effect=ProcessLookupError("No such process")
            ) as mock_killpg,
        ):
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None
            mock_process.stdout.readline.side_effect = ["test output\n", ""]
            mock_process.wait.return_value = None
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            runner.run("echo test")
            # Add the process back to simulate cleanup scenario
            runner._track_process(mock_process)

            # Should not raise exception when process doesn't exist
            runner.cleanup_processes()

            # Should have attempted to kill but handled the error
            mock_killpg.assert_called()

    def test_command_runner_integration_with_signal_handler(self):
        """Test that command runner integrates with signal handler for cleanup."""
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

            runner = CommandRunner()
            runner.run("echo test")

            # Should have registered cleanup with signal handler
            mock_handler.register_cleanup.assert_called()

    def test_command_runner_concurrent_process_management(self):
        """Test that command runner handles concurrent processes safely."""
        import threading

        runner = CommandRunner()

        with patch("subprocess.Popen") as mock_popen:
            mock_processes = []
            for i in range(3):
                mock_process = MagicMock()
                mock_process.pid = 12345 + i
                mock_process.stdout.readline.side_effect = ["test output\n", ""]
                mock_process.wait.return_value = None
                mock_process.returncode = 0
                mock_processes.append(mock_process)

            mock_popen.side_effect = mock_processes

            def run_command(cmd):
                runner.run(f"echo {cmd}")

            # Run multiple commands concurrently
            threads = []
            for i in range(3):
                thread = threading.Thread(target=run_command, args=(f"test{i}",))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # All processes should have completed and been untracked
            assert len(runner._active_processes) == 0
