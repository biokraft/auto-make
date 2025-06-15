"""Main CLI entry point for AutoMake."""

import os
import warnings
from pathlib import Path

# Suppress Pydantic serialization warnings early and comprehensively
os.environ.setdefault("PYTHONWARNINGS", "ignore::UserWarning:pydantic.*")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic.*")
warnings.filterwarnings("ignore", message=".*Pydantic serializer warnings.*")
warnings.filterwarnings("ignore", message=".*PydanticSerializationUnexpectedValue.*")

import typer  # noqa: E402
from rich.console import Console  # noqa: E402

from automake import __version__  # noqa: E402
from automake.cli.logs import (  # noqa: E402
    clear_logs,
    show_log_config,
    show_logs_location,
    view_log_content,
)
from automake.config import get_config  # noqa: E402
from automake.core.ai_agent import (  # noqa: E402
    CommandInterpretationError,
    create_ai_agent,
)
from automake.core.command_runner import CommandRunner  # noqa: E402
from automake.core.interactive import select_command  # noqa: E402
from automake.core.makefile_reader import (  # noqa: E402
    MakefileNotFoundError,
    MakefileReader,
)
from automake.utils.ollama_manager import (  # noqa: E402
    OllamaManagerError,
    ensure_model_available,
    get_available_models,
)
from automake.utils.output import MessageType, get_formatter  # noqa: E402

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

# Create a subcommand group for config operations
config_app = typer.Typer(
    name="config",
    help="Manage AutoMake configuration",
    add_completion=False,
    no_args_is_help=True,  # Show help when no subcommand is provided
)
app.add_typer(config_app, name="config")

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


# Config subcommands
@config_app.command("show")
def config_show(
    section: str = typer.Option(
        None,
        "--section",
        "-s",
        help="Show only a specific section",
    ),
) -> None:
    """Show current configuration."""
    try:
        config = get_config()

        if section:
            # Show specific section
            section_data = config.get_all_sections().get(section)
            if section_data is None:
                output.print_error_box(
                    f"Section '{section}' not found in configuration.",
                    hint="Use 'automake config show' to see all available sections.",
                )
                raise typer.Exit(1)

            # Format section data
            content = f"\\[{section}]\n"
            for key, value in section_data.items():
                if isinstance(value, str):
                    content += f'{key} = "{value}"\n'
                else:
                    content += f"{key} = {value}\n"

            output.print_status(
                content.strip(),
                MessageType.INFO,
                f"Configuration - {section}",
            )
        else:
            # Show all configuration
            all_config = config.get_all_sections()
            content = ""

            for section_name, section_data in all_config.items():
                content += f"\\[{section_name}]\n"
                for key, value in section_data.items():
                    if isinstance(value, str):
                        content += f'{key} = "{value}"\n'
                    else:
                        content += f"{key} = {value}\n"
                content += "\n"

            output.print_status(content.strip(), MessageType.INFO, "Configuration")

        # Show config file location
        output.print_status(
            f"Config file: {config.config_file_path}", MessageType.INFO, "Location"
        )

    except Exception as e:
        output.print_error_box(f"Failed to show configuration: {e}")
        raise typer.Exit(1) from e


@config_app.command("set")
def config_set(
    section: str = typer.Argument(
        ..., help="Configuration section (e.g., 'ollama', 'logging')"
    ),
    key: str = typer.Argument(..., help="Configuration key (e.g., 'model', 'level')"),
    value: str = typer.Argument(..., help="Value to set"),
) -> None:
    """Set a configuration value."""
    try:
        config = get_config()

        # Convert value to appropriate type
        converted_value = _convert_config_value(value)

        # Set the value
        config.set(section, key, converted_value)

        # Show updated section
        section_data = config.get_all_sections().get(section, {})
        content = f"\\[{section}]\n"
        for k, v in section_data.items():
            if isinstance(v, str):
                content += f'{k} = "{v}"\n'
            else:
                content += f"{k} = {v}\n"

        output.print_status(
            content.strip(), MessageType.INFO, f"Updated Section - {section}"
        )

    except Exception as e:
        output.print_error_box(f"Failed to set configuration: {e}")
        raise typer.Exit(1) from e


