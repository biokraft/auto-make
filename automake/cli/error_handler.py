"""Intelligent CLI error handling for AutoMake.

This module implements Phase 6 error handling by capturing CLI errors,
using the Manager Agent to suggest corrections, and presenting them to
the user for confirmation.
"""

import sys

from rich.console import Console
from rich.prompt import Confirm

from automake.agent.manager import ManagerAgentRunner
from automake.config import get_config
from automake.logging import get_logger, setup_logging
from automake.utils.output import MessageType, get_formatter

console = Console()


def handle_cli_error(error: Exception, argv: list[str]) -> None:
    """Handle CLI errors with AI assistance.

    Args:
        error: The caught CLI error
        argv: The original command line arguments
    """
    output = get_formatter()
    logger = get_logger()  # Get logger first

    # Setup logging
    try:
        config = get_config()
        logger = setup_logging(config)
    except Exception:
        # Don't fail if logging setup fails, use the default logger
        pass

    # Extract error information
    error_message = str(error)
    original_command = " ".join(argv)

    logger.info(f"CLI error occurred: {error_message}")
    logger.info(f"Original command: {original_command}")

    # Display the error
    with output.live_box("Command Error", MessageType.ERROR) as error_box:
        error_box.update(
            f"❌ Command failed: {error_message}\n\n💡 Let me suggest a correction..."
        )

    try:
        # Initialize the manager agent for error correction
        config = get_config()
        runner = ManagerAgentRunner(config)

        with output.live_box("AI Analysis", MessageType.INFO) as analysis_box:
            analysis_box.update("🤖 Analyzing error and generating suggestion...")
            runner.initialize()

        # Create prompt for the agent to suggest a correction
        correction_prompt = _create_error_correction_prompt(
            error_message, original_command
        )

        # Get suggestion from the agent
        with output.live_box(
            "Generating Suggestion", MessageType.INFO
        ) as suggestion_box:
            suggestion_box.update("🧠 AI is analyzing the error...")

            try:
                suggestion = runner.run(correction_prompt)
                suggestion_box.update("✅ Suggestion generated")
            except Exception as e:
                logger.error(f"Agent failed to generate suggestion: {e}")
                suggestion_box.update(f"❌ Failed to generate suggestion: {e}")
                _show_fallback_help(error_message, original_command)
                return

        # Present the suggestion to the user
        _present_suggestion(suggestion, original_command, output)

    except Exception as e:
        logger.error(f"Error handling failed: {e}")
        with output.live_box(
            "Error Handler Failed", MessageType.ERROR
        ) as handler_error_box:
            handler_error_box.update(
                f"❌ Unable to generate suggestion: {e}\n\n"
                f"💡 Try running 'automake help' for available commands."
            )
        sys.exit(1)


def _create_error_correction_prompt(error_message: str, original_command: str) -> str:
    """Create a prompt for the agent to suggest error corrections.

    Args:
        error_message: The error message from the CLI
        original_command: The original command that failed

    Returns:
        A formatted prompt for the agent
    """
    return f"""The user tried to run this command but it failed:

Command: {original_command}
Error: {error_message}

Please analyze this error and suggest a corrected command. Your response should:
1. Briefly explain what went wrong
2. Provide the exact corrected command the user should run
3. Be concise and helpful

Focus on common AutoMake usage patterns like:
- 'automake "natural language prompt"' for direct prompts
- 'automake agent' for interactive mode
- 'automake run "command"' for legacy mode
- 'automake help' for help
- 'automake config show' for configuration
- 'automake init' for initialization

If the user seems to be trying to use a natural language prompt, suggest the correct
syntax. If they're using invalid flags or commands, suggest the correct alternatives.
"""


