"""Tests for signal handling configuration."""

from automake.config.manager import Config


class TestSignalConfig:
    """Test signal handling configuration."""

    def test_default_config_has_signal_section(self, tmp_path):
        """Test that default config includes signal handling section."""
        # Arrange & Act
        config = Config(config_dir=tmp_path)

        # Assert
        assert "signal" in config._config_data
        assert isinstance(config._config_data["signal"], dict)

    def test_signal_handling_enabled_by_default(self, tmp_path):
        """Test that signal handling is enabled by default."""
        # Arrange & Act
        config = Config(config_dir=tmp_path)

        # Assert
        assert config.get("signal", "enabled") is True

    def test_signal_cleanup_timeout_default(self, tmp_path):
        """Test that signal cleanup timeout has a reasonable default."""
        # Arrange & Act
        config = Config(config_dir=tmp_path)

        # Assert
        timeout = config.get("signal", "cleanup_timeout")
        assert isinstance(timeout, int | float)
        assert timeout > 0
        assert timeout <= 30  # Should be reasonable timeout

    def test_force_kill_timeout_default(self, tmp_path):
        """Test that force kill timeout has a reasonable default."""
        # Arrange & Act
        config = Config(config_dir=tmp_path)

        # Assert
        timeout = config.get("signal", "force_kill_timeout")
        assert isinstance(timeout, int | float)
        assert timeout > 0
        assert timeout <= 10  # Should be shorter than cleanup timeout

    def test_signal_config_properties(self, tmp_path):
        """Test that Config class has signal handling properties."""
        # Arrange & Act
        config = Config(config_dir=tmp_path)

        # Assert
        assert hasattr(config, "signal_handling_enabled")
        assert hasattr(config, "signal_cleanup_timeout")
        assert hasattr(config, "signal_force_kill_timeout")

    def test_signal_handling_enabled_property(self, tmp_path):
        """Test signal_handling_enabled property."""
        # Arrange & Act
        config = Config(config_dir=tmp_path)

        # Assert
        assert isinstance(config.signal_handling_enabled, bool)
        assert config.signal_handling_enabled is True

    def test_signal_cleanup_timeout_property(self, tmp_path):
        """Test signal_cleanup_timeout property."""
        # Arrange & Act
        config = Config(config_dir=tmp_path)

        # Assert
        assert isinstance(config.signal_cleanup_timeout, int | float)
        assert config.signal_cleanup_timeout > 0

    def test_signal_force_kill_timeout_property(self, tmp_path):
        """Test signal_force_kill_timeout property."""
        # Arrange & Act
        config = Config(config_dir=tmp_path)

        # Assert
        assert isinstance(config.signal_force_kill_timeout, int | float)
        assert config.signal_force_kill_timeout > 0

    def test_signal_config_can_be_modified(self, tmp_path):
        """Test that signal configuration can be modified."""
        # Arrange
        config = Config(config_dir=tmp_path)

        # Act
        config.set("signal", "enabled", False)
        config.set("signal", "cleanup_timeout", 15)

        # Assert
        assert config.get("signal", "enabled") is False
        assert config.get("signal", "cleanup_timeout") == 15
