"""Tests for the logging setup module."""

import logging
import logging.handlers
from unittest.mock import Mock, mock_open, patch

import pytest

from automake.config import Config
from automake.logging import (
    LoggingSetupError,
    get_logger,
    log_command_execution,
    log_config_info,
    log_error,
    setup_logging,
)


class TestSetupLogging:
    """Test cases for the setup_logging function."""

    def test_setup_logging_with_custom_config_and_log_dir(self, tmp_path):
        """Test logging setup with custom config and log directory."""
        # Arrange
        config_dir = tmp_path / "config"
        log_dir = tmp_path / "logs"
        config = Config(config_dir=config_dir)

        # Act
        logger = setup_logging(config=config, log_dir=log_dir)

        # Assert
        assert isinstance(logger, logging.Logger)
        assert logger.name == "automake"
        assert log_dir.exists()
        assert (log_dir / "automake.log").exists()
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.handlers.TimedRotatingFileHandler)

    def test_setup_logging_with_default_config_and_log_dir(self):
        """Test logging setup with default config and log directory."""
        with (
            patch("appdirs.user_config_dir") as mock_config_dir,
            patch("appdirs.user_log_dir") as mock_log_dir,
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists") as mock_exists,
            patch("builtins.open", mock_open()),
            patch("tomllib.load") as mock_tomllib_load,
            patch("logging.handlers.TimedRotatingFileHandler") as mock_handler,
        ):
            mock_config_dir.return_value = "/mock/config"
            mock_log_dir.return_value = "/mock/logs"
            mock_exists.return_value = False
            mock_handler_instance = Mock()
            mock_handler.return_value = mock_handler_instance
            mock_tomllib_load.return_value = {
                "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:0.6b"},
                "logging": {"level": "INFO"},
            }

            # Act
            logger = setup_logging()

            # Assert
            assert isinstance(logger, logging.Logger)
            mock_config_dir.assert_called_once_with("automake")
            mock_log_dir.assert_called_once_with("automake")

    def test_setup_logging_with_debug_level(self, tmp_path):
        """Test logging setup with DEBUG level configuration."""
        # Arrange
        config_dir = tmp_path / "config"
        log_dir = tmp_path / "logs"
        config_dir.mkdir()
        config_file = config_dir / "config.toml"

        debug_config = """[ollama]
base_url = "http://localhost:11434"
model = "qwen3:0.6b"

[logging]
level = "DEBUG"
"""
        config_file.write_text(debug_config)
        config = Config(config_dir=config_dir)

        # Act
        logger = setup_logging(config=config, log_dir=log_dir)

        # Assert
        assert logger.level == logging.DEBUG

    def test_setup_logging_with_invalid_log_level(self, tmp_path):
        """Test logging setup with invalid log level falls back to INFO."""
        # Arrange
        config_dir = tmp_path / "config"
        log_dir = tmp_path / "logs"
        config_dir.mkdir()
        config_file = config_dir / "config.toml"

        invalid_config = """[ollama]
base_url = "http://localhost:11434"
model = "qwen3:0.6b"

[logging]
level = "INVALID_LEVEL"
"""
        config_file.write_text(invalid_config)
        config = Config(config_dir=config_dir)

        # Act
        logger = setup_logging(config=config, log_dir=log_dir)

        # Assert
        assert logger.level == logging.INFO  # Should fall back to INFO

    def test_setup_logging_log_directory_creation_failure(self, tmp_path):
        """Test handling of log directory creation failure."""
        # Arrange
        config_dir = tmp_path / "config"
        config = Config(config_dir=config_dir)

        # Create a file where we want to create the log directory
        blocked_log_path = tmp_path / "blocked_logs"
        blocked_log_path.write_text("blocking file")

        # Act & Assert
        with pytest.raises(LoggingSetupError, match="Failed to create log directory"):
            setup_logging(config=config, log_dir=blocked_log_path)

    def test_setup_logging_file_handler_creation_failure(self, tmp_path):
        """Test handling of file handler creation failure."""
        # Arrange
        config_dir = tmp_path / "config"
        log_dir = tmp_path / "logs"
        config = Config(config_dir=config_dir)

        with patch("logging.handlers.TimedRotatingFileHandler") as mock_handler:
            mock_handler.side_effect = OSError("Permission denied")

            # Act & Assert
            with pytest.raises(
                LoggingSetupError, match="Failed to create log file handler"
            ):
                setup_logging(config=config, log_dir=log_dir)

    def test_setup_logging_clears_existing_handlers(self, tmp_path):
        """Test that setup_logging clears existing handlers."""
        # Arrange
        config_dir = tmp_path / "config"
        log_dir = tmp_path / "logs"
        config = Config(config_dir=config_dir)

        # Add a dummy handler to the logger
        logger = logging.getLogger("automake")
        dummy_handler = logging.StreamHandler()
        logger.addHandler(dummy_handler)
        initial_handler_count = len(logger.handlers)

        # Act
        setup_logging(config=config, log_dir=log_dir)

        # Assert
        assert len(logger.handlers) == 1  # Should only have the new file handler
        assert initial_handler_count > 0  # Verify we had handlers before

    def test_setup_logging_file_handler_configuration(self, tmp_path):
        """Test that file handler is configured correctly."""
        # Arrange
        config_dir = tmp_path / "config"
        log_dir = tmp_path / "logs"
        config = Config(config_dir=config_dir)

        # Act
        logger = setup_logging(config=config, log_dir=log_dir)

        # Assert
        handler = logger.handlers[0]
        assert isinstance(handler, logging.handlers.TimedRotatingFileHandler)
        assert (
            handler.when.upper() == "MIDNIGHT"
        )  # TimedRotatingFileHandler converts to uppercase
        # Note: interval is converted to seconds internally (1 day = 86400 seconds)
        assert handler.interval == 86400  # 1 day in seconds
        assert handler.backupCount == 7
        assert handler.encoding == "utf-8"

        # Check formatter
        formatter = handler.formatter
        assert formatter is not None
        assert "%(asctime)s - %(name)s - %(levelname)s - %(message)s" in formatter._fmt

    def test_setup_logging_fallback_for_older_appdirs(self, tmp_path):
        """Test fallback behavior for older appdirs versions without user_log_dir."""
        with (
            patch("appdirs.user_config_dir") as mock_config_dir,
            patch("appdirs.user_data_dir") as mock_data_dir,
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists", return_value=False),
            patch("builtins.open", mock_open()),
            patch("tomllib.load") as mock_tomllib_load,
            patch("logging.handlers.TimedRotatingFileHandler"),
        ):
            mock_config_dir.return_value = "/mock/config"
            mock_data_dir.return_value = "/mock/data"
            mock_tomllib_load.return_value = {
                "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:0.6b"},
                "logging": {"level": "INFO"},
            }

            # Simulate older appdirs without user_log_dir by patching hasattr in the
            # module
            with patch("automake.logging.setup.hasattr") as mock_hasattr:
                # Make hasattr return False for user_log_dir check
                def hasattr_side_effect(obj, name):
                    if name == "user_log_dir":
                        return False
                    return True  # Return True for other attributes

                mock_hasattr.side_effect = hasattr_side_effect

                # Act
                logger = setup_logging()

                # Assert
                assert isinstance(logger, logging.Logger)
                mock_config_dir.assert_called_once_with("automake")
                mock_data_dir.assert_called_once_with("automake")


