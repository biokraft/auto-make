"""Main CLI entry point for AutoMake."""

import os
import time
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
from automake.logging_setup import (  # noqa: E402
    get_logger,
    log_command_execution,
    log_config_info,
    setup_logging,
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
    no_args_is_help=False,  # We'll handle this manually to avoid empty error box
)
app.add_typer(logs_app, name="logs")


@logs_app.callback(invoke_without_command=True)
def logs_main(ctx: typer.Context) -> None:
    """Manage AutoMake logs."""
    if ctx.invoked_subcommand is None:
        # Show help when no subcommand is provided
        ctx.get_help()
        raise typer.Exit()


# Create a subcommand group for config operations
config_app = typer.Typer(
    name="config",
    help="Manage AutoMake configuration",
    add_completion=False,
    no_args_is_help=False,  # We'll handle this manually to avoid empty error box
)
app.add_typer(config_app, name="config")


@config_app.callback(invoke_without_command=True)
def config_main(ctx: typer.Context) -> None:
    """Manage AutoMake configuration."""
    if ctx.invoked_subcommand is None:
        # Show help when no subcommand is provided
        ctx.get_help()
        raise typer.Exit()


# Help command - removed to avoid conflicts with callback


# Log subcommands
@logs_app.command("show")
def logs_show() -> None:
    """Show log files location and information."""
    console = Console()
    output = get_formatter(console)
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
    console = Console()
    output = get_formatter(console)
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
    console = Console()
    output = get_formatter(console)
    clear_logs(console, output, confirm=yes)


@logs_app.command("config")
def logs_config() -> None:
    """Show logging configuration."""
    console = Console()
    output = get_formatter(console)
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
    output = get_formatter()
    try:
        config = get_config()

        if section:
            # Show specific section
            section_data = config.get_all_sections().get(section)
            if section_data is None:
                with output.live_box(
                    "Configuration Error", MessageType.ERROR
                ) as error_box:
                    error_box.update(
                        f"❌ Section '{section}' not found in configuration.\n\n"
                        "💡 Hint: Use 'automake config show' to see all available "
                        "sections."
                    )
                raise typer.Exit(1)

            # Format section data
            content = f"\\[{section}]\n"
            for key, value in section_data.items():
                if isinstance(value, str):
                    content += f'{key} = "{value}"\n'
                else:
                    content += f"{key} = {value}\n"

            with output.live_box(
                f"Configuration - {section}", MessageType.INFO, transient=False
            ) as config_box:
                config_box.update(content.strip())
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

            with output.live_box(
                "Configuration", MessageType.INFO, transient=False
            ) as config_box:
                config_box.update(content.strip())

        # Show config file location
        with output.live_box(
            "Location", MessageType.INFO, transient=False
        ) as location_box:
            location_box.update(f"Config file: {config.config_file_path}")

    except Exception as e:
        with output.live_box("Configuration Error", MessageType.ERROR) as error_box:
            error_box.update(
                f"❌ Failed to show configuration: {e}\n\n"
                "💡 Hint: Check if the configuration file is accessible and "
                "properly formatted."
            )
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
    output = get_formatter()
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

        with output.live_box(
            f"Updated Section - {section}", MessageType.SUCCESS
        ) as success_box:
            success_box.update(
                f"✅ Configuration updated successfully\n\n{content.strip()}"
            )

    except Exception as e:
        with output.live_box("Configuration Error", MessageType.ERROR) as error_box:
            error_box.update(
                f"❌ Failed to set configuration: {e}\n\n"
                "💡 Hint: Check the section and key names, and ensure the value "
                "format is correct."
            )
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
    output = get_formatter()
    try:
        if not yes:
            import questionary

            confirm = questionary.confirm(
                "Are you sure you want to reset all configuration to defaults? "
                "This cannot be undone."
            ).ask()

            if not confirm:
                with output.live_box("Cancelled", MessageType.INFO) as info_box:
                    info_box.update("🚫 Configuration reset cancelled.")
                return

        config = get_config()
        config.reset_to_defaults()

        with output.live_box("Reset Complete", MessageType.SUCCESS) as success_box:
            success_box.update("🎉 Configuration has been reset to defaults.")

        # Show config file location
        with output.live_box(
            "Location", MessageType.INFO, transient=False
        ) as location_box:
            location_box.update(f"Config file: {config.config_file_path}")

    except Exception as e:
        with output.live_box("Configuration Error", MessageType.ERROR) as error_box:
            error_box.update(
                f"❌ Failed to reset configuration: {e}\n\n"
                "💡 Hint: Check if the configuration file is accessible and writable."
            )
        raise typer.Exit(1) from e


