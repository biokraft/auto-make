"""Tests for the config CLI commands."""

from pathlib import Path
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from automake.cli.app import app
from automake.cli.commands.config import _convert_config_value
from automake.config import ConfigError


class TestConfigShow:
    """Test cases for the config show command."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("automake.cli.commands.config.get_config")
    def test_config_show_all(self, mock_get_config):
        """Test showing all configuration sections."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:0.6b"},
            "logging": {"level": "INFO"},
            "ai": {"interactive_threshold": 80},
        }
        mock_config.config_file_path = Path("/test/config.toml")
        mock_get_config.return_value = mock_config

        result = self.runner.invoke(app, ["config", "show"])

        assert result.exit_code == 0
        mock_get_config.assert_called_once()

    @patch("automake.cli.commands.config.get_config")
    def test_config_show_specific_section(self, mock_get_config):
        """Test showing a specific configuration section."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:0.6b"},
            "logging": {"level": "INFO"},
        }
        mock_config.config_file_path = Path("/test/config.toml")
        mock_get_config.return_value = mock_config

        result = self.runner.invoke(app, ["config", "show", "ollama"])

        assert result.exit_code == 0
        mock_get_config.assert_called_once()

    @patch("automake.cli.commands.config.get_config")
    def test_config_show_nonexistent_section(self, mock_get_config):
        """Test showing a non-existent configuration section."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:0.6b"}
        }
        mock_get_config.return_value = mock_config

        result = self.runner.invoke(app, ["config", "show", "nonexistent"])

        assert result.exit_code == 1
        mock_get_config.assert_called_once()

    @patch("automake.cli.commands.config.get_config")
    def test_config_show_error(self, mock_get_config):
        """Test config show when an error occurs."""
        mock_get_config.side_effect = Exception("Config error")

        result = self.runner.invoke(app, ["config", "show"])

        assert result.exit_code == 1


class TestConfigSet:
    """Test cases for the config set command."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("automake.cli.commands.config.get_config")
    def test_config_set_success(self, mock_get_config):
        """Test successful configuration setting."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ollama": {"base_url": "http://localhost:11434", "model": "new-model"}
        }
        mock_get_config.return_value = mock_config

        result = self.runner.invoke(app, ["config", "set", "ollama.model", "new-model"])

        assert result.exit_code == 0
        mock_get_config.assert_called_once()

    @patch("automake.cli.commands.config.get_config")
    def test_config_set_model_success(self, mock_get_config):
        """Test that setting ollama.model succeeds and calls config.set correctly."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ollama": {"base_url": "http://localhost:11434", "model": "qwen2.5:7b"}
        }
        mock_get_config.return_value = mock_config

        result = self.runner.invoke(
            app, ["config", "set", "ollama.model", "qwen2.5:7b"]
        )

        assert result.exit_code == 0
        mock_config.set.assert_called_once_with("ollama", "model", "qwen2.5:7b")
        mock_get_config.assert_called_once()

    @patch("automake.cli.commands.config.get_config")
    def test_config_set_non_model_success(self, mock_get_config):
        """Test that setting non-model config succeeds
        and calls config.set correctly."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:0.6b"}
        }
        mock_get_config.return_value = mock_config

        result = self.runner.invoke(
            app, ["config", "set", "ollama.base_url", "http://localhost:11434"]
        )

        assert result.exit_code == 0
        mock_config.set.assert_called_once_with(
            "ollama", "base_url", "http://localhost:11434"
        )
        mock_get_config.assert_called_once()

    @patch("automake.cli.commands.config.get_config")
    def test_config_set_boolean_value(self, mock_get_config):
        """Test setting a boolean configuration value."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {"test": {"enabled": True}}
        mock_get_config.return_value = mock_config

        result = self.runner.invoke(app, ["config", "set", "test.enabled", "true"])

        assert result.exit_code == 0
        mock_get_config.assert_called_once()

    @patch("automake.cli.commands.config.get_config")
    def test_config_set_integer_value(self, mock_get_config):
        """Test setting an integer configuration value."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ai": {"interactive_threshold": 90}
        }
        mock_get_config.return_value = mock_config

        result = self.runner.invoke(
            app, ["config", "set", "ai.interactive_threshold", "90"]
        )

        assert result.exit_code == 0
        mock_get_config.assert_called_once()

    @patch("automake.cli.commands.config.get_config")
    def test_config_set_error(self, mock_get_config):
        """Test config set when an error occurs."""
        mock_config = Mock()
        mock_config.set.side_effect = ConfigError("Failed to save config")
        mock_get_config.return_value = mock_config

        result = self.runner.invoke(app, ["config", "set", "ollama.model", "llama2"])

        assert result.exit_code == 1

    def test_config_set_invalid_key_path_known_section(self):
        """Test config set with invalid key path for known section."""
        result = self.runner.invoke(app, ["config", "set", "ollama", "model"])

        assert result.exit_code == 1

    def test_config_set_invalid_key_path_unknown_section(self):
        """Test config set with invalid key path for unknown section."""
        result = self.runner.invoke(app, ["config", "set", "unknown", "value"])

        assert result.exit_code == 1


