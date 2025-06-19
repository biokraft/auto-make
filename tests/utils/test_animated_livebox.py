"""Tests for animated LiveBox functionality."""

import threading
from unittest.mock import Mock, patch

from rich.console import Console

from automake.utils.output.live_box import LiveBox


class TestAnimatedLiveBox:
    """Test animated LiveBox functionality."""

    @patch("automake.utils.output.live_box.animate_text")
    @patch("automake.config.manager.get_config")
    def test_animate_text_method_exists(self, mock_get_config, mock_animate_text):
        """Test that LiveBox has an animate_text method."""
        # Setup mock config
        mock_config = Mock()
        mock_config.ui_animation_enabled = True
        mock_config.ui_animation_speed = 50.0
        mock_get_config.return_value = mock_config

        console = Mock(spec=Console)
        live_box = LiveBox(console=console, title="Test")

        # Should have animate_text method
        assert hasattr(live_box, "animate_text")
        assert callable(live_box.animate_text)

    @patch("automake.utils.output.live_box.animate_text")
    @patch("automake.utils.output.live_box._get_animation_config")
    def test_animate_text_with_animation_enabled(
        self, mock_get_config, mock_animate_text
    ):
        """Test animate_text method when animation is enabled."""
        # Mock the animation config directly to bypass CI detection
        mock_get_config.return_value = (True, 75.0)

        console = Mock(spec=Console)
        live_box = LiveBox(console=console, title="Test")

        # Call animate_text
        live_box.animate_text("Test message")

        # Should call animate_text function with correct parameters
        mock_animate_text.assert_called_once()
        call_args = mock_animate_text.call_args

        # Check arguments
        assert call_args[0][0] == console  # console parameter
        assert call_args[0][1] == "Test message"  # text parameter
        assert callable(call_args[0][2])  # panel_factory parameter
        assert call_args[1]["speed"] == 75.0  # speed parameter
        assert call_args[1]["enabled"] is True  # enabled parameter

    @patch("automake.utils.output.live_box.animate_text")
    @patch("automake.utils.output.live_box._get_animation_config")
    def test_animate_text_with_animation_disabled(
        self, mock_get_config, mock_animate_text
    ):
        """Test animate_text method when animation is disabled."""
        # Mock the animation config directly to bypass CI detection
        mock_get_config.return_value = (False, 50.0)

        console = Mock(spec=Console)
        live_box = LiveBox(console=console, title="Test")

        # Call animate_text
        live_box.animate_text("Test message")

        # Should call animate_text with enabled=False
        mock_animate_text.assert_called_once()
        call_args = mock_animate_text.call_args
        assert call_args[1]["enabled"] is False

    @patch("automake.utils.output.live_box.animate_text")
    @patch("automake.utils.output.live_box._get_animation_config")
    def test_animate_text_panel_factory(self, mock_get_config, mock_animate_text):
        """Test that animate_text creates correct panel factory."""
        # Mock the animation config directly to bypass CI detection
        mock_get_config.return_value = (True, 50.0)

        console = Mock(spec=Console)
        live_box = LiveBox(console=console, title="Test Title", border_style="green")

        # Call animate_text
        live_box.animate_text("Test message")

        # Get the panel_factory function
        call_args = mock_animate_text.call_args
        panel_factory = call_args[0][2]

        # Test panel factory creates correct panel
        from rich.panel import Panel

        panel = panel_factory("Sample text")
        assert isinstance(panel, Panel)
        assert panel.title == "Test Title"
        assert panel.border_style == "green"

    @patch("automake.utils.output.live_box.animate_text")
    @patch("automake.utils.output.live_box._get_animation_config")
    def test_animate_text_thread_safety(self, mock_get_config, mock_animate_text):
        """Test that animate_text is thread-safe."""
        # Mock the animation config directly to bypass CI detection
        mock_get_config.return_value = (True, 50.0)

        console = Mock(spec=Console)
        live_box = LiveBox(console=console, title="Test")

        # Test concurrent calls don't interfere
        def animate_worker(message):
            live_box.animate_text(f"Message {message}")

        threads = []
        for i in range(3):
            thread = threading.Thread(target=animate_worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should have been called 3 times
        assert mock_animate_text.call_count == 3

    @patch("automake.utils.output.live_box.animate_text")
    @patch("automake.utils.output.live_box._get_animation_config")
    def test_animate_text_error_handling(self, mock_get_config, mock_animate_text):
        """Test animate_text handles errors gracefully."""
        # Setup mock config to raise exception
        mock_get_config.side_effect = Exception("Config error")

        console = Mock(spec=Console)
        live_box = LiveBox(console=console, title="Test")

        # Mock the update method to track fallback behavior
        live_box.update = Mock()

        # Should not raise exception
        live_box.animate_text("Test message")

        # Should not call animate_text if config fails
        mock_animate_text.assert_not_called()
        # Should call update as fallback
        live_box.update.assert_called_once_with("Test message")

    @patch("automake.utils.output.live_box.animate_text")
    @patch("automake.utils.output.live_box._get_animation_config")
    def test_update_method_compatibility(self, mock_get_config, mock_animate_text):
        """Test that existing update method still works."""
        # Mock the animation config directly to bypass CI detection
        mock_get_config.return_value = (True, 50.0)

        console = Mock(spec=Console)
        live_box = LiveBox(console=console, title="Test")

        # Mock the Live object and make it active
        live_box._live = Mock()
        live_box._is_active = True

        # Call existing update method
        live_box.update("Test content")

        # Should still work (update the live display)
        live_box._live.update.assert_called_once()

    @patch("automake.utils.output.live_box.animate_text")
    @patch("automake.utils.output.live_box._get_animation_config")
    def test_animate_text_with_custom_title(self, mock_get_config, mock_animate_text):
        """Test animate_text with custom title parameter."""
        # Mock the animation config directly to bypass CI detection
        mock_get_config.return_value = (True, 50.0)

        console = Mock(spec=Console)
        live_box = LiveBox(console=console, title="Default Title")

        # Call animate_text with custom title
        live_box.animate_text("Test message", title="Custom Title")

        # Get the panel_factory function
        call_args = mock_animate_text.call_args
        panel_factory = call_args[0][2]

        # Test panel factory uses custom title
        from rich.panel import Panel

        panel = panel_factory("Sample text")
        assert isinstance(panel, Panel)
        assert panel.title == "Custom Title"
