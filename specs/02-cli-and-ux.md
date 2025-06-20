# CLI and User Experience Specification

## 1. Purpose
This document outlines the command-line interface (CLI), user interaction patterns, and overall user experience for AutoMake, designed as an agent-first application. The implementation leverages the `smolagents` framework with a Manager Agent orchestrating specialist agents for task execution.

## 2. CLI Commands

### 2.1. Main Command: `automake "<prompt>"`
- The primary way to interact with the tool is via `automake "<prompt>"`.
- This command invokes the Manager Agent to interpret and execute the user's natural language request non-interactively.
- The agent's output and the results of any executed tools are streamed to the terminal.
- **Usage Examples**:
  ```bash
  # Execute a make target
  automake "build the project"

  # Run a general terminal command
  automake "list all the python files in this directory"

  # Ask a general question
  automake "what is the ip address of the google dns server?"
  ```

### 2.2. Interactive Agent Mode: `automake agent`
- For a conversational experience, users can run `automake agent`.
- This command launches a `rich`-based interactive chat session with the Manager Agent, maintaining context throughout the conversation.
- This mode is ideal for complex, multi-step tasks that benefit from interactive guidance.

### 2.3. Configuration Command: `automake config model`
- To provide a guided setup experience, users can run `automake config model`.
- This command launches the interactive model selection UI as defined in `specs/04-configuration-management.md`.

### 2.4. Other Commands
- Other commands like `init` and `logs` will remain as standard subcommands.

## 3. Non-functional Requirements / Constraints
- **Responsiveness**: The tool must provide immediate feedback. A dynamic live display will show the agent's status (e.g., "Thinking...", "Executing `ls -l`...").
- **Framework**: The CLI will continue to be built using the `Typer` library.

## 4. Error Handling
- **Invalid Prompt**: If the user does not provide a command string to `automake`, the CLI should exit gracefully with usage instructions.
- **Unrecognized Command/Flag**: If the user enters an invalid command or flag (e.g., `automake --bad-flag`), the intelligent error handler specified in `specs/01-core-functionality.md` will be triggered. The agent will attempt to suggest a valid command.
- **Execution Errors**: Errors from executed tools (e.g., a `make` command failing) will be clearly reported to the user.

## 5. Out of Scope
- Configuration via CLI flags (this is handled by `config.toml`).
- Shell completions.
