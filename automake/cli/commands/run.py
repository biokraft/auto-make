"""Run command implementation for AutoMake CLI.

This module contains the natural language command execution functionality.
Now uses the new agent-first architecture with the ManagerAgent.
"""

import typer
from rich.console import Console

from automake.agent.manager import ManagerAgentRunner
from automake.config import get_config
from automake.logging import (
    get_logger,
    log_command_execution,
    log_config_info,
    setup_logging,
)
from automake.utils.output import MessageType, get_formatter

console = Console()


def run_command(
    command: str = typer.Argument(
        ...,
        help="Natural language command to execute",
        metavar="COMMAND",
    ),
) -> None:
    """Execute natural language commands using the AI agent system.

    This command now uses the new agent-first architecture where a ManagerAgent
    orchestrates specialist agents to accomplish tasks.

    Examples:
        automake run "build the project"
        automake run "run all tests"
        automake run "deploy to staging"
        automake run "list all python files"
        automake run "create a simple hello world script"
    """
    # Handle special cases
    if command.lower() == "help":
        # Import here to avoid circular imports
        from automake.cli.display.help import print_help_with_ascii

        print_help_with_ascii()
        raise typer.Exit()

    # Execute using the new agent architecture
    _execute_agent_command(command)


def _execute_agent_command(command: str) -> None:
    """Execute a command using the new agent architecture."""
    output = get_formatter()
    logger = get_logger()

    # Setup logging
    try:
        config = get_config()
        logger = setup_logging(config)
        log_config_info(logger, config)
        log_command_execution(logger, command, "TBD")
    except Exception:
        # Don't fail the entire command if logging setup fails
        pass

    with output.live_box("Command Received", MessageType.INFO) as command_box:
        command_box.update(f"[cyan]{command}[/cyan]")

    try:
        # Initialize the manager agent
        runner = ManagerAgentRunner(config)

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

        # Execute the command through the manager agent
        with output.live_box("Agent Processing", MessageType.INFO) as processing_box:
            processing_box.update(f"🧠 Processing: [cyan]{command}[/cyan]")

            try:
                # Run the agent
                result = runner.run(command)

                # Display the result
                processing_box.update("✅ Task completed")

            except Exception as e:
                logger.error(f"Agent execution failed: {e}")
                processing_box.update(f"❌ Agent execution failed: {e}")
                raise typer.Exit(1) from e

        # Print the result
        console.print("\n[bold green]Agent Response:[/bold green]")
        console.print(result)

    except typer.Exit:
        # Re-raise typer.Exit without modification
        raise
    except Exception as e:
        with output.live_box("Agent Error", MessageType.ERROR) as error_box:
            error_box.update(f"❌ Failed to execute command: {e}")
        raise typer.Exit(1) from e