def _present_suggestion(suggestion: str, original_command: str, output) -> None:
    """Present the AI suggestion to the user and handle confirmation.

    Args:
        suggestion: The AI-generated suggestion
        original_command: The original failed command
        output: Output formatter
    """
    # Display the suggestion
    console.print("\n[bold green]💡 AI Suggestion:[/bold green]")
    console.print(suggestion)

    # Try to extract a command from the suggestion
    corrected_command = _extract_command_from_suggestion(suggestion)

    if corrected_command and corrected_command != original_command:
        console.print(
            f"\n[bold cyan]Suggested command:[/bold cyan] {corrected_command}"
        )

        # Ask for confirmation
        if Confirm.ask(
            "\n[bold yellow]Would you like to run the suggested command?[/bold yellow]"
        ):
            logger = get_logger()
            logger.info(f"User confirmed suggested command: {corrected_command}")

            # Execute the corrected command
            try:
                _execute_corrected_command(corrected_command, output)
            except Exception as e:
                logger.error(f"Failed to execute corrected command: {e}")
                console.print(f"[red]❌ Failed to execute suggested command: {e}[/red]")
                sys.exit(1)
        else:
            logger = get_logger()
            logger.info("User declined suggested command")
            console.print(
                "[yellow]👍 No problem! You can try other commands or run "
                "'automake help' for assistance.[/yellow]"
            )
    else:
        console.print("\n[yellow]💡 Please try the suggested approach above.[/yellow]")


def _extract_command_from_suggestion(suggestion: str) -> str | None:
    """Extract a command from the AI suggestion.

    Args:
        suggestion: The AI-generated suggestion text

    Returns:
        Extracted command or None if no clear command found
    """
    import re

    lines = suggestion.split("\n")

    # Look for lines that contain 'automake'
    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Look for lines with automake commands
        if "automake" in line.lower():
            # Try to extract from backticks first - handle multiple backticks
            if "`" in line:
                matches = re.findall(r"`([^`]*automake[^`]*)`", line)
                if matches:
                    return matches[0].strip()
            elif line.startswith("automake"):
                return line.strip()
            elif ": " in line and "automake" in line.lower():
                # Format like "Corrected command: automake ..." or
                # "Try using: automake ..."
                return line.split(": ", 1)[1].strip()
            elif line.startswith(("Try using:", "Try:", "Use:")):
                # Handle "Try using: automake ..." format
                if ":" in line:
                    cmd_part = line.split(":", 1)[1].strip()
                    if cmd_part.startswith("`") and cmd_part.endswith("`"):
                        cmd_part = cmd_part[1:-1]  # Remove backticks
                    return cmd_part

    return None


def _execute_corrected_command(command: str, output) -> None:
    """Execute the corrected command.

    Args:
        command: The corrected command to execute
        output: Output formatter
    """
    # Parse the command to extract the automake arguments
    parts = command.split()
    if not parts or parts[0] != "automake":
        raise ValueError(f"Invalid command format: {command}")

    # Remove 'automake' from the beginning
    args = parts[1:]

    with output.live_box("Executing Suggestion", MessageType.INFO) as exec_box:
        exec_box.update(f"🚀 Running: {command}")

    # Import here to avoid circular imports
    from automake.cli.app import app

    # Execute the command by calling the app with the parsed arguments
    try:
        # Use typer's testing approach to execute the command
        import typer.testing

        runner = typer.testing.CliRunner()
        result = runner.invoke(app, args, catch_exceptions=False)

        if result.exit_code != 0:
            raise RuntimeError(
                f"Command failed with exit code {result.exit_code}: {result.output}"
            )

    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to execute corrected command: {e}")
        raise


def _show_fallback_help(error_message: str, original_command: str) -> None:
    """Show fallback help when AI suggestion fails.

    Args:
        error_message: The original error message
        original_command: The original command that failed
    """
    console.print(
        "\n[bold yellow]💡 Here are some common AutoMake commands:[/bold yellow]"
    )
    console.print(
        '  [cyan]automake "build the project"[/cyan]     - Use natural language'
    )
    console.print("  [cyan]automake agent[/cyan]                    - Interactive mode")
    console.print("  [cyan]automake help[/cyan]                     - Show help")
    console.print(
        "  [cyan]automake init[/cyan]                     - Initialize AutoMake"
    )
    console.print(
        "  [cyan]automake config show[/cyan]              - Show configuration"
    )

    if (
        "unrecognized arguments" in error_message.lower()
        or "no such option" in error_message.lower()
    ):
        console.print(
            "\n[yellow]💡 It looks like you used an invalid option or "
            "argument.[/yellow]"
        )
        console.print(
            "[yellow]   Try using natural language in quotes instead![/yellow]"
        )
