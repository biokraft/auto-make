"""Interactive command selection for AutoMake.

This module provides functionality for the user to select a command from a list
when the AI's confidence is low.
"""

import logging

import questionary
from questionary import Choice

logger = logging.getLogger(__name__)


def select_command(commands: list[str]) -> str | None:
    """Present an interactive list of commands for the user to select.

    Args:
        commands: A list of command strings to choose from.

    Returns:
        The selected command string, or None if the user aborts.
    """
    if not commands:
        return None

    logger.debug("Starting interactive command selection with options: %s", commands)

    choices = [Choice(title=cmd, value=cmd) for cmd in commands]
    choices.append(Choice(title="[Abort]", value="abort"))

    try:
        selected_command = questionary.select(
            "I'm not completely sure which command you meant. Please select one:",
            choices=choices,
            use_indicator=True,
        ).ask()

        if selected_command == "abort" or selected_command is None:
            logger.info("User aborted interactive command selection.")
            return None

        logger.info("User selected command: %s", selected_command)
        return selected_command

    except (KeyboardInterrupt, EOFError):
        logger.warning("Interactive selection cancelled by user.")
        return None
    except Exception as e:
        logger.error(
            "An error occurred during interactive selection: %s", e, exc_info=True
        )
        # Fallback to returning None to prevent crashing
        return None
