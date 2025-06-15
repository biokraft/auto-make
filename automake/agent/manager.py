"""Manager agent for AutoMake.

This module implements the central ManagerAgent that orchestrates all specialist agents
using the smolagents framework.
"""

from collections.abc import Generator

from smolagents import CodeAgent, LiteLLMModel

from ..config import Config
from ..logging import get_logger
from ..utils.ollama_manager import ensure_ollama_running
from .specialists import get_all_specialist_tools

logger = get_logger()


def create_manager_agent(config: Config) -> tuple[CodeAgent, bool]:
    """Create and configure the manager agent with all specialist agents.

    Args:
        config: Configuration object containing Ollama settings

    Returns:
        Tuple of (manager_agent, ollama_was_started)

    Raises:
        Exception: If agent initialization fails
    """
    try:
        # Ensure Ollama is running
        is_running, ollama_was_started = ensure_ollama_running(config)

        # Create the LLM model
        model_name = f"ollama/{config.ollama_model}"
        model = LiteLLMModel(
            model_id=model_name,
            base_url=config.ollama_base_url,
        )

        # Get all specialist tools
        specialist_tools = get_all_specialist_tools()

        # Create the manager agent with all specialist tools
        manager_agent = CodeAgent(
            tools=specialist_tools,
            model=model,
        )

        logger.info("Manager agent created successfully")
        return manager_agent, ollama_was_started

    except Exception as e:
        logger.error(f"Failed to create manager agent: {e}")
        raise


class ManagerAgentRunner:
    """Runner class for the manager agent that provides a clean interface."""

    def __init__(self, config: Config):
        """Initialize the manager agent runner.

        Args:
            config: Configuration object
        """
        self.config = config
        self.agent = None
        self.ollama_was_started = False

    def initialize(self) -> bool:
        """Initialize the manager agent.

        Returns:
            True if Ollama was started, False otherwise

        Raises:
            Exception: If initialization fails
        """
        self.agent, self.ollama_was_started = create_manager_agent(self.config)
        return self.ollama_was_started

    def run(
        self, prompt: str, stream: bool = False
    ) -> str | Generator[str, None, None]:
        """Run a prompt through the manager agent.

        Args:
            prompt: The user's natural language command
            stream: Whether to stream the response

        Returns:
            The agent's response, either as a string or generator

        Raises:
            RuntimeError: If agent is not initialized
        """
        if self.agent is None:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        logger.info(f"Running prompt through manager agent: {prompt}")

        try:
            if stream:
                return self.agent.run(prompt, stream=True)
            else:
                result = self.agent.run(prompt)
                return result
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            raise
