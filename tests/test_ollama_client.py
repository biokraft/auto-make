"""Tests for the Ollama client module."""

import logging
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from ollama import ResponseError

from automake.config import Config
from automake.core.ollama_client import (
    AsyncOllamaClient,
    OllamaClient,
    OllamaClientError,
    create_async_ollama_client,
    create_ollama_client,
)


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Config(config_dir=Path(temp_dir))
        return config


@pytest.fixture
def mock_ollama_client():
    """Create a mock ollama.Client for testing."""
    return Mock()


@pytest.fixture
def mock_async_ollama_client():
    """Create a mock ollama.AsyncClient for testing."""
    return AsyncMock()


class TestOllamaClient:
    """Test cases for OllamaClient."""

    def test_init(self, mock_config):
        """Test OllamaClient initialization."""
        with patch("automake.core.ollama_client.Client") as mock_client_class:
            client = OllamaClient(mock_config)

            assert client.config == mock_config
            assert client.base_url == mock_config.ollama_base_url
            assert client.model == mock_config.ollama_model
            mock_client_class.assert_called_once_with(host=mock_config.ollama_base_url)

    def test_validate_connection_success(self, mock_config, mock_ollama_client):
        """Test successful connection validation."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            client = OllamaClient(mock_config)
            mock_ollama_client.list.return_value = {"models": []}

            result = client.validate_connection()

            assert result is True
            mock_ollama_client.list.assert_called_once()

    def test_validate_connection_response_error(self, mock_config, mock_ollama_client):
        """Test connection validation with ResponseError."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            client = OllamaClient(mock_config)
            mock_ollama_client.list.side_effect = ResponseError("Server error")

            with pytest.raises(OllamaClientError, match="Ollama server error"):
                client.validate_connection()

    def test_validate_connection_generic_error(self, mock_config, mock_ollama_client):
        """Test connection validation with generic error."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            client = OllamaClient(mock_config)
            mock_ollama_client.list.side_effect = ConnectionError("Connection refused")

            with pytest.raises(
                OllamaClientError, match="Failed to connect to Ollama server"
            ):
                client.validate_connection()

    def test_validate_model_success(self, mock_config, mock_ollama_client):
        """Test successful model validation."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            client = OllamaClient(mock_config)
            mock_ollama_client.show.return_value = {"model": "gemma3:4b"}

            result = client.validate_model()

            assert result is True
            mock_ollama_client.show.assert_called_once_with(mock_config.ollama_model)

    def test_validate_model_not_found(self, mock_config, mock_ollama_client):
        """Test model validation when model is not found."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            client = OllamaClient(mock_config)
            error = ResponseError("Model not found")
            error.status_code = 404
            mock_ollama_client.show.side_effect = error

            with pytest.raises(OllamaClientError, match="Model .* not found"):
                client.validate_model()

    def test_validate_model_other_response_error(self, mock_config, mock_ollama_client):
        """Test model validation with other ResponseError."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            client = OllamaClient(mock_config)
            error = ResponseError("Server error")
            error.status_code = 500
            mock_ollama_client.show.side_effect = error

            with pytest.raises(OllamaClientError, match="Error checking model"):
                client.validate_model()

    def test_chat_success(self, mock_config, mock_ollama_client):
        """Test successful chat request."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            client = OllamaClient(mock_config)
            messages = [{"role": "user", "content": "Hello"}]
            expected_response = {"message": {"content": "Hi there!"}}
            mock_ollama_client.chat.return_value = expected_response

            result = client.chat(messages)

            assert result == expected_response
            mock_ollama_client.chat.assert_called_once_with(
                model=mock_config.ollama_model, messages=messages, stream=False
            )

    def test_chat_with_stream(self, mock_config, mock_ollama_client):
        """Test chat request with streaming."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            client = OllamaClient(mock_config)
            messages = [{"role": "user", "content": "Hello"}]

            client.chat(messages, stream=True)

            mock_ollama_client.chat.assert_called_once_with(
                model=mock_config.ollama_model, messages=messages, stream=True
            )

    def test_chat_response_error(self, mock_config, mock_ollama_client):
        """Test chat request with ResponseError."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            client = OllamaClient(mock_config)
            messages = [{"role": "user", "content": "Hello"}]
            mock_ollama_client.chat.side_effect = ResponseError("Chat error")

            with pytest.raises(OllamaClientError, match="Ollama chat error"):
                client.chat(messages)

    def test_generate_success(self, mock_config, mock_ollama_client):
        """Test successful generation request."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            client = OllamaClient(mock_config)
            prompt = "What is the sky blue?"
            expected_response = {
                "response": "The sky is blue due to Rayleigh scattering."
            }
            mock_ollama_client.generate.return_value = expected_response

            result = client.generate(prompt)

            assert result == expected_response
            mock_ollama_client.generate.assert_called_once_with(
                model=mock_config.ollama_model, prompt=prompt, stream=False
            )

    def test_generate_response_error(self, mock_config, mock_ollama_client):
        """Test generation request with ResponseError."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            client = OllamaClient(mock_config)
            prompt = "Test prompt"
            mock_ollama_client.generate.side_effect = ResponseError("Generation error")

            with pytest.raises(OllamaClientError, match="Ollama generation error"):
                client.generate(prompt)

    def test_list_models_success(self, mock_config, mock_ollama_client):
        """Test successful model listing."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            client = OllamaClient(mock_config)
            expected_models = [{"name": "gemma3:4b"}, {"name": "llama3.2"}]
            mock_ollama_client.list.return_value = {"models": expected_models}

            result = client.list_models()

            assert result == expected_models
            mock_ollama_client.list.assert_called_once()

    def test_list_models_response_error(self, mock_config, mock_ollama_client):
        """Test model listing with ResponseError."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            client = OllamaClient(mock_config)
            mock_ollama_client.list.side_effect = ResponseError("List error")

            with pytest.raises(OllamaClientError, match="Error listing models"):
                client.list_models()


class TestAsyncOllamaClient:
    """Test cases for AsyncOllamaClient."""

    def test_init(self, mock_config):
        """Test AsyncOllamaClient initialization."""
        with patch("automake.core.ollama_client.AsyncClient") as mock_client_class:
            client = AsyncOllamaClient(mock_config)

            assert client.config == mock_config
            assert client.base_url == mock_config.ollama_base_url
            assert client.model == mock_config.ollama_model
            mock_client_class.assert_called_once_with(host=mock_config.ollama_base_url)

    @pytest.mark.asyncio
    async def test_validate_connection_success(
        self, mock_config, mock_async_ollama_client
    ):
        """Test successful async connection validation."""
        with patch(
            "automake.core.ollama_client.AsyncClient",
            return_value=mock_async_ollama_client,
        ):
            client = AsyncOllamaClient(mock_config)
            mock_async_ollama_client.list.return_value = {"models": []}

            result = await client.validate_connection()

            assert result is True
            mock_async_ollama_client.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_connection_response_error(
        self, mock_config, mock_async_ollama_client
    ):
        """Test async connection validation with ResponseError."""
        with patch(
            "automake.core.ollama_client.AsyncClient",
            return_value=mock_async_ollama_client,
        ):
            client = AsyncOllamaClient(mock_config)
            mock_async_ollama_client.list.side_effect = ResponseError("Server error")

            with pytest.raises(OllamaClientError, match="Ollama server error"):
                await client.validate_connection()

    @pytest.mark.asyncio
    async def test_validate_model_success(self, mock_config, mock_async_ollama_client):
        """Test successful async model validation."""
        with patch(
            "automake.core.ollama_client.AsyncClient",
            return_value=mock_async_ollama_client,
        ):
            client = AsyncOllamaClient(mock_config)
            mock_async_ollama_client.show.return_value = {"model": "gemma3:4b"}

            result = await client.validate_model()

            assert result is True
            mock_async_ollama_client.show.assert_called_once_with(
                mock_config.ollama_model
            )

    @pytest.mark.asyncio
    async def test_validate_model_not_found(
        self, mock_config, mock_async_ollama_client
    ):
        """Test async model validation when model is not found."""
        with patch(
            "automake.core.ollama_client.AsyncClient",
            return_value=mock_async_ollama_client,
        ):
            client = AsyncOllamaClient(mock_config)
            error = ResponseError("Model not found")
            error.status_code = 404
            mock_async_ollama_client.show.side_effect = error

            with pytest.raises(OllamaClientError, match="Model .* not found"):
                await client.validate_model()

    @pytest.mark.asyncio
    async def test_chat_success(self, mock_config, mock_async_ollama_client):
        """Test successful async chat request."""
        with patch(
            "automake.core.ollama_client.AsyncClient",
            return_value=mock_async_ollama_client,
        ):
            client = AsyncOllamaClient(mock_config)
            messages = [{"role": "user", "content": "Hello"}]
            expected_response = {"message": {"content": "Hi there!"}}
            mock_async_ollama_client.chat.return_value = expected_response

            result = await client.chat(messages)

            assert result == expected_response
            mock_async_ollama_client.chat.assert_called_once_with(
                model=mock_config.ollama_model, messages=messages, stream=False
            )

    @pytest.mark.asyncio
    async def test_chat_response_error(self, mock_config, mock_async_ollama_client):
        """Test async chat request with ResponseError."""
        with patch(
            "automake.core.ollama_client.AsyncClient",
            return_value=mock_async_ollama_client,
        ):
            client = AsyncOllamaClient(mock_config)
            messages = [{"role": "user", "content": "Hello"}]
            mock_async_ollama_client.chat.side_effect = ResponseError("Chat error")

            with pytest.raises(OllamaClientError, match="Ollama chat error"):
                await client.chat(messages)

    @pytest.mark.asyncio
    async def test_generate_success(self, mock_config, mock_async_ollama_client):
        """Test successful async generation request."""
        with patch(
            "automake.core.ollama_client.AsyncClient",
            return_value=mock_async_ollama_client,
        ):
            client = AsyncOllamaClient(mock_config)
            prompt = "What is the sky blue?"
            expected_response = {
                "response": "The sky is blue due to Rayleigh scattering."
            }
            mock_async_ollama_client.generate.return_value = expected_response

            result = await client.generate(prompt)

            assert result == expected_response
            mock_async_ollama_client.generate.assert_called_once_with(
                model=mock_config.ollama_model, prompt=prompt, stream=False
            )

    @pytest.mark.asyncio
    async def test_list_models_success(self, mock_config, mock_async_ollama_client):
        """Test successful async model listing."""
        with patch(
            "automake.core.ollama_client.AsyncClient",
            return_value=mock_async_ollama_client,
        ):
            client = AsyncOllamaClient(mock_config)
            expected_models = [{"name": "gemma3:4b"}, {"name": "llama3.2"}]
            mock_async_ollama_client.list.return_value = {"models": expected_models}

            result = await client.list_models()

            assert result == expected_models
            mock_async_ollama_client.list.assert_called_once()


class TestFactoryFunctions:
    """Test cases for factory functions."""

    def test_create_ollama_client_success(self, mock_config, mock_ollama_client):
        """Test successful client creation."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            mock_ollama_client.list.return_value = {"models": []}
            mock_ollama_client.show.return_value = {"model": "gemma3:4b"}

            client = create_ollama_client(mock_config)

            assert isinstance(client, OllamaClient)
            assert client.config == mock_config
            mock_ollama_client.list.assert_called_once()
            mock_ollama_client.show.assert_called_once_with(mock_config.ollama_model)

    def test_create_ollama_client_connection_failure(
        self, mock_config, mock_ollama_client
    ):
        """Test client creation with connection failure."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            mock_ollama_client.list.side_effect = ConnectionError("Connection refused")

            with pytest.raises(
                OllamaClientError, match="Failed to connect to Ollama server"
            ):
                create_ollama_client(mock_config)

    def test_create_ollama_client_model_not_found(
        self, mock_config, mock_ollama_client
    ):
        """Test client creation with model not found."""
        with patch(
            "automake.core.ollama_client.Client", return_value=mock_ollama_client
        ):
            mock_ollama_client.list.return_value = {"models": []}
            error = ResponseError("Model not found")
            error.status_code = 404
            mock_ollama_client.show.side_effect = error

            with pytest.raises(OllamaClientError, match="Model .* not found"):
                create_ollama_client(mock_config)

    @pytest.mark.asyncio
    async def test_create_async_ollama_client_success(
        self, mock_config, mock_async_ollama_client
    ):
        """Test successful async client creation."""
        with patch(
            "automake.core.ollama_client.AsyncClient",
            return_value=mock_async_ollama_client,
        ):
            mock_async_ollama_client.list.return_value = {"models": []}
            mock_async_ollama_client.show.return_value = {"model": "gemma3:4b"}

            client = await create_async_ollama_client(mock_config)

            assert isinstance(client, AsyncOllamaClient)
            assert client.config == mock_config
            mock_async_ollama_client.list.assert_called_once()
            mock_async_ollama_client.show.assert_called_once_with(
                mock_config.ollama_model
            )

    @pytest.mark.asyncio
    async def test_create_async_ollama_client_connection_failure(
        self, mock_config, mock_async_ollama_client
    ):
        """Test async client creation with connection failure."""
        with patch(
            "automake.core.ollama_client.AsyncClient",
            return_value=mock_async_ollama_client,
        ):
            mock_async_ollama_client.list.side_effect = ConnectionError(
                "Connection refused"
            )

            with pytest.raises(
                OllamaClientError, match="Failed to connect to Ollama server"
            ):
                await create_async_ollama_client(mock_config)


class TestIntegration:
    """Integration tests for Ollama client."""

    def test_client_with_real_config_structure(self):
        """Test client with real config structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(config_dir=Path(temp_dir))

            with patch("automake.core.ollama_client.Client") as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                mock_client.list.return_value = {"models": []}
                mock_client.show.return_value = {"model": "gemma3:4b"}

                client = OllamaClient(config)

                # Test that config values are properly used
                assert client.base_url == "http://localhost:11434"
                assert client.model == "gemma3:4b"
                mock_client_class.assert_called_once_with(host="http://localhost:11434")

    def test_error_propagation(self, mock_config):
        """Test that errors are properly propagated with context."""
        with patch("automake.core.ollama_client.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Test ResponseError propagation
            error = ResponseError("Detailed server error")
            error.status_code = 500
            mock_client.list.side_effect = error

            client = OllamaClient(mock_config)

            with pytest.raises(OllamaClientError) as exc_info:
                client.validate_connection()

            assert "Ollama server error: Detailed server error" in str(exc_info.value)
            assert exc_info.value.__cause__ == error

    def test_logging_integration(self, mock_config):
        """Test that logging works correctly."""

        with patch("automake.core.ollama_client.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Create a custom handler to capture log messages
            log_messages = []

            class TestHandler(logging.Handler):
                def emit(self, record):
                    log_messages.append(self.format(record))

            # Set up the logger with our test handler
            logger = logging.getLogger("automake.core.ollama_client")
            handler = TestHandler()
            handler.setLevel(logging.INFO)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

            try:
                OllamaClient(mock_config)

                # Check that the initialization message was logged
                init_messages = [
                    msg for msg in log_messages if "Initialized Ollama client" in msg
                ]
                assert len(init_messages) > 0, (
                    f"Expected initialization log message, got: {log_messages}"
                )

                # Check that the message contains expected details
                init_msg = init_messages[0]
                assert "base_url=http://localhost:11434" in init_msg
                assert "model=gemma3:4b" in init_msg

            finally:
                # Clean up the handler
                logger.removeHandler(handler)
