"""Command runner for AutoMake.

This module provides functionality to execute shell commands and stream their output.
"""

import logging
import subprocess

logger = logging.getLogger(__name__)


class CommandRunnerError(Exception):
    """Raised when there's an error running a command."""

    pass


class CommandRunner:
    """Handles running shell commands."""

    def run(self, command: str, capture_output: bool = False) -> str:
        """Run a make command and stream its output.

        Args:
            command: The make command to run (e.g., "build", "test")
            capture_output: Whether to capture and return the output instead of
                printing.

        Returns:
            The captured stdout if capture_output is True, otherwise an empty string.

        Raises:
            CommandRunnerError: If the command fails
        """
        full_command = f"make {command}"
        logger.info("Running command: %s", full_command)

        try:
            # Using subprocess.Popen to stream output in real-time
            process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line-buffered
            )

            stdout_lines = []

            # We must handle stdout and stderr separately to avoid deadlocks
            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    if capture_output:
                        stdout_lines.append(line)
                    else:
                        print(line, end="")  # Stream to console

            # Wait for the process to complete and get the return code
            process.wait()

            if process.returncode != 0:
                # Read stderr if there was an error
                stderr_output = process.stderr.read() if process.stderr else ""
                logger.error(
                    "Command failed with exit code %d:\n%s",
                    process.returncode,
                    stderr_output,
                )
                raise CommandRunnerError(
                    f"Command '{full_command}' failed with exit code "
                    f"{process.returncode}.\nError:\n{stderr_output}"
                )

            logger.info("Command finished successfully")
            return "".join(stdout_lines)

        except FileNotFoundError:
            logger.error(
                "`make` command not found. Is make installed and in your PATH?"
            )
            raise CommandRunnerError(
                "`make` command not found. Please ensure GNU Make is installed "
                "and in your system's PATH."
            ) from None
        except Exception as e:
            logger.error(
                "An unexpected error occurred while running the command: %s",
                e,
                exc_info=True,
            )
            raise CommandRunnerError(f"An unexpected error occurred: {e}") from e
