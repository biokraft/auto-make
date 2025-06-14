"""Main CLI entry point for AutoMake."""

from pathlib import Path

import typer
from rich.console import Console

from automake import __version__
from automake.makefile_reader import MakefileNotFoundError, MakefileReader
from automake.output import MessageType, get_formatter

app = typer.Typer(
    name="automake",
    help="AI-powered Makefile command execution",
    add_completion=False,
    add_help_option=False,  # Disable default help to use our custom one
)

console = Console()
output = get_formatter(console)


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
    usage_text = "automake [OPTIONS] COMMAND"
    description = (
        "Execute a natural language command using AI to interpret Makefile targets."
    )

    examples = [
        'automake "build the project"',
        'automake "run all tests"',
        'automake "deploy to staging"',
    ]

    # Print usage
    output.print_box(usage_text, MessageType.INFO, "Usage")

    # Print description
    output.print_box(description, MessageType.INFO, "Description")

    # Print examples
    examples_content = "\n".join(examples)
    output.print_box(examples_content, MessageType.INFO, "Examples")

    # Print arguments
    args_content = (
        "*    command      TEXT  Natural language command to execute [required]"
    )
    output.print_box(args_content, MessageType.INFO, "Arguments")

    # Print options
    options_content = (
        "--version  -v        Show version and exit\n"
        "--help     -h        Show this message and exit."
    )
    output.print_box(options_content, MessageType.INFO, "Options")


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


@app.command()
def main(
    command: str | None = typer.Argument(
        None,
        help="Natural language command to execute",
        metavar="COMMAND",
    ),
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
    """Execute a natural language command using AI to interpret Makefile targets.

    Examples:
        automake "build the project"
        automake "run all tests"
        automake "deploy to staging"
    """
    # Handle special cases
    if command is None:
        # No command provided - show welcome with ASCII art
        print_welcome()
        raise typer.Exit()

    if command.lower() == "help":
        # Explicit help command
        print_help_with_ascii()
        raise typer.Exit()

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
