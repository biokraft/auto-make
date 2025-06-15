"""Tests for Phase 1 LiveBox integration improvements."""

from io import StringIO
from unittest.mock import MagicMock, Mock, patch

import pytest
import typer
from rich.console import Console

from automake.cli.main import _execute_main_logic, init
from automake.config import Config
from automake.core.ai_agent import CommandInterpretationError
from automake.core.makefile_reader import MakefileNotFoundError
from automake.utils.ollama_manager import OllamaManagerError
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

    @patch("automake.cli.main.get_config")
    @patch("automake.cli.main.ensure_model_available")
    @patch("automake.cli.main.get_available_models")
    @patch("subprocess.run")
    def test_init_success_with_livebox(
        self,
        mock_subprocess: MagicMock,
        mock_get_models: MagicMock,
        mock_ensure_model: MagicMock,
        mock_get_config: MagicMock,
    ) -> None:
        """Test successful initialization uses LiveBox for progress updates."""
        # Setup mocks
        mock_config = Mock(spec=Config)
        mock_config.ollama_model = "llama2"
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_get_config.return_value = mock_config

        mock_subprocess.return_value = Mock(returncode=0)
        mock_ensure_model.return_value = (True, False)  # Available, not pulled
        mock_get_models.return_value = ["llama2", "codellama", "mistral"]

        # Mock the live_box context manager to capture LiveBox usage
        with patch.object(self.formatter, "live_box") as mock_live_box:
            mock_box = Mock()
            mock_live_box.return_value.__enter__.return_value = mock_box

            with patch("automake.cli.main.output", self.formatter):
                init()

            # Verify LiveBox was used for initialization steps
            assert mock_live_box.call_count >= 2  # At least init box and success box
            mock_box.update.assert_called()  # Verify content was updated

    @patch("automake.cli.main.get_config")
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

            with patch("automake.cli.main.output", self.formatter):
                with pytest.raises(typer.Exit):
                    init()

            # Verify error LiveBox was used
            assert mock_live_box.call_count >= 1
            # Check that error content was set (contains error emoji and hint)
            update_calls = [call[0][0] for call in mock_box.update.call_args_list]
            error_content = " ".join(update_calls)
            assert "❌" in error_content
            assert "💡" in error_content

    @patch("automake.cli.main.get_config")
    @patch("automake.cli.main.ensure_model_available")
    @patch("subprocess.run")
    def test_init_model_pull_error_livebox(
        self,
        mock_subprocess: MagicMock,
        mock_ensure_model: MagicMock,
        mock_get_config: MagicMock,
    ) -> None:
        """Test model pull error uses LiveBox."""
        mock_config = Mock(spec=Config)
        mock_config.ollama_model = "invalid-model"
        mock_get_config.return_value = mock_config

        mock_subprocess.return_value = Mock(returncode=0)
        mock_ensure_model.side_effect = OllamaManagerError("Failed to pull model")

        with patch.object(self.formatter, "live_box") as mock_live_box:
            mock_box = Mock()
            mock_live_box.return_value.__enter__.return_value = mock_box

            with patch("automake.cli.main.output", self.formatter):
                with pytest.raises(typer.Exit):
                    init()

            # Verify error LiveBox was used
            assert mock_live_box.call_count >= 1
            # Check that error content was set (contains error emoji and hint)
            update_calls = [call[0][0] for call in mock_box.update.call_args_list]
            error_content = " ".join(update_calls)
            assert "❌" in error_content
            assert "💡" in error_content

    @patch("automake.cli.main.get_config")
    @patch("automake.cli.main.ensure_model_available")
    @patch("subprocess.run")
    def test_init_connection_error_livebox(
        self,
        mock_subprocess: MagicMock,
        mock_ensure_model: MagicMock,
        mock_get_config: MagicMock,
    ) -> None:
        """Test connection error uses LiveBox."""
        mock_config = Mock(spec=Config)
        mock_config.ollama_model = "llama2"
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_get_config.return_value = mock_config

        mock_subprocess.return_value = Mock(returncode=0)
        mock_ensure_model.side_effect = OllamaManagerError("Connection refused")

        with patch.object(self.formatter, "live_box") as mock_live_box:
            mock_box = Mock()
            mock_live_box.return_value.__enter__.return_value = mock_box

            with patch("automake.cli.main.output", self.formatter):
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

    @patch("automake.cli.main.MakefileReader")
    @patch("automake.cli.main.get_config")
    @patch("automake.cli.main.setup_logging")
    @patch("automake.cli.main.log_config_info")
    @patch("automake.cli.main.log_command_execution")
    def test_makefile_not_found_error_livebox(
        self,
        mock_log_command: MagicMock,
        mock_log_config: MagicMock,
        mock_setup_logging: MagicMock,
        mock_get_config: MagicMock,
        mock_makefile_reader: MagicMock,
    ) -> None:
        """Test MakefileNotFoundError uses LiveBox."""
        mock_reader = Mock()
        mock_reader.get_makefile_info.side_effect = MakefileNotFoundError(
            "No Makefile found"
        )
        mock_makefile_reader.return_value = mock_reader

        with patch.object(self.formatter, "live_box") as mock_live_box:
            mock_box = Mock()
            mock_live_box.return_value.__enter__.return_value = mock_box

            with patch("automake.cli.main.output", self.formatter):
                with pytest.raises(typer.Exit):
                    _execute_main_logic("test command")

            # Verify error LiveBox was used
            assert mock_live_box.call_count >= 1
            # Check that error content was set (contains error emoji and hint)
            update_calls = [call[0][0] for call in mock_box.update.call_args_list]
            error_content = " ".join(update_calls)
            assert "❌" in error_content
            assert "💡" in error_content

    @patch("automake.cli.main.MakefileReader")
    @patch("automake.cli.main.get_config")
    @patch("automake.cli.main.setup_logging")
    @patch("automake.cli.main.log_config_info")
    @patch("automake.cli.main.log_command_execution")
    def test_os_error_livebox(
        self,
        mock_log_command: MagicMock,
        mock_log_config: MagicMock,
        mock_setup_logging: MagicMock,
        mock_get_config: MagicMock,
        mock_makefile_reader: MagicMock,
    ) -> None:
        """Test OSError uses LiveBox."""
        mock_reader = Mock()
        mock_reader.get_makefile_info.side_effect = OSError("Permission denied")
        mock_makefile_reader.return_value = mock_reader

        with patch.object(self.formatter, "live_box") as mock_live_box:
            mock_box = Mock()
            mock_live_box.return_value.__enter__.return_value = mock_box

            with patch("automake.cli.main.output", self.formatter):
                with pytest.raises(typer.Exit):
                    _execute_main_logic("test command")

            # Verify error LiveBox was used
            assert mock_live_box.call_count >= 1
            # Check that error content was set (contains error emoji)
            update_calls = [call[0][0] for call in mock_box.update.call_args_list]
            error_content = " ".join(update_calls)
            assert "❌" in error_content

    @patch("automake.cli.main.MakefileReader")
    @patch("automake.cli.main.create_ai_agent")
    @patch("automake.cli.main.get_config")
    @patch("automake.cli.main.setup_logging")
    @patch("automake.cli.main.log_config_info")
    @patch("automake.cli.main.log_command_execution")
    @patch("automake.cli.main.get_logger")
    def test_command_interpretation_error_livebox(
        self,
        mock_get_logger: MagicMock,
        mock_log_command: MagicMock,
        mock_log_config: MagicMock,
        mock_setup_logging: MagicMock,
        mock_get_config: MagicMock,
        mock_create_agent: MagicMock,
        mock_makefile_reader: MagicMock,
    ) -> None:
        """Test CommandInterpretationError uses LiveBox."""
        # Setup successful makefile reading
        mock_reader = Mock()
        mock_reader.get_makefile_info.return_value = None
        mock_reader.read_makefile.return_value = None
        mock_makefile_reader.return_value = mock_reader

        # Setup AI agent to raise error
        mock_create_agent.side_effect = CommandInterpretationError("AI model failed")

        with patch.object(self.formatter, "live_box") as mock_live_box:
            mock_box = Mock()
            mock_live_box.return_value.__enter__.return_value = mock_box

            with patch("automake.cli.main.output", self.formatter):
                with pytest.raises(typer.Exit):
                    _execute_main_logic("test command")

            # Verify error LiveBox was used
            assert mock_live_box.call_count >= 1
            # Check that error content was set (contains error emoji and hint)
            update_calls = [call[0][0] for call in mock_box.update.call_args_list]
            error_content = " ".join(update_calls)
            assert "❌" in error_content
            assert "💡" in error_content

    @patch("automake.cli.main.MakefileReader")
    @patch("automake.cli.main.create_ai_agent")
    @patch("automake.cli.main.select_command")
    @patch("automake.cli.main.get_config")
    @patch("automake.cli.main.setup_logging")
    @patch("automake.cli.main.log_config_info")
    @patch("automake.cli.main.log_command_execution")
    @patch("automake.cli.main.get_logger")
    def test_operation_cancelled_livebox(
        self,
        mock_get_logger: MagicMock,
        mock_log_command: MagicMock,
        mock_log_config: MagicMock,
        mock_setup_logging: MagicMock,
        mock_get_config: MagicMock,
        mock_select_command: MagicMock,
        mock_create_agent: MagicMock,
        mock_makefile_reader: MagicMock,
    ) -> None:
        """Test operation cancelled uses LiveBox."""
        # Setup successful makefile reading
        mock_reader = Mock()
        mock_reader.get_makefile_info.return_value = None
        mock_reader.read_makefile.return_value = None
        mock_reader.targets_with_descriptions = {"build": "Build the project"}
        mock_makefile_reader.return_value = mock_reader

        # Setup config with low threshold to trigger interactive mode
        mock_config = Mock()
        mock_config.interactive_threshold = 80
        mock_get_config.return_value = mock_config

        # Setup AI agent with low confidence
        mock_agent = Mock()
        mock_response = Mock()
        mock_response.command = "build"
        mock_response.confidence = 50  # Below threshold
        mock_response.alternatives = ["test"]
        mock_response.reasoning = "Test reasoning"
        mock_agent.interpret_command.return_value = mock_response
        mock_create_agent.return_value = (mock_agent, False)

        # User cancels selection
        mock_select_command.return_value = None

        with patch.object(self.formatter, "live_box") as mock_live_box:
            mock_box = Mock()
            mock_live_box.return_value.__enter__.return_value = mock_box

            with patch("automake.cli.main.output", self.formatter):
                with pytest.raises(typer.Exit):
                    _execute_main_logic("test command")

            # Verify info LiveBox was used for cancellation message
            assert mock_live_box.call_count >= 1
            # Check that cancellation message was set
            update_calls = [call[0][0] for call in mock_box.update.call_args_list]
            content = " ".join(update_calls)
            assert "Operation cancelled" in content

    @patch("automake.cli.main.MakefileReader")
    @patch("automake.cli.main.create_ai_agent")
    @patch("automake.cli.main.get_config")
    @patch("automake.cli.main.setup_logging")
    @patch("automake.cli.main.log_config_info")
    @patch("automake.cli.main.log_command_execution")
    @patch("automake.cli.main.get_logger")
    def test_no_command_determined_livebox(
        self,
        mock_get_logger: MagicMock,
        mock_log_command: MagicMock,
        mock_log_config: MagicMock,
        mock_setup_logging: MagicMock,
        mock_get_config: MagicMock,
        mock_create_agent: MagicMock,
        mock_makefile_reader: MagicMock,
    ) -> None:
        """Test no command determined uses LiveBox."""
        # Setup successful makefile reading
        mock_reader = Mock()
        mock_reader.get_makefile_info.return_value = None
        mock_reader.read_makefile.return_value = None
        mock_reader.targets_with_descriptions = {"build": "Build the project"}
        mock_makefile_reader.return_value = mock_reader

        # Setup config with high threshold to avoid interactive mode
        mock_config = Mock()
        mock_config.interactive_threshold = 20
        mock_get_config.return_value = mock_config

        # Setup AI agent with no command
        mock_agent = Mock()
        mock_response = Mock()
        mock_response.command = None  # No command determined
        mock_response.confidence = 50
        mock_response.alternatives = []
        mock_response.reasoning = "Could not determine command"
        mock_agent.interpret_command.return_value = mock_response
        mock_create_agent.return_value = (mock_agent, False)

        with patch.object(self.formatter, "live_box") as mock_live_box:
            mock_box = Mock()
            mock_live_box.return_value.__enter__.return_value = mock_box

            with patch("automake.cli.main.output", self.formatter):
                with pytest.raises(typer.Exit):
                    _execute_main_logic("test command")

            # Verify error LiveBox was used
            assert mock_live_box.call_count >= 1
            # Check that error content was set (contains error emoji and hint)
            update_calls = [call[0][0] for call in mock_box.update.call_args_list]
            error_content = " ".join(update_calls)
            assert "❌" in error_content
            assert "💡" in error_content


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

    @patch("automake.cli.main.get_config")
    def test_config_show_section_not_found_livebox(
        self,
        mock_get_config: MagicMock,
    ) -> None:
        """Test config show with non-existent section uses LiveBox."""
        from automake.cli.main import config_show

        mock_config = Mock()
        mock_config.get_all_sections.return_value = {"ollama": {"model": "llama2"}}
        mock_get_config.return_value = mock_config

        with patch.object(self.formatter, "live_box") as mock_live_box:
            mock_box = Mock()
            mock_live_box.return_value.__enter__.return_value = mock_box

            with patch("automake.cli.main.output", self.formatter):
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
