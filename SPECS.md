# AutoMake Specifications

## 1. Project Overview
AutoMake is a Python-based command-line tool that leverages a local Large Language Model (LLM) to interpret natural language commands and execute corresponding `Makefile` targets. Users can run commands like `automake "deploy the app to staging"` without needing to know the exact `Makefile` syntax. The project uses the `smolagents` framework for its core AI logic and is built following modern Python development standards.

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

## 3. Future Work
This section captures features and ideas that are currently out of scope but are being considered for future versions:
- **Ambiguity Resolution**: When a command is unclear, prompt the user with the top 3 most likely `make` targets to choose from.
- **Dry-Run Mode**: Add a flag (e.g., `--dry-run`) to display the interpreted command without executing it.
- **Failure Detection**: Implement logic to detect when the LLM fails to return a valid command or when the executed command fails.
- **Configuration File**: Allow users to configure the LLM model and other settings via a project-level configuration file.
- **Makefile Generation**: Add a new command, `automake makefile`, that intelligently scans the repository for DevOps patterns (e.g., `Dockerfile`, CI scripts) and generates a comprehensive `Makefile` using the configured LLM.
- **Multi-Provider LLM Support**: Extend `automake init` to support configuring major LLM providers like OpenAI and Anthropic via API keys, in addition to the default Ollama integration.

## 4. Implementation Plan
The following table outlines the granular steps to implement the AutoMake tool based on the defined specifications.

| Phase | Focus Area | Key Deliverables | Related Specs | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Project Setup | Initialize project structure, `pyproject.toml` with `uv`, and pre-commit hooks. | `specs/03-architecture-and-tech-stack.md` | ✅ DONE |
| 2 | Config & Logging Setup | Implement logic to create/read `config.toml` and set up file-based logging. | `specs/04-configuration-management.md`, `specs/06-logging-strategy.md` | TBD |
| 3 | CLI Scaffolding | Create the basic `Typer` application, argument parsing, and help text. | `specs/02-cli-and-ux.md` | ✅ DONE |
| 4 | Makefile Reader | Implement the logic to find and read the `Makefile` from the current directory. | `specs/01-core-functionality.md` | TBD |
| 5 | Ollama Integration | Create a module to handle communication with the local Ollama server, using settings from `config.toml`. | `specs/01-core-functionality.md`, `specs/04-configuration-management.md` | TBD |
| 6 | Smolagent Core | Develop the `smolagent` with the prompt defined in the prompting spec. | `specs/01-core-functionality.md`, `specs/05-ai-prompting.md` | TBD |
| 7 | Execution Engine | Implement the subprocess logic to run the `make` command and stream output. | `specs/01-core-functionality.md` | TBD |
| 8 | End-to-End Wiring | Integrate all components: CLI -> Config -> Logging -> Makefile Reader -> Agent -> Ollama -> Execution. | All | TBD |
| 9 | Unit & Integration Tests | Write tests for CLI, config, logging, execution, and mocked agent/Ollama interactions. | `specs/03-architecture-and-tech-stack.md` | 🔄 IN PROGRESS |
| 10 | CI/CD Pipeline | Implement GitHub Actions workflow for tests, coverage, and reporting. | `specs/08-cicd-pipeline.md` | TBD |
| 11 | Packaging & Distribution | Configure `pyproject.toml` with dependencies and script entry points for `uvx` distribution. | `specs/07-packaging-and-distribution.md` | ✅ DONE |
| 12 | Documentation | Write a `README.md` with installation, configuration, and usage instructions, including CI status badges. | All, `specs/08-cicd-pipeline.md` | TBD |
| 13 | MCP Integration | Implement the MCP-compliant interface for autonomous tool use. | `specs/09-model-context-protocol.md` | TBD |
