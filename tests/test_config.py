"""Tests for the configuration management module."""

import tomllib
from unittest.mock import mock_open, patch

import pytest

from automake.config import Config, ConfigError, get_config


class TestConfig:
    """Test cases for the Config class."""

    def test_init_with_custom_config_dir(self, tmp_path):
        """Test Config initialization with custom config directory."""
        config_dir = tmp_path / "custom_config"
        config = Config(config_dir=config_dir)

        assert config.config_dir == config_dir
        assert config.config_file == config_dir / "config.toml"
        assert config_dir.exists()
        assert config.config_file.exists()

    def test_init_with_default_config_dir(self):
        """Test Config initialization with default config directory."""
        with patch("appdirs.user_config_dir") as mock_user_config_dir:
            mock_user_config_dir.return_value = "/mock/config/dir"

            with (
                patch("pathlib.Path.mkdir"),
                patch("pathlib.Path.exists") as mock_exists,
                patch("builtins.open", mock_open()),
            ):
                mock_exists.return_value = False  # Config file doesn't exist

                # Mock tomllib.load to return valid config data
                with patch("tomllib.load") as mock_tomllib_load:
                    mock_tomllib_load.return_value = {
                        "ollama": {
                            "base_url": "http://localhost:11434",
                            "model": "llama3",
                        },
                        "logging": {"level": "INFO"},
                    }

                    config = Config()

                    assert str(config.config_dir) == "/mock/config/dir"
                    mock_user_config_dir.assert_called_once_with("automake")

    def test_default_config_creation(self, tmp_path):
        """Test that default config file is created correctly."""
        config_dir = tmp_path / "test_config"
        config = Config(config_dir=config_dir)

        # Check that config file was created
        assert config.config_file.exists()

        # Check content of created config file
        with open(config.config_file, "rb") as f:
            config_data = tomllib.load(f)

        expected_config = {
            "ollama": {"base_url": "http://localhost:11434", "model": "llama3"},
            "logging": {"level": "INFO"},
        }

        assert config_data == expected_config

    def test_load_existing_config(self, tmp_path):
        """Test loading an existing config file."""
        config_dir = tmp_path / "test_config"
        config_dir.mkdir()
        config_file = config_dir / "config.toml"

        # Create a custom config file
        custom_config = """[ollama]
base_url = "http://custom:8080"
model = "custom-model"

[logging]
level = "DEBUG"
"""
        config_file.write_text(custom_config)

        config = Config(config_dir=config_dir)

        assert config.ollama_base_url == "http://custom:8080"
        assert config.ollama_model == "custom-model"
        assert config.log_level == "DEBUG"

    def test_load_partial_config_with_defaults(self, tmp_path):
        """Test loading partial config file with missing keys filled by defaults."""
        config_dir = tmp_path / "test_config"
        config_dir.mkdir()
        config_file = config_dir / "config.toml"

        # Create a partial config file (missing logging section)
        partial_config = """[ollama]
base_url = "http://partial:9000"
"""
        config_file.write_text(partial_config)

        config = Config(config_dir=config_dir)

        # Should have custom ollama settings
        assert config.ollama_base_url == "http://partial:9000"
        # Should have default model since it's missing
        assert config.ollama_model == "llama3"
        # Should have default logging level since section is missing
        assert config.log_level == "INFO"

    def test_invalid_toml_file(self, tmp_path):
        """Test handling of invalid TOML file."""
        config_dir = tmp_path / "test_config"
        config_dir.mkdir()
        config_file = config_dir / "config.toml"

        # Create invalid TOML content
        config_file.write_text("invalid toml content [[[")

        with pytest.raises(ConfigError, match="Failed to load config"):
            Config(config_dir=config_dir)

    def test_config_file_read_permission_error(self, tmp_path):
        """Test handling of file permission errors."""
        config_dir = tmp_path / "test_config"
        config_dir.mkdir()
        config_file = config_dir / "config.toml"
        config_file.write_text("[ollama]\nbase_url = 'test'")

        # Make file unreadable
        config_file.chmod(0o000)

        try:
            with pytest.raises(ConfigError, match="Failed to load config"):
                Config(config_dir=config_dir)
        finally:
            # Restore permissions for cleanup
            config_file.chmod(0o644)

    def test_config_properties(self, tmp_path):
        """Test config property accessors."""
        config_dir = tmp_path / "test_config"
        config = Config(config_dir=config_dir)

        # Test default values
        assert config.ollama_base_url == "http://localhost:11434"
        assert config.ollama_model == "llama3"
        assert config.log_level == "INFO"
        assert config.config_file_path == config.config_file

    def test_get_method(self, tmp_path):
        """Test the get method for accessing config values."""
        config_dir = tmp_path / "test_config"
        config = Config(config_dir=config_dir)

        # Test existing values
        assert config.get("ollama", "base_url") == "http://localhost:11434"
        assert config.get("ollama", "model") == "llama3"
        assert config.get("logging", "level") == "INFO"

        # Test non-existing values with defaults
        assert config.get("nonexistent", "key", "default") == "default"
        assert config.get("ollama", "nonexistent", "default") == "default"

        # Test non-existing values without defaults
        assert config.get("nonexistent", "key") is None

    def test_reload_config(self, tmp_path):
        """Test reloading configuration from file."""
        config_dir = tmp_path / "test_config"
        config = Config(config_dir=config_dir)

        # Initial values
        assert config.ollama_model == "llama3"

        # Modify config file
        new_config = """[ollama]
base_url = "http://localhost:11434"
model = "new-model"

[logging]
level = "INFO"
"""
        config.config_file.write_text(new_config)

        # Reload and check new values
        config.reload()
        assert config.ollama_model == "new-model"

    def test_config_directory_creation_failure(self, tmp_path):
        """Test handling of config directory creation failure."""
        # Create a file where we want to create a directory
        config_path = tmp_path / "blocked_config"
        config_path.write_text("blocking file")

        # The actual error will come from trying to create a directory where a file
        # exists
        # This is a real filesystem error, not a mocked one
        with pytest.raises(OSError):
            Config(config_dir=config_path)

    def test_default_config_content_format(self, tmp_path):
        """Test that the default config file has the expected format and comments."""
        config_dir = tmp_path / "test_config"
        config = Config(config_dir=config_dir)

        content = config.config_file.read_text()

        # Check for expected comments and structure
        assert "# Configuration for AutoMake" in content
        assert "# The base URL for the local Ollama server." in content
        assert "# The model to use for interpreting commands." in content
        assert "# Set log level to" in content
        assert "[ollama]" in content
        assert "[logging]" in content


