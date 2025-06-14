"""Pytest configuration file."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_config():
    """Fixture for a mock Config object."""
    config = MagicMock()
    config.ollama_base_url = "http://localhost:11434"
    config.ollama_model = "test-model"
    config.interactive_threshold = 90
    return config
