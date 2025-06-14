"""Tests for the Ollama manager module."""

import subprocess
from unittest.mock import Mock, patch

import pytest
import requests

from automake.utils.ollama_manager import (
    OllamaManagerError,
    ensure_model_available,
    ensure_ollama_running,
    get_available_models,
    is_model_available,
    is_ollama_running,
    pull_model,
    start_ollama_server,
    wait_for_ollama_ready,
)


class TestIsOllamaRunning:
    """Test cases for is_ollama_running function."""

    @patch("requests.get")
    def test_ollama_running_success(self, mock_get):
        """Test successful detection of running Ollama."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = is_ollama_running("http://localhost:11434")

        assert result is True
        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)

    @patch("requests.get")
    def test_ollama_not_running_connection_error(self, mock_get):
        """Test detection when Ollama is not running (connection error)."""
        mock_get.side_effect = requests.ConnectionError("Connection refused")

        result = is_ollama_running("http://localhost:11434")

        assert result is False

    @patch("requests.get")
    def test_ollama_not_running_bad_status(self, mock_get):
        """Test detection when Ollama returns non-200 status."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = is_ollama_running("http://localhost:11434")

        assert result is False

    @patch("requests.get")
    def test_ollama_running_with_custom_timeout(self, mock_get):
        """Test with custom timeout parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = is_ollama_running("http://localhost:11434", timeout=10)

        assert result is True
        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=10)


class TestStartOllamaServer:
    """Test cases for start_ollama_server function."""

    @patch("subprocess.Popen")
    @patch("time.sleep")
    def test_start_ollama_success(self, mock_sleep, mock_popen):
        """Test successful Ollama startup."""
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process still running
        mock_popen.return_value = mock_process

        result = start_ollama_server()

        assert result is True
        mock_popen.assert_called_once_with(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        mock_sleep.assert_called_once_with(2)

    @patch("subprocess.Popen")
    @patch("time.sleep")
    def test_start_ollama_process_exits(self, mock_sleep, mock_popen):
        """Test when Ollama process exits immediately."""
        mock_process = Mock()
        mock_process.poll.return_value = 1  # Process exited with code 1
        mock_popen.return_value = mock_process

        result = start_ollama_server()

        assert result is False

    @patch("subprocess.Popen")
    def test_start_ollama_command_not_found(self, mock_popen):
        """Test when Ollama command is not found."""
        mock_popen.side_effect = FileNotFoundError("ollama command not found")

        with pytest.raises(OllamaManagerError, match="Ollama command not found"):
            start_ollama_server()

    @patch("subprocess.Popen")
    def test_start_ollama_unexpected_error(self, mock_popen):
        """Test handling of unexpected errors during startup."""
        mock_popen.side_effect = Exception("Unexpected error")

        with pytest.raises(OllamaManagerError, match="Failed to start Ollama server"):
            start_ollama_server()


class TestWaitForOllamaReady:
    """Test cases for wait_for_ollama_ready function."""

    @patch("automake.utils.ollama_manager.is_ollama_running")
    @patch("time.sleep")
    def test_wait_for_ollama_ready_immediate(self, mock_sleep, mock_is_running):
        """Test when Ollama is ready immediately."""
        mock_is_running.return_value = True

        result = wait_for_ollama_ready("http://localhost:11434", max_wait=10)

        assert result is True
        mock_is_running.assert_called_once_with("http://localhost:11434")
        mock_sleep.assert_not_called()

    @patch("automake.utils.ollama_manager.is_ollama_running")
    @patch("time.sleep")
    @patch("time.time")
    def test_wait_for_ollama_ready_after_delay(
        self, mock_time, mock_sleep, mock_is_running
    ):
        """Test when Ollama becomes ready after a delay."""
        # Mock time progression
        mock_time.side_effect = [
            0,
            1,
            2,
            3,
        ]  # Start, first check, second check, third check
        mock_is_running.side_effect = [
            False,
            False,
            True,
        ]  # Not ready, not ready, ready

        result = wait_for_ollama_ready("http://localhost:11434", max_wait=10)

        assert result is True
        assert mock_is_running.call_count == 3

    @patch("automake.utils.ollama_manager.is_ollama_running")
    @patch("time.sleep")
    @patch("time.time")
    def test_wait_for_ollama_ready_timeout(
        self, mock_time, mock_sleep, mock_is_running
    ):
        """Test when Ollama doesn't become ready within timeout."""
        # Mock time progression to exceed max_wait
        mock_time.side_effect = [0, 5, 10, 15, 20, 25, 30, 35]
        mock_is_running.return_value = False

        result = wait_for_ollama_ready("http://localhost:11434", max_wait=10)

        assert result is False


