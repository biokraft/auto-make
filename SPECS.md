# AutoMake Specifications

## 1. Project Overview
AutoMake is a Python-based, agent-first command-line tool. It uses a sophisticated multi-agent system, built on the `smolagents` framework, to interpret and execute a wide range of natural language commands. The user can interact with a Manager Agent that orchestrates a team of specialists to perform tasks like running `Makefile` targets, executing terminal commands, writing code, and searching the web. This design transforms AutoMake from a simple `Makefile` wrapper into a powerful, general-purpose AI assistant for the command line. The initial implementation is now complete, delivering the core features outlined in the specification library.

## 2. Specification Library
The following table links to the detailed specifications for each domain and technical topic.

| Filename                                             | Description                                                  |
| ---------------------------------------------------- | ------------------------------------------------------------ |
| `specs/01-core-functionality.md`                     | Defines the agent-first architecture where a Manager Agent orchestrates all tasks. |
| `specs/02-cli-and-ux.md`                             | Outlines the `automake` CLI, focusing on the agent as the primary command entry point. |
| `specs/03-architecture-and-tech-stack.md`            | Specifies the overall architecture, technology choices, and development standards. |
| `specs/04-configuration-management.md`               | Details the `config.toml` file for user-specific settings like the Ollama model. |
| `specs/05-ai-prompting.md`                           | Defines the precise prompt templates for reliable LLM-based command interpretation. |
| `specs/06-logging-strategy.md`                       | Outlines the file-based logging approach with a 7-day rotation policy. |
| `specs/07-packaging-and-distribution.md`             | Details the `pyproject.toml` setup for `uvx` installation and distribution. |
| `specs/08-cicd-pipeline.md`                          | Defines the GitHub Actions CI pipeline for automated testing and coverage reporting. |
| `specs/09-model-context-protocol.md`                 | Describes the integration with Anthropic's Model Context Protocol (MCP) for autonomous use by LLMs. |
| `specs/10-interactive-sessions.md`                   | Specifies the interactive session for resolving ambiguous commands based on LLM confidence scores. |
| `specs/11-live-output-component.md`                  | Defines a real-time, updatable box for streaming content like AI model tokens. |
| `specs/12-autonomous-agent-mode.md`                  | Specifies a multi-agent architecture for autonomous, interactive task execution. |

## 3. Future Work
This section captures features and ideas that are currently out of scope but are being considered for future versions:
- **Dry-Run Mode**: Add a flag (e.g., `--dry-run`) to display the interpreted command without executing it.
- **Failure Detection**: Implement logic to detect when the LLM fails to return a valid command or when the executed command fails.
- **Makefile Generation**: Add a new command, `automake makefile`, that intelligently scans the repository for DevOps patterns (e.g., `Dockerfile`, CI scripts) and generates a comprehensive `Makefile` using the configured LLM.
- **Multi-Provider LLM Support**: Extend `automake init` to support configuring major LLM providers like OpenAI and Anthropic via API keys, in addition to the default Ollama integration.

## 4. Implementation Plan
This plan outlines the steps to implement the agent-first architecture for AutoMake.

| Phase | Focus Area                  | Key Deliverables                                                                                                                                                             | Related Specs                                                                                               | Status |
| ----- | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------ |
| 1     | Foundational Agent Setup    | - Implement the core `ManagerAgent` and specialist `ManagedAgent` instances (Terminal, Coding, Web, Makefile).<br>- Refactor the main CLI entry point to invoke the `ManagerAgent`. | `specs/01-core-functionality.md`<br>`specs/12-autonomous-agent-mode.md`                                    | TBD    |
| 2     | Non-Interactive Agent Mode  | - Implement the `automake "<prompt>"` flow.<br>- Ensure agent output is streamed correctly to the terminal using the `LiveBox` component.                                      | `specs/02-cli-and-ux.md`<br>`specs/11-live-output-component.md`                                            | TBD    |
| 3     | Interactive Agent Mode      | - Implement the `automake agent` command to launch the `rich`-based interactive chat UI.                                                                                     | `specs/02-cli-and-ux.md`<br>`specs/12-autonomous-agent-mode.md`                                            | TBD    |
| 4     | Intelligent Error Handling  | - Implement the `try/except` wrapper around the CLI to capture errors.<br>- Create the agent prompt for suggesting corrections and implement the user confirmation flow.       | `specs/01-core-functionality.md`                                                                            | TBD    |
| 5     | Interactive Model Config    | - Implement `automake config model` command.<br>- Build the `rich`-based UI to list local Ollama models.<br>- Add online search and selection functionality.                   | `specs/04-configuration-management.md`<br>`specs/02-cli-and-ux.md`                                         | TBD    |
| 6     | Documentation Overhaul      | - Update `README.md` and all specifications to reflect the agent-first architecture.<br>- Create a comprehensive user guide for the new agent capabilities.                      | `README.md`<br>All `specs/*.md` files                                                                       | TBD    |
