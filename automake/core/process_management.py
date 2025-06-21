"""Process management utilities for AutoMake.

This module provides enhanced process management capabilities including:
- Process group management
- Child process tracking
- Signal propagation
- Graceful shutdown with timeouts
- Zombie process prevention
"""

import logging
import os
import signal
import subprocess
import threading
import time

from automake.core.signal_handler import SignalHandler

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages process groups and child processes with enhanced cleanup capabilities."""

    def __init__(self):
        """Initialize the process manager."""
        self._processes: dict[int, subprocess.Popen] = {}
        self._process_groups: set[int] = set()
        self._lock = threading.Lock()
        self._signal_handler = SignalHandler()

        # Register cleanup with signal handler
        self._signal_handler.register_cleanup(self.cleanup_all_processes)

    def create_process_group(
        self, command: str, shell: bool = True, **kwargs
    ) -> subprocess.Popen:
        """Create a new process in its own process group.

        Args:
            command: Command to execute
            shell: Whether to use shell execution
            **kwargs: Additional arguments for subprocess.Popen

        Returns:
            The created subprocess.Popen object

        Raises:
            OSError: If process creation fails
        """
        try:
            # Set process group creation
            if os.name == "posix":
                # On Unix-like systems, create new process group
                kwargs["preexec_fn"] = os.setsid

            # Create the process
            process = subprocess.Popen(command, shell=shell, **kwargs)

            with self._lock:
                # Track the process
                self._processes[process.pid] = process

                # Track process group if created
                if os.name == "posix":
                    self._process_groups.add(process.pid)

            logger.debug(f"Created process {process.pid} in new process group")
            return process

        except Exception as e:
            logger.error(f"Failed to create process group: {e}")
            raise

    def track_process(self, process: subprocess.Popen) -> None:
        """Track an existing process for cleanup.

        Args:
            process: Process to track
        """
        with self._lock:
            if process.pid:
                self._processes[process.pid] = process
                logger.debug(f"Now tracking process {process.pid}")

    def terminate_process(
        self, pid: int, timeout: float = 5.0, force_timeout: float = 2.0
    ) -> bool:
        """Terminate a process gracefully with escalating signals.

        Args:
            pid: Process ID to terminate
            timeout: Total timeout for termination
            force_timeout: Timeout before escalating to SIGKILL

        Returns:
            True if process was terminated successfully
        """
        with self._lock:
            process = self._processes.get(pid)

        if not process:
            logger.debug(f"Process {pid} not found in tracked processes")
            return True

        try:
            # Check if already terminated
            if process.poll() is not None:
                logger.debug(f"Process {pid} already terminated")
                self._cleanup_process(pid)
                return True

            # First try SIGTERM
            logger.debug(f"Sending SIGTERM to process {pid}")
            if os.name == "posix":
                # Send to process group if it's a group leader
                if pid in self._process_groups:
                    os.killpg(pid, signal.SIGTERM)
                else:
                    process.terminate()
            else:
                process.terminate()

            # Wait for graceful termination
            try:
                process.wait(timeout=force_timeout)
                logger.debug(f"Process {pid} terminated gracefully")
                self._cleanup_process(pid)
                return True
            except subprocess.TimeoutExpired:
                pass

            # Escalate to SIGKILL
            logger.debug(f"Escalating to SIGKILL for process {pid}")
            if os.name == "posix":
                if pid in self._process_groups:
                    os.killpg(pid, signal.SIGKILL)
                else:
                    process.kill()
            else:
                process.kill()

            # Final wait
            try:
                process.wait(timeout=timeout - force_timeout)
                logger.debug(f"Process {pid} force-killed")
                self._cleanup_process(pid)
                return True
            except subprocess.TimeoutExpired:
                logger.error(f"Failed to terminate process {pid} within timeout")
                return False

        except ProcessLookupError:
            # Process already dead
            logger.debug(f"Process {pid} already dead")
            self._cleanup_process(pid)
            return True
        except Exception as e:
            logger.error(f"Error terminating process {pid}: {e}")
            return False

    def cleanup_all_processes(self, timeout: float = 10.0) -> None:
        """Clean up all tracked processes.

        Args:
            timeout: Maximum time to wait for all processes to terminate
        """
        with self._lock:
            process_ids = list(self._processes.keys())

        if not process_ids:
            logger.debug("No processes to clean up")
            return

        logger.info(f"Cleaning up {len(process_ids)} tracked processes")

        # Terminate all processes concurrently
        start_time = time.time()
        per_process_timeout = min(timeout / len(process_ids), 5.0)

        for pid in process_ids:
            remaining_time = timeout - (time.time() - start_time)
            if remaining_time <= 0:
                logger.warning("Timeout reached during process cleanup")
                break

            actual_timeout = min(per_process_timeout, remaining_time)
            self.terminate_process(pid, timeout=actual_timeout)

    def _cleanup_process(self, pid: int) -> None:
        """Remove process from tracking.

        Args:
            pid: Process ID to clean up
        """
        with self._lock:
            self._processes.pop(pid, None)
            self._process_groups.discard(pid)

    def get_tracked_processes(self) -> list[int]:
        """Get list of currently tracked process IDs.

        Returns:
            List of tracked process IDs
        """
        with self._lock:
            return list(self._processes.keys())

    def is_process_running(self, pid: int) -> bool:
        """Check if a tracked process is still running.

        Args:
            pid: Process ID to check

        Returns:
            True if process is running
        """
        with self._lock:
            process = self._processes.get(pid)

        if not process:
            return False

        return process.poll() is None


# Global process manager instance
_process_manager: ProcessManager | None = None


def get_process_manager() -> ProcessManager:
    """Get the global process manager instance.

    Returns:
        The global ProcessManager instance
    """
    global _process_manager
    if _process_manager is None:
        _process_manager = ProcessManager()
    return _process_manager


def create_managed_process(
    command: str, shell: bool = True, **kwargs
) -> subprocess.Popen:
    """Create a process with automatic management and cleanup.

    Args:
        command: Command to execute
        shell: Whether to use shell execution
        **kwargs: Additional arguments for subprocess.Popen

    Returns:
        The created subprocess.Popen object
    """
    manager = get_process_manager()
    return manager.create_process_group(command, shell=shell, **kwargs)
