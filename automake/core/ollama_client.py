"""Ollama client for AutoMake.

This module handles communication with the local Ollama server for LLM inference.
It provides both synchronous and asynchronous clients with proper error handling
and configuration management.
"""

import logging
from typing import Any

from ollama import AsyncClient, Client, ResponseError

from ..config import Config

logger = logging.getLogger(__name__)


class OllamaClientError(Exception):
    """Raised when there's an error with Ollama client operations."""

    pass


class OllamaClient:
    """Synchronous Ollama client for AutoMake."""

    def __init__(self, config: Config):
        """Initialize the Ollama client.

        Args:
            config: AutoMake configuration instance
        """
        self.config = config
        self.base_url = config.ollama_base_url
        self.model = config.ollama_model

        # Create client with custom configuration
        self.client = Client(host=self.base_url)

        logger.info(
            "Initialized Ollama client with base_url=%s, model=%s",
            self.base_url,
            self.model,
        )

    def validate_connection(self) -> bool:
        """Validate connection to Ollama server.

        Returns:
            True if connection is successful, False otherwise

        Raises:
            OllamaClientError: If there's a connection error
        """
        try:
            # Try to list models to test connection
            self.client.list()
            logger.debug("Successfully connected to Ollama server")
            return True
        except ResponseError as e:
            logger.error(f"Ollama server error: {e.error}")
            raise OllamaClientError(f"Ollama server error: {e.error}") from e
        except Exception as e:
            logger.error(
                "Failed to connect to Ollama server at %s: %s", self.base_url, e
            )
            raise OllamaClientError(
                f"Failed to connect to Ollama server at {self.base_url}. "
                f"Please ensure Ollama is running and accessible at {self.base_url}"
            ) from e

    def validate_model(self) -> bool:
        """Validate that the configured model is available.

        Returns:
            True if model is available, False otherwise

        Raises:
            OllamaClientError: If model is not available or there's an error
        """
        try:
            # Try to show model info to verify it exists
            self.client.show(self.model)
            logger.debug("Model %s is available", self.model)
            return True
        except ResponseError as e:
            if e.status_code == 404:
                logger.error(
                    "Model %s not found. Please pull it first: ollama pull %s",
                    self.model,
                    self.model,
                )
                raise OllamaClientError(
                    f"Model '{self.model}' not found. "
                    f"Please pull it first with: ollama pull {self.model}"
                ) from e
            else:
                logger.error("Error checking model %s: %s", self.model, e.error)
                raise OllamaClientError(
                    f"Error checking model {self.model}: {e.error}"
                ) from e
        except Exception as e:
            logger.error("Unexpected error checking model %s: %s", self.model, e)
            raise OllamaClientError(
                f"Unexpected error checking model {self.model}: {e}"
            ) from e

    def chat(
        self, messages: list[dict[str, str]], stream: bool = False, **kwargs: Any
    ) -> Any:
        """Send a chat completion request to Ollama.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            stream: Whether to stream the response
            **kwargs: Additional arguments to pass to the chat method

        Returns:
            Chat response from Ollama

        Raises:
            OllamaClientError: If there's an error with the chat request
        """
        try:
            logger.debug("Sending chat request with %d messages", len(messages))
            response = self.client.chat(
                model=self.model, messages=messages, stream=stream, **kwargs
            )
            logger.debug("Successfully received chat response")
            return response
        except ResponseError as e:
            logger.error(f"Ollama chat error: {e.error}")
            raise OllamaClientError(f"Ollama chat error: {e.error}") from e
        except Exception as e:
            logger.error(f"Unexpected error during chat: {e}")
            raise OllamaClientError(f"Unexpected error during chat: {e}") from e

    def generate(self, prompt: str, stream: bool = False, **kwargs: Any) -> Any:
        """Send a generation request to Ollama.

        Args:
            prompt: The prompt to generate from
            stream: Whether to stream the response
            **kwargs: Additional arguments to pass to the generate method

        Returns:
            Generation response from Ollama

        Raises:
            OllamaClientError: If there's an error with the generation request
        """
        try:
            logger.debug(
                "Sending generation request with prompt length: %d", len(prompt)
            )
            response = self.client.generate(
                model=self.model, prompt=prompt, stream=stream, **kwargs
            )
            logger.debug("Successfully received generation response")
            return response
        except ResponseError as e:
            logger.error(f"Ollama generation error: {e.error}")
            raise OllamaClientError(f"Ollama generation error: {e.error}") from e
        except Exception as e:
            logger.error(f"Unexpected error during generation: {e}")
            raise OllamaClientError(f"Unexpected error during generation: {e}") from e

    def list_models(self) -> list[dict[str, Any]]:
        """List available models on the Ollama server.

        Returns:
            List of model information dictionaries

        Raises:
            OllamaClientError: If there's an error listing models
        """
        try:
            response = self.client.list()
            models = response.get("models", [])
            logger.debug(f"Found {len(models)} available models")
            return models
        except ResponseError as e:
            logger.error(f"Error listing models: {e.error}")
            raise OllamaClientError(f"Error listing models: {e.error}") from e
        except Exception as e:
            logger.error(f"Unexpected error listing models: {e}")
            raise OllamaClientError(f"Unexpected error listing models: {e}") from e


