"""Run command implementation for AutoMake CLI.

This module contains the natural language command execution functionality.
"""

import time

import typer

from automake.config_new import get_config
from automake.core.ai_agent import (
    CommandInterpretationError,
    create_ai_agent,
)
from automake.core.command_runner import CommandRunner
from automake.core.interactive import select_command
from automake.core.makefile_reader import (
    MakefileNotFoundError,
    MakefileReader,
)
from automake.logging_new import (
    get_logger,
    log_command_execution,
    log_config_info,
    setup_logging,
)
from automake.utils.output_new import MessageType, get_formatter


def run_command(
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
        # Import here to avoid circular imports
        from automake.cli.display.help import print_help_with_ascii

        print_help_with_ascii()
        raise typer.Exit()

    # Execute the main logic
    _execute_main_logic(command)


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
