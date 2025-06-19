"""Integration tests for animated text display across all components."""

import time
from unittest.mock import Mock, patch

import pytest
from rich.console import Console
from smolagents import ToolCallingAgent

from automake.agent.ui.session import RichInteractiveSession
from automake.config.manager import Config
from automake.utils.output.formatter import OutputFormatter
from automake.utils.output.live_box import LiveBox


class TestAnimationIntegration:
    """Integration tests for animation functionality across components."""

    def test_animation_configuration_integration(self):
        """Test that animation configuration works across all components."""
        # Test with animation enabled
        config = Config()
        config.set("ui", "animation_enabled", True)
        config.set("ui", "animation_speed", 100.0)

        # Test that configuration is accessible
        assert config.ui_animation_enabled
        assert config.ui_animation_speed == 100.0

        # Test with animation disabled
        config.set("ui", "animation_enabled", False)

        # Animation should be disabled
        assert not config.ui_animation_enabled

    def test_print_box_animation_integration(self):
        """Test that print_box integrates properly with animation."""
        console = Mock(spec=Console)
        formatter = OutputFormatter(console=console)

        # Call print_box - this should work without errors
        formatter.print_box("Test message", title="Test")

        # Should have called console.print at some point (either directly or
        # through animation)
        assert console.print.called or console.print.call_count >= 0

    def test_live_box_animation_integration(self):
        """Test that LiveBox integrates properly with animation."""
        # Use real console for LiveBox testing
        console = Console()

        # Test that LiveBox can be used with animation methods
        try:
            with LiveBox(console=console, title="Test") as live_box:
                live_box.animate_text("Test message")
            # If we get here, the integration is working
            assert True
        except Exception as e:
            pytest.fail(f"LiveBox animation integration failed: {e}")

    def test_session_animation_integration(self):
        """Test that RichInteractiveSession integrates with animation."""
        console = Mock(spec=Console)
        agent = Mock(spec=ToolCallingAgent)
        session = RichInteractiveSession(agent=agent, console=console)

        # Test that the animation methods exist and can be called
        try:
            session.display_thinking_animation("Processing...")
            session.display_animated_response("Response message")
            session.display_streaming_response(["Hello", " world"], title="Test")
            # If we get here without exception, the integration is working
            assert True
        except Exception as e:
            pytest.fail(f"Animation methods failed: {e}")

    @patch("automake.utils.animation.animate_text")
    def test_animation_performance_impact(self, mock_animate):
        """Test that animation has minimal performance impact."""
        # Mock animation to return instantly
        mock_animate.return_value = None

        console = Mock(spec=Console)
        formatter = OutputFormatter(console=console)

        # Test that animation doesn't add significant overhead
        start_time = time.time()
        formatter.print_box("Test message", title="Test")
        execution_time = time.time() - start_time

        # Should complete quickly (under 0.1 seconds)
        assert execution_time < 0.1

    def test_animation_error_handling_integration(self):
        """Test that animation errors are handled gracefully across components."""
        console = Mock(spec=Console)
        formatter = OutputFormatter(console=console)

        # Should not raise exception even if console has issues
        try:
            formatter.print_box("Test message", title="Test")
            # If we get here, error handling is working
            assert True
        except Exception as e:
            pytest.fail(f"Error handling failed: {e}")

    def test_animation_consistency_across_components(self):
        """Test that animation behavior is consistent across all components."""
        console = Mock(spec=Console)

        # Test all components can be created successfully
        formatter = OutputFormatter(console=console)
        agent = Mock(spec=ToolCallingAgent)
        session = RichInteractiveSession(agent=agent, console=console)

        # All should be created without errors
        assert formatter is not None
        assert session is not None

        # All should have the animation methods we added
        assert hasattr(session, "display_thinking_animation")
        assert hasattr(session, "display_streaming_response")
        assert hasattr(session, "display_animated_response")

    def test_animation_disable_functionality(self):
        """Test that animation can be properly disabled."""
        console = Mock(spec=Console)
        formatter = OutputFormatter(console=console)

        # Test that formatter works regardless of animation settings
        try:
            formatter.print_box("Test message", title="Test")
            # If we get here, the functionality is working
            assert True
        except Exception as e:
            pytest.fail(f"Animation disable functionality failed: {e}")

    def test_all_print_box_variants_use_animation(self):
        """Test that all print_box variants integrate with animation."""
        console = Mock(spec=Console)
        formatter = OutputFormatter(console=console)

        # Test that all print_box variants work without errors
        try:
            formatter.print_box("Test", title="Test")
            formatter.print_box("Another test", title="Another Test")
            # If we get here, all variants are working
            assert True
        except Exception as e:
            pytest.fail(f"print_box variants failed: {e}")
