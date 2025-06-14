"""Tests for the AI Agent module."""

import json
from unittest.mock import patch

import pytest

from automake.core.ai_agent import (
    CommandInterpretationError,
    CommandResponse,
    MakefileCommandAgent,
    create_ai_agent,
)


# Test CommandResponse JSON parsing
@pytest.mark.parametrize(
    ("json_str", "expected_command", "expected_confidence"),
    [
        (
            '{"reasoning": "test", "command": "build", "alternatives": [], '
            '"confidence": 100}',
            "build",
            100,
        ),
        (
            '```json\n{"reasoning": "test", "command": null, "alternatives": '
            '["test"], "confidence": 0}\n```',
            None,
            0,
        ),
        (
            '{"reasoning": "str", "command": "cmd", "alternatives": [], '
            '"confidence": "90"}',
            "cmd",
            90,
        ),
    ],
)
def test_command_response_from_json_valid(
    json_str, expected_command, expected_confidence
):
    response = CommandResponse.from_json(json_str)
    assert response.command == expected_command
    assert response.confidence == expected_confidence


@pytest.mark.parametrize(
    ("invalid_json", "error_message"),
    [
        ("not json", "Invalid JSON"),
        ('{"reasoning": "test"}', "Missing required fields"),
        (
            '{"reasoning": 1, "command": "c", "alternatives": [], "confidence": 1}',
            "'reasoning' must be a string",
        ),
        (
            '{"reasoning": "r", "command": 1, "alternatives": [], "confidence": 1}',
            "'command' must be a string or null",
        ),
        (
            '{"reasoning": "r", "command": "c", "alternatives": "a", "confidence": 1}',
            "'alternatives' must be a list",
        ),
        (
            '{"reasoning": "r", "command": "c", "alternatives": [1], "confidence": 1}',
            "items in 'alternatives' must be strings",
        ),
        (
            '{"reasoning": "r", "command": "c", "alternatives": [], "confidence": "c"}',
            "'confidence' must be an integer",
        ),
        (
            '{"reasoning": "r", "command": "c", "alternatives": [], "confidence": 101}',
            "between 0 and 100",
        ),
        (
            '{"reasoning": "r", "command": null, "alternatives": [], "confidence": 50}',
            "If 'command' is null",
        ),
    ],
)
def test_command_response_from_json_invalid(invalid_json, error_message):
    with pytest.raises(CommandInterpretationError, match=error_message):
        CommandResponse.from_json(invalid_json)


# Test MakefileCommandAgent
@patch("automake.core.ai_agent.ensure_ollama_running")
@patch("automake.core.ai_agent.ollama")
@patch("automake.core.ai_agent.LiteLLMModel")
def test_create_ai_agent_success(
    mock_litellm, mock_ollama, mock_ensure_ollama, mock_config
):
    """Test successful creation of AI agent."""
    # Mock Ollama management
    mock_ensure_ollama.return_value = (
        True,
        False,
    )  # Running, not started automatically

    # Mock validation methods to succeed
    mock_ollama.Client.return_value.list.return_value = {
        "models": [{"name": "qwen3:0.6b"}]
    }

    agent, was_started = create_ai_agent(mock_config)
    assert isinstance(agent, MakefileCommandAgent)
    assert was_started is False
    mock_litellm.assert_called_once()


@patch("automake.core.ai_agent.ensure_ollama_running")
@patch("automake.core.ai_agent.ollama")
@patch("automake.core.ai_agent.LiteLLMModel")
def test_create_ai_agent_connection_error(
    mock_litellm, mock_ollama, mock_ensure_ollama, mock_config
):
    """Test connection error during agent creation."""
    # Mock Ollama management to succeed
    mock_ensure_ollama.return_value = (True, False)

    mock_ollama.Client.return_value.list.side_effect = Exception("Connection failed")
    with pytest.raises(CommandInterpretationError, match="Failed to create AI agent"):
        create_ai_agent(mock_config)


@patch("automake.core.ai_agent.ensure_ollama_running")
@patch("automake.core.ai_agent.ollama")
@patch("automake.core.ai_agent.LiteLLMModel")
def test_create_ai_agent_model_not_found(
    mock_litellm, mock_ollama, mock_ensure_ollama, mock_config
):
    """Test model not found error during agent creation."""
    # Mock Ollama management to succeed
    mock_ensure_ollama.return_value = (True, False)

    mock_ollama.Client.return_value.list.return_value = {
        "models": [{"name": "other-model"}]
    }

    with pytest.raises(
        CommandInterpretationError, match="Model 'qwen3:0.6b' not found"
    ):
        create_ai_agent(mock_config)


@patch("automake.core.ai_agent.ensure_ollama_running")
@patch("automake.core.ai_agent.ollama")
@patch("automake.core.ai_agent.LiteLLMModel")
def test_create_ai_agent_ollama_started_automatically(
    mock_litellm, mock_ollama, mock_ensure_ollama, mock_config
):
    """Test that the function returns True when Ollama is started automatically."""
    # Mock Ollama management to indicate it was started automatically
    mock_ensure_ollama.return_value = (True, True)  # Running, started automatically

    # Mock validation methods to succeed
    mock_ollama.Client.return_value.list.return_value = {
        "models": [{"name": "qwen3:0.6b"}]
    }

    agent, was_started = create_ai_agent(mock_config)
    assert isinstance(agent, MakefileCommandAgent)
    assert was_started is True
    mock_litellm.assert_called_once()


@patch("automake.core.ai_agent.ensure_ollama_running")
def test_create_ai_agent_ollama_startup_failure(mock_ensure_ollama, mock_config):
    """Test OllamaManagerError is properly converted to CommandInterpretationError."""
    from automake.utils.ollama_manager import OllamaManagerError

    # Mock Ollama management to fail
    mock_ensure_ollama.side_effect = OllamaManagerError("Failed to start Ollama")

    with pytest.raises(CommandInterpretationError, match="Failed to start Ollama"):
        create_ai_agent(mock_config)


@patch("automake.core.ai_agent.ollama")
@patch("automake.core.ai_agent.CodeAgent")
@patch("automake.core.ai_agent.LiteLLMModel")
def test_interpret_command_success(
    mock_litellm, mock_code_agent, mock_ollama, mock_config
):
    """Test successful command interpretation."""
    # Setup mock agent
    agent_instance = mock_code_agent.return_value
    mock_response = {
        "reasoning": "The user wants to build.",
        "command": "build",
        "alternatives": ["all"],
        "confidence": 95,
    }
    agent_instance.run.return_value = json.dumps(mock_response)

    # Create agent
    agent = MakefileCommandAgent(mock_config)
    agent.agent = agent_instance  # Inject mocked CodeAgent

    # Run interpretation
    response = agent.interpret_command("build the project", ["build", "all"])
    assert response.command == "build"
    assert response.confidence == 95
    agent_instance.run.assert_called_once()


@patch("automake.core.ai_agent.ollama")
@patch("automake.core.ai_agent.CodeAgent")
@patch("automake.core.ai_agent.LiteLLMModel")
def test_interpret_command_json_error(
    mock_litellm, mock_code_agent, mock_ollama, mock_config
):
    """Test that a JSON parsing error is handled."""
    agent_instance = mock_code_agent.return_value
    agent_instance.run.return_value = "This is not JSON"

    agent = MakefileCommandAgent(mock_config)
    agent.agent = agent_instance

    with pytest.raises(CommandInterpretationError, match="Invalid JSON response"):
        agent.interpret_command("test", ["test"])
