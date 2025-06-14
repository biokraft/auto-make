"""Tests for the config CLI commands."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import typer

from automake.cli.main import (
    _convert_config_value,
    config_edit,
    config_reset,
    config_set,
    config_show,
)
from automake.config import ConfigError


class TestConfigShow:
    """Test cases for the config show command."""

    @patch("automake.cli.main.get_config")
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

        # Should not raise
        config_show(section=None)

    @patch("automake.cli.main.get_config")
    def test_config_show_specific_section(self, mock_get_config):
        """Test showing a specific configuration section."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:0.6b"},
            "logging": {"level": "INFO"},
        }
        mock_config.config_file_path = Path("/test/config.toml")
        mock_get_config.return_value = mock_config

        # Should not raise
        config_show(section="ollama")

    @patch("automake.cli.main.get_config")
    def test_config_show_nonexistent_section(self, mock_get_config):
        """Test showing a non-existent configuration section."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:0.6b"}
        }
        mock_get_config.return_value = mock_config

        with pytest.raises(typer.Exit) as exc_info:
            config_show(section="nonexistent")

        assert exc_info.value.exit_code == 1

    @patch("automake.cli.main.get_config")
    def test_config_show_error(self, mock_get_config):
        """Test config show when an error occurs."""
        mock_get_config.side_effect = Exception("Config error")

        with pytest.raises(typer.Exit) as exc_info:
            config_show(section=None)

        assert exc_info.value.exit_code == 1


class TestConfigSet:
    """Test cases for the config set command."""

    @patch("automake.cli.main.get_config")
    def test_config_set_success(self, mock_get_config):
        """Test successful configuration setting."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ollama": {"base_url": "http://localhost:11434", "model": "new-model"}
        }
        mock_get_config.return_value = mock_config

        # Should not raise
        config_set(section="ollama", key="model", value="new-model")

        mock_config.set.assert_called_once_with("ollama", "model", "new-model")

    @patch("automake.cli.main.get_config")
    def test_config_set_boolean_value(self, mock_get_config):
        """Test setting a boolean configuration value."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {"test": {"enabled": True}}
        mock_get_config.return_value = mock_config

        # Should not raise
        config_set(section="test", key="enabled", value="true")

        mock_config.set.assert_called_once_with("test", "enabled", True)

    @patch("automake.cli.main.get_config")
    def test_config_set_integer_value(self, mock_get_config):
        """Test setting an integer configuration value."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ai": {"interactive_threshold": 90}
        }
        mock_get_config.return_value = mock_config

        # Should not raise
        config_set(section="ai", key="interactive_threshold", value="90")

        mock_config.set.assert_called_once_with("ai", "interactive_threshold", 90)

    @patch("automake.cli.main.get_config")
    def test_config_set_error(self, mock_get_config):
        """Test config set when an error occurs."""
        mock_config = Mock()
        mock_config.set.side_effect = ConfigError("Failed to save config")
        mock_get_config.return_value = mock_config

        with pytest.raises(typer.Exit) as exc_info:
            config_set(section="test", key="key", value="value")

        assert exc_info.value.exit_code == 1


class TestConfigReset:
    """Test cases for the config reset command."""

    @patch("automake.cli.main.get_config")
    def test_config_reset_with_yes_flag(self, mock_get_config):
        """Test config reset with --yes flag."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:0.6b"}
        }
        mock_get_config.return_value = mock_config

        # Should not raise
        config_reset(yes=True)

        mock_config.reset_to_defaults.assert_called_once()

    @patch("questionary.confirm")
    @patch("automake.cli.main.get_config")
    def test_config_reset_with_confirmation_yes(
        self, mock_get_config, mock_questionary
    ):
        """Test config reset with user confirmation (yes)."""
        mock_config = Mock()
        mock_config.get_all_sections.return_value = {
            "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:0.6b"}
        }
        mock_get_config.return_value = mock_config

        mock_questionary.return_value.ask.return_value = True

        # Should not raise
        config_reset(yes=False)

        mock_config.reset_to_defaults.assert_called_once()

    @patch("questionary.confirm")
    @patch("automake.cli.main.get_config")
    def test_config_reset_with_confirmation_no(self, mock_get_config, mock_questionary):
        """Test config reset with user confirmation (no)."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config

        mock_questionary.return_value.ask.return_value = False

        # Should not raise
        config_reset(yes=False)

        mock_config.reset_to_defaults.assert_not_called()

    @patch("automake.cli.main.get_config")
    def test_config_reset_error(self, mock_get_config):
        """Test config reset when an error occurs."""
        mock_config = Mock()
        mock_config.reset_to_defaults.side_effect = ConfigError(
            "Failed to reset config"
        )
        mock_get_config.return_value = mock_config

        with pytest.raises(typer.Exit) as exc_info:
            config_reset(yes=True)

        assert exc_info.value.exit_code == 1