@config_app.command("edit")
def config_edit() -> None:
    """Open configuration file in default editor."""
    output = get_formatter()
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
            with output.live_box("Editor", MessageType.SUCCESS) as success_box:
                success_box.update(f"✅ Configuration file opened with {editor}.")
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

                with output.live_box("Editor", MessageType.SUCCESS) as success_box:
                    success_box.update(
                        "✅ Configuration file opened with system default application."
                    )
                return
            except subprocess.CalledProcessError:
                pass

            with output.live_box("Editor Error", MessageType.ERROR) as error_box:
                error_box.update(
                    f"❌ Could not open configuration file with editor '{editor}' "
                    "or system default.\n\n"
                    f"💡 Hint: You can manually edit the file at: {config_path}"
                )
            raise typer.Exit(1) from None

    except Exception as e:
        with output.live_box("Configuration Error", MessageType.ERROR) as error_box:
            error_box.update(
                f"❌ Failed to edit configuration: {e}\n\n"
                "💡 Hint: Check if the configuration file exists and is accessible."
            )
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
    output = get_formatter()
    try:
        # Load configuration
        config = get_config()

        # Use LiveBox for initialization process
        with output.live_box("AutoMake Initialization", MessageType.INFO) as init_box:
            init_box.update(
                f"🔧 Initializing AutoMake with model: {config.ollama_model}"
            )

            # Check if Ollama is installed by trying to run ollama --version
            try:
                import subprocess

                init_box.update("🔍 Checking Ollama installation...")
                result = subprocess.run(
                    ["ollama", "--version"], capture_output=True, text=True, timeout=10
                )
                if result.returncode != 0:
                    raise FileNotFoundError("Ollama command failed")

                init_box.update("✅ Ollama installation verified")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                init_box.update("❌ Ollama not found")
                # Use LiveBox for error display
                with output.live_box(
                    "Installation Error", MessageType.ERROR
                ) as error_box:
                    error_box.update(
                        "❌ Ollama is not installed or not available in your PATH.\n\n"
                        "💡 Hint: Please install Ollama from https://ollama.ai/ and "
                        "ensure it's in your PATH."
                    )
                raise typer.Exit(1) from None

            # Ensure model is available
            try:
                init_box.update(
                    f"📥 Checking model availability: {config.ollama_model}"
                )
                is_available, was_pulled = ensure_model_available(config)

                if was_pulled:
                    init_box.update(
                        f"✅ Model '{config.ollama_model}' has been pulled and is "
                        "now ready."
                    )
                else:
                    init_box.update(
                        f"✅ Model '{config.ollama_model}' is already available and "
                        "ready."
                    )

                # Show available models
                try:
                    init_box.update("📋 Fetching available models...")
                    available_models = get_available_models(config.ollama_base_url)
                    if available_models:
                        models_text = "Available models:\n" + "\n".join(
                            f"• {model}" for model in available_models[:10]
                        )
                        if len(available_models) > 10:
                            models_text += (
                                f"\n... and {len(available_models) - 10} more"
                            )

                        init_box.update(models_text)
                except OllamaManagerError:
                    # Don't fail if we can't list models, the main goal is achieved
                    init_box.update("⚠️ Could not fetch available models list")
            except OllamaManagerError as e:
                # Use LiveBox for different error types
                if "Ollama command not found" in str(e):
                    with output.live_box(
                        "Installation Error", MessageType.ERROR
                    ) as error_box:
                        error_box.update(
                            "❌ Ollama is not installed or not available in your "
                            "PATH.\n\n"
                            "💡 Hint: Please install Ollama from https://ollama.ai/ "
                            "and ensure it's in your PATH."
                        )
                elif "Connection" in str(e) or "connect" in str(e).lower():
                    with output.live_box(
                        "Connection Error", MessageType.ERROR
                    ) as error_box:
                        error_box.update(
                            f"❌ Could not connect to Ollama server at "
                            f"{config.ollama_base_url}.\n\n"
                            "💡 Hint: Make sure Ollama is running. Try: ollama serve"
                        )
                elif "pull" in str(e).lower() or "model" in str(e).lower():
                    with output.live_box("Model Error", MessageType.ERROR) as error_box:
                        error_box.update(
                            f"❌ Failed to pull model '{config.ollama_model}': {e}\n\n"
                            f"💡 Hint: Check if '{config.ollama_model}' is a valid "
                            f"model name. You can see available models at "
                            f"https://ollama.ai/library"
                        )
                else:
                    with output.live_box(
                        "Initialization Error", MessageType.ERROR
                    ) as error_box:
                        error_box.update(
                            f"❌ Initialization failed: {e}\n\n"
                            "💡 Hint: Check your Ollama setup and configuration."
                        )
                raise typer.Exit(1) from e

                # Final success message with LiveBox
        with output.live_box("Ready", MessageType.SUCCESS) as success_box:
            success_box.update(
                "🎉 AutoMake is ready to use!\n\n"
                'Try running: automake run "your command here"'
            )

    except Exception as e:
        with output.live_box("Unexpected Error", MessageType.ERROR) as error_box:
            error_box.update(
                f"❌ An unexpected error occurred during initialization: {e}"
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
    output = get_formatter()
    # Phase 1: Setup logging
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

    # Phase 4: Makefile Reader Implementation
    try:
        reader = MakefileReader()
        reader.get_makefile_info()  # Validate makefile exists and is readable
        reader.read_makefile()  # Validate makefile content

    except MakefileNotFoundError as e:
        with output.live_box("Makefile Error", MessageType.ERROR) as error_box:
            error_box.update(
                f"❌ {str(e)}\n\n"
                "💡 Hint: Make sure you're in a directory with a Makefile"
            )
        raise typer.Exit(1) from e
    except OSError as e:
        with output.live_box("File System Error", MessageType.ERROR) as error_box:
            error_box.update(f"❌ Error reading Makefile: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        with output.live_box("Unexpected Error", MessageType.ERROR) as error_box:
            error_box.update(f"❌ Unexpected error: {e}")
        raise typer.Exit(1) from e

    # Phase 2: AI Core
    try:
        config = get_config()
        logger = get_logger()
        agent, ollama_was_started = create_ai_agent(config)

        # Show notice if Ollama was started automatically
        if ollama_was_started:
            with output.live_box("Notice", MessageType.INFO) as notice_box:
                notice_box.update(
                    "ℹ️ Ollama server was not running and has been started "
                    "automatically."
                )

        # Use the new AI thinking box for better UX
        with output.ai_thinking_box("AI Command Analysis") as thinking_box:
            # The first message is already animated by ai_thinking_box

            thinking_box.update("🧠 Processing Makefile targets...")

            # Log target descriptions for debugging
            targets_with_desc = reader.targets_with_descriptions
            logger.debug(f"Found {len(targets_with_desc)} targets in Makefile")
            for target, desc in targets_with_desc.items():
                if desc:
                    logger.debug(f"Target '{target}': {desc}")
                else:
                    logger.debug(f"Target '{target}': (no description)")

            time.sleep(0.2)

            thinking_box.update("🔍 Finding best match...")
            response = agent.interpret_command(command, reader)

        # Show AI reasoning with streaming effect
        output.print_ai_reasoning_streaming(response.reasoning, response.confidence)

        # Show which command was chosen with animation
        output.print_command_chosen_animated(response.command, response.confidence)

        final_command = response.command
        # Phase 3: Interactive session
        if response.confidence < config.interactive_threshold:
            with output.live_box("Interaction", MessageType.WARNING) as warning_box:
                warning_box.update(
                    f"⚠️ Confidence is below threshold "
                    f"({config.interactive_threshold}%), starting interactive session."
                )
            command_options = (
                [response.command] if response.command else []
            ) + response.alternatives
            if not command_options:
                with output.live_box(
                    "AI Analysis Error", MessageType.ERROR
                ) as error_box:
                    error_box.update(
                        "❌ AI could not determine a command and provided no "
                        "alternatives.\n\n"
                        "💡 Hint: Try rephrasing your command or checking your "
                        "Makefile."
                    )
                raise typer.Exit()

            final_command = select_command(command_options, output)
            if final_command is None:
                with output.live_box(
                    "Operation Cancelled", MessageType.INFO
                ) as info_box:
                    info_box.update("🚫 Operation cancelled by user.")
                raise typer.Exit()

        if not final_command:
            with output.live_box("AI Analysis Error", MessageType.ERROR) as error_box:
                error_box.update(
                    "❌ AI could not determine a command to run.\n\n"
                    "💡 Hint: Try rephrasing your command."
                )
            raise typer.Exit()

        # Log the final command that will be executed
        logger.info(f"Final command selected: '{final_command}'")

        # Phase 2: Execution Engine with LiveBox
        runner = CommandRunner()
        with output.command_execution_box(final_command) as execution_box:
            runner.run(final_command, live_box=execution_box)

    except CommandInterpretationError as e:
        with output.live_box("AI Interpretation Error", MessageType.ERROR) as error_box:
            error_box.update(
                f"❌ {str(e)}\n\n💡 Hint: Check your Ollama setup and configuration."
            )
        raise typer.Exit(1) from e
    except Exception as e:
        with output.live_box("AI Core Error", MessageType.ERROR) as error_box:
            error_box.update(f"❌ An unexpected error occurred in the AI core: {e}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
