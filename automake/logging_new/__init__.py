"""Logging package for AutoMake.

This package configures file-based logging with daily rotation and 7-day retention
according to the logging strategy specification.
"""

from .setup import (
    LoggingSetupError,
    get_logger,
    log_command_execution,
    log_config_info,
    log_error,
    setup_logging,
)

__all__ = [
    "LoggingSetupError",
    "setup_logging",
    "get_logger",
    "log_config_info",
    "log_command_execution",
    "log_error",
]