class TestEnsureOllamaRunning:
    """Test cases for ensure_ollama_running function."""

    @patch("automake.utils.ollama_manager.is_ollama_running")
    def test_ensure_ollama_already_running(self, mock_is_running, mock_config):
        """Test when Ollama is already running."""
        mock_is_running.return_value = True

        is_running, was_started = ensure_ollama_running(mock_config)

        assert is_running is True
        assert was_started is False

    @patch("automake.utils.ollama_manager.wait_for_ollama_ready")
    @patch("automake.utils.ollama_manager.start_ollama_server")
    @patch("automake.utils.ollama_manager.is_ollama_running")
    def test_ensure_ollama_start_success(
        self, mock_is_running, mock_start, mock_wait, mock_config
    ):
        """Test successful automatic startup of Ollama."""
        mock_is_running.return_value = False  # Not running initially
        mock_start.return_value = True  # Started successfully
        mock_wait.return_value = True  # Became ready

        is_running, was_started = ensure_ollama_running(mock_config)

        assert is_running is True
        assert was_started is True
        mock_start.assert_called_once()
        mock_wait.assert_called_once_with(mock_config.ollama_base_url, max_wait=15)

    @patch("automake.utils.ollama_manager.start_ollama_server")
    @patch("automake.utils.ollama_manager.is_ollama_running")
    def test_ensure_ollama_start_failure(
        self, mock_is_running, mock_start, mock_config
    ):
        """Test when Ollama fails to start."""
        mock_is_running.return_value = False  # Not running initially
        mock_start.return_value = False  # Failed to start

        with pytest.raises(OllamaManagerError, match="Failed to start Ollama server"):
            ensure_ollama_running(mock_config)

    @patch("automake.utils.ollama_manager.wait_for_ollama_ready")
    @patch("automake.utils.ollama_manager.start_ollama_server")
    @patch("automake.utils.ollama_manager.is_ollama_running")
    def test_ensure_ollama_not_ready_timeout(
        self, mock_is_running, mock_start, mock_wait, mock_config
    ):
        """Test when Ollama starts but doesn't become ready in time."""
        mock_is_running.return_value = False  # Not running initially
        mock_start.return_value = True  # Started successfully
        mock_wait.return_value = False  # Didn't become ready in time

        with pytest.raises(
            OllamaManagerError, match="did not become ready within 15 seconds"
        ):
            ensure_ollama_running(mock_config)


