"""Interactive session scaffolding for agent conversations.

This module provides the abstract base class and concrete implementation
for managing interactive, multi-turn agent sessions with rich UI.
"""

import threading
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from smolagents import ToolCallingAgent

from ...logging import get_logger
from ...utils.output.formatter import get_formatter

logger = get_logger()


class SessionStatus(Enum):
    """Status of the interactive session."""

    WAITING_FOR_INPUT = "waiting_for_input"
    THINKING = "thinking"
    EXECUTING_TOOL = "executing_tool"
    COMPLETED = "completed"
    ERROR = "error"


class InteractiveSession(ABC):
    """Abstract base class for managing interactive agent sessions.

    This class defines the contract for any component that manages a live,
    interactive agent conversation, including UI rendering, user input,
    and confirmation handling.
    """

    def __init__(self, agent: ToolCallingAgent):
        """Initialize the interactive session.

        Args:
            agent: The smolagents agent instance to interact with
        """
        self.agent = agent
        self.history: list[dict[str, Any]] = []
        self.status = SessionStatus.WAITING_FOR_INPUT
        self.last_tool_call: dict[str, Any] | None = None

    @abstractmethod
    def start(self) -> None:
        """Start the interactive session and enter the main conversation loop."""
        pass

    @abstractmethod
    def render(self, content: Any) -> None:
        """Render agent output and conversation state.

        Args:
            content: Content to render (thoughts, tool calls, final answers)
        """
        pass

    @abstractmethod
    def get_user_input(self) -> str:
        """Get input from the user.

        Returns:
            The user's input string
        """
        pass

    @abstractmethod
    def get_confirmation(self, action: dict[str, Any]) -> bool:
        """Display confirmation UI and get user approval.

        Args:
            action: Dictionary containing action details to confirm

        Returns:
            True if user confirms, False if user cancels
        """
        pass

    @abstractmethod
    def update_state(
        self, new_status: SessionStatus, tool_call: dict[str, Any] = None
    ) -> None:
        """Update and render the agent's current status.

        Args:
            new_status: The new session status
            tool_call: Optional tool call information for detailed rendering
        """
        pass


