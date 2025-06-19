"""Tests for animation utilities."""

from unittest.mock import Mock, patch

from rich.console import Console
from rich.panel import Panel

from automake.utils.animation import TypewriterAnimator, animate_text


class TestTypewriterAnimator:
    """Test the TypewriterAnimator class."""

    def test_init_with_defaults(self):
        """Test TypewriterAnimator initialization with default values."""
        animator = TypewriterAnimator()
        assert animator.speed == 50.0
        assert animator.enabled is True

    def test_init_with_custom_values(self):
        """Test TypewriterAnimator initialization with custom values."""
        animator = TypewriterAnimator(speed=100.0, enabled=False)
        assert animator.speed == 100.0
        assert animator.enabled is False

    def test_calculate_delay(self):
        """Test delay calculation based on speed."""
        animator = TypewriterAnimator(speed=50.0)
        # At 50 chars/sec, delay should be 1/50 = 0.02 seconds
        assert animator._calculate_delay() == 0.02

        animator = TypewriterAnimator(speed=100.0)
        # At 100 chars/sec, delay should be 1/100 = 0.01 seconds
        assert animator._calculate_delay() == 0.01

    @patch("time.sleep")
    def test_animate_disabled(self, mock_sleep):
        """Test that animation is skipped when disabled."""
        console = Mock(spec=Console)
        animator = TypewriterAnimator(enabled=False)

        def panel_factory(text):
            return Panel(text, title="Test")

        animator.animate(console, "Hello World", panel_factory)

        # Should print final text immediately without animation
        console.print.assert_called_once()
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_animate_enabled(self, mock_sleep):
        """Test that animation works when enabled."""
        console = Mock(spec=Console)
        animator = TypewriterAnimator(speed=50.0, enabled=True)

        def panel_factory(text):
            return Panel(text, title="Test")

        text = "Hi"
        animator.animate(console, text, panel_factory)

        # Should have called print for each character + final
        assert console.print.call_count == len(text) + 1
        # Should have slept between characters
        assert mock_sleep.call_count == len(text)

    @patch("time.sleep")
    def test_animate_empty_string(self, mock_sleep):
        """Test animation with empty string."""
        console = Mock(spec=Console)
        animator = TypewriterAnimator()

        def panel_factory(text):
            return Panel(text, title="Test")

        animator.animate(console, "", panel_factory)

        # Should print once (empty panel)
        console.print.assert_called_once()
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_animate_single_character(self, mock_sleep):
        """Test animation with single character."""
        console = Mock(spec=Console)
        animator = TypewriterAnimator()

        def panel_factory(text):
            return Panel(text, title="Test")

        animator.animate(console, "A", panel_factory)

        # Should print twice (partial + final)
        assert console.print.call_count == 2
        mock_sleep.assert_called_once()

    @patch("time.sleep")
    def test_animate_with_keyboard_interrupt(self, mock_sleep):
        """Test that KeyboardInterrupt is handled gracefully."""
        console = Mock(spec=Console)
        animator = TypewriterAnimator()

        def panel_factory(text):
            return Panel(text, title="Test")

        # Make sleep raise KeyboardInterrupt on first call
        mock_sleep.side_effect = KeyboardInterrupt()

        # Should not raise exception
        animator.animate(console, "Hello", panel_factory)

        # Should still print the final text
        console.print.assert_called()


class TestAnimateTextFunction:
    """Test the animate_text convenience function."""

    @patch("automake.utils.animation.TypewriterAnimator")
    def test_animate_text_calls_animator(self, mock_animator_class):
        """Test that animate_text creates and uses TypewriterAnimator."""
        mock_animator = Mock()
        mock_animator_class.return_value = mock_animator

        console = Mock(spec=Console)
        text = "Test text"
        panel_factory = Mock()

        animate_text(console, text, panel_factory, speed=75.0, enabled=False)

        # Should create animator with correct parameters
        mock_animator_class.assert_called_once_with(speed=75.0, enabled=False)
        # Should call animate on the animator
        mock_animator.animate.assert_called_once_with(console, text, panel_factory)

    @patch("automake.utils.animation.TypewriterAnimator")
    def test_animate_text_default_parameters(self, mock_animator_class):
        """Test animate_text with default parameters."""
        mock_animator = Mock()
        mock_animator_class.return_value = mock_animator

        console = Mock(spec=Console)
        text = "Test text"
        panel_factory = Mock()

        animate_text(console, text, panel_factory)

        # Should create animator with default parameters
        mock_animator_class.assert_called_once_with(speed=50.0, enabled=True)
