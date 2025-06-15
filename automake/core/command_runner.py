"""Command runner for AutoMake.

This module provides functionality to execute shell commands and stream their output.
"""

import logging
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automake.utils.output import LiveBox

logger = logging.getLogger(__name__)


class CommandRunnerError(Exception):
    """Raised when there's an error running a command."""

    pass


class CommandRunner:
    """Handles running shell commands."""

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
            live_box.update(f"🚀 Executing: [cyan]{full_command}[/cyan]")

        try:
            # Use Popen for real-time output streaming
            process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,
            )

            output_lines = []
            output_buffer = ""

            # Stream output in real-time
            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    if line:
                        output_lines.append(line.rstrip())
                        if not capture_output:
                            print(line.rstrip())

                        # Update live box if provided
                        if live_box:
                            output_buffer += line
                            # Keep only last 20 lines for display
                            lines = output_buffer.split("\n")
                            if len(lines) > 20:
                                lines = lines[-20:]
                                output_buffer = "\n".join(lines)

                            live_box.update(
                                f"🚀 Executing: [cyan]{full_command}[/cyan]\n\n"
                                f"[dim]{output_buffer}[/dim]"
                            )

            # Wait for process to complete
            process.wait()

            # Final output
            full_output = "\n".join(output_lines)

            if process.returncode == 0:
                logger.info(f"Command '{command}' completed successfully")
                if live_box:
                    success_msg = (
                        f"✅ Command completed successfully: "
                        f"[green]{full_command}[/green]\n\n"
                        f"[dim]{output_buffer}[/dim]"
                    )
                    live_box.update(success_msg)
                return full_output
            else:
                error_msg = (
                    f"Command '{command}' failed with exit code {process.returncode}"
                )
                logger.error(error_msg)
                if live_box:
                    live_box.update(
                        f"❌ Command failed with exit code {process.returncode}\n\n"
                        f"[red]{output_buffer}[/red]"
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
