"""Output formatting utilities for AutoMake.

This module provides consistent, beautiful console output formatting
that matches the style of Typer's error boxes.
"""

import threading
import time
from enum import Enum

from rich.console import Console
from rich.live import Live
from rich.panel import Panel


class MessageType(Enum):
    """Types of messages that can be displayed."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    HINT = "hint"


class OutputFormatter:
    """Handles consistent formatting of console output."""

    def __init__(self, console: Console | None = None) -> None:
        """Initialize the output formatter.

        Args:
            console: Rich console instance. If None, creates a new one.
        """
        self.console = console or Console()

        # Style configurations for different message types
        self._styles = {
            MessageType.INFO: {
                "title": "Info",
                "title_color": "dim",
                "border_style": "dim",
                "emoji": "ℹ️",
            },
            MessageType.SUCCESS: {
                "title": "Success",
                "title_color": "green",
                "border_style": "green",
                "emoji": "✅",
            },
            MessageType.WARNING: {
                "title": "Warning",
                "title_color": "yellow",
                "border_style": "yellow",
                "emoji": "⚠️",
            },
            MessageType.ERROR: {
                "title": "Error",
                "title_color": "red",
                "border_style": "red",
                "emoji": "❌",
            },
            MessageType.HINT: {
                "title": "Hint",
                "title_color": "dim",
                "border_style": "dim",
                "emoji": "💡",
            },
        }

    def print_box(
        self,
        message: str,
        message_type: MessageType = MessageType.INFO,
        title: str | None = None,
    ) -> None:
        """Print a message in a styled box similar to Typer's error boxes.

        Args:
            message: The message content to display
            message_type: Type of message (affects styling)
            title: Optional custom title (overrides default for message type)
        """
        style_config = self._styles[message_type]

        # Use custom title or default from style config
        box_title = title or style_config["title"]

        # Create the panel with consistent styling
        panel = Panel(
            message,
            title=box_title,
            title_align="left",
            border_style=style_config["border_style"],
            padding=(0, 1),
            expand=False,
        )

        self.console.print(panel)

    def print_simple(
        self,
        message: str,
        message_type: MessageType = MessageType.INFO,
        prefix: bool = True,
    ) -> None:
        """Print a simple message with optional emoji prefix.

        Args:
            message: The message to display
            message_type: Type of message (affects styling and emoji)
            prefix: Whether to include emoji prefix
        """
        style_config = self._styles[message_type]

        if prefix:
            emoji = style_config["emoji"]
            formatted_message = f"{emoji} {message}"
        else:
            formatted_message = message

        # Apply color styling based on message type
        if message_type == MessageType.ERROR:
            self.console.print(f"[red]{formatted_message}[/red]")
        elif message_type == MessageType.SUCCESS:
            self.console.print(f"[green]{formatted_message}[/green]")
        elif message_type == MessageType.WARNING:
            self.console.print(f"[yellow]{formatted_message}[/yellow]")
        elif message_type == MessageType.HINT:
            self.console.print(f"[dim]{formatted_message}[/dim]")
        else:
            self.console.print(formatted_message)

    def print_command_received(self, command: str) -> None:
        """Print the command received message with consistent styling."""
        self.print_box(
            f"[bold cyan]{command}[/bold cyan]", MessageType.INFO, "Command Received"
        )

    def print_makefile_found(self, name: str, size: str) -> None:
        """Print makefile found message."""
        self.print_box(
            f"Found Makefile: [green]{name}[/green] ({size} bytes)", MessageType.SUCCESS
        )

    def print_targets_preview(self, targets: list[str], total_count: int) -> None:
        """Print available targets preview."""
        # Build the content for the box
        content_lines = []
        for target in targets:
            content_lines.append(f"• [yellow]{target}[/yellow]")

        if total_count > len(targets):
            remaining = total_count - len(targets)
            content_lines.append(f"... and {remaining} more targets")

        content = "\n".join(content_lines)
        self.print_box(content, MessageType.INFO, "Available Targets")

    def print_error_box(self, message: str, hint: str | None = None) -> None:
        """Print an error in a box with optional hint.

        Args:
            message: Error message
            hint: Optional hint message to display after the error box
        """
        self.print_box(message, MessageType.ERROR)

        if hint:
            self.print_simple(hint, MessageType.HINT, prefix=True)

    def print_status(
        self,
        message: str,
        status_type: MessageType = MessageType.INFO,
        title: str | None = None,
    ) -> None:
        """Print a status message in a box with appropriate styling.

        Args:
            message: Status message
            status_type: Type of status message
            title: Optional custom title (overrides default for message type)
        """
        self.print_box(message, status_type, title)

    def print_ascii_art(self, art_content: str) -> None:
        """Print ASCII art content.

        Args:
            art_content: The ASCII art content to display
        """
        if art_content.strip():
            self.console.print(art_content)

    def print_ai_reasoning(self, reasoning: str, confidence: int | None = None) -> None:
        """Print AI reasoning in a formatted box.

        Args:
            reasoning: The AI's reasoning or explanation
            confidence: Optional confidence score to include in the display
        """
        if confidence is not None:
            title = f"AI Reasoning (Confidence: {confidence}%)"
            content = reasoning
        else:
            title = "AI Reasoning"
            content = reasoning

        self.print_box(content, MessageType.INFO, title)

    def print_command_execution(self, command: str) -> None:
        """Print command execution message.

        Args:
            command: The command that will be executed
        """
        self.print_box(
            f"Executing: [bold cyan]make {command}[/bold cyan]",
            MessageType.INFO,
            "Execution",
        )

    def print_loading_indicator(self) -> None:
        """Print a loading indicator with three dots that build up and down."""
        self.console.print("[dim]Loading...[/dim]")
        for _ in range(3):
            self.console.print(".", end="", flush=True)
            time.sleep(0.5)
            self.console.print("\b", end="", flush=True)
        self.console.print("\n")

    def start_ai_thinking_animation(self) -> tuple[threading.Event, threading.Thread]:
        """Start an animated loading indicator for AI thinking.

        Returns:
            A tuple of (stop_event, thread) to control the animation.
        """
        stop_event = threading.Event()

        def animate():
            patterns = [".", "..", "...", "..", "."]
            pattern_index = 0

            # Create initial panel
            panel = Panel(
                f"[dim]{patterns[pattern_index]}[/dim]",
                title="AI Reasoning",
                title_align="left",
                border_style="dim",
                padding=(0, 1),
                expand=False,
            )

            # Use Rich Live display for smooth animation
            with Live(
                panel, console=self.console, refresh_per_second=2, transient=True
            ) as live:
                while not stop_event.is_set():
                    pattern_index = (pattern_index + 1) % len(patterns)
                    dots = patterns[pattern_index]

                    # Create new panel with updated dots
                    new_panel = Panel(
                        f"[dim]{dots}[/dim]",
                        title="AI Reasoning",
                        title_align="left",
                        border_style="dim",
                        padding=(0, 1),
                        expand=False,
                    )

                    # Update the live display
                    live.update(new_panel)
                    time.sleep(0.5)

        thread = threading.Thread(target=animate, daemon=True)
        thread.start()
        return stop_event, thread

    def stop_ai_thinking_animation(
        self, stop_event: threading.Event, thread: threading.Thread
    ) -> None:
        """Stop the AI thinking animation.

        Args:
            stop_event: The event to signal the animation to stop
            thread: The animation thread to wait for
        """
        stop_event.set()
        thread.join(timeout=1.0)  # Wait up to 1 second for thread to finish
        # The Live display with transient=True will automatically clean up


# Global formatter instance for convenience
_global_formatter: OutputFormatter | None = None


def get_formatter(console: Console | None = None) -> OutputFormatter:
    """Get the global output formatter instance.

    Args:
        console: Optional console instance. Only used on first call.

    Returns:
        Global OutputFormatter instance
    """
    global _global_formatter

    if _global_formatter is None:
        _global_formatter = OutputFormatter(console)

    return _global_formatter


# Convenience functions for common operations
def print_box(
    message: str, message_type: MessageType = MessageType.INFO, title: str | None = None
) -> None:
    """Print a message in a styled box."""
    get_formatter().print_box(message, message_type, title)


def print_error_box(message: str, hint: str | None = None) -> None:
    """Print an error message in a box with optional hint."""
    get_formatter().print_error_box(message, hint)


def print_status(
    message: str, status_type: MessageType = MessageType.INFO, title: str | None = None
) -> None:
    """Print a status message."""
    get_formatter().print_status(message, status_type, title)
