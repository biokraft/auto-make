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
                            "model": "qwen3:0.6b",
                        },
                        "logging": {"level": "INFO"},
                    }

                    config = Config()

                    assert str(config.config_dir) == "/mock/config/dir"
                    mock_user_config_dir.assert_called_once_with("automake")

    def test_default_config_creation(self, tmp_path):
        """Test that default config is created correctly."""
        config_dir = tmp_path / "config"
        config = Config(config_dir)

        # Check that config file was created
        assert config.config_file_path.exists()

        # Check default values
        expected_config = {
            "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:0.6b"},
            "logging": {"level": "INFO"},
            "ai": {"interactive_threshold": 80},
            "agent": {"require_confirmation": False},
        }

        # Read the config file directly to verify content
        with open(config.config_file_path, "rb") as f:
            config_data = tomllib.load(f)

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
        """Test loading partial config with default fallbacks."""
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True)

        # Create partial config (missing some values)
        partial_config = """[ollama]
base_url = "http://custom:8080"
"""
        config_file = config_dir / "config.toml"
        config_file.write_text(partial_config)

        config = Config(config_dir)

        # Should have custom value
        assert config.ollama_base_url == "http://custom:8080"
        # Should have default values for missing keys
        assert config.ollama_model == "qwen3:0.6b"
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
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True)

        config_content = """[ollama]
base_url = "http://test:9999"
model = "test-model"

[logging]
level = "DEBUG"
"""
        config_file = config_dir / "config.toml"
        config_file.write_text(config_content)

        config = Config(config_dir)

        assert config.ollama_base_url == "http://test:9999"
        assert config.ollama_model == "test-model"
        assert config.log_level == "DEBUG"

        # Test with defaults
        config_default = Config(tmp_path / "default")
        assert config_default.ollama_base_url == "http://localhost:11434"
        assert config_default.ollama_model == "qwen3:0.6b"
        assert config_default.log_level == "INFO"

    def test_get_method(self, tmp_path):
        """Test the get method for accessing config values."""
        config = Config(tmp_path / "config")

        # Test existing values
        assert config.get("ollama", "base_url") == "http://localhost:11434"
        assert config.get("ollama", "model") == "qwen3:0.6b"
        assert config.get("logging", "level") == "INFO"

        # Test non-existing values with defaults
        assert config.get("ollama", "timeout", 30) == 30
        assert config.get("nonexistent", "key", "default") == "default"

    def test_reload_config(self, tmp_path):
        """Test config reloading functionality."""
        config_dir = tmp_path / "config"
        config = Config(config_dir)

        # Initial state
        assert config.ollama_model == "qwen3:0.6b"

        # Modify config file
        new_config = """[ollama]
base_url = "http://localhost:11434"
model = "new-model"

[logging]
level = "INFO"
"""
        config.config_file_path.write_text(new_config)

        # Reload and check
        config.reload()
        assert config.ollama_model == "new-model"

    def test_set_config_value(self, tmp_path):
        """Test setting a configuration value."""
        config = Config(tmp_path / "config")

        # Set a value in existing section
        config.set("ollama", "model", "new-model")

        # Verify the value was set
        assert config.get("ollama", "model") == "new-model"

        # Verify it was saved to file
        config_reloaded = Config(tmp_path / "config")
        assert config_reloaded.get("ollama", "model") == "new-model"

    def test_set_config_value_new_section(self, tmp_path):
        """Test setting a configuration value in a new section."""
        config = Config(tmp_path / "config")

        # Set a value in new section
        config.set("new_section", "new_key", "new_value")

        # Verify the value was set
        assert config.get("new_section", "new_key") == "new_value"

        # Verify it was saved to file
        config_reloaded = Config(tmp_path / "config")
        assert config_reloaded.get("new_section", "new_key") == "new_value"

    def test_reset_to_defaults(self, tmp_path):
        """Test resetting configuration to defaults."""
        config = Config(tmp_path / "config")

        # Modify some values
        config.set("ollama", "model", "custom-model")
        config.set("logging", "level", "DEBUG")

        # Reset to defaults
        config.reset_to_defaults()

        # Verify defaults are restored
        assert config.get("ollama", "model") == "qwen3:0.6b"
        assert config.get("logging", "level") == "INFO"

        # Verify it was saved to file
        config_reloaded = Config(tmp_path / "config")
        assert config_reloaded.get("ollama", "model") == "qwen3:0.6b"
        assert config_reloaded.get("logging", "level") == "INFO"

    def test_get_all_sections(self, tmp_path):
        """Test getting all configuration sections."""
        config = Config(tmp_path / "config")

        result = config.get_all_sections()

        expected = {
            "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:0.6b"},
            "logging": {"level": "INFO"},
            "ai": {"interactive_threshold": 80},
            "agent": {"require_confirmation": False},
        }

        assert result == expected
        # Should return a copy, not the original
        assert result is not config._config_data

    def test_save_config_import_error(self, tmp_path):
        """Test config saving when tomli-w is not available."""
        config = Config(tmp_path / "config")

        # Mock the import statement inside _save_config
        original_import = __builtins__["__import__"]

        def mock_import(name, *args, **kwargs):
            if name == "tomli_w":
                raise ImportError("No module named 'tomli_w'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            with pytest.raises(ConfigError, match="tomli-w package is required"):
                config.set("test", "key", "value")

    def test_save_config_os_error(self, tmp_path):
        """Test config saving when file operation fails."""
        config = Config(tmp_path / "config")

        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(ConfigError, match="Failed to save config"):
                config.set("test", "key", "value")

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
                    "ollama": {
                        "base_url": "http://localhost:11434",
                        "model": "qwen3:0.6b",
                    },
                    "logging": {"level": "INFO"},
                }

                config = get_config()

                assert isinstance(config, Config)
                mock_user_config_dir.assert_called_once_with("automake")


class TestConfigIntegration:
    """Integration tests for config functionality."""

    def test_full_config_lifecycle(self, tmp_path):
        """Test complete config lifecycle: create, read, modify, reload."""
        config_dir = tmp_path / "lifecycle"

        # 1. Create new config (should create default)
        config = Config(config_dir)
        assert config.config_file_path.exists()
        assert config.ollama_model == "qwen3:0.6b"

        # 2. Modify config file externally
        new_content = """[ollama]
base_url = "http://modified:8080"
model = "modified-model"

[logging]
level = "DEBUG"
"""
        config.config_file_path.write_text(new_content)

        # 3. Reload and verify changes
        config.reload()
        assert config.ollama_base_url == "http://modified:8080"
        assert config.ollama_model == "modified-model"
        assert config.log_level == "DEBUG"

    def test_concurrent_config_access(self, tmp_path):
        """Test that multiple Config instances work correctly."""
        config_dir = tmp_path / "concurrent"

        # Create first instance
        config1 = Config(config_dir)
        assert config1.ollama_model == "qwen3:0.6b"

        # Create second instance (should read existing file)
        config2 = Config(config_dir)
        assert config2.ollama_model == "qwen3:0.6b"

        # Both should have same values
        assert config1.ollama_base_url == config2.ollama_base_url
        assert config1.log_level == config2.log_level
