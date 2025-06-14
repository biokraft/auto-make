# Core Functionality Specification

## 1. Purpose
This document specifies the core AI-driven functionality of AutoMake, which is to interpret natural language commands, translate them into valid `Makefile` commands, and execute them.

## 2. Functional Requirements
- The system must accept a natural language string as input from the command line.
- It must use an LLM via Ollama to interpret the natural language input.
- The interpreted command must be a valid command found within the project's `Makefile`.
- The system shall execute the identified `Makefile` command directly.
- The tool will be developed using the `smolagents` framework for the core AI logic.

## 3. Non-functional Requirements / Constraints
- **Model Flexibility**: The specific LLM used for interpretation will be configurable via `config.toml`. The connection to the LLM will be managed through a local Ollama server instance, accessed via `smolagents`.
- **Conditional Execution**: Commands are executed immediately only if the LLM's confidence is high. Low-confidence interpretations will trigger an interactive user confirmation step.
- **Transient State**: The tool is primarily stateless between invocations. A transient state exists only during a single run to manage an interactive command-selection session when required.

## 4. Architecture & Data Flow
1. **Input**: The user provides a string via the `automake` CLI (e.g., `automake "deploy the app to staging"`).
2. **Contextualization**: The tool reads the contents of the `Makefile` in the current directory.
3. **Agent Invocation**: The natural language input and the `Makefile` contents are passed to a `smolagent`.
4. **Interpretation**: The agent's task is to determine the single most appropriate `Makefile` command that corresponds to the user's request. The agent's response must be a JSON object containing the command, a confidence score, and a list of alternative commands. See `specs/10-interactive-sessions.md`.
5. **Confidence Check & Execution**:
    - The CLI receives the JSON object from the agent.
    - It checks the `confidence` score against a configured threshold.
    - **If confidence is high**: The command is executed directly.
    - **If confidence is low (or command is null with alternatives)**: An interactive session is triggered. The selected command is then executed. See `specs/10-interactive-sessions.md`.
    - **If no command or alternatives are found**: The tool prints a help message and exits, as defined in `specs/02-cli-and-ux.md`.
6. **Output**: The standard output and standard error from the `make` command execution are streamed directly to the user's terminal.

## 5. Ollama Integration via smolagents
AutoMake will leverage the native Ollama integration provided by the `smolagents` library through its `LiteLLMModel` wrapper. This approach simplifies the architecture by removing the need for a custom client library.

### 5.1. Configuration
- The `LiteLLMModel` will be configured using settings from `config.toml`.
- **`model_id`**: The model identifier will be constructed as `ollama/{config.ollama_model}`.
- **`base_url`**: The Ollama server URL will be taken from `config.ollama_base_url`.

### 5.2. `smolagents` Implementation
- The core logic will be encapsulated in a `MakefileCommandAgent` class.
- This agent will be a `CodeAgent` initialized with the configured `LiteLLMModel`.
- The agent will be responsible for sending the system and user prompts to the LLM and parsing the JSON response.

```python
from smolagents import CodeAgent, LiteLLMModel
from automake.config import Config

# Example initialization within the agent
config = Config()
model = LiteLLMModel(
    model_id=f"ollama/{config.ollama_model}",
    base_url=config.ollama_base_url
)

agent = CodeAgent(tools=[], model=model)
```

### 5.3. Error Handling and Validation
- The `MakefileCommandAgent` will be responsible for validating the connection to the Ollama server at startup.
- It will check if the configured model is available on the Ollama instance.
- It will implement robust error handling for API communication issues (e.g., connection refused, model not found) and provide clear feedback to the user.

## 6. Implementation Notes
- The `smolagent` will be given a clear, concise prompt that instructs it to act as an expert in `makefiles` and to only return the single best command, as defined in `specs/05-ai-prompting.md`.
- All logic for AI interaction will be contained within `automake/core/ai_agent.py`.
- Implement proper logging for debugging `smolagents` and Ollama interactions.

## 7. Out of Scope
- User confirmation before execution (beyond the new interactive selection for low-confidence results).
- Failure detection and recovery if a command is misinterpreted or fails.
- Interactive chat or conversational features.

## 8. Future Considerations
- A "dry run" mode to show the command without executing it.
- Caching strategies to speed up interpretation for repeated commands.
- Support for fine-tuned models specific to Makefile interpretation.
- Integration with Ollama's embedding models for semantic search of Makefile targets.
