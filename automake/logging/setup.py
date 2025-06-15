"""Logging setup for AutoMake.

This module configures file-based logging with PID-based unique filenames
and startup-based cleanup for concurrent session support.
"""

import logging
import os
import time
from datetime import datetime
from pathlib import Path

import appdirs

from ..config import Config


class LoggingSetupError(Exception):
    """Raised when there's an error setting up logging."""

    pass


def cleanup_old_log_files(log_dir: Path, retention_days: int = 7) -> None:
    """Clean up log files older than the retention period.

    This function is called on startup to remove old log files from previous
    sessions, supporting concurrent execution by cleaning up based on file
    modification time.

    Args:
        log_dir: Directory containing log files
        retention_days: Number of days to retain log files (default: 7)
    """
    if not log_dir.exists():
        return

    cutoff_time = time.time() - (retention_days * 24 * 60 * 60)

    # Find all automake log files
    log_pattern = "automake_*.log"
    for log_file in log_dir.glob(log_pattern):
        try:
            # Use modification time for cross-platform compatibility
            file_time = log_file.stat().st_mtime
            if file_time < cutoff_time:
                log_file.unlink()
        except OSError:
            # Ignore errors when deleting files (e.g., permission issues)
            pass


def _generate_log_filename() -> str:
    """Generate a unique log filename with PID and date.

    Returns:
        Log filename in format: automake_YYYY-MM-DD_PID.log
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    pid = os.getpid()
    return f"automake_{current_date}_{pid}.log"


def setup_logging(
    config: Config | None = None, log_dir: Path | None = None
) -> logging.Logger:
    """Set up file-based logging with PID-based unique filenames.

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
        from ..config import get_config

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

    # Clean up old log files before setting up new logging
    cleanup_old_log_files(log_dir)

    # Configure root logger
    logger = logging.getLogger("automake")

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()

    # Set log level from config
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create unique log file path with PID
    log_filename = _generate_log_filename()
    log_file = log_dir / log_filename

    try:
        # Create standard file handler (no rotation needed with unique filenames)
        file_handler = logging.FileHandler(
            filename=str(log_file),
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
