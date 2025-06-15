"""LiveBox component for real-time, updatable console output.

This module provides the LiveBox class for displaying streaming content
in a styled box that can be updated in real time.
"""

# TODO: Move LiveBox class from automake/utils/output.py
# TODO: Move any LiveBox-related helper functions
# TODO: Update imports in automake/utils/output/__init__.py

import threading
from typing import Any

from rich.console import Console, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.text import Text


class LiveBox:
    """A real-time, updatable box for displaying streaming content.

    This component provides a rich.live instance that can be updated in real time,
    styled as a box consistent with the existing print_box function. It supports
    streaming text content and other rich renderables with thread safety.
    """

    def __init__(
        self,
        console: Console,
        title: str = "Live Output",
        border_style: str = "blue",
        refresh_per_second: float = 4.0,
        transient: bool = True,
    ) -> None:
        """Initialize the LiveBox.

        Args:
            console: Rich console instance to use for display
            title: Title for the live box
            border_style: Border style for the panel
            refresh_per_second: Refresh rate for the live display
            transient: Whether the box should disappear when done
        """
        self.console = console
        self.title = title
        self.border_style = border_style
        self.refresh_per_second = refresh_per_second
        self.transient = transient

        # Thread safety
        self._lock = threading.Lock()
        self._content = Text("")
        self._live: Live | None = None
        self._is_active = False

    def _create_panel(self) -> Panel:
        """Create a panel with current content.

        Returns:
            Panel with current content and styling
        """
        with self._lock:
            content = self._content.copy()

        return Panel(
            content,
            title=self.title,
            title_align="left",
            border_style=self.border_style,
            padding=(0, 1),
            expand=False,
        )

    def start(self) -> None:
        """Start the live display."""
        if self._is_active:
            return

        self._live = Live(
            self._create_panel(),
            console=self.console,
            refresh_per_second=self.refresh_per_second,
            transient=self.transient,
        )
        self._live.start()
        self._is_active = True

    def stop(self) -> None:
        """Stop the live display."""
        if not self._is_active or self._live is None:
            return

        self._live.stop()
        self._live = None
        self._is_active = False

    def update(self, content: RenderableType | str) -> None:
        """Update the content of the live box.

        Args:
            content: New content to display (Text, str, or other renderable)
        """
        with self._lock:
            if isinstance(content, str):
                # Parse Rich markup in strings
                self._content = Text.from_markup(content)
            elif isinstance(content, Text):
                self._content = content
            else:
                # For other renderables, convert to text representation
                self._content = Text(str(content))

        if self._is_active and self._live is not None:
            self._live.update(self._create_panel())

    def append_text(self, text: str, style: str | None = None) -> None:
        """Append text to the current content.

        Args:
            text: Text to append
            style: Optional style to apply to the appended text
        """
        with self._lock:
            self._content.append(text, style=style)

        if self._is_active and self._live is not None:
            self._live.update(self._create_panel())

    def clear(self) -> None:
        """Clear the current content."""
        with self._lock:
            self._content = Text("")

        if self._is_active and self._live is not None:
            self._live.update(self._create_panel())

    def set_title(self, title: str) -> None:
        """Update the title of the live box.

        Args:
            title: New title for the box
        """
        self.title = title
        if self._is_active and self._live is not None:
            self._live.update(self._create_panel())

    def __enter__(self) -> "LiveBox":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.stop()