class TestConfigEdit:
    """Test cases for the config edit command."""

    @patch("subprocess.run")
    @patch("automake.cli.main.get_config")
    def test_config_edit_with_editor_success(self, mock_get_config, mock_subprocess):
        """Test config edit with successful editor launch."""
        mock_config = Mock()
        mock_config.config_file_path = Path("/test/config.toml")
        mock_get_config.return_value = mock_config

        mock_subprocess.return_value = Mock(returncode=0)

        with patch.dict("os.environ", {"EDITOR": "vim"}):
            # Should not raise
            config_edit()

        mock_subprocess.assert_called_once_with(
            ["vim", "/test/config.toml"], check=True
        )

    @patch("subprocess.run")
    @patch("automake.cli.main.get_config")
    def test_config_edit_fallback_to_open(self, mock_get_config, mock_subprocess):
        """Test config edit fallback to system open command."""
        mock_config = Mock()
        mock_config.config_file_path = Path("/test/config.toml")
        mock_get_config.return_value = mock_config

        # First call (editor) fails with CalledProcessError, second call (open) succeeds
        def side_effect(*args, **kwargs):
            if args[0][0] == "vim":
                from subprocess import CalledProcessError

                raise CalledProcessError(1, "vim")
            else:
                return Mock(returncode=0)

        mock_subprocess.side_effect = side_effect

        with patch.dict("os.environ", {"EDITOR": "vim"}):
            # Should not raise
            config_edit()

        assert mock_subprocess.call_count == 2

    @patch("subprocess.run")
    @patch("automake.cli.main.get_config")
    def test_config_edit_both_fail(self, mock_get_config, mock_subprocess):
        """Test config edit when both editor and open fail."""
        mock_config = Mock()
        mock_config.config_file_path = Path("/test/config.toml")
        mock_get_config.return_value = mock_config

        # Both calls fail
        def side_effect(*args, **kwargs):
            from subprocess import CalledProcessError

            raise CalledProcessError(1, args[0][0])

        mock_subprocess.side_effect = side_effect

        with patch.dict("os.environ", {"EDITOR": "vim"}):
            with pytest.raises(typer.Exit) as exc_info:
                config_edit()

        assert exc_info.value.exit_code == 1

    @patch("automake.cli.main.get_config")
    def test_config_edit_error(self, mock_get_config):
        """Test config edit when an error occurs."""
        mock_get_config.side_effect = Exception("Config error")

        with pytest.raises(typer.Exit) as exc_info:
            config_edit()

        assert exc_info.value.exit_code == 1


class TestConvertConfigValue:
    """Test cases for the _convert_config_value function."""

    def test_convert_boolean_true(self):
        """Test converting 'true' to boolean."""
        result = _convert_config_value("true")
        assert result is True

    def test_convert_boolean_false(self):
        """Test converting 'false' to boolean."""
        result = _convert_config_value("false")
        assert result is False

    def test_convert_boolean_case_insensitive(self):
        """Test converting boolean values case insensitively."""
        assert _convert_config_value("TRUE") is True
        assert _convert_config_value("False") is False
        assert _convert_config_value("TrUe") is True

    def test_convert_integer(self):
        """Test converting integer values."""
        result = _convert_config_value("42")
        assert result == 42
        assert isinstance(result, int)

    def test_convert_negative_integer(self):
        """Test converting negative integer values."""
        result = _convert_config_value("-10")
        assert result == -10
        assert isinstance(result, int)

    def test_convert_string(self):
        """Test converting string values."""
        result = _convert_config_value("hello world")
        assert result == "hello world"
        assert isinstance(result, str)

    def test_convert_string_that_looks_like_number(self):
        """Test converting strings that contain numbers but aren't pure numbers."""
        result = _convert_config_value("123abc")
        assert result == "123abc"
        assert isinstance(result, str)

    def test_convert_empty_string(self):
        """Test converting empty string."""
        result = _convert_config_value("")
        assert result == ""
        assert isinstance(result, str)