class TestConfigReset:
    """Test cases for the config reset command."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("automake.cli.commands.config.get_config")
    def test_config_reset_with_yes_flag(self, mock_get_config):
        """Test config reset with --yes flag."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:0.6b"}
        }
        mock_get_config.return_value = mock_config

        result = self.runner.invoke(app, ["config", "reset", "--yes"])

        assert result.exit_code == 0
        mock_get_config.assert_called_once()

    @patch("automake.cli.commands.config.get_config")
    def test_config_reset_with_confirmation_yes(self, mock_get_config):
        """Test config reset with user confirmation (yes)."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config

        result = self.runner.invoke(app, ["config", "reset"], input="y\n")

        assert result.exit_code == 0
        mock_get_config.assert_called_once()

    @patch("automake.cli.commands.config.get_config")
    def test_config_reset_with_confirmation_no(self, mock_get_config):
        """Test config reset with user confirmation (no)."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config

        result = self.runner.invoke(app, ["config", "reset"], input="n\n")

        assert result.exit_code == 0
        # get_config should NOT be called when user says no
        mock_get_config.assert_not_called()

    @patch("automake.cli.commands.config.get_config")
    def test_config_reset_error(self, mock_get_config):
        """Test config reset when an error occurs."""
        mock_config = Mock()
        mock_config.reset_to_defaults.side_effect = ConfigError(
            "Failed to reset config"
        )
        mock_get_config.return_value = mock_config

        result = self.runner.invoke(app, ["config", "reset", "--yes"])

        assert result.exit_code == 1


class TestConfigEdit:
    """Test cases for the config edit command."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("automake.cli.commands.config.get_config")
    def test_config_edit_with_editor_success(self, mock_get_config):
        """Test config edit with successful editor launch."""
        mock_config = Mock()
        mock_config.config_file_path = Path("/test/config.toml")
        mock_get_config.return_value = mock_config

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            result = self.runner.invoke(app, ["config", "edit"])

        assert result.exit_code == 0
        mock_get_config.assert_called_once()

    @patch("automake.cli.commands.config.get_config")
    def test_config_edit_fallback_to_open(self, mock_get_config):
        """Test config edit with fallback to open command."""
        mock_config = Mock()
        mock_config.config_file_path = Path("/test/config.toml")
        mock_get_config.return_value = mock_config

        with patch("subprocess.run") as mock_run:
            # First call (editor) fails, second call (open) succeeds
            def side_effect(*args, **kwargs):
                if "EDITOR" in str(args) or "nano" in str(args):
                    raise FileNotFoundError("Editor not found")
                return Mock(returncode=0)

            mock_run.side_effect = side_effect
            result = self.runner.invoke(app, ["config", "edit"])

        assert result.exit_code == 0
        # Should try editor first, then fallback to open
        assert mock_run.call_count == 2

    @patch("automake.cli.commands.config.get_config")
    def test_config_edit_both_fail(self, mock_get_config):
        """Test config edit when both editor and open fail."""
        mock_config = Mock()
        mock_config.config_file_path = Path("/test/config.toml")
        mock_get_config.return_value = mock_config

        with patch("subprocess.run") as mock_run:
            # Both calls fail
            def side_effect(*args, **kwargs):
                raise FileNotFoundError("Command not found")

            mock_run.side_effect = side_effect
            result = self.runner.invoke(app, ["config", "edit"])

        assert result.exit_code == 1
        mock_get_config.assert_called_once()

    @patch("automake.cli.commands.config.get_config")
    def test_config_edit_error(self, mock_get_config):
        """Test config edit when an error occurs."""
        mock_get_config.side_effect = Exception("Config error")

        result = self.runner.invoke(app, ["config", "edit"])

        assert result.exit_code == 1


class TestConvertConfigValue:
    """Test cases for the _convert_config_value function."""

    def test_convert_boolean_true(self):
        """Test converting boolean true values."""
        assert _convert_config_value("true") is True
        assert _convert_config_value("True") is True

    def test_convert_boolean_false(self):
        """Test converting boolean false values."""
        assert _convert_config_value("false") is False
        assert _convert_config_value("False") is False

    def test_convert_boolean_case_insensitive(self):
        """Test boolean conversion is case insensitive."""
        assert _convert_config_value("TRUE") is True
        assert _convert_config_value("FALSE") is False

    def test_convert_integer(self):
        """Test converting integer values."""
        assert _convert_config_value("42") == 42
        assert _convert_config_value("0") == 0

    def test_convert_negative_integer(self):
        """Test converting negative integer values."""
        assert _convert_config_value("-42") == -42
        assert _convert_config_value("-1") == -1

    def test_convert_string(self):
        """Test converting string values."""
        assert _convert_config_value("hello") == "hello"
        assert _convert_config_value("world") == "world"

    def test_convert_string_that_looks_like_number(self):
        """Test converting strings that look like numbers but aren't."""
        assert _convert_config_value("42.5") == "42.5"  # Float as string
        assert _convert_config_value("1e10") == "1e10"  # Scientific notation as string

    def test_convert_empty_string(self):
        """Test converting empty string."""
        assert _convert_config_value("") == ""
