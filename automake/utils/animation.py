"""Animation utilities for typewriter-style text display.

This module provides utilities for creating typewriter-style animations
for text content in rich panels and boxes.
"""

import time
from collections.abc import Callable

from rich.console import Console
from rich.panel import Panel


class TypewriterAnimator:
    """Handles typewriter-style character-by-character text animation."""

    def __init__(self, speed: float = 50.0, enabled: bool = True) -> None:
        """Initialize the TypewriterAnimator.

        Args:
            speed: Animation speed in characters per second
            enabled: Whether animation is enabled
        """
        self.speed = speed
        self.enabled = enabled

    def _calculate_delay(self) -> float:
        """Calculate delay between characters based on speed.

        Returns:
            Delay in seconds between each character
        """
        return 1.0 / self.speed

    def animate(
        self,
        console: Console,
        text: str,
        panel_factory: Callable[[str], Panel],
    ) -> None:
        """Animate text character by character in a panel.

        Args:
            console: Rich console instance for output
            text: Text to animate
            panel_factory: Function that creates a Panel from text
        """
        if not self.enabled or not text:
            # If animation is disabled or text is empty, just print final result
            console.print(panel_factory(text))
            return

        delay = self._calculate_delay()

        try:
            # Animate character by character
            for i in range(1, len(text) + 1):
                partial_text = text[:i]
                console.print(panel_factory(partial_text))
                time.sleep(delay)  # Sleep after each character

            # Print final complete text
            console.print(panel_factory(text))

        except KeyboardInterrupt:
            # If interrupted, still show the final text
            console.print(panel_factory(text))


def animate_text(
    console: Console,
    text: str,
    panel_factory: Callable[[str], Panel],
    speed: float = 50.0,
    enabled: bool = True,
) -> None:
    """Convenience function for animating text with typewriter effect.

    Args:
        console: Rich console instance for output
        text: Text to animate
        panel_factory: Function that creates a Panel from text
        speed: Animation speed in characters per second
        enabled: Whether animation is enabled
    """
    animator = TypewriterAnimator(speed=speed, enabled=enabled)
    animator.animate(console, text, panel_factory)