class TestGetConfig:
    """Test cases for the get_config function."""

    def test_get_config_with_custom_dir(self, tmp_path):
        """Test get_config with custom directory."""
        config_dir = tmp_path / "custom"
        config = get_config(config_dir=config_dir)

        assert isinstance(config, Config)
        assert config.config_dir == config_dir

    def test_get_config_with_default_dir(self):
        """Test get_config with default directory."""
        with patch("appdirs.user_config_dir") as mock_user_config_dir:
            mock_user_config_dir.return_value = "/mock/default"

            with (
                patch("pathlib.Path.mkdir"),
                patch("pathlib.Path.exists", return_value=False),
                patch("builtins.open", mock_open()),
                patch("tomllib.load") as mock_tomllib_load,
            ):
                mock_tomllib_load.return_value = {
                    "ollama": {"base_url": "http://localhost:11434", "model": "llama3"},
                    "logging": {"level": "INFO"},
                }

                config = get_config()

                assert isinstance(config, Config)
                mock_user_config_dir.assert_called_once_with("automake")


class TestConfigIntegration:
    """Integration tests for config functionality."""

    def test_full_config_lifecycle(self, tmp_path):
        """Test complete config lifecycle: create, read, modify, reload."""
        config_dir = tmp_path / "lifecycle_test"

        # 1. Create config with defaults
        config = Config(config_dir=config_dir)
        assert config.ollama_model == "llama3"
        assert config.log_level == "INFO"

        # 2. Verify file was created correctly
        assert config.config_file.exists()
        with open(config.config_file, "rb") as f:
            data = tomllib.load(f)
        assert data["ollama"]["model"] == "llama3"

        # 3. Manually modify the file
        modified_config = """[ollama]
base_url = "http://modified:1234"
model = "modified-model"

[logging]
level = "DEBUG"

[new_section]
new_key = "new_value"
"""
        config.config_file.write_text(modified_config)

        # 4. Reload and verify changes
        config.reload()
        assert config.ollama_base_url == "http://modified:1234"
        assert config.ollama_model == "modified-model"
        assert config.log_level == "DEBUG"
        assert config.get("new_section", "new_key") == "new_value"

        # 5. Create new config instance and verify it loads the modified file
        config2 = Config(config_dir=config_dir)
        assert config2.ollama_model == "modified-model"
        assert config2.log_level == "DEBUG"

    def test_concurrent_config_access(self, tmp_path):
        """Test that multiple Config instances can access the same config file."""
        config_dir = tmp_path / "concurrent_test"

        # Create first config instance
        config1 = Config(config_dir=config_dir)
        assert config1.ollama_model == "llama3"

        # Create second config instance (should read existing file)
        config2 = Config(config_dir=config_dir)
        assert config2.ollama_model == "llama3"

        # Both should have the same values
        assert config1.ollama_base_url == config2.ollama_base_url
        assert config1.log_level == config2.log_level
