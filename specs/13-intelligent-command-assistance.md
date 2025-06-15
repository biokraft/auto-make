# 13. Intelligent Command Assistance Specification

## Purpose
To evolve `automake` from a `Makefile` utility into a general-purpose, agent-driven command-line assistant. This feature enables `automake` to handle natural language commands that go beyond `Makefile` targets and to intelligently assist users when they make mistakes with the CLI.

## Functional Requirements
1.  **Natural Language Command Execution**:
    - When a user provides a command in natural language (e.g., `automake "list all folders"`), `automake` shall invoke the autonomous agent mode to interpret and execute the request.
    - The agent will have access to tools for file system operations, command execution, and other relevant tasks.
2.  **Intelligent Error Handling**:
    - When the `automake` CLI encounters an unrecognized command or invalid options, it shall not just exit with an error.
    - Instead, it will capture the CLI framework's error output (e.g., from `typer`).
    - This output will be passed to the autonomous agent.
    - The agent will analyze the error and the original command to suggest a valid command or a corrective action.
    - The user will be prompted to confirm the suggested action before it is executed.

## Non-functional Requirements / Constraints
- **Responsiveness**: The agent's analysis and suggestion should be fast to avoid user frustration. A timeout of 5-10 seconds should be targeted for the suggestion.
- **Clarity**: The agent's suggestions must be clear, concise, and explain why the original command failed.
- **Safety**: The user must always give explicit confirmation before any suggested command is executed. There should be no automatic execution of corrected commands.

## Architecture & Data Flow
1.  **Command Invocation Flow**:
    - The main `automake` entry point will receive the user's command.
    - A pre-processing step will determine if the command is a recognized CLI command (like `agent`, `init`, etc.) or a natural language directive for a `Makefile`.
    - If the command is not a recognized internal command, it's assumed to be a natural language prompt. Currently, it's passed to the `Makefile` interpretation logic. This will be changed.
    - The new logic will first attempt to match the command to a `Makefile` target with a high confidence score.
    - If confidence is low, or the command structure suggests a general task (heuristic-based, e.g., contains verbs like "list", "show", "find"), it will be routed to the autonomous agent mode directly.
2.  **Error Handling Flow**:
    - The `typer` application will be wrapped in a try/except block to catch CLI errors (e.g., `typer.Exit`, `click.exceptions.UsageError`).
    - The exception message, which contains the formatted error from `typer`, will be captured.
    - The captured error and the original `sys.argv` will be passed as context to a specialized agent prompt.
    - The agent's response, containing the suggested command, will be parsed.
    - A confirmation prompt will be displayed to the user. If confirmed, the new command will be executed.

## Implementation Notes
- A new CLI command or mode might not be needed. This can be integrated into the main application flow.
- The prompt for error correction should be carefully designed to be specific and guide the LLM to produce a corrected command. Example: "The user command failed. Here is the command and the error message. Please provide a corrected command. If you cannot, say so."

## Acceptance Criteria
- Running `automake "list all files in the current directory"` should trigger the agent, which then executes `ls -l` or an equivalent command.
- Running `automake --non-existent-flag` should result in the agent suggesting a correction, e.g., "Unknown option '--non-existent-flag'. Did you mean '--some-valid-flag'?" and prompting for action.

## Out of Scope
- Proactively suggesting commands without user input.
- Complex, multi-step command chain corrections. The focus is on correcting single, simple CLI errors.
