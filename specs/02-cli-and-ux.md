# CLI and User Experience Specification

## 1. Purpose
This document outlines the command-line interface (CLI), user interaction patterns, and overall user experience for the AutoMake tool.

## 2. Functional Requirements
- The tool must be invocable from the command line via an executable named `automake`.
- It must accept a single positional argument: a string containing the natural language command to be interpreted.
- The command string must be enclosed in quotes to be treated as a single argument by the shell.
- The tool should stream the output of the executed `make` command directly to the standard output/error streams of the user's terminal in real-time.

## 3. Non-functional Requirements / Constraints
- **Simplicity**: The CLI should be simple, with a single, clear purpose. No complex flags or subcommands are required for the initial version.
- **Responsiveness**: The tool should provide immediate feedback that it has started processing. A simple "Interpreting your command..." message is sufficient before the AI/Make process begins.
- **Framework**: The CLI will be built using the `Typer` library to ensure a modern and maintainable implementation.

## 4. Usage Examples
```bash
# Example 1: Simple command
automake "build the project"

# Example 2: Command with parameters
automake "deploy the grafana service to the staging environment"

# Example 3: Running tests
automake "run all the unit tests"
```

## 5. Error Handling
- If the user does not provide a command string, the CLI should exit gracefully with a clear error message and usage instructions.
- If no `Makefile` is found in the current directory, the tool should exit with a clear error message.
- If the LLM is unable to interpret the user's command (i.e., it returns no primary command and no alternatives), the CLI will display the standard help/usage message and exit gracefully.

## 6. Out of Scope
- Interactive prompts.
- Configuration via CLI flags (e.g., `--model`, `--verbose`). Configuration will be handled via a separate configuration file if needed.
- Shell completions.
