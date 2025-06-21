"""Main CLI application setup for AutoMake.

This module defines the main Typer application and sets up command groups.
Individual command implementations are in the commands/ package.
"""

import click
import typer
from typer.core import TyperGroup

from automake.agent.manager import ManagerAgentRunner
from automake.cli.commands.agent import _run_non_interactive, agent_command
from automake.cli.commands.config import (
    config_edit_command,
    config_model_command,
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
from automake.config import get_config
from automake.core.signal_handler import SignalHandler
from automake.logging import (
    log_command_execution,
    log_config_info,
    setup_logging,
)
from automake.utils.output import MessageType, get_formatter


class CustomGroup(TyperGroup):
    """Custom Typer group that handles unrecognized commands as prompts."""

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        """Override get_command to handle unrecognized commands."""
        command = super().get_command(ctx, cmd_name)
        if command is None:
            # Create a dummy command that will execute the prompt
            def prompt_command():
                # Get all remaining arguments
                if cmd_name in ctx.args:
                    remaining_args = ctx.args[ctx.args.index(cmd_name) :]
                else:
                    remaining_args = [cmd_name]
                prompt = " ".join(remaining_args)
                _execute_primary_interface(prompt)

            # Create a click command for this
            return click.Command(
                name=cmd_name,
                callback=prompt_command,
                params=[],
            )
        return command


# Main CLI application
app = typer.Typer(
    name="automake",
    help="AI-powered Makefile command execution",
    add_completion=False,
    no_args_is_help=False,
    invoke_without_command=True,
    cls=CustomGroup,
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
@app.callback()
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
    The primary way to use AutoMake is with direct prompts.

    Examples:
        automake "build the project"
        automake "list all python files"
        automake "what is the ip address of google dns?"
        automake agent  # Interactive mode
        automake run "deploy to staging"  # Legacy command

    Signal Handling:
        Ctrl+C (SIGINT): Graceful shutdown with cleanup
        Ctrl+D (EOF): Exit interactive sessions normally
    """
    # Register signal handler early
    signal_handler = SignalHandler.get_instance()
    signal_handler.register_signal_handlers("CLI main")

    # If no subcommand is invoked, show welcome message
    if ctx.invoked_subcommand is None:
        print_welcome()


def _execute_primary_interface(prompt: str) -> None:
    """Execute the primary interface with a prompt."""
    # Setup logging
    try:
        config = get_config()
        logger = setup_logging(config)
        log_config_info(logger, config)
        log_command_execution(logger, f"main: {prompt}", "TBD")
    except Exception:
        # Don't fail the entire command if logging setup fails
        pass

    output = get_formatter()

    try:
        # Initialize the manager agent
        runner = ManagerAgentRunner(config)

        # Register cleanup with signal handler
        signal_handler = SignalHandler.get_instance()
        signal_handler.register_cleanup(runner.shutdown, "Manager agent runner cleanup")

        with output.live_box("Agent Initialization", MessageType.INFO) as init_box:
            init_box.update("🤖 Initializing AI agent system...")
            ollama_was_started = runner.initialize()

            if ollama_was_started:
                init_box.update(
                    "🤖 AI agent system initialized\n"
                    "✅ Ollama server started automatically"
                )
            else:
                init_box.update("🤖 AI agent system initialized")

        # Run in non-interactive mode
        _run_non_interactive(runner, prompt, output)

    except Exception as e:
        with output.live_box("Agent Error", MessageType.ERROR) as error_box:
            error_box.update(f"❌ Failed to initialize agent: {e}")
        raise typer.Exit(1) from e


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
config_app.command("model")(config_model_command)
