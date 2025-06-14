"""AI Agent module for AutoMake.

This module implements the smolagent responsible for interpreting natural language
commands and translating them into Makefile targets using Ollama LLM.
"""

import io
import json
import logging
import warnings
from contextlib import redirect_stderr, redirect_stdout

import ollama
from smolagents import CodeAgent, LiteLLMModel

from ..config import Config

# Suppress Pydantic serialization warnings from LiteLLM
warnings.filterwarnings(
    "ignore",
    message=".*PydanticSerializationUnexpectedValue.*",
    category=UserWarning,
    module="pydantic.*",
)

# Also suppress the broader Pydantic serializer warnings
warnings.filterwarnings(
    "ignore",
    message=".*Pydantic serializer warnings.*",
    category=UserWarning,
)

logger = logging.getLogger(__name__)


class CommandInterpretationError(Exception):
    """Raised when there's an error interpreting the command."""

    pass


class CommandResponse:
    """Represents the response from the AI agent for command interpretation."""

    def __init__(
        self,
        reasoning: str,
        command: str | None,
        alternatives: list[str],
        confidence: int,
    ):
        """Initialize the command response.

        Args:
            reasoning: Brief explanation of why the command was chosen
            command: The most appropriate make target (None if no suitable command
                found)
            alternatives: List of alternative commands that could be relevant
            confidence: Confidence level (0-100) in the chosen command
        """
        self.reasoning = reasoning
        self.command = command
        self.alternatives = alternatives
        self.confidence = confidence

    @classmethod
    def from_json(cls, json_str: str) -> "CommandResponse":
        """Parse a CommandResponse from JSON string.

        Args:
            json_str: JSON string containing the response data

        Returns:
            CommandResponse instance

        Raises:
            CommandInterpretationError: If JSON parsing fails or required fields
                are missing
        """
        try:
            # Handle JSON wrapped in markdown code blocks
            if "```json" in json_str:
                start = json_str.find("```json") + 7
                end = json_str.find("```", start)
                json_str = json_str[start:end].strip()
            elif "```" in json_str:
                start = json_str.find("```") + 3
                end = json_str.find("```", start)
                json_str = json_str[start:end].strip()

            data = json.loads(json_str)

            # Validate required fields
            required_fields = ["reasoning", "command", "alternatives", "confidence"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise CommandInterpretationError(
                    f"Missing required fields: {missing_fields}"
                )

            # Validate types and values
            if not isinstance(data["reasoning"], str):
                raise CommandInterpretationError("'reasoning' must be a string")
            if data["command"] is not None and not isinstance(data["command"], str):
                raise CommandInterpretationError("'command' must be a string or null")
            if not isinstance(data["alternatives"], list):
                raise CommandInterpretationError("'alternatives' must be a list")
            if not all(isinstance(alt, str) for alt in data["alternatives"]):
                raise CommandInterpretationError(
                    "All items in 'alternatives' must be strings"
                )

            # Handle confidence as string or int
            if isinstance(data["confidence"], str):
                try:
                    data["confidence"] = int(data["confidence"])
                except ValueError as e:
                    raise CommandInterpretationError(
                        "'confidence' must be an integer"
                    ) from e
            elif not isinstance(data["confidence"], int):
                raise CommandInterpretationError("'confidence' must be an integer")

            if not 0 <= data["confidence"] <= 100:
                raise CommandInterpretationError(
                    "'confidence' must be between 0 and 100"
                )

            # Validate business logic
            if data["command"] is None and data["confidence"] != 0:
                raise CommandInterpretationError(
                    "If 'command' is null, 'confidence' must be 0"
                )

            return cls(
                reasoning=data["reasoning"],
                command=data["command"],
                alternatives=data["alternatives"] or [],
                confidence=data["confidence"],
            )

        except json.JSONDecodeError as e:
            raise CommandInterpretationError(f"Invalid JSON response: {e}") from e
        except (KeyError, TypeError) as e:
            raise CommandInterpretationError(f"Invalid response format: {e}") from e


class MakefileCommandAgent:
    """AI agent for interpreting natural language commands into Makefile targets."""

    def __init__(self, config: Config):
        """Initialize the AI agent.

        Args:
            config: Configuration object containing Ollama settings

        Raises:
            CommandInterpretationError: If agent initialization fails
        """
        self.config = config
        try:
            # Create LiteLLM model for Ollama
            model_name = f"ollama/{config.ollama_model}"
            self.model = LiteLLMModel(
                model_id=model_name,
                api_base=config.ollama_base_url,
            )

            # Initialize the CodeAgent with minimal tools
            self.agent = CodeAgent(
                tools=[],  # No tools needed for our use case
                model=self.model,
                max_steps=3,  # Allow a few steps for command interpretation
                additional_authorized_imports=["json"],  # Allow json import
            )

            logger.info("AI agent initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize AI agent: %s", e)
            raise CommandInterpretationError(
                f"Failed to initialize AI agent: {e}"
            ) from e

    def interpret_command(
        self, user_command: str, makefile_targets: list[str]
    ) -> CommandResponse:
        """Interpret a natural language command into a Makefile target.

        Args:
            user_command: The natural language command from the user
            makefile_targets: List of available Makefile targets

        Returns:
            CommandResponse with the interpretation results

        Raises:
            CommandInterpretationError: If command interpretation fails
        """
        try:
            # Create the prompt for command interpretation
            prompt = self._create_interpretation_prompt(user_command, makefile_targets)

            # Use the agent to interpret the command with output suppression
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                result = self.agent.run(prompt)

            # Parse the result as JSON
            response = CommandResponse.from_json(str(result))

            logger.info(
                "Command interpreted: %s -> %s (confidence: %d%%)",
                user_command,
                response.command,
                response.confidence,
            )

            return response

        except Exception as e:
            logger.error("Failed to interpret command '%s': %s", user_command, e)
            raise CommandInterpretationError(f"Failed to interpret command: {e}") from e

    def _create_interpretation_prompt(
        self, user_command: str, makefile_targets: list[str]
    ) -> str:
        """Create the prompt for command interpretation.

        Args:
            user_command: The user's natural language command
            makefile_targets: Available Makefile targets

        Returns:
            Formatted prompt string
        """
        targets_list = "\n".join(f"- {target}" for target in makefile_targets)

        return f"""You are an AI assistant that interprets natural language commands and maps them to Makefile targets.

Given the user command: "{user_command}"

Available Makefile targets:
{targets_list}

Your task is to analyze the user command and create a JSON response. Use the final_answer() function to return your result.

Write Python code that creates a JSON response with this structure:
{{
    "reasoning": "Brief explanation of why this command was chosen",
    "command": "most_appropriate_target_name_or_null",
    "alternatives": ["list", "of", "alternative", "targets"],
    "confidence": 85
}}

Rules:
1. If no suitable target exists, set "command" to null
2. Confidence should be 0-100 (0 = no match, 100 = perfect match)
3. Include 2-3 alternatives even if confidence is high
4. Consider semantic similarity, not just exact matches
5. Use final_answer() to return the JSON string

Example code structure:
```python
import json

# Analyze the command and targets
response = {{
    "reasoning": "Your reasoning here",
    "command": "target_name_or_null",
    "alternatives": ["alt1", "alt2"],
    "confidence": 85
}}

# Return the JSON response
final_answer(json.dumps(response))
```

Now analyze the command and provide your response:"""  # noqa: E501


def create_ai_agent(config: Config) -> MakefileCommandAgent:
    """Create and initialize an AI agent.

    Args:
        config: Configuration object

    Returns:
        Initialized MakefileCommandAgent

    Raises:
        CommandInterpretationError: If agent creation fails
    """
    try:
        # Verify Ollama connection
        client = ollama.Client(host=config.ollama_base_url)
        models_response = client.list()

        # Extract model names from the response
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

        if config.ollama_model not in available_models:
            raise CommandInterpretationError(
                f"Model '{config.ollama_model}' not found. "
                f"Available models: {available_models}"
            )

        logger.info(
            "Ollama connection verified, model '%s' is available", config.ollama_model
        )

        return MakefileCommandAgent(config)

    except Exception as e:
        if "ollama" in str(type(e)).lower() or "response" in str(type(e)).lower():
            logger.error("Failed to connect to Ollama: %s", e)
            raise CommandInterpretationError(f"Failed to connect to Ollama: {e}") from e
        else:
            logger.error("Unexpected error creating AI agent: %s", e)
            raise CommandInterpretationError(f"Failed to create AI agent: {e}") from e
