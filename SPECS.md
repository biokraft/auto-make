# AutoMake Specifications

## 1. Project Overview
AutoMake is a Python-based command-line tool that leverages a local Large Language Model (LLM) to interpret natural language commands and execute corresponding `Makefile` targets. Users can run commands like `automake "deploy the app to staging"` without needing to know the exact `Makefile` syntax. The project uses the `smolagents` framework for its core AI logic and is built following modern Python development standards. The initial implementation is now complete, delivering the core features outlined in the specification library.

## 2. Specification Library
The following table links to the detailed specifications for each domain and technical topic.

| Filename                                             | Description                                                  |
| ---------------------------------------------------- | ------------------------------------------------------------ |
| `specs/01-core-functionality.md`                     | Defines the AI-driven command interpretation and execution flow using Ollama and `smolagents`. |
| `specs/02-cli-and-ux.md`                             | Outlines the `automake` command-line interface, usage patterns, and user experience. |
| `specs/03-architecture-and-tech-stack.md`            | Specifies the overall architecture, technology choices, and development standards. |
| `specs/04-configuration-management.md`               | Details the `config.toml` file for user-specific settings like the Ollama model. |
| `specs/05-ai-prompting.md`                           | Defines the precise prompt templates for reliable LLM-based command interpretation. |
| `specs/06-logging-strategy.md`                       | Outlines the file-based logging approach with a 7-day rotation policy. |
| `specs/07-packaging-and-distribution.md`             | Details the `pyproject.toml` setup for `uvx` installation and distribution. |
| `specs/08-cicd-pipeline.md`                          | Defines the GitHub Actions CI pipeline for automated testing and coverage reporting. |
| `specs/09-model-context-protocol.md`                 | Describes the integration with Anthropic's Model Context Protocol (MCP) for autonomous use by LLMs. |
| `specs/10-interactive-sessions.md`                   | Specifies the interactive session for resolving ambiguous commands based on LLM confidence scores. |
| `specs/11-live-output-component.md`                  | Defines a real-time, updatable box for streaming content like AI model tokens. |
| `specs/12-autonomous-agent-mode.md`                  | Defines the CLI-based autonomous agent mode for interactive task execution. |

## 3. Future Work
This section captures features and ideas that are currently out of scope but are being considered for future versions:
- **Dry-Run Mode**: Add a flag (e.g., `--dry-run`) to display the interpreted command without executing it.
- **Failure Detection**: Implement logic to detect when the LLM fails to return a valid command or when the executed command fails.
- **Configuration File**: Allow users to configure the LLM model and other settings via a project-level configuration file.
- **Makefile Generation**: Add a new command, `automake makefile`, that intelligently scans the repository for DevOps patterns (e.g., `Dockerfile`, CI scripts) and generates a comprehensive `Makefile` using the configured LLM.
- **Multi-Provider LLM Support**: Extend `automake init` to support configuring major LLM providers like OpenAI and Anthropic via API keys, in addition to the default Ollama integration.

## 4. Implementation Plan
This plan outlines the steps to implement the features defined in the specification library, including the adoption of a universal live output component.

| Phase | Focus Area                  | Key Deliverables                                                                                                                                                             | Related Specs                                                                                               | Status |
| ----- | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------ |
| 1     | UI Component Refactoring    | - Replace static messages (e.g., "Interpreting...") with the `LiveBox` component.<br>- Refactor error messages to use the `LiveBox` for consistent UI.                             | `specs/02-cli-and-ux.md`<br>`specs/11-live-output-component.md`                                            | TBD    |
| 2     | Interactive Session Rework  | - Replace `questionary` with a custom `rich`-based interactive selection component.<br>- Ensure the new component renders within a `LiveBox` and supports keyboard navigation. | `specs/10-interactive-sessions.md`<br>`specs/11-live-output-component.md`                                  | TBD    |
| 3     | Autonomous Agent Mode       | - Implement `automake agent` command for interactive and non-interactive use.<br>- Build a `rich`-based chat UI for the agent.<br>- Integrate tools for terminal, code, web, and Makefile access. | `specs/02-cli-and-ux.md`<br>`specs/12-autonomous-agent-mode.md`                                            | TBD    |
| 4     | Documentation Overhaul      | - Update `README.md` to reflect the project's evolution into an agentic tool.<br>- Revise the project overview and all specifications to align with the new capabilities.<br>- Create a comprehensive user guide for the new agent mode. | `README.md`<br>All `specs/*.md` files                                                                       | TBD    |
| 5     | Core Feature Implementation | - Implement dry-run mode (`--dry-run` flag).<br>- Implement failure detection for LLM and command execution.                                                                     | `specs/01-core-functionality.md`                                                                            | TBD    |
| 6     | Advanced Features           | - Implement `automake makefile` for intelligent `Makefile` generation.<br>- Add support for multiple LLM providers (OpenAI, Anthropic).                                        | `specs/01-core-functionality.md`<br>`specs/04-configuration-management.md`                                   | TBD    |
