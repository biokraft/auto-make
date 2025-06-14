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
- **Model Flexibility**: The specific LLM used for interpretation will be configurable, but the system will be developed and tested with a default model (to be determined). The connection to the LLM will be managed through a local Ollama server instance.
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

## 5. Ollama Integration Details

### 5.1 Ollama Client Library
- Use the official `ollama` Python library for integration: `pip install ollama`
- The library provides both synchronous and asynchronous clients
- Supports streaming responses for better user experience

### 5.2 Connection Management
- Default connection to `http://localhost:11434` (Ollama's default port)
- Connection parameters should be configurable via `config.toml`
- Implement proper error handling for connection failures
- Support for custom base URLs if Ollama is running on different host/port

### 5.3 Model Selection
- Support for any model available in the local Ollama instance
- Default model should be configurable (e.g., `llama3.2`, `mistral`, `phi4-mini`)
- Model availability should be validated at startup
- Graceful fallback if configured model is not available

### 5.4 API Usage Patterns
The system will use Ollama's chat completion API for structured conversations:

```python
import ollama

# Basic chat completion
response = ollama.chat(
    model='llama3.2',
    messages=[
        {
            'role': 'system',
            'content': 'You are an expert at interpreting Makefile commands...'
        },
        {
            'role': 'user',
            'content': f'Given this Makefile:\n{makefile_content}\n\nWhat command should I run for: {user_input}'
        }
    ],
    stream=False
)
```

### 5.5 Smolagents Integration
- Use `smolagents` with Ollama via the `LiteLLMModel` wrapper
- Configure the model to point to local Ollama instance
- Implement custom tools for Makefile parsing and command validation

```python
from smolagents import CodeAgent, LiteLLMModel

# Configure Ollama model for smolagents
model = LiteLLMModel(
    model_id="ollama/llama3.2",
    base_url="http://localhost:11434"
)

# Create agent with Makefile-specific tools
agent = CodeAgent(
    tools=[MakefileParserTool(), CommandValidatorTool()],
    model=model
)
```

### 5.6 Error Handling
- Handle Ollama server not running (connection refused)
- Handle model not found errors
- Handle malformed responses from the LLM
- Implement retry logic with exponential backoff
- Provide clear error messages to users

### 5.7 Performance Considerations
- Use streaming responses when possible for better perceived performance
- Implement model keep-alive settings to avoid reload delays
- Cache Makefile parsing results when appropriate
- Consider using smaller, faster models for simple commands

## 6. Implementation Notes
- The logic for interacting with the Ollama API should be encapsulated in a dedicated module (`ollama_client.py`)
- The `smolagent` will be given a clear, concise prompt that instructs it to act as an expert in `makefiles` and to only return the single best command
- Implement proper logging for debugging Ollama interactions
- Support for both local and remote Ollama instances

## 7. Out of Scope
- User confirmation before execution (beyond the new interactive selection for low-confidence results).
- Failure detection and recovery if a command is misinterpreted or fails.
- Interactive chat or conversational features.

## 8. Future Considerations
- A "dry run" mode to show the command without executing it.
- Caching strategies to speed up interpretation for repeated commands.
- Support for fine-tuned models specific to Makefile interpretation.
- Integration with Ollama's embedding models for semantic search of Makefile targets.
