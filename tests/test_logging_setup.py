"""Tests for the logging setup module."""

import logging
import os
import time
from datetime import datetime
from pathlib import Path
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
from automake.logging.setup import _generate_log_filename, cleanup_old_log_files


class TestConcurrentSessionSupport:
    """Test cases for concurrent session support features."""

    def test_generate_log_filename_format(self):
        """Test that log filename follows the correct format."""
        with patch("os.getpid", return_value=12345):
            filename = _generate_log_filename()

            # Should match format: automake_YYYY-MM-DD_PID.log
            assert filename.startswith("automake_")
            assert filename.endswith("_12345.log")

            # Extract date part and verify it's today's date
            date_part = filename.split("_")[1]
            expected_date = datetime.now().strftime("%Y-%m-%d")
            assert date_part == expected_date

    def test_generate_log_filename_uniqueness(self):
        """Test that different PIDs generate different filenames."""
        with patch("os.getpid", return_value=11111):
            filename1 = _generate_log_filename()

        with patch("os.getpid", return_value=22222):
            filename2 = _generate_log_filename()

        assert filename1 != filename2
        assert "11111" in filename1
        assert "22222" in filename2

    def test_cleanup_old_log_files_nonexistent_directory(self):
        """Test cleanup when log directory doesn't exist."""
        non_existent_dir = Path("/non/existent/directory")
        # Should not raise an exception
        cleanup_old_log_files(non_existent_dir)

    def test_cleanup_old_log_files_removes_old_files(self, tmp_path):
        """Test that old log files are removed during cleanup."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()

        # Create old log files (older than 7 days)
        old_time = time.time() - (8 * 24 * 60 * 60)  # 8 days ago
        old_log1 = log_dir / "automake_2023-01-01_1111.log"
        old_log2 = log_dir / "automake_2023-01-02_2222.log"

        old_log1.write_text("old log 1")
        old_log2.write_text("old log 2")

        # Set old modification times
        os.utime(old_log1, (old_time, old_time))
        os.utime(old_log2, (old_time, old_time))

        # Create recent log file (within 7 days)
        recent_time = time.time() - (3 * 24 * 60 * 60)  # 3 days ago
        recent_log = log_dir / "automake_2023-12-01_3333.log"
        recent_log.write_text("recent log")
        os.utime(recent_log, (recent_time, recent_time))

        # Create non-automake log file (should be ignored)
        other_log = log_dir / "other.log"
        other_log.write_text("other log")
        os.utime(other_log, (old_time, old_time))

        # Run cleanup
        cleanup_old_log_files(log_dir)

        # Check results
        assert not old_log1.exists()
        assert not old_log2.exists()
        assert recent_log.exists()
        assert other_log.exists()  # Should not be deleted

    def test_cleanup_old_log_files_custom_retention(self, tmp_path):
        """Test cleanup with custom retention period."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()

        # Create log file that's 2 days old
        old_time = time.time() - (2 * 24 * 60 * 60)
        log_file = log_dir / "automake_2023-12-01_1111.log"
        log_file.write_text("test log")
        os.utime(log_file, (old_time, old_time))

        # With 3-day retention, file should remain
        cleanup_old_log_files(log_dir, retention_days=3)
        assert log_file.exists()

        # With 1-day retention, file should be removed
        cleanup_old_log_files(log_dir, retention_days=1)
        assert not log_file.exists()

    def test_cleanup_old_log_files_handles_permission_errors(self, tmp_path):
        """Test that cleanup handles permission errors gracefully."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()

        old_log = log_dir / "automake_2023-01-01_1111.log"
        old_log.write_text("old log")

        # Mock unlink to raise permission error
        with patch.object(Path, "unlink", side_effect=PermissionError("Access denied")):
            # Should not raise an exception
            cleanup_old_log_files(log_dir)

    def test_setup_logging_calls_cleanup(self, tmp_path):
        """Test that setup_logging calls cleanup_old_log_files."""
        config_dir = tmp_path / "config"
        log_dir = tmp_path / "logs"
        config = Config(config_dir=config_dir)

        with patch("automake.logging.setup.cleanup_old_log_files") as mock_cleanup:
            setup_logging(config=config, log_dir=log_dir)
            mock_cleanup.assert_called_once_with(log_dir)

    def test_setup_logging_creates_pid_based_log_file(self, tmp_path):
        """Test that setup_logging creates a PID-based log file."""
        config_dir = tmp_path / "config"
        log_dir = tmp_path / "logs"
        config = Config(config_dir=config_dir)

        with patch("os.getpid", return_value=99999):
            logger = setup_logging(config=config, log_dir=log_dir)

            # Check that the log file was created with PID in name
            expected_date = datetime.now().strftime("%Y-%m-%d")
            expected_filename = f"automake_{expected_date}_99999.log"
            expected_path = log_dir / expected_filename

            assert expected_path.exists()

            # Verify handler is FileHandler, not TimedRotatingFileHandler
            assert len(logger.handlers) == 1
            handler = logger.handlers[0]
            assert isinstance(handler, logging.FileHandler)
            assert not hasattr(handler, "when")  # TimedRotatingFileHandler attribute


class TestSetupLogging:
    """Test cases for the setup_logging function."""

    def test_setup_logging_with_custom_config_and_log_dir(self, tmp_path):
        """Test logging setup with custom config and log directory."""
        # Arrange
        config_dir = tmp_path / "config"
        log_dir = tmp_path / "logs"
        config = Config(config_dir=config_dir)

        # Act
        with patch("os.getpid", return_value=12345):
            logger = setup_logging(config=config, log_dir=log_dir)

        # Assert
        assert isinstance(logger, logging.Logger)
        assert logger.name == "automake"
        assert log_dir.exists()

        # Check PID-based log file exists
        expected_date = datetime.now().strftime("%Y-%m-%d")
        expected_log = log_dir / f"automake_{expected_date}_12345.log"
        assert expected_log.exists()

        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.FileHandler)

    def test_setup_logging_with_default_config_and_log_dir(self):
        """Test logging setup with default config and log directory."""
        with (
            patch("appdirs.user_config_dir") as mock_config_dir,
            patch("appdirs.user_log_dir") as mock_log_dir,
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists") as mock_exists,
            patch("builtins.open", mock_open()),
            patch("tomllib.load") as mock_tomllib_load,
            patch("logging.FileHandler") as mock_handler,
            patch("automake.logging.setup.cleanup_old_log_files"),
            patch("os.getpid", return_value=54321),
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
        with patch("os.getpid", return_value=12345):
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
        with patch("os.getpid", return_value=12345):
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

        with patch("logging.FileHandler") as mock_handler:
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
        with patch("os.getpid", return_value=12345):
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
        with patch("os.getpid", return_value=12345):
            logger = setup_logging(config=config, log_dir=log_dir)

        # Assert
        handler = logger.handlers[0]
        assert isinstance(handler, logging.FileHandler)
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
            patch("logging.FileHandler"),
            patch("automake.logging.setup.cleanup_old_log_files"),
            patch("os.getpid", return_value=12345),
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
        with patch("os.getpid", return_value=99999):
            logger = setup_logging(config=config, log_dir=log_dir)

            # Log various types of messages
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")

            # Force handler to flush
            for handler in logger.handlers:
                handler.flush()

            # Assert - Check log file content with PID-based naming
            expected_date = datetime.now().strftime("%Y-%m-%d")
            log_file = log_dir / f"automake_{expected_date}_99999.log"
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
        with patch("os.getpid", return_value=88888):
            logger = setup_logging(config=config, log_dir=log_dir)

            # Log messages at different levels
            logger.debug("Debug message")  # Should not appear
            logger.info("Info message")  # Should not appear
            logger.warning("Warning message")  # Should appear
            logger.error("Error message")  # Should appear

            # Force handler to flush
            for handler in logger.handlers:
                handler.flush()

            # Assert - Check PID-based log file
            expected_date = datetime.now().strftime("%Y-%m-%d")
            log_file = log_dir / f"automake_{expected_date}_88888.log"
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

        # Act - Use helper functions
        with patch("os.getpid", return_value=77777):
            logger = setup_logging(config=config, log_dir=log_dir)

            log_config_info(logger, config)
            log_command_execution(logger, "build app", "make build")
            log_error(logger, "Test error", ValueError("Test exception"))

            # Force handler to flush
            for handler in logger.handlers:
                handler.flush()

            # Assert - Check PID-based log file
            expected_date = datetime.now().strftime("%Y-%m-%d")
            log_file = log_dir / f"automake_{expected_date}_77777.log"
            log_content = log_file.read_text()

            assert "AutoMake starting up" in log_content
            assert "Configuration loaded from" in log_content
            assert "Interpreting user command: 'build app'" in log_content
            assert "Executing command: 'make build'" in log_content
            assert "Test error: Test exception" in log_content
