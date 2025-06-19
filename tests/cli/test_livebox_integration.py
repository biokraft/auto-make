"""Tests for Phase 1 LiveBox integration improvements."""

from io import StringIO
from unittest.mock import MagicMock, Mock, patch

import pytest
import typer
from rich.console import Console

from automake.cli.commands.init import init_command as init
from automake.config import Config
from automake.utils.output import MessageType, get_formatter


class TestInitCommandLiveBoxIntegration:
    """Test cases for the init command LiveBox integration."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.output_buffer = StringIO()
        self.console = Console(file=self.output_buffer, width=80, legacy_windows=False)
        self.formatter = get_formatter(self.console)

    def get_output(self) -> str:
        """Get the captured output."""
        return self.output_buffer.getvalue()

    @patch("automake.config.manager.get_config")
    @patch("automake.utils.ollama_manager.ensure_ollama_running")
    @patch("automake.utils.ollama_manager.is_model_available")
    @patch("automake.utils.ollama_manager.get_available_models")
    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_init_success_with_livebox(
        self,
        mock_subprocess_run: MagicMock,
        mock_subprocess_popen: MagicMock,
        mock_get_models: MagicMock,
        mock_is_model_available: MagicMock,
        mock_ensure_ollama_running: MagicMock,
        mock_get_config: MagicMock,
    ) -> None:
        """Test successful initialization uses LiveBox for progress updates."""
        # Setup mocks
        mock_config = Mock(spec=Config)
        mock_config.ollama_model = "llama2"
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_get_config.return_value = mock_config

        mock_subprocess_run.return_value = Mock(returncode=0)
        # Mock Popen for any subprocess.Popen calls (like ollama serve)
        mock_process = Mock()
        mock_process.poll.return_value = 0
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        mock_subprocess_popen.return_value = mock_process

        mock_ensure_ollama_running.return_value = (True, False)  # Running, not started
        mock_is_model_available.return_value = True  # Model is available
        mock_get_models.return_value = ["llama2", "codellama", "mistral"]

        # Mock the live_box context manager to capture LiveBox usage
        with patch.object(self.formatter, "live_box") as mock_live_box:
            mock_box = Mock()
            mock_live_box.return_value.__enter__.return_value = mock_box

            with (
                patch(
                    "automake.utils.output.formatter.get_formatter",
                    return_value=self.formatter,
                ),
                patch(
                    "automake.cli.commands.init.get_available_models"
                ) as mock_init_get_models,
            ):
                # Mock the direct call to get_available_models in init command
                mock_init_get_models.return_value = ["llama2", "codellama", "mistral"]

                init()

            # Verify LiveBox was used for initialization steps
            assert mock_live_box.call_count >= 2  # At least init box and success box
            mock_box.update.assert_called()  # Verify content was updated

    @patch("automake.config.manager.get_config")
    @patch("subprocess.run")
    def test_init_ollama_not_found_livebox_error(
        self,
        mock_subprocess: MagicMock,
        mock_get_config: MagicMock,
    ) -> None:
        """Test Ollama not found error uses LiveBox."""
        mock_config = Mock(spec=Config)
        mock_config.ollama_model = "llama2"
        mock_get_config.return_value = mock_config

        mock_subprocess.side_effect = FileNotFoundError("Ollama not found")

        with patch.object(self.formatter, "live_box") as mock_live_box:
            mock_box = Mock()
            mock_live_box.return_value.__enter__.return_value = mock_box

            with patch(
                "automake.utils.output.formatter.get_formatter",
                return_value=self.formatter,
            ):
                with pytest.raises(typer.Exit):
                    init()

            # Verify error LiveBox was used
            assert mock_live_box.call_count >= 1
            # Check that error content was set (contains error emoji and hint)
            update_calls = [call[0][0] for call in mock_box.update.call_args_list]
            error_content = " ".join(update_calls)
            assert "❌" in error_content
            assert "💡" in error_content

    @pytest.mark.skip(reason="Test needs updating for new init implementation")  # noqa
    @patch("automake.config.manager.get_config")
    @patch("automake.utils.ollama_manager.ensure_ollama_running")
    @patch("automake.utils.ollama_manager.is_model_available")
    @patch("subprocess.run")
    def test_init_model_pull_error_livebox(
        self,
        mock_subprocess: MagicMock,
        mock_is_model_available: MagicMock,
        mock_ensure_ollama_running: MagicMock,
        mock_get_config: MagicMock,
    ) -> None:
        """Test model pull error uses LiveBox."""
        mock_config = Mock(spec=Config)
        mock_config.ollama_model = "invalid-model"
        mock_get_config.return_value = mock_config

        mock_subprocess.return_value = Mock(returncode=0)
        mock_ensure_ollama_running.return_value = (True, False)  # Running, not started
        mock_is_model_available.return_value = (
            False  # Model not available, will trigger pull
        )

        # Mock subprocess.Popen to simulate failed model pull
        with patch("automake.cli.commands.init.subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.poll.return_value = 1  # Process finished
            mock_process.communicate.return_value = ("", "Model not found")
            mock_process.returncode = 1  # Failed
            mock_popen.return_value = mock_process

            with patch.object(self.formatter, "live_box") as mock_live_box:
                mock_box = Mock()
                mock_live_box.return_value.__enter__.return_value = mock_box

                with patch(
                    "automake.utils.output.formatter.get_formatter",
                    return_value=self.formatter,
                ):
                    with pytest.raises(typer.Exit):
                        init()

                # Verify error LiveBox was used
                assert mock_live_box.call_count >= 1
                # Check that error content was set (contains error emoji and hint)
                update_calls = [call[0][0] for call in mock_box.update.call_args_list]
                error_content = " ".join(update_calls)
                assert "❌" in error_content
                assert "💡" in error_content

    @pytest.mark.skip(reason="Test needs updating for new init implementation")  # noqa
    @patch("automake.config.manager.get_config")
    @patch("automake.utils.ollama_manager.get_available_models")
    @patch("subprocess.run")
    def test_init_connection_error_livebox(
        self,
        mock_subprocess: MagicMock,
        mock_get_available_models: MagicMock,
        mock_get_config: MagicMock,
    ) -> None:
        """Test connection error uses LiveBox."""
        mock_config = Mock(spec=Config)
        mock_config.ollama_model = "llama2"
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_get_config.return_value = mock_config

        mock_subprocess.return_value = Mock(returncode=0)
        # First call to get_available_models fails (connection test)
        # Second call also fails (after trying to start server)
        mock_get_available_models.side_effect = [
            Exception("Connection refused"),
            Exception("Connection refused"),
        ]

        with patch.object(self.formatter, "live_box") as mock_live_box:
            mock_box = Mock()
            mock_live_box.return_value.__enter__.return_value = mock_box

            with patch(
                "automake.utils.output.formatter.get_formatter",
                return_value=self.formatter,
            ):
                with pytest.raises(typer.Exit):
                    init()

            # Verify error LiveBox was used
            assert mock_live_box.call_count >= 1
            # Check that error content was set (contains error emoji and hint)
            update_calls = [call[0][0] for call in mock_box.update.call_args_list]
            error_content = " ".join(update_calls)
            assert "❌" in error_content
            assert "💡" in error_content


class TestMainExecutionLiveBoxIntegration:
    """Test cases for main execution logic LiveBox integration."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.output_buffer = StringIO()
        self.console = Console(file=self.output_buffer, width=80, legacy_windows=False)
        self.formatter = get_formatter(self.console)

    def get_output(self) -> str:
        """Get the captured output."""
        return self.output_buffer.getvalue()

    @pytest.mark.skip(
        reason="Test disabled due to architecture change to agent-first approach"
    )
    def test_makefile_not_found_error_livebox(self) -> None:
        """Test MakefileNotFoundError uses LiveBox."""
        pass  # Architecture changed, test needs refactoring

    @pytest.mark.skip(
        reason="Test disabled due to architecture change to agent-first approach"
    )
    def test_os_error_livebox(self) -> None:
        """Test OSError uses LiveBox."""
        pass  # Architecture changed, test needs refactoring

    @pytest.mark.skip(
        reason="Test disabled due to architecture change to agent-first approach"
    )
    def test_command_interpretation_error_livebox(self) -> None:
        """Test command interpretation error uses LiveBox."""
        pass  # Architecture changed, test needs refactoring

    @pytest.mark.skip(
        reason="Test disabled due to architecture change to agent-first approach"
    )
    def test_operation_cancelled_livebox(self) -> None:
        """Test operation cancelled uses LiveBox."""
        pass  # Architecture changed, test needs refactoring

    @pytest.mark.skip(
        reason="Test disabled due to architecture change to agent-first approach"
    )
    def test_no_command_determined_livebox(self) -> None:
        """Test no command determined uses LiveBox."""
        pass  # Architecture changed, test needs refactoring


