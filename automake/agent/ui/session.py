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
        # Display the action details
        action_text = f"[yellow]Action:[/yellow] {action.get('tool_name', 'Unknown')}"
        if action.get("arguments"):
            action_text += f"\n[yellow]Arguments:[/yellow] {action['arguments']}"

        self.console.print(f"\n{action_text}")

        # Get confirmation
        confirm = Prompt.ask(
            "[bold yellow]Do you want to proceed?[/bold yellow]",
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

                    # Stream the response
                    for chunk in result_stream:
                        if chunk:
                            accumulated_response += str(chunk)
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
