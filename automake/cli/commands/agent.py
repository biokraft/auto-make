"""Agent command implementation for AutoMake CLI.

This module contains the agent mode functionality for interactive and non-interactive
agent sessions.
"""

import typer
from rich.console import Console

from automake.agent.manager import ManagerAgentRunner
from automake.agent.ui import RichInteractiveSession
from automake.config import get_config
from automake.logging import (
    get_logger,
    log_command_execution,
    log_config_info,
    setup_logging,
)
from automake.utils.output import MessageType, get_formatter

console = Console()


def agent_command(
    prompt: str = typer.Argument(
        None,
        help="Optional prompt to execute non-interactively",
        metavar="PROMPT",
    ),
) -> None:
    """Launch the AI agent in interactive or non-interactive mode.

    If a prompt is provided, the agent will execute it and exit.
    If no prompt is provided, an interactive chat session will start.

    Examples:
        automake agent "list all python files"
        automake agent
    """
    # Setup logging
    try:
        config = get_config()
        logger = setup_logging(config)
        log_config_info(logger, config)
        if prompt:
            log_command_execution(logger, f"agent: {prompt}", "TBD")
        else:
            log_command_execution(logger, "agent (interactive)", "TBD")
    except Exception:
        # Don't fail the entire command if logging setup fails
        pass

    output = get_formatter()

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

        if prompt:
            # Non-interactive mode
            _run_non_interactive(runner, prompt, output)
        else:
            # Interactive mode
            _run_interactive(runner, output)

    except Exception as e:
        with output.live_box("Agent Error", MessageType.ERROR) as error_box:
            error_box.update(f"❌ Failed to initialize agent: {e}")
        raise typer.Exit(1) from e


def _run_non_interactive(runner: ManagerAgentRunner, prompt: str, output) -> None:
    """Run the agent in non-interactive mode with a single prompt."""
    logger = get_logger()

    with output.live_box("Agent Processing", MessageType.INFO) as processing_box:
        processing_box.update(f"🧠 Processing: [cyan]{prompt}[/cyan]")

        try:
            # Run the agent
            result = runner.run(prompt)

            # Display the result
            processing_box.update("✅ Task completed")

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            processing_box.update(f"❌ Agent execution failed: {e}")
            raise typer.Exit(1) from e

    # Print the result
    console.print("\n[bold green]Agent Response:[/bold green]")
    console.print(result)


def _run_interactive(runner: ManagerAgentRunner, output) -> None:
    """Run the agent in interactive chat mode using RichInteractiveSession."""
    logger = get_logger()

    try:
        # Get configuration
        config = get_config()

        # Create and start the rich interactive session
        session = RichInteractiveSession(
            agent=runner.agent,
            console=console,
            require_confirmation=config.agent_require_confirmation,
        )

        session.start()

    except Exception as e:
        logger.error(f"Interactive session failed: {e}")
        console.print(f"[red]❌ Interactive session failed: {e}[/red]")
        raise typer.Exit(1) from e
