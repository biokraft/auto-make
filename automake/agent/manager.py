"""Manager agent for AutoMake.

This module implements the central ManagerAgent that orchestrates all specialist agents
using the smolagents framework.
"""

import os
import threading
import time
from collections.abc import Callable, Generator
from typing import Any

from smolagents import LiteLLMModel, ToolCallingAgent

from ..config import Config
from ..core.signal_handler import SignalHandler
from ..logging import get_logger
from ..utils.ollama_manager import (
    OllamaManagerError,
    ensure_ollama_running,
    get_available_models,
    is_model_available,
)
from .specialists import get_all_specialist_tools

logger = get_logger()


def create_manager_agent(config: Config) -> tuple[ToolCallingAgent, bool]:
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

        # Check if the configured model is available
        if not is_model_available(config.ollama_base_url, config.ollama_model):
            try:
                available_models = get_available_models(config.ollama_base_url)
                if available_models:
                    available_models_str = "\n".join(
                        f"  • {model}" for model in available_models
                    )
                else:
                    available_models_str = "  • none"

                raise OllamaManagerError(
                    f"Model '{config.ollama_model}' is not available in Ollama.\n"
                    f"Available models:\n{available_models_str}\n\n"
                    f"To fix this, either:\n"
                    f"1. Pull the model: ollama pull {config.ollama_model}\n"
                    f"2. Or change your configuration to use an available model:\n"
                    f"   automake config set ollama.model <model_name>"
                )
            except OllamaManagerError:
                # Re-raise the model availability error
                raise
            except Exception as e:
                # If we can't get available models, still show the main error
                raise OllamaManagerError(
                    f"Model '{config.ollama_model}' is not available in Ollama.\n"
                    f"Could not retrieve available models: {e}\n\n"
                    f"To fix this, try:\n"
                    f"1. Pull the model: ollama pull {config.ollama_model}\n"
                    f"2. Check if Ollama is running: ollama list"
                ) from e

        # Create the LLM model
        model_name = f"ollama/{config.ollama_model}"
        model = LiteLLMModel(
            model_id=model_name,
            base_url=config.ollama_base_url,
        )

        # Get all specialist tools
        specialist_tools = get_all_specialist_tools()

        # Create the manager agent with all specialist tools
        manager_agent = ToolCallingAgent(
            tools=specialist_tools,
            model=model,
        )

        logger.info("Manager agent created successfully")
        return manager_agent, ollama_was_started

    except OllamaManagerError:
        # Re-raise Ollama-specific errors with their detailed messages
        raise
    except Exception as e:
        logger.error(f"Failed to create manager agent: {e}")
        # Wrap other exceptions with a more generic message
        raise OllamaManagerError(f"Failed to create manager agent: {e}") from e


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
        self._child_processes: list[Any] = []
        self._temp_files: list[str] = []
        self._cleanup_functions: list[Callable[[], None]] = []
        self._shutdown_lock = threading.Lock()
        self._is_shutdown = False
        self._signal_cleanup_id = None

    def initialize(self) -> bool:
        """Initialize the manager agent.

        Returns:
            True if Ollama was started, False otherwise

        Raises:
            Exception: If initialization fails
        """
        self.agent, self.ollama_was_started = create_manager_agent(self.config)

        # Register shutdown with signal handler
        signal_handler = SignalHandler.get_instance()
        self._signal_cleanup_id = signal_handler.register_cleanup(
            self.shutdown, "Agent manager shutdown"
        )

        return self.ollama_was_started

    def run(self, prompt: str, stream: bool = False) -> str | Generator[str]:
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

    def shutdown(self, timeout: float = 3.0) -> None:
        """Shutdown the manager agent and clean up all resources.

        Args:
            timeout: Maximum time to wait for child processes to terminate
        """
        with self._shutdown_lock:
            if self._is_shutdown:
                return

            self._is_shutdown = True
            logger.info("Shutting down agent manager...")

        try:
            # Run cleanup functions
            for cleanup_func in self._cleanup_functions:
                try:
                    cleanup_func()
                except Exception as e:
                    logger.error(f"Error in cleanup function: {e}")

            # Terminate child processes
            self._terminate_child_processes(timeout)

            # Clean up temporary files
            self._cleanup_temp_files()

            # Clear agent reference
            self.agent = None

            # Unregister from signal handler
            if self._signal_cleanup_id:
                signal_handler = SignalHandler.get_instance()
                signal_handler.unregister_cleanup(self._signal_cleanup_id)
                self._signal_cleanup_id = None

            logger.info("Agent manager shutdown completed")

        except Exception as e:
            logger.error(f"Error during agent manager shutdown: {e}")

    def _terminate_child_processes(self, timeout: float) -> None:
        """Terminate all child processes with timeout.

        Args:
            timeout: Maximum time to wait for processes to terminate
        """
        if not self._child_processes:
            return

        logger.debug(f"Terminating {len(self._child_processes)} child processes")

        # First, try graceful termination
        for process in self._child_processes:
            try:
                if hasattr(process, "terminate"):
                    process.terminate()
            except Exception as e:
                logger.error(f"Error terminating process: {e}")

        # Wait for processes to terminate
        start_time = time.time()
        while time.time() - start_time < timeout:
            remaining_processes = []
            for process in self._child_processes:
                try:
                    if hasattr(process, "poll") and process.poll() is None:
                        remaining_processes.append(process)
                except Exception:
                    pass

            if not remaining_processes:
                break

            time.sleep(0.1)
            self._child_processes = remaining_processes

        # Force kill any remaining processes
        for process in self._child_processes:
            try:
                if hasattr(process, "kill"):
                    process.kill()
                    logger.warning(
                        f"Force killed process {getattr(process, 'pid', 'unknown')}"
                    )
            except Exception as e:
                logger.error(f"Error force killing process: {e}")

        self._child_processes.clear()

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files created during agent execution."""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    logger.debug(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                logger.error(f"Error cleaning up temporary file {temp_file}: {e}")

        self._temp_files.clear()