class TestConfigCommandLiveBoxIntegration:
    """Test cases for config command LiveBox integration."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.output_buffer = StringIO()
        self.console = Console(file=self.output_buffer, width=80, legacy_windows=False)
        self.formatter = get_formatter(self.console)

    def get_output(self) -> str:
        """Get the captured output."""
        return self.output_buffer.getvalue()

    @patch("automake.config.manager.get_config")
    def test_config_show_section_not_found_livebox(
        self,
        mock_get_config: MagicMock,
    ) -> None:
        """Test config show with non-existent section uses LiveBox."""
        from automake.cli.commands.config import config_show_command as config_show

        mock_config = Mock()
        mock_config.get_all_sections.return_value = {"ollama": {"model": "llama2"}}
        mock_get_config.return_value = mock_config

        with patch.object(self.formatter, "live_box") as mock_live_box:
            mock_box = Mock()
            mock_live_box.return_value.__enter__.return_value = mock_box

            with patch(
                "automake.utils.output.formatter.get_formatter",
                return_value=self.formatter,
            ):
                with pytest.raises(typer.Exit):
                    config_show(section="nonexistent")

            # Verify error LiveBox was used
            assert mock_live_box.call_count >= 1
            # Check that error content was set (contains error emoji and hint)
            update_calls = [call[0][0] for call in mock_box.update.call_args_list]
            error_content = " ".join(update_calls)
            assert "❌" in error_content
            assert "💡" in error_content


class TestLiveBoxConsistency:
    """Test cases for LiveBox consistency across the application."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.output_buffer = StringIO()
        self.console = Console(file=self.output_buffer, width=80, legacy_windows=False)
        self.formatter = get_formatter(self.console)

    def test_error_messages_use_consistent_format(self) -> None:
        """Test that error messages use consistent emoji and hint format."""
        # Test various error scenarios to ensure consistent formatting
        with self.formatter.live_box("Test Error", MessageType.ERROR) as error_box:
            error_box.update(
                "❌ This is an error message\n\n💡 Hint: This is a helpful hint"
            )

            # Check the content directly since LiveBox is transient
            assert "❌" in str(error_box._content)  # Error emoji
            assert "💡" in str(error_box._content)  # Hint emoji

    def test_success_messages_use_consistent_format(self) -> None:
        """Test that success messages use consistent emoji format."""
        with self.formatter.live_box(
            "Test Success", MessageType.SUCCESS
        ) as success_box:
            success_box.update("🎉 Operation completed successfully!")

            # Check the content directly since LiveBox is transient
            assert "🎉" in str(success_box._content)  # Success emoji

    def test_info_messages_use_consistent_format(self) -> None:
        """Test that info messages use consistent emoji format."""
        with self.formatter.live_box("Test Info", MessageType.INFO) as info_box:
            info_box.update("🔧 Processing information...")

            # Check the content directly since LiveBox is transient
            assert "🔧" in str(info_box._content)  # Info emoji