@config_app.command("reset")
def config_reset(
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Reset configuration to defaults."""
    try:
        if not yes:
            import questionary

            confirm = questionary.confirm(
                "Are you sure you want to reset all configuration to defaults? "
                "This cannot be undone."
            ).ask()

            if not confirm:
                output.print_status(
                    "Configuration reset cancelled.", MessageType.INFO, "Cancelled"
                )
                return

        config = get_config()
        config.reset_to_defaults()

        output.print_status(
            "Configuration has been reset to defaults.",
            MessageType.SUCCESS,
            "Reset Complete",
        )

        # Show config file location
        output.print_status(
            f"Config file: {config.config_file_path}",
            MessageType.INFO,
            "Location",
        )

    except Exception as e:
        output.print_error_box(f"Failed to reset configuration: {e}")
        raise typer.Exit(1) from e


@config_app.command("edit")
def config_edit() -> None:
    """Open configuration file in default editor."""
    try:
        config = get_config()
        config_path = config.config_file_path

        # Try to open with system default editor
        import os
        import platform
        import subprocess

        editor = os.environ.get("EDITOR", "vim")

        try:
            subprocess.run([editor, str(config_path)], check=True)
            output.print_status(
                f"Configuration file opened with {editor}.",
                MessageType.SUCCESS,
                "Editor",
            )
            return
        except subprocess.CalledProcessError:
            # Fallback to system default open command
            try:
                if platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", str(config_path)], check=True)
                elif platform.system() == "Windows":  # Windows
                    subprocess.run(["start", str(config_path)], shell=True, check=True)
                else:  # Linux and others
                    subprocess.run(["xdg-open", str(config_path)], check=True)

                output.print_status(
                    "Configuration file opened with system default application.",
                    MessageType.SUCCESS,
                    "Editor",
                )
                return
            except subprocess.CalledProcessError:
                pass

            output.print_error_box(
                f"Could not open configuration file with editor '{editor}' "
                "or system default.",
                hint=f"You can manually edit the file at: {config_path}",
            )
            raise typer.Exit(1) from None

    except Exception as e:
        output.print_error_box(f"Failed to edit configuration: {e}")
        raise typer.Exit(1) from e


def _convert_config_value(value: str) -> str | int | bool:
    """Convert string value to appropriate type for configuration.

    Args:
        value: String value to convert

    Returns:
        Converted value (str, int, or bool)
    """
    # Try to convert to boolean
    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    # Try to convert to integer
    try:
        return int(value)
    except ValueError:
        pass

    # Return as string
    return value


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
    """Print ASCII art with version and author credit and simple usage info."""
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
        "init                 Initialize AutoMake and ensure model is ready\n"
        "config               Manage AutoMake configuration\n"
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

    # Print config subcommands
    config_subcommands_content = (
        "config show          Show current configuration\n"
        "config set           Set a configuration value\n"
        "config reset         Reset configuration to defaults\n"
        "config edit          Open configuration file in editor"
    )
    output.print_box(config_subcommands_content, MessageType.INFO, "Config Commands")

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

    # Execute the main logic
    _execute_main_logic(command)


# Help command
@app.command()
def init() -> None:
    """Initialize AutoMake by ensuring Ollama and the configured model are ready."""
    try:
        # Load configuration
        config = get_config()

        output.print_status(
            f"Initializing AutoMake with model: {config.ollama_model}",
            MessageType.INFO,
            "Initialization",
        )

        # Check if Ollama is installed by trying to run ollama --version
        try:
            import subprocess

            result = subprocess.run(
                ["ollama", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                raise FileNotFoundError("Ollama command failed")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            output.print_error_box(
                "Ollama is not installed or not available in your PATH.",
                hint="Please install Ollama from https://ollama.ai/ and ensure "
                "it's in your PATH.",
            )
            raise typer.Exit(1) from None

        # Ensure model is available
        try:
            is_available, was_pulled = ensure_model_available(config)

            if was_pulled:
                output.print_status(
                    f"Model '{config.ollama_model}' has been pulled and is now ready.",
                    MessageType.SUCCESS,
                    "Model Ready",
                )
            else:
                output.print_status(
                    f"Model '{config.ollama_model}' is already available and ready.",
                    MessageType.SUCCESS,
                    "Model Ready",
                )

            # Show available models
            try:
                available_models = get_available_models(config.ollama_base_url)
                if available_models:
                    models_text = "\n".join(
                        f"• {model}" for model in available_models[:10]
                    )
                    if len(available_models) > 10:
                        models_text += f"\n... and {len(available_models) - 10} more"

                    output.print_status(
                        models_text, MessageType.INFO, "Available Models"
                    )
            except OllamaManagerError:
                # Don't fail if we can't list models, the main goal is achieved
                pass

            output.print_status(
                "AutoMake is ready to use! Try running: "
                'automake run "your command here"',
                MessageType.SUCCESS,
                "Ready",
            )

        except OllamaManagerError as e:
            if "Ollama command not found" in str(e):
                output.print_error_box(
                    "Ollama is not installed or not available in your PATH.",
                    hint="Please install Ollama from https://ollama.ai/ and ensure "
                    "it's in your PATH.",
                )
            elif "Connection" in str(e) or "connect" in str(e).lower():
                output.print_error_box(
                    f"Could not connect to Ollama server at {config.ollama_base_url}.",
                    hint="Make sure Ollama is running. Try: ollama serve",
                )
            elif "pull" in str(e).lower() or "model" in str(e).lower():
                output.print_error_box(
                    f"Failed to pull model '{config.ollama_model}': {e}",
                    hint=f"Check if '{config.ollama_model}' is a valid model name. "
                    f"You can see available models at https://ollama.ai/library",
                )
            else:
                output.print_error_box(
                    f"Initialization failed: {e}",
                    hint="Check your Ollama setup and configuration.",
                )
            raise typer.Exit(1) from e

    except Exception as e:
        output.print_error_box(
            f"An unexpected error occurred during initialization: {e}"
        )
        raise typer.Exit(1) from e


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
        reader = MakefileReader()
        reader.get_makefile_info()  # Validate makefile exists and is readable
        reader.read_makefile()  # Validate makefile content

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

    # Phase 2: AI Core
    try:
        config = get_config()
        agent, ollama_was_started = create_ai_agent(config)

        # Show notice if Ollama was started automatically
        if ollama_was_started:
            output.print_status(
                "Ollama server was not running and has been started automatically.",
                MessageType.INFO,
                "Notice",
            )

        # Start the AI thinking animation
        stop_event, animation_thread = output.start_ai_thinking_animation()

        try:
            response = agent.interpret_command(command, reader.targets)
        finally:
            # Stop the animation regardless of success or failure
            output.stop_ai_thinking_animation(stop_event, animation_thread)

        # Show which command was chosen
        output.print_command_chosen(response.command, response.confidence)

        final_command = response.command
        # Phase 3: Interactive session
        if response.confidence < config.interactive_threshold:
            output.print_status(
                f"Confidence is below threshold ({config.interactive_threshold}%), "
                "starting interactive session.",
                MessageType.WARNING,
                "Interaction",
            )
            command_options = (
                [response.command] if response.command else []
            ) + response.alternatives
            if not command_options:
                output.print_error_box(
                    "AI could not determine a command and provided no alternatives.",
                    hint="Try rephrasing your command or checking your Makefile.",
                )
                raise typer.Exit()

            final_command = select_command(command_options)
            if final_command is None:
                output.print_status("Operation cancelled.", MessageType.INFO, "Abort")
                raise typer.Exit()

        if not final_command:
            output.print_error_box(
                "AI could not determine a command to run.",
                hint="Try rephrasing your command.",
            )
            raise typer.Exit()

        # Phase 2: Execution Engine
        runner = CommandRunner()
        runner.run(final_command)

    except CommandInterpretationError as e:
        output.print_error_box(
            str(e), hint="Check your Ollama setup and configuration."
        )
        raise typer.Exit(1) from e
    except Exception as e:
        output.print_error_box(f"An unexpected error occurred in the AI core: {e}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
