"""Ollama server management utilities for AutoMake.

This module provides functionality to check if Ollama is running and
automatically start it if needed.
"""

import logging
import subprocess
import time

import ollama
import requests

from ..config import Config

logger = logging.getLogger(__name__)


class OllamaManagerError(Exception):
    """Raised when there's an error managing Ollama."""

    pass


def is_ollama_running(base_url: str, timeout: int = 5) -> bool:
    """Check if Ollama server is running and accessible.

    Args:
        base_url: The Ollama server base URL
        timeout: Request timeout in seconds

    Returns:
        True if Ollama is running and accessible, False otherwise
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=timeout)
        return response.status_code == 200
    except (requests.RequestException, requests.ConnectionError):
        return False


def start_ollama_server() -> bool:
    """Attempt to start the Ollama server.

    Returns:
        True if Ollama was started successfully, False otherwise

    Raises:
        OllamaManagerError: If there's an error starting Ollama
    """
    try:
        logger.info("Attempting to start Ollama server...")

        # Try to start Ollama in the background
        process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,  # Detach from parent process
        )

        # Give Ollama a moment to start
        time.sleep(2)

        # Check if the process is still running (not immediately crashed)
        if process.poll() is None:
            logger.info("Ollama server started successfully")
            return True
        else:
            logger.error("Ollama server failed to start (process exited)")
            return False

    except FileNotFoundError:
        logger.error("Ollama command not found - is Ollama installed?")
        raise OllamaManagerError(
            "Ollama command not found. Please install Ollama from https://ollama.ai/"
        ) from None
    except Exception as e:
        logger.error("Failed to start Ollama server: %s", e)
        raise OllamaManagerError(f"Failed to start Ollama server: {e}") from e


def wait_for_ollama_ready(base_url: str, max_wait: int = 30) -> bool:
    """Wait for Ollama server to become ready.

    Args:
        base_url: The Ollama server base URL
        max_wait: Maximum time to wait in seconds

    Returns:
        True if Ollama becomes ready within the timeout, False otherwise
    """
    start_time = time.time()

    while time.time() - start_time < max_wait:
        if is_ollama_running(base_url):
            return True
        time.sleep(1)

    return False


def ensure_ollama_running(config: Config) -> tuple[bool, bool]:
    """Ensure Ollama is running, starting it automatically if needed.

    Args:
        config: Configuration object containing Ollama settings

    Returns:
        Tuple of (is_running, was_started_automatically)
        - is_running: True if Ollama is now running
        - was_started_automatically: True if we started Ollama automatically

    Raises:
        OllamaManagerError: If Ollama cannot be started or accessed
    """
    base_url = config.ollama_base_url

    # First check if Ollama is already running
    if is_ollama_running(base_url):
        logger.debug("Ollama server is already running")
        return True, False

    logger.info("Ollama server not detected, attempting to start automatically...")

    # Try to start Ollama
    if not start_ollama_server():
        raise OllamaManagerError("Failed to start Ollama server")

    # Wait for Ollama to become ready
    if not wait_for_ollama_ready(base_url, max_wait=15):
        raise OllamaManagerError(
            f"Ollama server started but did not become ready within 15 seconds. "
            f"Check if it's accessible at {base_url}"
        )

    logger.info("Ollama server started and is ready")
    return True, True


def get_available_models(base_url: str) -> list[str]:
    """Get list of available models from Ollama.

    Args:
        base_url: The Ollama server base URL

    Returns:
        List of available model names

    Raises:
        OllamaManagerError: If unable to connect to Ollama or retrieve models
    """
    try:
        client = ollama.Client(host=base_url)
        models_response = client.list()

        available_models = []
        if hasattr(models_response, "models"):
            # New ollama client API - models_response is a ListResponse object
            for model in models_response.models:
                if hasattr(model, "model"):
                    available_models.append(model.model)
                elif hasattr(model, "name"):
                    available_models.append(model.name)
        elif isinstance(models_response, dict) and "models" in models_response:
            # Legacy API - models_response is a dictionary
            model_list = models_response["models"]
            for model in model_list:
                if isinstance(model, dict):
                    model_name = (
                        model.get("name") or model.get("model") or model.get("id")
                    )
                    if model_name:
                        available_models.append(model_name)
                elif isinstance(model, str):
                    available_models.append(model)
        else:
            # Fallback for other response types
            model_list = models_response
            for model in model_list:
                if isinstance(model, dict):
                    model_name = (
                        model.get("name") or model.get("model") or model.get("id")
                    )
                    if model_name:
                        available_models.append(model_name)
                elif isinstance(model, str):
                    available_models.append(model)

        return available_models

    except Exception as e:
        logger.error("Failed to retrieve models from Ollama: %s", e)
        raise OllamaManagerError(f"Failed to retrieve models from Ollama: {e}") from e


def is_model_available(base_url: str, model_name: str) -> bool:
    """Check if a specific model is available in Ollama.

    Args:
        base_url: The Ollama server base URL
        model_name: Name of the model to check

    Returns:
        True if model is available, False otherwise
    """
    try:
        available_models = get_available_models(base_url)
        return model_name in available_models
    except OllamaManagerError:
        return False


def pull_model(base_url: str, model_name: str) -> bool:
    """Pull a model in Ollama.

    Args:
        base_url: The Ollama server base URL
        model_name: Name of the model to pull

    Returns:
        True if model was pulled successfully, False otherwise

    Raises:
        OllamaManagerError: If there's an error pulling the model
    """
    try:
        logger.info("Pulling model '%s' from Ollama...", model_name)
        client = ollama.Client(host=base_url)

        # Pull the model - this may take a while for large models
        client.pull(model_name)

        logger.info("Model '%s' pulled successfully", model_name)
        return True

    except Exception as e:
        logger.error("Failed to pull model '%s': %s", model_name, e)
        raise OllamaManagerError(f"Failed to pull model '{model_name}': {e}") from e


def ensure_model_available(config: Config) -> tuple[bool, bool]:
    """Ensure the configured model is available in Ollama, pulling it if necessary.

    Args:
        config: Configuration object containing Ollama settings

    Returns:
        Tuple of (is_available, was_pulled)
        - is_available: True if model is now available
        - was_pulled: True if we pulled the model

    Raises:
        OllamaManagerError: If model cannot be made available
    """
    base_url = config.ollama_base_url
    model_name = config.ollama_model

    # First ensure Ollama is running
    is_running, was_started = ensure_ollama_running(config)
    if not is_running:
        raise OllamaManagerError(
            "Ollama server is not running and could not be started"
        )

    # Check if model is already available
    if is_model_available(base_url, model_name):
        logger.debug("Model '%s' is already available", model_name)
        return True, False

    logger.info("Model '%s' not found, attempting to pull...", model_name)

    # Try to pull the model
    if not pull_model(base_url, model_name):
        raise OllamaManagerError(f"Failed to pull model '{model_name}'")

    # Verify the model is now available
    if not is_model_available(base_url, model_name):
        raise OllamaManagerError(
            f"Model '{model_name}' was pulled but is not showing as available"
        )

    logger.info("Model '%s' is now available", model_name)
    return True, True