class RichInteractiveSession(InteractiveSession):
    """Rich-based implementation of InteractiveSession.

    This class provides a polished terminal interface using the rich library
    for managing interactive agent conversations.
    """

    def __init__(
        self,
        agent: ToolCallingAgent,
        console: Console | None = None,
        require_confirmation: bool = False,
    ):
        """Initialize the rich interactive session.

        Args:
            agent: The smolagents agent instance to interact with
            console: Optional rich console instance
            require_confirmation: Whether to require confirmation for actions
        """
        super().__init__(agent)
        self.console = console or Console()
        self.require_confirmation = require_confirmation
        self._live: Live | None = None
        self._current_content = Text("")
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start the interactive session and enter the main conversation loop."""
        logger.info("Starting rich interactive session")

        self.console.print(
            "\n[bold blue]🤖 AutoMake Agent - Interactive Mode[/bold blue]"
        )
        self.console.print(
            "Type your commands in natural language. "
            "Type 'exit' or 'quit' to end the session.\n"
        )

        try:
            while True:
                try:
                    # Update status to waiting for input
                    self.update_state(SessionStatus.WAITING_FOR_INPUT)

                    # Get user input
                    user_input = self.get_user_input()

                    # Check for exit commands
                    if user_input.lower().strip() in ["exit", "quit", "q"]:
                        self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                        break

                    if not user_input.strip():
                        continue

                    # Add user message to history
                    self.history.append({"role": "user", "content": user_input})

                    # Process the command with the agent
                    self._process_agent_response(user_input)

                except KeyboardInterrupt:
                    self.console.print(
                        "\n[yellow]👋 Session interrupted. Goodbye![/yellow]"
                    )
                    break
                except EOFError:
                    self.console.print("\n[yellow]👋 Session ended. Goodbye![/yellow]")
                    break

        except Exception as e:
            logger.error(f"Interactive session failed: {e}")
            self.console.print(f"[red]❌ Interactive session failed: {e}[/red]")
            self.update_state(SessionStatus.ERROR)
            raise

    def render(self, content: Any) -> None:
        """Render agent output and conversation state.

        Args:
            content: Content to render (thoughts, tool calls, final answers)
        """
        with self._lock:
            if isinstance(content, str):
                self._current_content = Text.from_markup(content)
            elif isinstance(content, Text):
                self._current_content = content
            else:
                self._current_content = Text(str(content))

            if self._live is not None:
                self._live.update(self._create_panel())

    def get_user_input(self) -> str:
        """Get input from the user using rich prompt.

        Returns:
            The user's input string
        """
        return Prompt.ask("[bold cyan]You[/bold cyan]")

    def get_confirmation(self, action: dict[str, Any]) -> bool:
        """Display confirmation UI and get user approval.

        Args:
            action: Dictionary containing action details to confirm

        Returns:
            True if user confirms, False if user cancels
        """
        import json

        from rich.panel import Panel

        # Create a detailed action display
        tool_name = action.get("tool_name", "Unknown")
        arguments = action.get("arguments", {})

        # Create main content
        content_lines = []
        content_lines.append(
            f"[bold cyan]🔧 Tool:[/bold cyan] [yellow]{tool_name}[/yellow]"
        )

        if arguments:
            content_lines.append("\n[bold cyan]📋 Arguments:[/bold cyan]")

            # Format arguments nicely
            if isinstance(arguments, dict):
                for key, value in arguments.items():
                    # Handle different value types
                    if isinstance(value, str) and len(value) > 50:
                        # Truncate long strings
                        display_value = f"{value[:47]}..."
                    elif isinstance(value, list | dict):
                        # Format complex structures
                        display_value = json.dumps(value, indent=2)[:100]
                        if len(json.dumps(value)) > 100:
                            display_value += "..."
                    else:
                        display_value = str(value)

                    content_lines.append(
                        f"  • [green]{key}:[/green] [white]{display_value}[/white]"
                    )
            else:
                content_lines.append(f"  [white]{arguments}[/white]")

        # Create the confirmation panel
        content = "\n".join(content_lines)
        panel = Panel(
            content,
            title="[bold red]⚠️  Action Confirmation Required[/bold red]",
            title_align="center",
            border_style="yellow",
            padding=(1, 2),
        )

        self.console.print("\n")
        self.console.print(panel)

        # Get confirmation with enhanced prompt
        confirm = Prompt.ask(
            "\n[bold yellow]❓ Do you want to proceed with this action?[/bold yellow]",
            choices=["y", "n", "yes", "no"],
            default="y",
        )

        return confirm.lower() in ["y", "yes"]

    def update_state(
        self, new_status: SessionStatus, tool_call: dict[str, Any] = None
    ) -> None:
        """Update and render the agent's current status.

        Args:
            new_status: The new session status
            tool_call: Optional tool call information for detailed rendering
        """
        self.status = new_status
        self.last_tool_call = tool_call

        # Create status message
        status_messages = {
            SessionStatus.WAITING_FOR_INPUT: "💭 Waiting for your input...",
            SessionStatus.THINKING: "🧠 Thinking...",
            SessionStatus.EXECUTING_TOOL: (
                f"🔧 Executing tool: "
                f"{tool_call.get('tool_name', 'Unknown') if tool_call else 'Unknown'}"
            ),
            SessionStatus.COMPLETED: "✅ Task completed",
            SessionStatus.ERROR: "❌ Error occurred",
        }

        status_text = status_messages.get(new_status, "🤖 Processing...")
        self.render(status_text)

    def _create_panel(self) -> Panel:
        """Create a panel with current content and status.

        Returns:
            Panel with current content and styling
        """
        # Note: This method is called from render() which already holds the lock
        content = self._current_content.copy()

        return Panel(
            content,
            title="🤖 Agent",
            title_align="left",
            border_style="blue",
            padding=(0, 1),
            expand=False,
        )

    def _process_agent_response(self, user_input: str) -> None:
        """Process the agent response with streaming and confirmation handling.

        Args:
            user_input: The user's input to process
        """
        try:
            self.update_state(SessionStatus.THINKING)

            # Start live display for agent response
            with Live(
                self._create_panel(),
                console=self.console,
                refresh_per_second=4,
                transient=False,
            ) as live:
                self._live = live

                # Run the agent with streaming
                result_stream = self.agent.run(user_input, stream=True)

                # Handle streaming response
                if hasattr(result_stream, "__iter__"):
                    accumulated_response = ""

                    # Stream the response and handle confirmations
                    for chunk in result_stream:
                        if chunk:
                            # Check if chunk is an action that needs confirmation
                            if self._is_action(chunk) and self.require_confirmation:
                                # Temporarily exit live mode for confirmation
                                self._live = None
                                live.stop()

                                # Request confirmation
                                if not self.get_confirmation(chunk):
                                    # User cancelled the action
                                    self.render("❌ Action cancelled by user")
                                    self.update_state(SessionStatus.COMPLETED)
                                    return

                                # Resume live mode
                                live.start()
                                self._live = live

                                # Update status to executing tool
                                self.update_state(SessionStatus.EXECUTING_TOOL, chunk)

                            # Continue processing the chunk
                            if isinstance(chunk, str):
                                accumulated_response += chunk
                                self.render(accumulated_response)
                            else:
                                # For action objects, show execution status
                                if isinstance(chunk, dict):
                                    tool_name = chunk.get("tool_name", "Unknown")
                                else:
                                    tool_name = "Unknown"
                                accumulated_response += f"\n🔧 Executed: {tool_name}"
                                self.render(accumulated_response)

                    # Add final response to history
                    if accumulated_response:
                        self.history.append(
                            {"role": "assistant", "content": accumulated_response}
                        )

                else:
                    # Non-streaming response
                    response = str(result_stream)
                    self.render(response)
                    self.history.append({"role": "assistant", "content": response})

                self.update_state(SessionStatus.COMPLETED)

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            error_msg = f"❌ Error: {e}"
            self.render(error_msg)
            self.update_state(SessionStatus.ERROR)

        finally:
            self._live = None

        # Add some spacing after response
        self.console.print()

    def _is_action(self, chunk: Any) -> bool:
        """Check if a chunk represents an action that needs confirmation.

        Args:
            chunk: The chunk to check

        Returns:
            True if the chunk is an action, False otherwise
        """
        # An action is typically a dictionary with tool_name
        return (
            isinstance(chunk, dict)
            and "tool_name" in chunk
            and chunk.get("tool_name") is not None
        )

    def display_thinking_animation(self, message: str) -> None:
        """Display thinking animation with typewriter effect.

        Args:
            message: Message to display with animation
        """
        try:
            formatter = get_formatter(self.console)
            live_box = formatter.create_live_box(
                title="AI Processing", refresh_per_second=4.0, transient=False
            )
            live_box.animate_text(message)
        except Exception:
            # Fallback to regular display
            try:
                formatter = get_formatter(self.console)
                formatter.print_box(message, title="AI Processing")
            except Exception:
                # Ultimate fallback
                self.console.print(f"🤖 {message}")

    def display_streaming_response(
        self, response_chunks: list[str], title: str = "AI Response"
    ) -> None:
        """Display streaming response with animation.

        Args:
            response_chunks: List of response chunks to animate
            title: Title for the response box
        """
        try:
            formatter = get_formatter(self.console)
            live_box = formatter.create_live_box(
                title=title, refresh_per_second=8.0, transient=False
            )
            full_response = "".join(response_chunks)
            live_box.animate_text(full_response)
        except Exception:
            # Fallback to regular display
            try:
                formatter = get_formatter(self.console)
                full_response = "".join(response_chunks)
                formatter.print_box(full_response, title=title)
            except Exception:
                # Ultimate fallback
                full_response = "".join(response_chunks)
                self.console.print(f"🤖 {full_response}")

    def display_animated_response(
        self, message: str, title: str = "Agent Response"
    ) -> None:
        """Display response with typewriter animation.

        Args:
            message: Message to display with animation
            title: Title for the response box
        """
        try:
            formatter = get_formatter(self.console)
            formatter.print_box(message, title=title)
        except Exception:
            # Fallback to regular display
            self.console.print(f"🤖 {message}")