class TestGetAvailableModels:
    """Test cases for get_available_models function."""

    @patch("automake.utils.ollama_manager.ollama")
    def test_get_available_models_success(self, mock_ollama):
        """Test successful retrieval of available models."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client

        # Mock response with models attribute
        mock_response = Mock()
        mock_response.models = [
            Mock(model="qwen3:0.6b"),
            Mock(model="llama2:7b"),
        ]
        mock_client.list.return_value = mock_response

        result = get_available_models("http://localhost:11434")

        assert result == ["qwen3:0.6b", "llama2:7b"]
        mock_ollama.Client.assert_called_once_with(host="http://localhost:11434")

    @patch("automake.utils.ollama_manager.ollama")
    def test_get_available_models_dict_format(self, mock_ollama):
        """Test with dictionary format response."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client

        mock_client.list.return_value = {
            "models": [
                {"name": "qwen3:0.6b"},
                {"name": "llama2:7b"},
            ]
        }

        result = get_available_models("http://localhost:11434")

        assert result == ["qwen3:0.6b", "llama2:7b"]

    @patch("automake.utils.ollama_manager.ollama")
    def test_get_available_models_connection_error(self, mock_ollama):
        """Test when connection to Ollama fails."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client
        mock_client.list.side_effect = Exception("Connection failed")

        with pytest.raises(OllamaManagerError, match="Failed to retrieve models"):
            get_available_models("http://localhost:11434")


class TestIsModelAvailable:
    """Test cases for is_model_available function."""

    @patch("automake.utils.ollama_manager.get_available_models")
    def test_is_model_available_true(self, mock_get_models):
        """Test when model is available."""
        mock_get_models.return_value = ["qwen3:0.6b", "llama2:7b"]

        result = is_model_available("http://localhost:11434", "qwen3:0.6b")

        assert result is True

    @patch("automake.utils.ollama_manager.get_available_models")
    def test_is_model_available_false(self, mock_get_models):
        """Test when model is not available."""
        mock_get_models.return_value = ["llama2:7b"]

        result = is_model_available("http://localhost:11434", "qwen3:0.6b")

        assert result is False

    @patch("automake.utils.ollama_manager.get_available_models")
    def test_is_model_available_error(self, mock_get_models):
        """Test when get_available_models raises an error."""
        mock_get_models.side_effect = OllamaManagerError("Connection failed")

        result = is_model_available("http://localhost:11434", "qwen3:0.6b")

        assert result is False


class TestPullModel:
    """Test cases for pull_model function."""

    @patch("automake.utils.ollama_manager.ollama")
    def test_pull_model_success(self, mock_ollama):
        """Test successful model pull."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client

        result = pull_model("http://localhost:11434", "qwen3:0.6b")

        assert result is True
        mock_client.pull.assert_called_once_with("qwen3:0.6b")

    @patch("automake.utils.ollama_manager.ollama")
    def test_pull_model_failure(self, mock_ollama):
        """Test when model pull fails."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client
        mock_client.pull.side_effect = Exception("Pull failed")

        with pytest.raises(OllamaManagerError, match="Failed to pull model"):
            pull_model("http://localhost:11434", "qwen3:0.6b")


class TestEnsureModelAvailable:
    """Test cases for ensure_model_available function."""

    @patch("automake.utils.ollama_manager.is_model_available")
    @patch("automake.utils.ollama_manager.ensure_ollama_running")
    def test_ensure_model_already_available(
        self, mock_ensure_ollama, mock_is_available, mock_config
    ):
        """Test when model is already available."""
        mock_ensure_ollama.return_value = (True, False)
        mock_is_available.return_value = True

        is_available, was_pulled = ensure_model_available(mock_config)

        assert is_available is True
        assert was_pulled is False

    @patch("automake.utils.ollama_manager.is_model_available")
    @patch("automake.utils.ollama_manager.pull_model")
    @patch("automake.utils.ollama_manager.ensure_ollama_running")
    def test_ensure_model_pull_success(
        self, mock_ensure_ollama, mock_pull, mock_is_available, mock_config
    ):
        """Test successful model pull when not available."""
        mock_ensure_ollama.return_value = (True, False)
        mock_is_available.side_effect = [
            False,
            True,
        ]  # Not available, then available after pull
        mock_pull.return_value = True

        is_available, was_pulled = ensure_model_available(mock_config)

        assert is_available is True
        assert was_pulled is True
        mock_pull.assert_called_once_with(
            mock_config.ollama_base_url, mock_config.ollama_model
        )

    @patch("automake.utils.ollama_manager.ensure_ollama_running")
    def test_ensure_model_ollama_not_running(self, mock_ensure_ollama, mock_config):
        """Test when Ollama cannot be started."""
        mock_ensure_ollama.return_value = (False, False)

        with pytest.raises(OllamaManagerError, match="Ollama server is not running"):
            ensure_model_available(mock_config)

    @patch("automake.utils.ollama_manager.is_model_available")
    @patch("automake.utils.ollama_manager.pull_model")
    @patch("automake.utils.ollama_manager.ensure_ollama_running")
    def test_ensure_model_pull_failure(
        self, mock_ensure_ollama, mock_pull, mock_is_available, mock_config
    ):
        """Test when model pull fails."""
        mock_ensure_ollama.return_value = (True, False)
        mock_is_available.return_value = False
        mock_pull.return_value = False

        with pytest.raises(OllamaManagerError, match="Failed to pull model"):
            ensure_model_available(mock_config)
