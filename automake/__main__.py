"""Entry point for running automake as a module."""

import sys
import traceback

import click
import typer

from automake.cli.app import app
from automake.cli.error_handler import handle_cli_error
from automake.core.signal_handler import SignalHandler


def main() -> None:
    """Main entry point with intelligent error handling."""
    # Register signal handler early
    signal_handler = SignalHandler.get_instance()
    signal_handler.register_handlers()

    try:
        app()
    except (click.exceptions.UsageError, click.exceptions.ClickException) as e:
        # Handle CLI usage errors with AI assistance
        handle_cli_error(e, sys.argv)
    except typer.Exit:
        # Re-raise typer.Exit to maintain proper exit codes
        raise
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        typer.echo("\n👋 Goodbye!", err=True)
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        # Handle unexpected errors
        typer.echo(f"❌ An unexpected error occurred: {e}", err=True)
        if "--debug" in sys.argv or "-d" in sys.argv:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