class TestGetLogger:
    """Test cases for the get_logger function."""

    def test_get_logger_default_name(self):
        """Test get_logger with default name."""
        # Act
        logger = get_logger()

        # Assert
        assert isinstance(logger, logging.Logger)
        assert logger.name == "automake"

    def test_get_logger_custom_name(self):
        """Test get_logger with custom name."""
        # Act
        logger = get_logger("custom.module")

        # Assert
        assert isinstance(logger, logging.Logger)
        assert logger.name == "custom.module"


class TestLoggingHelpers:
    """Test cases for logging helper functions."""

    def test_log_config_info(self, tmp_path):
        """Test log_config_info function."""
        # Arrange
        config_dir = tmp_path / "config"
        config = Config(config_dir=config_dir)
        logger = Mock()

        # Act
        log_config_info(logger, config)

        # Assert
        assert logger.info.call_count == 5
        logger.info.assert_any_call("AutoMake starting up")
        logger.info.assert_any_call(
            f"Configuration loaded from: {config.config_file_path}"
        )
        logger.info.assert_any_call(f"Ollama base URL: {config.ollama_base_url}")
        logger.info.assert_any_call(f"Ollama model: {config.ollama_model}")
        logger.info.assert_any_call(f"Log level: {config.log_level}")

    def test_log_command_execution(self):
        """Test log_command_execution function."""
        # Arrange
        logger = Mock()
        user_command = "deploy to staging"
        make_command = "make deploy-staging"

        # Act
        log_command_execution(logger, user_command, make_command)

        # Assert
        assert logger.info.call_count == 2
        logger.info.assert_any_call(f"Interpreting user command: '{user_command}'")
        logger.info.assert_any_call(f"Executing command: '{make_command}'")

    def test_log_error_without_exception(self):
        """Test log_error function without exception."""
        # Arrange
        logger = Mock()
        error_msg = "Something went wrong"

        # Act
        log_error(logger, error_msg)

        # Assert
        logger.error.assert_called_once_with(error_msg)

    def test_log_error_with_exception(self):
        """Test log_error function with exception."""
        # Arrange
        logger = Mock()
        error_msg = "Something went wrong"
        exception = ValueError("Test exception")

        # Act
        log_error(logger, error_msg, exception)

        # Assert
        logger.error.assert_called_once_with(f"{error_msg}: {exception}", exc_info=True)


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_full_logging_lifecycle(self, tmp_path):
        """Test complete logging lifecycle: setup, log messages, verify output."""
        # Arrange
        config_dir = tmp_path / "config"
        log_dir = tmp_path / "logs"
        config = Config(config_dir=config_dir)

        # Act - Setup logging
        logger = setup_logging(config=config, log_dir=log_dir)

        # Log various types of messages
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")

        # Force handler to flush
        for handler in logger.handlers:
            handler.flush()

        # Assert - Check log file content
        log_file = log_dir / "automake.log"
        assert log_file.exists()

        log_content = log_file.read_text()
        assert "Test info message" in log_content
        assert "Test warning message" in log_content
        assert "Test error message" in log_content
        assert "automake" in log_content  # Logger name should be in format
        assert "INFO" in log_content
        assert "WARNING" in log_content
        assert "ERROR" in log_content

    def test_logging_with_different_levels(self, tmp_path):
        """Test logging behavior with different log levels."""
        # Arrange - Create config with WARNING level
        config_dir = tmp_path / "config"
        log_dir = tmp_path / "logs"
        config_dir.mkdir()
        config_file = config_dir / "config.toml"

        warning_config = """[ollama]
base_url = "http://localhost:11434"
model = "qwen3:0.6b"

[logging]
level = "WARNING"
"""
        config_file.write_text(warning_config)
        config = Config(config_dir=config_dir)

        # Act
        logger = setup_logging(config=config, log_dir=log_dir)

        # Log messages at different levels
        logger.debug("Debug message")  # Should not appear
        logger.info("Info message")  # Should not appear
        logger.warning("Warning message")  # Should appear
        logger.error("Error message")  # Should appear

        # Force handler to flush
        for handler in logger.handlers:
            handler.flush()

        # Assert
        log_file = log_dir / "automake.log"  # Fixed path - removed extra "logs"
        log_content = log_file.read_text()

        assert "Debug message" not in log_content
        assert "Info message" not in log_content
        assert "Warning message" in log_content
        assert "Error message" in log_content

    def test_logging_helper_functions_integration(self, tmp_path):
        """Test integration of logging helper functions."""
        # Arrange
        config_dir = tmp_path / "config"
        log_dir = tmp_path / "logs"
        config = Config(config_dir=config_dir)
        logger = setup_logging(config=config, log_dir=log_dir)

        # Act - Use helper functions
        log_config_info(logger, config)
        log_command_execution(logger, "build app", "make build")
        log_error(logger, "Test error", ValueError("Test exception"))

        # Force handler to flush
        for handler in logger.handlers:
            handler.flush()

        # Assert
        log_file = log_dir / "automake.log"
        log_content = log_file.read_text()

        assert "AutoMake starting up" in log_content
        assert "Configuration loaded from" in log_content
        assert "Interpreting user command: 'build app'" in log_content
        assert "Executing command: 'make build'" in log_content
        assert "Test error: Test exception" in log_content
