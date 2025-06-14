"""Core functionality for AutoMake.

This module contains the core business logic for reading and processing Makefiles.
"""

from .makefile_reader import MakefileNotFoundError, MakefileReader
from .ollama_client import (
    AsyncOllamaClient,
    OllamaClient,
    OllamaClientError,
    create_async_ollama_client,
    create_ollama_client,
)

__all__ = [
    "MakefileReader",
    "MakefileNotFoundError",
    "OllamaClient",
    "AsyncOllamaClient",
    "OllamaClientError",
    "create_ollama_client",
    "create_async_ollama_client",
]
