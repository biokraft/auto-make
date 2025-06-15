"""Tests for the updated configuration with Phase 3 agent settings."""

import tempfile
from pathlib import Path

import pytest

from automake.config.manager import Config


class TestConfigPhase3:
    """Test the updated configuration with agent settings."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary config directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_default_config_includes_agent_section(self, temp_config_dir):
        """Test that default config includes agent section."""
        config = Config(temp_config_dir)

        # Check that agent section exists in defaults
        defaults = config._get_default_config()
        assert "agent" in defaults
        assert "require_confirmation" in defaults["agent"]
        assert defaults["agent"]["require_confirmation"] is False

    def test_agent_require_confirmation_property(self, temp_config_dir):
        """Test the agent_require_confirmation property."""
        config = Config(temp_config_dir)

        # Should return default value
        assert config.agent_require_confirmation is False

    def test_agent_require_confirmation_from_file(self, temp_config_dir):
        """Test reading agent_require_confirmation from config file."""
        # Create config file with agent section
        config_file = temp_config_dir / "config.toml"
        config_content = """
[ollama]
base_url = "http://localhost:11434"
model = "qwen3:0.6b"

[logging]
level = "INFO"

[ai]
interactive_threshold = 80

[agent]
require_confirmation = true
"""
        config_file.write_text(config_content)

        config = Config(temp_config_dir)
        assert config.agent_require_confirmation is True

    def test_set_agent_require_confirmation(self, temp_config_dir):
        """Test setting agent_require_confirmation value."""
        config = Config(temp_config_dir)

        # Set the value
        config.set("agent", "require_confirmation", True)

        # Verify it was set
        assert config.agent_require_confirmation is True

        # Verify it persists after reload
        config.reload()
        assert config.agent_require_confirmation is True

    def test_created_config_file_includes_agent_section(self, temp_config_dir):
        """Test that newly created config file includes agent section."""
        # Remove any existing config file
        config_file = temp_config_dir / "config.toml"
        if config_file.exists():
            config_file.unlink()

        # Create new config
        Config(temp_config_dir)

        # Read the created file
        config_content = config_file.read_text()

        # Verify agent section is present
        assert "[agent]" in config_content
        assert "require_confirmation = false" in config_content

    def test_config_migration_adds_missing_agent_section(self, temp_config_dir):
        """Test that missing agent section is added during config load."""
        # Create config file without agent section
        config_file = temp_config_dir / "config.toml"
        config_content = """
[ollama]
base_url = "http://localhost:11434"
model = "qwen3:0.6b"

[logging]
level = "INFO"

[ai]
interactive_threshold = 80
"""
        config_file.write_text(config_content)

        # Load config - should add missing agent section
        config = Config(temp_config_dir)

        # Verify agent section is available
        assert config.agent_require_confirmation is False

        # Verify it's in the internal config data
        assert "agent" in config._config_data
        assert "require_confirmation" in config._config_data["agent"]

    def test_get_all_sections_includes_agent(self, temp_config_dir):
        """Test that get_all_sections includes agent section."""
        config = Config(temp_config_dir)

        all_sections = config.get_all_sections()

        assert "agent" in all_sections
        assert "require_confirmation" in all_sections["agent"]
        assert all_sections["agent"]["require_confirmation"] is False

    def test_reset_to_defaults_includes_agent_section(self, temp_config_dir):
        """Test that reset_to_defaults includes agent section."""
        config = Config(temp_config_dir)

        # Modify some values
        config.set("agent", "require_confirmation", True)
        config.set("logging", "level", "DEBUG")

        # Reset to defaults
        config.reset_to_defaults()

        # Verify agent section is reset
        assert config.agent_require_confirmation is False
        assert config.log_level == "INFO"

    def test_get_method_with_agent_section(self, temp_config_dir):
        """Test the generic get method with agent section."""
        config = Config(temp_config_dir)

        # Test getting existing value
        value = config.get("agent", "require_confirmation")
        assert value is False

        # Test getting non-existent value with default
        value = config.get("agent", "non_existent", "default_value")
        assert value == "default_value"

        # Test getting from non-existent section
        value = config.get("non_existent", "key", "default")
        assert value == "default"
