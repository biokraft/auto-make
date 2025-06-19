"""Output formatter for consistent console output formatting.

This module provides the OutputFormatter class for handling all console output
with consistent styling and formatting.
"""

import threading
import time
from collections.abc import Generator
from colorsys import hsv_to_rgb
from contextlib import contextmanager

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from ..animation import animate_text
from .live_box import LiveBox
from .types import MessageType


def _get_animation_config() -> tuple[bool, float]:
    """Get animation configuration settings.

    Returns:
        Tuple of (enabled, speed) with fallback defaults if config unavailable
    """
    import os

    # Check for CI environment variables - disable animations in CI
    ci_env_vars = [
        "CI",
        "GITHUB_ACTIONS",
        "GITLAB_CI",
        "TRAVIS",
        "CIRCLECI",
        "JENKINS_URL",
    ]
    is_ci = any(os.getenv(var) for var in ci_env_vars)

    try:
        from ...config.manager import get_config

        config = get_config()
        # Disable animations in CI environments regardless of config
        animation_enabled = config.ui_animation_enabled and not is_ci
        return animation_enabled, config.ui_animation_speed
    except Exception:
        # Fallback to defaults if config is unavailable, but still respect CI detection
        return not is_ci, 50.0


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

    @contextmanager
    def live_box(
        self,
        title: str = "Live Output",
        message_type: MessageType = MessageType.INFO,
        refresh_per_second: float = 4.0,
        transient: bool = True,
    ) -> Generator[LiveBox]:
        """Create and manage a LiveBox context manager.

        Args:
            title: Title for the live box
            message_type: Type of message (affects border styling)
            refresh_per_second: Refresh rate for the live display
            transient: Whether the box should disappear when done

        Yields:
            LiveBox instance for updating content
        """
        style_config = self._styles[message_type]
        border_style = style_config["border_style"]

        live_box = LiveBox(
            console=self.console,
            title=title,
            border_style=border_style,
            refresh_per_second=refresh_per_second,
            transient=transient,
        )

        try:
            with live_box:
                yield live_box
        finally:
            # Ensure cleanup even if exception occurs
            pass

    def create_live_box(
        self,
        title: str = "Live Output",
        message_type: MessageType = MessageType.INFO,
        refresh_per_second: float = 4.0,
        transient: bool = True,
    ) -> LiveBox:
        """Create a LiveBox instance (not started).

        Args:
            title: Title for the live box
            message_type: Type of message (affects border styling)
            refresh_per_second: Refresh rate for the live display
            transient: Whether the box should disappear when done

        Returns:
            LiveBox instance (call start() to begin display)
        """
        style_config = self._styles[message_type]
        border_style = style_config["border_style"]

        return LiveBox(
            console=self.console,
            title=title,
            border_style=border_style,
            refresh_per_second=refresh_per_second,
            transient=transient,
        )

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

        # Create panel factory function for animation
        def panel_factory(text: str) -> Panel:
            return Panel(
                text,
                title=box_title,
                title_align="left",
                border_style=style_config["border_style"],
                padding=(0, 1),
                expand=False,
            )

        # Try to use animation, fallback to direct print if any issues
        try:
            # Get animation configuration
            animation_enabled, animation_speed = _get_animation_config()

            animate_text(
                self.console,
                message,
                panel_factory,
                speed=animation_speed,
                enabled=animation_enabled,
            )
        except Exception:
            # Fallback to direct print if animation or config fails
            self.console.print(panel_factory(message))

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
        """Print that a command was received."""
        self.print_box(f"[cyan]{command}[/cyan]", MessageType.INFO, "Command Received")

    def print_makefile_found(self, name: str, size: str) -> None:
        """Print that a Makefile was found."""
        self.print_simple(f"Found {name} ({size})", MessageType.SUCCESS)

    def print_targets_preview(self, targets: list[str], total_count: int) -> None:
        """Print a preview of available targets."""
        if targets:
            targets_text = ", ".join(targets[:5])
            if total_count > 5:
                targets_text += f" (and {total_count - 5} more)"
            self.print_simple(f"Available targets: {targets_text}", MessageType.INFO)
        else:
            self.print_simple("No targets found in Makefile", MessageType.WARNING)

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

    def print_rainbow_ascii_art(self, art_content: str, duration: float = 3.0) -> None:
        """Print ASCII art with animated rainbow colors.

        Args:
            art_content: The ASCII art content to display
            duration: Duration in seconds to show the animation
        """
        if not art_content.strip():
            return

        # Split art into lines for processing
        lines = art_content.strip().split("\n")

        # Animation parameters
        frame_rate = 60  # FPS (increased for smoother animation)
        frame_time = 1.0 / frame_rate
        total_frames = int(duration * frame_rate)

        def create_rainbow_frame(hue_offset: float):
            """Create a single frame of rainbow-colored ASCII art.

            Args:
                hue_offset: Offset for the hue cycle (0.0 to 1.0)

            Returns:
                Rich Text object with rainbow colors
            """

            # Create a Text object to hold the entire ASCII art
            rainbow_text = Text()

            for line_idx, line in enumerate(lines):
                if line_idx > 0:
                    rainbow_text.append("\n")

                for char_idx, char in enumerate(line):
                    if char.strip():  # Only color non-whitespace characters
                        # Calculate hue based on position and time offset
                        # This creates a rainbow effect that moves across the art
                        position_factor = (
                            char_idx + line_idx * 0.5
                        ) / 20.0  # Adjust for rainbow spread
                        hue = (position_factor + hue_offset) % 1.0

                        # Convert HSV to RGB (reduced saturation for readability)
                        r, g, b = hsv_to_rgb(hue, 0.8, 1.0)

                        # Convert to 0-255 range
                        r_int = int(r * 255)
                        g_int = int(g * 255)
                        b_int = int(b * 255)

                        # Add character with RGB color
                        rainbow_text.append(char, style=f"rgb({r_int},{g_int},{b_int})")
                    else:
                        # Add whitespace without color
                        rainbow_text.append(char)

            return rainbow_text

        # Create and run the animation
        try:
            with Live(
                create_rainbow_frame(0.0),
                console=self.console,
                refresh_per_second=frame_rate,
                transient=False,  # Keep the final frame visible
            ) as live:
                for frame in range(total_frames):
                    # Calculate hue offset for this frame (cycles through 0-1)
                    # Multiply by 2 for faster color cycling
                    hue_offset = (frame / total_frames * 2) % 1.0

                    # Update the display with new rainbow frame
                    live.update(create_rainbow_frame(hue_offset))

                    # Wait for next frame
                    time.sleep(frame_time)

        except KeyboardInterrupt:
            # Allow graceful exit if user interrupts
            pass

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

    def print_command_chosen(self, command: str | None, confidence: int) -> None:
        """Print the chosen command."""
        if command:
            self.print_box(
                f"make {command} (confidence: {confidence}%)",
                MessageType.SUCCESS,
                "Command Selected",
            )
        else:
            self.print_box(
                f"No suitable command found (confidence: {confidence}%)",
                MessageType.ERROR,
                "No Match",
            )

    def print_command_execution(self, command: str) -> None:
        """Print that a command is being executed."""
        self.print_box(
            f"Executing: make {command}",
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
        start_time = time.time()

        def animate():
            min_display_time = 0.5  # Minimum time to show animation
            frame_time = 0.3  # Time between frames

            frames = [
                "🤔 Thinking",
                "🤔 Thinking.",
                "🤔 Thinking..",
                "🤔 Thinking...",
            ]
            frame_index = 0

            # Create the panel that will be updated
            def create_panel(frame_text: str) -> Panel:
                return Panel(
                    f"[dim]{frame_text}[/dim]",
                    title="AI Processing",
                    title_align="left",
                    border_style="blue",
                    padding=(0, 1),
                    expand=False,
                )

            # Use Live display for smooth animation
            with Live(
                create_panel(frames[0]),
                console=self.console,
                refresh_per_second=10,
                transient=True,  # Remove when done
            ) as live:
                while True:
                    # Update the display with current frame
                    live.update(create_panel(frames[frame_index]))

                    # Move to next frame
                    frame_index = (frame_index + 1) % len(frames)

                    # Wait for frame time
                    time.sleep(frame_time)

                    # Check if minimum time has passed AND we've been asked to stop
                    elapsed = time.time() - start_time
                    if elapsed >= min_display_time and stop_event.is_set():
                        break

        thread = threading.Thread(target=animate, daemon=True)
        thread.start()

        # Give the animation a moment to start displaying
        time.sleep(0.1)

        return stop_event, thread

    def stop_ai_thinking_animation(
        self, stop_event: threading.Event, thread: threading.Thread
    ) -> None:
        """Stop the AI thinking animation.

        Args:
            stop_event: The event to signal the animation to stop.
            thread: The animation thread to wait for.
        """
        stop_event.set()
        thread.join(timeout=3.0)  # Wait longer for animation to complete

    def animate_thinking_message(
        self, live_box: LiveBox, message: str, delay: float = 0.08
    ) -> None:
        """Animate a thinking message token by token.

        Args:
            live_box: LiveBox instance to update
            message: Message to animate
            delay: Delay between tokens in seconds
        """
        import time

        # Split message into tokens (words and punctuation)
        tokens = []
        current_token = ""

        for char in message:
            if char.isspace():
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                tokens.append(char)
            else:
                current_token += char

        if current_token:
            tokens.append(current_token)

        # Animate token by token
        animated_text = ""
        for token in tokens:
            animated_text += token
            live_box.update(animated_text)
            time.sleep(delay)

        # Final pause to let user read the complete message
        time.sleep(0.5)

    @contextmanager
    def ai_thinking_box(self, title: str = "AI Processing") -> Generator[LiveBox]:
        """Context manager for AI thinking with LiveBox.

        Args:
            title: Title for the thinking box

        Yields:
            LiveBox instance for updating content
        """
        with self.live_box(title, MessageType.INFO, transient=True) as live_box:
            # Start with animated thinking message
            self.animate_thinking_message(live_box, "🤔 Analyzing your command...")
            yield live_box

    @contextmanager
    def command_execution_box(self, command: str) -> Generator[LiveBox]:
        """Context manager for command execution with LiveBox.

        Args:
            command: The command being executed

        Yields:
            LiveBox instance for updating execution progress
        """
        title = f"Executing: make {command}"
        # Use higher refresh rate for smoother streaming of command output
        with self.live_box(
            title, MessageType.INFO, refresh_per_second=10.0, transient=False
        ) as live_box:
            yield live_box

    @contextmanager
    def model_streaming_box(self, title: str = "AI Response") -> Generator[LiveBox]:
        """Context manager for streaming AI model responses.

        Args:
            title: Title for the streaming box

        Yields:
            LiveBox instance for streaming content
        """
        with self.live_box(title, MessageType.INFO, transient=False) as live_box:
            live_box.update("🤖 Generating response...")
            yield live_box

    def print_ai_reasoning_streaming(
        self, reasoning: str, confidence: int | None = None
    ) -> None:
        """Print AI reasoning with streaming effect.

        Args:
            reasoning: The AI's reasoning or explanation
            confidence: Optional confidence score to include in the display
        """
        if confidence is not None:
            title = f"AI Reasoning (Confidence: {confidence}%)"
        else:
            title = "AI Reasoning"

        with self.live_box(title, MessageType.INFO, transient=False) as live_box:
            # Stream the reasoning text word by word for dramatic effect
            words = reasoning.split()
            current_text = ""

            for i, word in enumerate(words):
                current_text += word
                if i < len(words) - 1:
                    current_text += " "

                live_box.update(current_text)
                time.sleep(0.05)  # Small delay for streaming effect

    def print_command_chosen_animated(
        self, command: str | None, confidence: int
    ) -> None:
        """Print the chosen command with animated reveal.

        Args:
            command: The chosen make command
            confidence: Confidence percentage
        """
        title = "Command Selected"

        with self.live_box(title, MessageType.SUCCESS, transient=False) as live_box:
            if command:
                # Animate the command reveal
                live_box.update("🎯 Command identified...")
                time.sleep(0.5)

                live_box.update(f"🎯 Selected: make {command}")
                time.sleep(0.3)

                live_box.update(
                    f"🎯 Selected: make {command}\n📊 Confidence: {confidence}%"
                )
            else:
                live_box.update(
                    f"❌ No suitable command found (confidence: {confidence}%)"
                )


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
