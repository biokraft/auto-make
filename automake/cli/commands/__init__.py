"""Command implementations for AutoMake CLI.

This package contains individual command modules that implement the CLI functionality.
Each module focuses on a specific command or group of related commands.
"""

from .config import (
    config_edit_command,
    config_reset_command,
    config_set_command,
    config_show_command,
)
from .init import init_command
from .logs import (
    logs_clear_command,
    logs_config_command,
    logs_show_command,
    logs_view_command,
)
from .run import run_command

__all__ = [
    # Main commands
    "run_command",
    "init_command",
    # Config commands
    "config_show_command",
    "config_set_command",
    "config_reset_command",
    "config_edit_command",
    # Logs commands
    "logs_show_command",
    "logs_view_command",
    "logs_clear_command",
    "logs_config_command",
]
