"""Main CLI application setup for AutoMake.

This module defines the main Typer application and sets up command groups.
Individual command implementations are in the commands/ package.
"""

import typer

from automake.cli.commands.agent import agent_command
from automake.cli.commands.config import (
    config_edit_command,
    config_reset_command,
    config_set_command,
    config_show_command,
)
from automake.cli.commands.init import init_command
from automake.cli.commands.logs import (
    logs_clear_command,
    logs_config_command,
    logs_show_command,
    logs_view_command,
)
from automake.cli.commands.run import run_command
from automake.cli.display.callbacks import help_callback, help_command, version_callback
from automake.cli.display.help import print_welcome

# Main CLI application
app = typer.Typer(
    name="automake",
    help="AI-powered Makefile command execution",
    add_completion=False,
    no_args_is_help=False,
)

# Command group applications
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


# Main callback - handles global options
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
    """AI-powered command-line assistant.

    AutoMake uses AI agents to interpret and execute natural language commands.
    Use specific subcommands for different features.

    Examples:
        automake agent "install python v3.13"
        automake agent "build the project"
        automake agent "list all python files"
        automake agent  # Interactive mode
        automake run "deploy to staging"
    """
    # If no command is provided, show welcome message
    if ctx.invoked_subcommand is None:
        print_welcome()


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


# Register main commands
app.command("run")(run_command)
app.command("agent")(agent_command)
app.command("init")(init_command)
app.command("help")(help_command)

# Register logs subcommands
logs_app.command("show")(logs_show_command)
logs_app.command("view")(logs_view_command)
logs_app.command("clear")(logs_clear_command)
logs_app.command("config")(logs_config_command)

# Register config subcommands
config_app.command("show")(config_show_command)
config_app.command("set")(config_set_command)
config_app.command("reset")(config_reset_command)
config_app.command("edit")(config_edit_command)