class AsyncOllamaClient:
    """Asynchronous Ollama client for AutoMake."""

    def __init__(self, config: Config):
        """Initialize the async Ollama client.

        Args:
            config: AutoMake configuration instance
        """
        self.config = config
        self.base_url = config.ollama_base_url
        self.model = config.ollama_model

        # Create async client with custom configuration
        self.client = AsyncClient(host=self.base_url)

        logger.info(
            "Initialized async Ollama client with base_url=%s, model=%s",
            self.base_url,
            self.model,
        )

    async def validate_connection(self) -> bool:
        """Validate connection to Ollama server asynchronously.

        Returns:
            True if connection is successful, False otherwise

        Raises:
            OllamaClientError: If there's a connection error
        """
        try:
            # Try to list models to test connection
            await self.client.list()
            logger.debug("Successfully connected to Ollama server (async)")
            return True
        except ResponseError as e:
            logger.error(f"Ollama server error (async): {e.error}")
            raise OllamaClientError(f"Ollama server error: {e.error}") from e
        except Exception as e:
            logger.error(
                "Failed to connect to Ollama server at %s (async): %s",
                self.base_url,
                e,
            )
            raise OllamaClientError(
                f"Failed to connect to Ollama server at {self.base_url}. "
                f"Please ensure Ollama is running and accessible at {self.base_url}"
            ) from e

    async def validate_model(self) -> bool:
        """Validate that the configured model is available asynchronously.

        Returns:
            True if model is available, False otherwise

        Raises:
            OllamaClientError: If model is not available or there's an error
        """
        try:
            # Try to show model info to verify it exists
            await self.client.show(self.model)
            logger.debug("Model %s is available (async)", self.model)
            return True
        except ResponseError as e:
            if e.status_code == 404:
                logger.error(
                    "Model %s not found (async). Please pull it first: ollama pull %s",
                    self.model,
                    self.model,
                )
                raise OllamaClientError(
                    f"Model '{self.model}' not found. "
                    f"Please pull it first with: ollama pull {self.model}"
                ) from e
            else:
                logger.error("Error checking model %s (async): %s", self.model, e.error)
                raise OllamaClientError(
                    f"Error checking model {self.model}: {e.error}"
                ) from e
        except Exception as e:
            logger.error(
                "Unexpected error checking model %s (async): %s", self.model, e
            )
            raise OllamaClientError(
                f"Unexpected error checking model {self.model}: {e}"
            ) from e

    async def chat(
        self, messages: list[dict[str, str]], stream: bool = False, **kwargs: Any
    ) -> Any:
        """Send a chat completion request to Ollama asynchronously.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            stream: Whether to stream the response
            **kwargs: Additional arguments to pass to the chat method

        Returns:
            Chat response from Ollama

        Raises:
            OllamaClientError: If there's an error with the chat request
        """
        try:
            logger.debug("Sending async chat request with %d messages", len(messages))
            response = await self.client.chat(
                model=self.model, messages=messages, stream=stream, **kwargs
            )
            logger.debug("Successfully received async chat response")
            return response
        except ResponseError as e:
            logger.error(f"Ollama chat error (async): {e.error}")
            raise OllamaClientError(f"Ollama chat error: {e.error}") from e
        except Exception as e:
            logger.error(f"Unexpected error during async chat: {e}")
            raise OllamaClientError(f"Unexpected error during chat: {e}") from e

    async def generate(self, prompt: str, stream: bool = False, **kwargs: Any) -> Any:
        """Send a generation request to Ollama asynchronously.

        Args:
            prompt: The prompt to generate from
            stream: Whether to stream the response
            **kwargs: Additional arguments to pass to the generate method

        Returns:
            Generation response from Ollama

        Raises:
            OllamaClientError: If there's an error with the generation request
        """
        try:
            logger.debug(
                "Sending async generation request with prompt length: %d",
                len(prompt),
            )
            response = await self.client.generate(
                model=self.model, prompt=prompt, stream=stream, **kwargs
            )
            logger.debug("Successfully received async generation response")
            return response
        except ResponseError as e:
            logger.error(f"Ollama generation error (async): {e.error}")
            raise OllamaClientError(f"Ollama generation error: {e.error}") from e
        except Exception as e:
            logger.error(f"Unexpected error during async generation: {e}")
            raise OllamaClientError(f"Unexpected error during generation: {e}") from e

    async def list_models(self) -> list[dict[str, Any]]:
        """List available models on the Ollama server asynchronously.

        Returns:
            List of model information dictionaries

        Raises:
            OllamaClientError: If there's an error listing models
        """
        try:
            response = await self.client.list()
            models = response.get("models", [])
            logger.debug(f"Found {len(models)} available models (async)")
            return models
        except ResponseError as e:
            logger.error(f"Error listing models (async): {e.error}")
            raise OllamaClientError(f"Error listing models: {e.error}") from e
        except Exception as e:
            logger.error(f"Unexpected error listing models (async): {e}")
            raise OllamaClientError(f"Unexpected error listing models: {e}") from e


def create_ollama_client(config: Config) -> OllamaClient:
    """Create and validate an Ollama client.

    Args:
        config: AutoMake configuration instance

    Returns:
        Configured and validated OllamaClient instance

    Raises:
        OllamaClientError: If client creation or validation fails
    """
    client = OllamaClient(config)

    # Validate connection and model availability
    client.validate_connection()
    client.validate_model()

    return client


async def create_async_ollama_client(config: Config) -> AsyncOllamaClient:
    """Create and validate an async Ollama client.

    Args:
        config: AutoMake configuration instance

    Returns:
        Configured and validated AsyncOllamaClient instance

    Raises:
        OllamaClientError: If client creation or validation fails
    """
    client = AsyncOllamaClient(config)

    # Validate connection and model availability
    await client.validate_connection()
    await client.validate_model()

    return client
