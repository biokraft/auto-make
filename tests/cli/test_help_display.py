"""Tests for the help display functionality."""

from io import StringIO
from unittest.mock import Mock, patch

from rich.console import Console

from automake.cli.display.help import (
    print_help_with_ascii,
    print_welcome,
    read_ascii_art,
)


class TestPrintWelcome:
    """Test cases for the print_welcome function."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.output_buffer = StringIO()
        self.console = Console(file=self.output_buffer, width=80, legacy_windows=False)

    def get_output(self) -> str:
        """Get the captured output."""
        return self.output_buffer.getvalue()

    @patch("automake.cli.display.help.get_formatter")
    @patch("automake.cli.display.help.read_ascii_art")
    def test_print_welcome_with_ascii_art(
        self, mock_read_ascii_art, mock_get_formatter
    ):
        """Test print_welcome with ASCII art present."""
        # Mock ASCII art content
        mock_ascii_art = "  ___  \n /   \\ \n \\___/ "
        mock_read_ascii_art.return_value = mock_ascii_art

        # Mock formatter
        mock_formatter = Mock()
        mock_get_formatter.return_value = mock_formatter

        print_welcome()

        # Verify ASCII art was displayed with version info
        mock_formatter.print_rainbow_ascii_art.assert_called_once()
        call_args = mock_formatter.print_rainbow_ascii_art.call_args[0][0]
        assert mock_ascii_art in call_args
        assert "version" in call_args

        # Verify both boxes were printed
        assert mock_formatter.print_box.call_count == 2

        # Check Welcome box
        welcome_call = mock_formatter.print_box.call_args_list[0]
        assert (
            'Run "automake help" for detailed usage information.' in welcome_call[0][0]
        )
        assert welcome_call[0][2] == "Welcome"

        # Check First time user box
        first_time_call = mock_formatter.print_box.call_args_list[1]
        first_time_content = first_time_call[0][0]
        assert "Set your preferred model (default: qwen3:0.6b)" in first_time_content
        assert "automake config set ollama.model <model_name>" in first_time_content
        assert "Initialize and fetch the model:" in first_time_content
        assert "automake init" in first_time_content
        assert first_time_call[0][2] == "First time user?"

    @patch("automake.cli.display.help.get_formatter")
    @patch("automake.cli.display.help.read_ascii_art")
    def test_print_welcome_without_ascii_art(
        self, mock_read_ascii_art, mock_get_formatter
    ):
        """Test print_welcome when ASCII art is not available."""
        # Mock no ASCII art
        mock_read_ascii_art.return_value = ""

        # Mock formatter
        mock_formatter = Mock()
        mock_get_formatter.return_value = mock_formatter

        print_welcome()

        # Verify ASCII art was not displayed
        mock_formatter.print_rainbow_ascii_art.assert_not_called()

        # Verify both boxes were still printed
        assert mock_formatter.print_box.call_count == 2

    def test_first_time_user_content_structure(self):
        """Test that the first-time user content has the correct structure."""
        with patch("automake.cli.display.help.get_formatter") as mock_get_formatter:
            mock_formatter = Mock()
            mock_get_formatter.return_value = mock_formatter

            with patch("automake.cli.display.help.read_ascii_art", return_value=""):
                print_welcome()

            # Get the first-time user content
            first_time_call = mock_formatter.print_box.call_args_list[1]
            content = first_time_call[0][0]

            # Verify numbered steps structure
            assert "1. Set your preferred model" in content
            assert "2. Initialize and fetch the model:" in content

            # Verify specific commands are present
            assert "automake config set ollama.model <model_name>" in content
            assert "automake init" in content

            # Verify default model is mentioned
            assert "qwen3:0.6b" in content

    @patch("automake.cli.display.help.get_formatter")
    @patch("automake.cli.display.help.read_ascii_art")
    def test_print_welcome_message_types(self, mock_read_ascii_art, mock_get_formatter):
        """Test that print_welcome uses correct message types."""
        mock_read_ascii_art.return_value = ""
        mock_formatter = Mock()
        mock_get_formatter.return_value = mock_formatter

        from automake.utils.output import MessageType

        print_welcome()

        # Both boxes should use INFO message type
        for call in mock_formatter.print_box.call_args_list:
            assert call[0][1] == MessageType.INFO


class TestReadAsciiArt:
    """Test cases for the read_ascii_art function."""

    def test_read_ascii_art_exception_handling(self):
        """Test that read_ascii_art handles exceptions gracefully."""
        with patch("automake.cli.display.help.Path") as mock_path:
            # Mock path to raise an exception
            mock_path.side_effect = Exception("File system error")

            result = read_ascii_art()

            assert result == ""

    def test_read_ascii_art_returns_empty_when_no_files_exist(self):
        """Test that read_ascii_art returns empty string when no ASCII art files exist."""  # noqa: E501
        # This is a simple integration test that doesn't mock the complex path logic
        # but verifies the function handles missing files gracefully
        with patch("automake.cli.display.help.Path") as mock_path_class:
            # Create a mock file path
            mock_file_path = Mock()

            # Create mock for resources path that doesn't exist
            mock_resources_file = Mock()
            mock_resources_file.exists.return_value = False

            # Create mock for CLI path that doesn't exist
            mock_cli_file = Mock()
            mock_cli_file.exists.return_value = False

            # Mock the path construction
            def mock_path_construction(*args):
                if "resources" in str(args):
                    return mock_resources_file
                else:
                    return mock_cli_file

            # Setup the path hierarchy
            mock_parent = Mock()
            mock_parent.__truediv__ = Mock(side_effect=mock_path_construction)
            mock_parent.parent = Mock()
            mock_parent.parent.__truediv__ = Mock(side_effect=mock_path_construction)
            mock_parent.parent.parent = Mock()
            mock_parent.parent.parent.__truediv__ = Mock(
                side_effect=mock_path_construction
            )

            mock_file_path.parent = mock_parent
            mock_path_class.return_value = mock_file_path

            result = read_ascii_art()

            assert result == ""


class TestPrintHelpWithAscii:
    """Test cases for the print_help_with_ascii function."""

    @patch("automake.cli.display.help.get_formatter")
    @patch("automake.cli.display.help.read_ascii_art")
    def test_print_help_with_ascii_basic(self, mock_read_ascii_art, mock_get_formatter):
        """Test basic functionality of print_help_with_ascii."""
        mock_read_ascii_art.return_value = "ASCII ART"
        mock_formatter = Mock()
        mock_get_formatter.return_value = mock_formatter

        print_help_with_ascii()

        # Should display ASCII art
        mock_formatter.print_rainbow_ascii_art.assert_called_once_with(
            "ASCII ART", duration=0
        )

        # Should print multiple help boxes
        assert (
            mock_formatter.print_box.call_count >= 5
        )  # At least Usage, Description, Examples, Commands, etc.

    @patch("automake.cli.display.help.get_formatter")
    @patch("automake.cli.display.help.read_ascii_art")
    def test_print_help_with_author_credit(
        self, mock_read_ascii_art, mock_get_formatter
    ):
        """Test print_help_with_ascii with author credit."""
        mock_read_ascii_art.return_value = "ASCII ART"
        mock_formatter = Mock()
        mock_get_formatter.return_value = mock_formatter

        print_help_with_ascii(show_author=True)

        # Should display ASCII art with author credit
        call_args = mock_formatter.print_rainbow_ascii_art.call_args[0][0]
        assert "ASCII ART" in call_args
        assert "by Seán Baufeld" in call_args
