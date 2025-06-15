# 1. Core Functionality: The Agent-First Architecture

## 1. Purpose
This document specifies the core functionality of AutoMake, which has evolved into an agent-first command-line assistant. The primary entry point of the tool is a sophisticated multi-agent system, powered by `smolagents`, that interprets and executes a wide range of natural language commands. This architecture subsumes the original `Makefile`-centric logic, treating it as one of several capabilities managed by the agent ecosystem.

## 2. Functional Requirements

### 2.1. Unified Command Interpretation
- The `automake "<prompt>"` command serves as the single entry point for all user requests.
- All prompts are routed directly to the **Manager Agent**, as defined in `specs/12-autonomous-agent-mode.md`.
- The Manager Agent is responsible for understanding the user's intent and dispatching the task to the appropriate specialist agent (e.g., `MakefileAgent`, `TerminalAgent`, `CodingAgent`, `WebAgent`).

### 2.2. Makefile Integration as a Tool
- The original core feature—interpreting natural language for `Makefile` targets—is now a specialized capability handled by the `MakefileAgent`.
- The Manager Agent will learn to recognize prompts related to `make` tasks (e.g., "build the project," "deploy to staging") and delegate them accordingly.
- This preserves all previous `Makefile` functionality but within a more powerful and flexible agentic framework.

### 2.3. Intelligent CLI Error Handling
- When the `automake` CLI encounters an unrecognized command or invalid options (e.g., `automake --non-existent-flag`), it will not immediately exit.
- The CLI error message will be captured and passed to the Manager Agent.
- The agent will analyze the error and the original command to suggest a valid, corrected command.
- The user will be prompted to confirm the suggested command before it is executed, ensuring user control and safety.

## 3. Architecture & Data Flow

1.  **Input**: The user provides a string via the `automake "<prompt>"` CLI.
2.  **Agent Invocation**: The prompt is passed directly to the `run` method of the central `ManagerAgent`.
3.  **Task Orchestration**: The Manager Agent, following the ReAct loop, reasons about the prompt and decides which specialist agent is best suited to handle the task.
4.  **Execution**: The chosen specialist agent executes the task (e.g., the `MakefileAgent` runs a `make` command; the `TerminalAgent` runs a shell command).
5.  **Output**: The output from the specialist agent is streamed back through the Manager Agent to the user's terminal via the `rich`-based UI.

### 3.1. Error Handling Flow
1.  A top-level `try/except` block wraps the main CLI application (`typer`).
2.  On a `click.exceptions.UsageError` or similar exception, the error message and original arguments (`sys.argv`) are captured.
3.  These details are formatted into a specific task for the Manager Agent (e.g., "The user's command failed. Analyze the error and suggest a correction.").
4.  The agent's suggested command is presented to the user for confirmation. If accepted, the command is executed.

## 4. Implementation Notes
- The primary logic will be moved from a dedicated `Makefile` interpreter to the `automake.agent` module.
- The top-level `automake` command in `automake/cli/main.py` will be simplified to primarily initialize and invoke the `ManagerAgent`.
- The `MakefileAgent` will internally use the logic previously designed for high-confidence `Makefile` command interpretation, but now as a tool available to the broader system.
- The prompt for error correction must be carefully engineered to guide the LLM effectively.

## 5. Out of Scope
- Proactively suggesting commands without user input.
- Multi-step conversational error correction. The goal is to correct a single failed command.
