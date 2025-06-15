"""Logs command implementation for AutoMake CLI.

This module contains all log management commands that wrap the functionality
from automake.cli.logs.
"""

import typer
from rich.console import Console

from automake.cli.logs import (
    clear_logs,
    show_log_config,
    show_logs_location,
    view_log_content,
)
from automake.utils.output import get_formatter


def logs_show_command() -> None:
    """Show log files location and information."""
    console = Console()
    output = get_formatter(console)
    show_logs_location(console, output)


def logs_view_command(
    lines: int = typer.Option(
        50,
        "--lines",
        "-n",
        help="Number of lines to show from the end of the log",
        min=1,
    ),
    follow: bool = typer.Option(
        False,
        "--follow",
        "-f",
        help="Follow the log file (like tail -f)",
    ),
    file: str = typer.Option(
        None,
        "--file",
        help="Specific log file to view (defaults to current log)",
    ),
) -> None:
    """View log file contents."""
    console = Console()
    output = get_formatter(console)
    view_log_content(console, output, lines=lines, follow=follow, log_file=file)


def logs_clear_command(
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Clear all log files."""
    console = Console()
    output = get_formatter(console)
    clear_logs(console, output, confirm=yes)


def logs_config_command() -> None:
    """Show logging configuration."""
    console = Console()
    output = get_formatter(console)
    show_log_config(console, output)
