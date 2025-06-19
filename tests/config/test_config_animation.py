"""Tests for animation configuration settings."""

from pathlib import Path
from tempfile import TemporaryDirectory

from automake.config.manager import Config


class TestAnimationConfig:
    """Test animation configuration settings."""

    def test_default_animation_enabled(self):
        """Test that animation is enabled by default."""
        with TemporaryDirectory() as temp_dir:
            config = Config(config_dir=Path(temp_dir))
            assert config.ui_animation_enabled is True

    def test_default_animation_speed(self):
        """Test default animation speed."""
        with TemporaryDirectory() as temp_dir:
            config = Config(config_dir=Path(temp_dir))
            assert config.ui_animation_speed == 50.0

    def test_get_animation_enabled(self):
        """Test getting animation enabled setting via get method."""
        with TemporaryDirectory() as temp_dir:
            config = Config(config_dir=Path(temp_dir))
            assert config.get("ui", "animation_enabled", False) is True

    def test_get_animation_speed(self):
        """Test getting animation speed setting via get method."""
        with TemporaryDirectory() as temp_dir:
            config = Config(config_dir=Path(temp_dir))
            assert config.get("ui", "animation_speed", 25.0) == 50.0

    def test_set_animation_enabled(self):
        """Test setting animation enabled configuration."""
        with TemporaryDirectory() as temp_dir:
            config = Config(config_dir=Path(temp_dir))

            # Set animation to disabled
            config.set("ui", "animation_enabled", False)

            # Verify it was set
            assert config.ui_animation_enabled is False
            assert config.get("ui", "animation_enabled") is False

    def test_set_animation_speed(self):
        """Test setting animation speed configuration."""
        with TemporaryDirectory() as temp_dir:
            config = Config(config_dir=Path(temp_dir))

            # Set animation speed
            config.set("ui", "animation_speed", 100.0)

            # Verify it was set
            assert config.ui_animation_speed == 100.0
            assert config.get("ui", "animation_speed") == 100.0

    def test_animation_config_persistence(self):
        """Test that animation config persists across instances."""
        with TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # Create first config instance and set values
            config1 = Config(config_dir=config_dir)
            config1.set("ui", "animation_enabled", False)
            config1.set("ui", "animation_speed", 75.0)

            # Create second config instance and verify values persisted
            config2 = Config(config_dir=config_dir)
            assert config2.ui_animation_enabled is False
            assert config2.ui_animation_speed == 75.0

    def test_config_file_contains_ui_section(self):
        """Test that generated config file contains UI section."""
        with TemporaryDirectory() as temp_dir:
            config = Config(config_dir=Path(temp_dir))

            # Read the config file content
            config_content = config.config_file.read_text()

            # Should contain UI section and animation settings
            assert "[ui]" in config_content
            assert "animation_enabled" in config_content
            assert "animation_speed" in config_content

    def test_reload_preserves_animation_config(self):
        """Test that reloading config preserves animation settings."""
        with TemporaryDirectory() as temp_dir:
            config = Config(config_dir=Path(temp_dir))

            # Set custom values
            config.set("ui", "animation_enabled", False)
            config.set("ui", "animation_speed", 25.0)

            # Reload config
            config.reload()

            # Verify values are preserved
            assert config.ui_animation_enabled is False
            assert config.ui_animation_speed == 25.0
