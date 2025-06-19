"""Agent command implementation for AutoMake CLI.

This module contains the agent mode functionality for interactive and non-interactive
agent sessions.
"""

import json

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

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

    The agent may request confirmation before executing actions (like file operations
    or system commands). This behavior can be configured using:
        automake config set agent.require_confirmation true/false

    Examples:
        automake agent "list all python files"
        automake agent
        automake config set agent.require_confirmation false
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


def _is_action(item) -> bool:
    """Check if an item represents an action that needs confirmation.

    Args:
        item: The item to check

    Returns:
        True if the item is an action, False otherwise
    """
    return (
        isinstance(item, dict)
        and "tool_name" in item
        and item.get("tool_name") is not None
    )


def _get_non_interactive_confirmation(action: dict) -> bool:
    """Display confirmation UI for non-interactive mode and get user approval.

    Args:
        action: Dictionary containing action details to confirm

    Returns:
        True if user confirms, False if user cancels
    """
    # Create a detailed action display
    tool_name = action.get("tool_name", "Unknown")
    arguments = action.get("arguments", {})

    # Create main content
    content_lines = []
    content_lines.append(
        f"[bold cyan]🔧 Tool:[/bold cyan] [yellow]{tool_name}[/yellow]"
    )

    if arguments:
        content_lines.append("\n[bold cyan]📋 Arguments:[/bold cyan]")

        # Format arguments nicely
        if isinstance(arguments, dict):
            for key, value in arguments.items():
                # Handle different value types
                if isinstance(value, str) and len(value) > 50:
                    # Truncate long strings
                    display_value = f"{value[:47]}..."
                elif isinstance(value, list | dict):
                    # Format complex structures
                    display_value = json.dumps(value, indent=2)[:100]
                    if len(json.dumps(value)) > 100:
                        display_value += "..."
                else:
                    display_value = str(value)

                content_lines.append(
                    f"  • [green]{key}:[/green] [white]{display_value}[/white]"
                )
        else:
            content_lines.append(f"  [white]{arguments}[/white]")

    # Create the confirmation panel
    content = "\n".join(content_lines)
    panel = Panel(
        content,
        title="[bold red]⚠️  Action Confirmation Required[/bold red]",
        title_align="center",
        border_style="yellow",
        padding=(1, 2),
    )

    console.print("\n")
    console.print(panel)

    # Get confirmation with enhanced prompt
    confirm = Prompt.ask(
        "\n[bold yellow]❓ Do you want to proceed with this action?[/bold yellow]",
        choices=["y", "n", "yes", "no"],
        default="y",
    )

    return confirm.lower() in ["y", "yes"]


def _process_result_with_confirmation(result):
    """Process agent result and handle confirmation for actions.

    Args:
        result: The result from the agent (can be string, list, or dict)

    Returns:
        The processed result

    Raises:
        typer.Exit: If user cancels an action
    """
    # Handle different result types
    if isinstance(result, str):
        # Simple string response, no confirmation needed
        return result
    elif isinstance(result, list):
        # List of items, check each for actions
        processed_items = []
        for item in result:
            if _is_action(item):
                if not _get_non_interactive_confirmation(item):
                    console.print("\n[red]❌ Action cancelled by user[/red]")
                    raise typer.Exit(1)
                processed_items.append(
                    f"✅ Executed: {item.get('tool_name', 'Unknown')}"
                )
            else:
                processed_items.append(str(item))
        return "\n".join(processed_items)
    elif _is_action(result):
        # Single action
        if not _get_non_interactive_confirmation(result):
            console.print("\n[red]❌ Action cancelled by user[/red]")
            raise typer.Exit(1)
        return f"✅ Executed: {result.get('tool_name', 'Unknown')}"
    else:
        # Other types, convert to string
        return str(result)


def _run_non_interactive(runner: ManagerAgentRunner, prompt: str, output) -> None:
    """Run the agent in non-interactive mode with a single prompt."""
    logger = get_logger()
    config = get_config()

    with output.live_box("Agent Processing", MessageType.INFO) as processing_box:
        processing_box.update(f"🧠 Processing: [cyan]{prompt}[/cyan]")

        try:
            # Run the agent
            result = runner.run(prompt)

            # Handle confirmation if enabled
            if config.agent_require_confirmation:
                result = _process_result_with_confirmation(result)

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
