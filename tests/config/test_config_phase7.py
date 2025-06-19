"""Tests for Phase 7: Action Confirmation configuration."""

import tempfile
from pathlib import Path

from automake.config import Config


class TestActionConfirmationConfig:
    """Test action confirmation configuration."""

    def test_require_confirmation_defaults_to_true(self):
        """Test that require_confirmation defaults to True for security."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config = Config(config_dir)

            # Should default to True for security
            assert config.agent_require_confirmation is True

    def test_require_confirmation_can_be_disabled(self):
        """Test that require_confirmation can be set to False."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config = Config(config_dir)

            # Change to False
            config.set("agent", "require_confirmation", False)

            # Verify it's False
            assert config.agent_require_confirmation is False

            # Reload and verify persistence
            config.reload()
            assert config.agent_require_confirmation is False

    def test_config_file_template_has_correct_default(self):
        """Test that the created config file has require_confirmation = true."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config = Config(config_dir)

            # Read the created config file
            config_content = config.config_file.read_text()

            # Should contain require_confirmation = true
            assert "require_confirmation = true" in config_content
