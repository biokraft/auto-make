"""Main CLI entry point for AutoMake."""

from pathlib import Path

import typer
from rich.console import Console

from automake import __version__
from automake.cli.logs import (
    clear_logs,
    show_log_config,
    show_logs_location,
    view_log_content,
)
from automake.core.makefile_reader import MakefileNotFoundError, MakefileReader
from automake.utils.output import MessageType, get_formatter

app = typer.Typer(
    name="automake",
    help="AI-powered Makefile command execution",
    add_completion=False,
    no_args_is_help=False,
)

# Create a subcommand group for log operations
logs_app = typer.Typer(
    name="logs",
    help="Manage AutoMake logs",
    add_completion=False,
    no_args_is_help=True,  # Show help when no subcommand is provided
)
app.add_typer(logs_app, name="logs")

console = Console()
output = get_formatter(console)


# Help command - removed to avoid conflicts with callback


# Log subcommands
@logs_app.command("show")
def logs_show() -> None:
    """Show log files location and information."""
    show_logs_location(console, output)


@logs_app.command("view")
def logs_view(
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
    view_log_content(console, output, lines=lines, follow=follow, log_file=file)


@logs_app.command("clear")
def logs_clear(
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Clear all log files."""
    clear_logs(console, output, confirm=yes)


@logs_app.command("config")
def logs_config() -> None:
    """Show logging configuration."""
    show_log_config(console, output)


def read_ascii_art() -> str:
    """Read ASCII art from file.

    Returns:
        ASCII art content as string, empty if file not found or error.
    """
    try:
        art_file = Path(__file__).parent / "ascii_art.txt"
        if art_file.exists():
            return art_file.read_text(encoding="utf-8")
    except Exception:
        # Silently fail if ASCII art can't be read
        pass
    return ""


def print_welcome() -> None:
    """Print ASCII art and simple usage info."""
    # Print ASCII art first
    ascii_art = read_ascii_art()
    if ascii_art:
        output.print_ascii_art(ascii_art)
        console.print()  # Add blank line after ASCII art

    # Print simple usage info
    usage_info = 'Run "automake help" for detailed usage information.'
    output.print_box(usage_info, MessageType.INFO, "Welcome")


def print_help_with_ascii() -> None:
    """Print ASCII art followed by help information."""
    # Print ASCII art first
    ascii_art = read_ascii_art()
    if ascii_art:
        output.print_ascii_art(ascii_art)
        console.print()  # Add blank line after ASCII art

    # Create help content
    usage_text = "automake [OPTIONS] COMMAND [ARGS]..."
    description = (
        "AI-powered Makefile command execution with natural language processing."
    )

    examples = [
        'automake run "build the project"',
        'automake run "run all tests"',
        'automake run "deploy to staging"',
        'automake run "execute the cicd pipeline"',
    ]

    # Print usage
    output.print_box(usage_text, MessageType.INFO, "Usage")

    # Print description
    output.print_box(description, MessageType.INFO, "Description")

    # Print examples
    examples_content = "\n".join(examples)
    output.print_box(examples_content, MessageType.INFO, "Examples")

    # Print commands
    commands_content = (
        "run                  Execute natural language commands\n"
        "help                 Show this help information\n"
        "logs                 Manage AutoMake logs"
    )
    output.print_box(commands_content, MessageType.INFO, "Commands")

    # Print options
    options_content = (
        "--version  -v        Show version and exit\n"
        "--help     -h        Show this message and exit."
    )
    output.print_box(options_content, MessageType.INFO, "Options")

    # Print log subcommands
    log_subcommands_content = (
        "logs show            Show log files location and information\n"
        "logs view            View log file contents\n"
        "logs clear           Clear all log files\n"
        "logs config          Show logging configuration"
    )
    output.print_box(log_subcommands_content, MessageType.INFO, "Log Commands")


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
        print_welcome()


# Natural language command execution
@app.command()
def run(
    command: str = typer.Argument(
        ...,
        help="Natural language command to execute",
        metavar="COMMAND",
    ),
) -> None:
    """Execute a natural language command using AI to interpret Makefile targets.

    Examples:
        automake run "build the project"
        automake run "run all tests"
        automake run "deploy to staging"
        automake run "execute the cicd pipeline"
    """
    # Handle special cases
    if command.lower() == "help":
        # Explicit help command
        print_help_with_ascii()
        raise typer.Exit()

    # Check if this is a logs-related command
    if "logs" in command.lower():
        # Show log commands help
        log_subcommands_content = (
            "logs show            Show log files location and information\n"
            "logs view            View log file contents\n"
            "logs clear           Clear all log files\n"
            "logs config          Show logging configuration"
        )
        output.print_box(log_subcommands_content, MessageType.INFO, "Log Commands")
        raise typer.Exit()

    # Execute the main logic
    _execute_main_logic(command)


# Help command
@app.command("help")
def help_command() -> None:
    """Show help information with ASCII art."""
    print_help_with_ascii()


# Help command removed - handled in main callback


# The rest of the main command logic needs to be added back to the main function
def _execute_main_logic(command: str) -> None:
    """Execute the main command logic."""
    output.print_command_received(command)

    # Phase 4: Makefile Reader Implementation
    try:
        output.print_status(
            "Reading Makefile from current directory...", MessageType.INFO, "Scanning"
        )
        reader = MakefileReader()
        makefile_info = reader.get_makefile_info()
        makefile_content = reader.read_makefile()

        output.print_makefile_found(makefile_info["name"], makefile_info["size"])

        # Show a preview of the Makefile content (first few lines with targets)
        lines = makefile_content.split("\n")
        target_lines = [
            line
            for line in lines[:20]
            if line.strip()
            and not line.startswith("#")
            and ":" in line
            and not line.startswith("\t")
        ]

        if target_lines:
            target_names = [line.split(":")[0].strip() for line in target_lines[:5]]
            output.print_targets_preview(target_names, len(target_lines))

        # TODO: This will be replaced with actual AI integration in Phase 6
        output.print_status(
            "AI integration not yet implemented (Phase 4 complete)", MessageType.WARNING
        )
        output.print_status(
            "Makefile reading functionality is now working!", MessageType.HINT
        )
        output.print_status(
            "Next: Phase 5 (Ollama Integration) and Phase 6 (Smolagent Core)",
            MessageType.HINT,
        )

    except MakefileNotFoundError as e:
        output.print_error_box(
            str(e), hint="Make sure you're in a directory with a Makefile"
        )
        raise typer.Exit(1) from e
    except OSError as e:
        output.print_error_box(f"Error reading Makefile: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        output.print_error_box(f"Unexpected error: {e}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
