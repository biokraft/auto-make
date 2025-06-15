"""Help and ASCII art display functionality for AutoMake CLI.

This module contains functions for displaying help information and ASCII art.
"""

from pathlib import Path

from rich.console import Console

from automake import __version__
from automake.utils.output import MessageType, get_formatter


def read_ascii_art() -> str:
    """Read ASCII art from file.

    Returns:
        ASCII art content as string, empty if file not found or error.
    """
    try:
        # Look for ASCII art in the resources directory first
        resources_art = (
            Path(__file__).parent.parent.parent / "resources" / "ascii_art.txt"
        )
        if resources_art.exists():
            return resources_art.read_text(encoding="utf-8")

        # Fallback to the old location in cli directory
        cli_art = Path(__file__).parent.parent / "ascii_art.txt"
        if cli_art.exists():
            return cli_art.read_text(encoding="utf-8")
    except Exception:
        # Silently fail if ASCII art can't be read
        pass
    return ""


def print_welcome() -> None:
    """Print ASCII art with version and author credit and simple usage info."""
    console = Console()
    output = get_formatter(console)
    # Print ASCII art with version and author credit
    ascii_art = read_ascii_art()
    if ascii_art:
        # Combine ASCII art with version and author credit for unified rainbow animation
        combined_art = ascii_art + f"\nversion {__version__}\n- by Seán Baufeld"
        output.print_rainbow_ascii_art(combined_art, duration=1.5)
        console.print()  # Add blank line after ASCII art
        console.print()  # Add extra blank line for better spacing

    # Print simple usage info
    usage_info = 'Run "automake help" for detailed usage information.'
    output.print_box(usage_info, MessageType.INFO, "Welcome")


def print_help_with_ascii(show_author: bool = False) -> None:
    """Print ASCII art followed by help information.

    Args:
        show_author: Whether to include the author credit in the ASCII art
    """
    console = Console()
    output = get_formatter(console)
    # Print ASCII art
    ascii_art = read_ascii_art()
    if ascii_art:
        if show_author:
            # Combine ASCII art with author credit for unified rainbow animation
            combined_art = ascii_art + "\n- by Seán Baufeld"
            output.print_rainbow_ascii_art(combined_art, duration=0)
        else:
            output.print_rainbow_ascii_art(ascii_art, duration=0)
        console.print()  # Add blank line after ASCII art

    # Create help content
    usage_text = 'automake "PROMPT" | automake [COMMAND] [ARGS]...'
    description = (
        "AI-powered command-line assistant that interprets natural language commands.\n"
        'The primary interface is direct prompts: automake "your command here"'
    )

    examples = [
        'automake "build the project"',
        'automake "list all python files"',
        'automake "run all tests"',
        'automake "what is the ip address of google dns?"',
    ]

    # Print usage
    output.print_box(usage_text, MessageType.INFO, "Usage")

    # Print description
    output.print_box(description, MessageType.INFO, "Description")

    # Print examples
    examples_content = "\n".join(examples)
    output.print_box(examples_content, MessageType.INFO, "Primary Examples")

    # Print commands
    commands_content = (
        "agent                Launch the AI agent\n"
        "run                  Execute natural language commands (legacy)\n"
        "init                 Initialize AutoMake and ensure model is ready\n"
        "config               Manage AutoMake configuration\n"
        "help                 Show this help information\n"
        "logs                 Manage AutoMake logs"
    )
    output.print_box(commands_content, MessageType.INFO, "Commands")

    # Print agent examples
    agent_examples_content = (
        'automake agent "create a new python file"  # Single command\n'
        "automake agent                             # Interactive chat mode"
    )
    output.print_box(agent_examples_content, MessageType.INFO, "Agent Examples")

    # Print options
    options_content = (
        "--version  -v        Show version and exit\n"
        "--help     -h        Show this message and exit."
    )
    output.print_box(options_content, MessageType.INFO, "Options")

    # Print config subcommands
    config_subcommands_content = (
        "config show          Show current configuration\n"
        "config set           Set a configuration value\n"
        "config reset         Reset configuration to defaults\n"
        "config edit          Open configuration file in editor"
    )
    output.print_box(config_subcommands_content, MessageType.INFO, "Config Commands")

    # Print config examples
    config_examples_content = (
        'automake config set ollama.model "qwen3:8b"\n'
        'automake config set ollama.base_url "http://localhost:11434"\n'
        'automake config set logging.level "DEBUG"\n'
        "automake config set ai.interactive_threshold 90\n"
        "\n"
        "💡 After changing the model, run 'automake init' to initialize it"
    )
    output.print_box(config_examples_content, MessageType.INFO, "Config Examples")

    # Print log subcommands
    log_subcommands_content = (
        "logs show            Show log files location and information\n"
        "logs view            View log file contents\n"
        "logs clear           Clear all log files\n"
        "logs config          Show logging configuration"
    )
    output.print_box(log_subcommands_content, MessageType.INFO, "Log Commands")
