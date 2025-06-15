"""Configuration management package for AutoMake.

This package handles reading and creating the config.toml file for user-specific
settings like Ollama server configuration and logging preferences.
"""

from .manager import Config, ConfigError, get_config

__all__ = ["Config", "ConfigError", "get_config"]
