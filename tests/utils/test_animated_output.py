"""Tests for animated output functionality."""

from unittest.mock import Mock, patch

from rich.console import Console
from rich.panel import Panel

from automake.utils.output.formatter import OutputFormatter
from automake.utils.output.types import MessageType


class TestAnimatedPrintBox:
    """Test animated print_box functionality."""

    @patch("automake.utils.output.formatter.animate_text")
    @patch("automake.utils.output.formatter._get_animation_config")
    def test_print_box_with_animation_enabled(self, mock_get_config, mock_animate_text):
        """Test print_box uses animation when enabled in config."""
        # Mock the animation config directly to bypass CI detection
        mock_get_config.return_value = (True, 50.0)

        console = Mock(spec=Console)
        formatter = OutputFormatter(console=console)

        formatter.print_box("Test message", MessageType.INFO, "Test Title")

        # Should call animate_text instead of console.print
        mock_animate_text.assert_called_once()
        console.print.assert_not_called()

        # Check animate_text was called with correct parameters
        call_args = mock_animate_text.call_args
        assert call_args[0][0] == console  # console parameter
        assert call_args[0][1] == "Test message"  # text parameter
        assert callable(call_args[0][2])  # panel_factory parameter
        assert call_args[1]["speed"] == 50.0  # speed parameter
        assert call_args[1]["enabled"] is True  # enabled parameter

    @patch("automake.utils.output.formatter.animate_text")
    @patch("automake.utils.output.formatter._get_animation_config")
    def test_print_box_with_animation_disabled(
        self, mock_get_config, mock_animate_text
    ):
        """Test print_box uses direct print when animation disabled."""
        # Mock the animation config directly to bypass CI detection
        mock_get_config.return_value = (False, 50.0)

        console = Mock(spec=Console)
        formatter = OutputFormatter(console=console)

        formatter.print_box("Test message", MessageType.INFO, "Test Title")

        # Should call animate_text with enabled=False
        mock_animate_text.assert_called_once()

        # Check animate_text was called with correct parameters
        call_args = mock_animate_text.call_args
        assert call_args[1]["enabled"] is False

    @patch("automake.utils.output.formatter.animate_text")
    @patch("automake.utils.output.formatter._get_animation_config")
    def test_print_box_panel_factory(self, mock_get_config, mock_animate_text):
        """Test that panel_factory creates correct panel."""
        # Mock the animation config directly to bypass CI detection
        mock_get_config.return_value = (True, 75.0)

        console = Mock(spec=Console)
        formatter = OutputFormatter(console=console)

        formatter.print_box("Test message", MessageType.ERROR, "Error Title")

        # Get the panel_factory function that was passed to animate_text
        call_args = mock_animate_text.call_args
        panel_factory = call_args[0][2]

        # Test the panel factory creates correct panel
        panel = panel_factory("Sample text")
        assert isinstance(panel, Panel)
        assert panel.title == "Error Title"
        assert panel.title_align == "left"
        assert panel.border_style == "red"  # Error message type style

    @patch("automake.utils.output.formatter.animate_text")
    @patch("automake.utils.output.formatter._get_animation_config")
    def test_print_error_box_animated(self, mock_get_config, mock_animate_text):
        """Test print_error_box uses animation."""
        # Mock the animation config directly to bypass CI detection
        mock_get_config.return_value = (True, 50.0)

        console = Mock(spec=Console)
        formatter = OutputFormatter(console=console)

        formatter.print_error_box("Error message", "Hint text")

        # Should call animate_text for the error box
        mock_animate_text.assert_called_once()

        # Should also print the hint (not animated)
        console.print.assert_called_once()

    @patch("automake.utils.output.formatter.animate_text")
    @patch("automake.utils.output.formatter._get_animation_config")
    def test_print_status_animated(self, mock_get_config, mock_animate_text):
        """Test print_status uses animation."""
        # Mock the animation config directly to bypass CI detection
        mock_get_config.return_value = (True, 50.0)

        console = Mock(spec=Console)
        formatter = OutputFormatter(console=console)

        formatter.print_status("Status message", MessageType.SUCCESS, "Success")

        # Should call animate_text
        mock_animate_text.assert_called_once()

    @patch("automake.utils.output.formatter.animate_text")
    @patch("automake.utils.output.formatter._get_animation_config")
    def test_config_error_fallback(self, mock_get_config, mock_animate_text):
        """Test fallback behavior when config is unavailable."""
        # Setup mock config to raise an exception
        mock_get_config.side_effect = Exception("Config error")

        console = Mock(spec=Console)
        formatter = OutputFormatter(console=console)

        formatter.print_box("Test message", MessageType.INFO, "Test Title")

        # Should fallback to direct console.print
        console.print.assert_called_once()
        mock_animate_text.assert_not_called()


class TestConvenienceFunctions:
    """Test animated convenience functions."""

    @patch("automake.utils.output.formatter.get_formatter")
    def test_print_box_convenience_function(self, mock_get_formatter):
        """Test that print_box convenience function uses animation."""
        from automake.utils.output import print_box

        mock_formatter = Mock()
        mock_get_formatter.return_value = mock_formatter

        print_box("Test message", MessageType.INFO, "Test Title")

        # Should call the formatter's print_box method
        mock_formatter.print_box.assert_called_once_with(
            "Test message", MessageType.INFO, "Test Title"
        )
