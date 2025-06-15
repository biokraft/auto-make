"""Main CLI application setup for AutoMake.

This module defines the main Typer application and sets up command groups.
Individual command implementations are in the commands/ package.
"""

import typer

from automake import __version__

# Main CLI application
app = typer.Typer(
    name="automake",
    help="AI-powered Makefile command execution",
    add_completion=False,
    no_args_is_help=False,
)

# Command group applications (will be populated during migration)
logs_app = typer.Typer(
    name="logs",
    help="Manage AutoMake logs",
    add_completion=False,
    no_args_is_help=False,
)

config_app = typer.Typer(
    name="config",
    help="Manage AutoMake configuration",
    add_completion=False,
    no_args_is_help=False,
)

# Add command groups to main app
app.add_typer(logs_app, name="logs")
app.add_typer(config_app, name="config")


# Placeholder callbacks (will be moved from main.py during migration)
def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"AutoMake version {__version__}")
        raise typer.Exit()


def help_callback(value: bool) -> None:
    """Print help information using our custom formatting and exit."""
    if value:
        # This will be implemented when display/help.py is created
        typer.echo("Help system will be implemented during migration")
        raise typer.Exit()


# Main callback - handles global options only
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    help_flag: bool | None = typer.Option(
        None,
        "--help",
        "-h",
        callback=help_callback,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """AI-powered Makefile command execution."""
    # If no command is provided, show welcome message
    if ctx.invoked_subcommand is None:
        # This will be implemented when display/help.py is created
        typer.echo("Welcome message will be implemented during migration")


# Command group callbacks
@logs_app.callback(invoke_without_command=True)
def logs_main(ctx: typer.Context) -> None:
    """Manage AutoMake logs."""
    if ctx.invoked_subcommand is None:
        ctx.get_help()
        raise typer.Exit()


@config_app.callback(invoke_without_command=True)
def config_main(ctx: typer.Context) -> None:
    """Manage AutoMake configuration."""
    if ctx.invoked_subcommand is None:
        ctx.get_help()
        raise typer.Exit()


# Individual commands will be added here during migration
# from .commands.run import run_command
# from .commands.init import init_command
# etc.
