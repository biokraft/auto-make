"""Command runner for AutoMake.

This module provides functionality to execute shell commands and stream their output.
"""

import logging
import os
import signal
import subprocess
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automake.utils.output import LiveBox

logger = logging.getLogger(__name__)


class CommandRunnerError(Exception):
    """Raised when there's an error running a command."""

    pass


class CommandRunner:
    """Handles running shell commands with enhanced process management."""

    def __init__(self):
        """Initialize the command runner with process tracking."""
        self._active_processes: list[subprocess.Popen] = []
        self._process_lock = threading.Lock()
        self._register_with_signal_handler()

    def _register_with_signal_handler(self):
        """Register cleanup with the signal handler."""
        try:
            from automake.core.signal_handler import SignalHandler

            handler = SignalHandler.get_instance()
            handler.register_cleanup(
                self.cleanup_processes, "CommandRunner process cleanup"
            )
        except ImportError:
            # Signal handler not available, continue without registration
            pass

    def _create_process_group(self):
        """Create a new process group for child processes (Unix only)."""
        if os.name != "nt":  # Unix/Linux/macOS
            os.setsid()

    def _track_process(self, process: subprocess.Popen):
        """Track a process for cleanup."""
        with self._process_lock:
            self._active_processes.append(process)

    def _untrack_process(self, process: subprocess.Popen):
        """Stop tracking a process."""
        with self._process_lock:
            if process in self._active_processes:
                self._active_processes.remove(process)

    def run(
        self,
        command: str,
        capture_output: bool = False,
        live_box: "LiveBox | None" = None,
    ) -> str:
        """Run a make command and stream its output.

        Args:
            command: The make command to run (e.g., "build", "test")
            capture_output: Whether to capture and return the output instead of
                printing.
            live_box: Optional LiveBox instance for real-time output display

        Returns:
            The captured stdout if capture_output is True, otherwise an empty string.

        Raises:
            CommandRunnerError: If the command fails
        """
        full_command = f"make {command}"
        logger.info("Running command: %s", full_command)

        if live_box:
            # Start with empty content, will be filled with command output
            live_box.update("")

        try:
            # Use Popen for real-time output streaming with process group
            process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,
                preexec_fn=self._create_process_group if os.name != "nt" else None,
            )

            # Track the process for cleanup
            self._track_process(process)

            output_lines = []
            output_buffer = ""

            # Stream output in real-time
            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    if line:
                        output_lines.append(line.rstrip())
                        # Only print to console if no live_box and not capturing output
                        if not capture_output and not live_box:
                            print(line.rstrip())

                        # Update live box if provided
                        if live_box:
                            output_buffer += line
                            # Keep only last 20 lines for display
                            lines = output_buffer.split("\n")
                            if len(lines) > 20:
                                lines = lines[-20:]
                                output_buffer = "\n".join(lines)

                            # Show only the command output, dimmed
                            live_box.update(f"[dim]{output_buffer.rstrip()}[/dim]")

            # Wait for process to complete
            process.wait()

            # Untrack the process now that it's complete
            self._untrack_process(process)

            # Final output
            full_output = "\n".join(output_lines)

            if process.returncode == 0:
                logger.info(f"Command '{command}' completed successfully")
                return full_output
            else:
                error_msg = (
                    f"Command '{command}' failed with exit code {process.returncode}"
                )
                logger.error(error_msg)
                if live_box:
                    live_box.update(
                        f"❌ Command failed with exit code {process.returncode}\n\n"
                        f"{output_buffer.rstrip()}"
                    )
                raise CommandRunnerError(error_msg)

        except FileNotFoundError:
            logger.error(
                "`make` command not found. Is make installed and in your PATH?"
            )
            error_msg = (
                "`make` command not found. Please ensure GNU Make is installed "
                "and in your system's PATH."
            )

            if live_box:
                live_box.update(f"❌ Error: {error_msg}")

            raise CommandRunnerError(error_msg) from None
        except Exception as e:
            logger.error(
                "An unexpected error occurred while running the command: %s",
                e,
                exc_info=True,
            )
            error_msg = f"An unexpected error occurred: {e}"

            if live_box:
                live_box.update(f"❌ Error: {error_msg}")

            raise CommandRunnerError(error_msg) from e

    def cleanup_processes(self, timeout: float = 5.0):
        """Clean up all active processes.

        Args:
            timeout: Maximum time to wait for graceful termination
        """
        with self._process_lock:
            processes_to_cleanup = self._active_processes.copy()

        for process in processes_to_cleanup:
            try:
                if process.poll() is None:  # Process still running
                    # Try graceful termination first
                    if os.name != "nt":
                        try:
                            os.killpg(process.pid, signal.SIGTERM)
                        except ProcessLookupError:
                            # Process already terminated
                            continue
                    else:
                        process.terminate()

                    # Wait for graceful termination
                    try:
                        process.wait(timeout=timeout / 2)
                    except subprocess.TimeoutExpired:
                        # Force termination
                        if os.name != "nt":
                            try:
                                os.killpg(process.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                        else:
                            process.kill()

                        # Wait for force termination
                        try:
                            process.wait(timeout=timeout / 2)
                        except subprocess.TimeoutExpired:
                            logger.warning(
                                f"Process {process.pid} did not terminate after SIGKILL"
                            )
                else:
                    # Process already finished, just wait to prevent zombies
                    process.wait()

            except Exception as e:
                logger.warning(f"Error cleaning up process {process.pid}: {e}")

        # Clear the tracked processes
        with self._process_lock:
            self._active_processes.clear()

    def send_signal_to_processes(self, sig: int):
        """Send a signal to all active processes.

        Args:
            sig: Signal to send (e.g., signal.SIGINT)
        """
        with self._process_lock:
            processes = self._active_processes.copy()

        for process in processes:
            try:
                if process.poll() is None:  # Process still running
                    if os.name != "nt":
                        os.killpg(process.pid, sig)
                    else:
                        # Windows doesn't have process groups, send to process
                        if sig == signal.SIGINT:
                            process.send_signal(signal.CTRL_C_EVENT)
                        elif sig == signal.SIGTERM:
                            process.terminate()
                        else:
                            process.send_signal(sig)
            except (ProcessLookupError, OSError) as e:
                logger.debug(
                    f"Could not send signal {sig} to process {process.pid}: {e}"
                )
