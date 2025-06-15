"""Callback functions for AutoMake CLI global options.

This module contains callback functions for global CLI options like --version
and --help.
"""

import typer

from automake import __version__
from automake.cli.display.help import print_help_with_ascii


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"AutoMake version {__version__}")
        raise typer.Exit()


def help_callback(value: bool) -> None:
    """Print help information using our custom formatting and exit."""
    if value:
        print_help_with_ascii()
        raise typer.Exit()


def help_command() -> None:
    """Show help information with ASCII art."""
    print_help_with_ascii()
