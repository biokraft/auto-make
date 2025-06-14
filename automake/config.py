"""Configuration management for AutoMake.

This module handles reading and creating the config.toml file for user-specific
settings like Ollama server configuration and logging preferences.
"""

import tomllib
from pathlib import Path
from typing import Any

import appdirs


class ConfigError(Exception):
    """Raised when there's an error with configuration."""

    pass


class Config:
    """Manages AutoMake configuration from config.toml file."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize configuration manager.

        Args:
            config_dir: Optional custom config directory path. If None, uses
                       platform-specific user config directory.
        """
        if config_dir is None:
            config_dir = Path(appdirs.user_config_dir("automake"))

        self.config_dir = config_dir
        self.config_file = self.config_dir / "config.toml"
        self._config_data: dict[str, Any] = {}
        self._load_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration values."""
        return {
            "ollama": {"base_url": "http://localhost:11434", "model": "gemma3:4b"},
            "logging": {"level": "INFO"},
            "ai": {"interactive_threshold": 80},
        }

    def _create_default_config(self) -> None:
        """Create default config.toml file."""
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Create default config content
        config_content = """# Configuration for AutoMake

[ollama]
# The base URL for the local Ollama server.
base_url = "http://localhost:11434"

# The model to use for interpreting commands.
# The user must ensure this model is available on their Ollama server.
model = "gemma3:4b"

[logging]
# Set log level to "DEBUG" for verbose output for troubleshooting.
# Accepted values: "INFO", "DEBUG", "WARNING", "ERROR"
level = "INFO"

[ai]
# Confidence threshold for interactive mode (0-100)
# If AI confidence is below this threshold, interactive mode will be triggered
interactive_threshold = 80
"""

        # Write the config file
        with open(self.config_file, "w", encoding="utf-8") as f:
            f.write(config_content)

    def _load_config(self) -> None:
        """Load configuration from file or create default if not exists."""
        if not self.config_file.exists():
            self._create_default_config()

        try:
            with open(self.config_file, "rb") as f:
                self._config_data = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError) as e:
            raise ConfigError(
                f"Failed to load config from {self.config_file}: {e}"
            ) from e

        # Merge with defaults to ensure all required keys exist
        defaults = self._get_default_config()
        for section, values in defaults.items():
            if section not in self._config_data:
                self._config_data[section] = {}
            for key, default_value in values.items():
                if key not in self._config_data[section]:
                    self._config_data[section][key] = default_value

    @property
    def ollama_base_url(self) -> str:
        """Get Ollama base URL."""
        return self._config_data["ollama"]["base_url"]

    @property
    def ollama_model(self) -> str:
        """Get Ollama model name."""
        return self._config_data["ollama"]["model"]

    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self._config_data["logging"]["level"]

    @property
    def interactive_threshold(self) -> int:
        """Get AI interactive threshold."""
        return self._config_data["ai"]["interactive_threshold"]

    @property
    def config_file_path(self) -> Path:
        """Get the path to the config file."""
        return self.config_file

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            section: Configuration section name
            key: Configuration key name
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self._config_data.get(section, {}).get(key, default)

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()


def get_config(config_dir: Path | None = None) -> Config:
    """Get a Config instance.

    Args:
        config_dir: Optional custom config directory path

    Returns:
        Config instance
    """
    return Config(config_dir)
