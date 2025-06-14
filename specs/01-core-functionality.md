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
- **Immediate Execution**: For the initial version, the translated command will be executed immediately without a user confirmation step.
- **No State**: The tool is stateless. Each invocation is independent and has no memory of previous commands.

## 4. Architecture & Data Flow
1. **Input**: The user provides a string via the `automake` CLI (e.g., `automake "deploy the app to staging"`).
2. **Contextualization**: The tool reads the contents of the `Makefile` in the current directory.
3. **Agent Invocation**: The natural language input and the `Makefile` contents are passed to a `smolagent`.
4. **Interpretation**: The agent's task is to determine the single most appropriate `Makefile` command that corresponds to the user's request. The output must be only the command itself (e.g., `deploy-staging`).
5. **Execution**: The CLI receives the command from the agent and executes it using the system's `make` utility (e.g., runs `make deploy-staging`).
6. **Output**: The standard output and standard error from the `make` command execution are streamed directly to the user's terminal.

## 5. Implementation Notes
- The logic for interacting with the Ollama API should be encapsulated in a dedicated module.
- The `smolagent` will be given a clear, concise prompt that instructs it to act as an expert in `makefiles` and to only return the single best command.

## 6. Out of Scope
- User confirmation before execution.
- Handling of ambiguous commands (e.g., prompting the user with choices).
- Failure detection and recovery if a command is misinterpreted or fails.
- Interactive chat or conversational features.

## 7. Future Considerations
- A mechanism to handle ambiguity by presenting the user with the top N interpreted commands.
- A "dry run" mode to show the command without executing it.
- Caching strategies to speed up interpretation for repeated commands. 