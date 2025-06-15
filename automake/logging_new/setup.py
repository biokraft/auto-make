"""Logging setup for AutoMake.

This module configures file-based logging with daily rotation and 7-day retention
according to the logging strategy specification.
"""

import logging
import logging.handlers
from pathlib import Path

import appdirs

from ..config_new import Config


class LoggingSetupError(Exception):
    """Raised when there's an error setting up logging."""

    pass


def setup_logging(
    config: Config | None = None, log_dir: Path | None = None
) -> logging.Logger:
    """Set up file-based logging with rotation.

    Args:
        config: Optional Config instance. If None, creates a new one.
        log_dir: Optional custom log directory path. If None, uses
                platform-specific user log directory.

    Returns:
        Configured logger instance

    Raises:
        LoggingSetupError: If logging setup fails
    """
    if config is None:
        from ..config_new import get_config

        config = get_config()

    if log_dir is None:
        # Use platform-specific log directory
        if hasattr(appdirs, "user_log_dir"):
            log_dir = Path(appdirs.user_log_dir("automake"))
        else:
            # Fallback for older appdirs versions
            log_dir = Path(appdirs.user_data_dir("automake")) / "logs"

    # Ensure log directory exists
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise LoggingSetupError(f"Failed to create log directory {log_dir}: {e}") from e

    # Configure root logger
    logger = logging.getLogger("automake")

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()

    # Set log level from config
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create log file path
    log_file = log_dir / "automake.log"

    try:
        # Create rotating file handler
        # Daily rotation with 7-day retention (backupCount=7)
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=str(log_file),
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8",
        )

        # Set log format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(file_handler)

    except OSError as e:
        raise LoggingSetupError(f"Failed to create log file handler: {e}") from e

    # Prevent propagation to root logger to avoid duplicate console output
    logger.propagate = False

    return logger


def get_logger(name: str = "automake") -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (defaults to "automake")

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_config_info(logger: logging.Logger, config: Config) -> None:
    """Log configuration information at startup.

    Args:
        logger: Logger instance
        config: Configuration instance
    """
    logger.info("AutoMake starting up")
    logger.info(f"Configuration loaded from: {config.config_file_path}")
    logger.info(f"Ollama base URL: {config.ollama_base_url}")
    logger.info(f"Ollama model: {config.ollama_model}")
    logger.info(f"Log level: {config.log_level}")


def log_command_execution(
    logger: logging.Logger, user_command: str, make_command: str
) -> None:
    """Log command interpretation and execution.

    Args:
        logger: Logger instance
        user_command: Original user command
        make_command: Interpreted make command
    """
    logger.info(f"Interpreting user command: '{user_command}'")
    logger.info(f"Executing command: '{make_command}'")


def log_error(
    logger: logging.Logger, error_msg: str, exception: Exception | None = None
) -> None:
    """Log an error with optional exception details.

    Args:
        logger: Logger instance
        error_msg: Error message
        exception: Optional exception instance
    """
    if exception:
        logger.error(f"{error_msg}: {exception}", exc_info=True)
    else:
        logger.error(error_msg)
