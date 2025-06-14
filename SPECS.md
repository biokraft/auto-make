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
| `specs/10-interactive-sessions.md`                   | Specifies the interactive session for resolving ambiguous commands based on LLM confidence scores. |

## 3. Future Work
This section captures features and ideas that are currently out of scope but are being considered for future versions:
- **Dry-Run Mode**: Add a flag (e.g., `--dry-run`) to display the interpreted command without executing it.
- **Failure Detection**: Implement logic to detect when the LLM fails to return a valid command or when the executed command fails.
- **Configuration File**: Allow users to configure the LLM model and other settings via a project-level configuration file.
- **Makefile Generation**: Add a new command, `automake makefile`, that intelligently scans the repository for DevOps patterns (e.g., `Dockerfile`, CI scripts) and generates a comprehensive `Makefile` using the configured LLM.
- **Multi-Provider LLM Support**: Extend `automake init` to support configuring major LLM providers like OpenAI and Anthropic via API keys, in addition to the default Ollama integration.

## 4. Implementation Plan
The following table outlines the granular steps to implement the AutoMake tool based on the defined specifications.

| Phase | Focus Area | Key Deliverables | Related Specs | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Foundation & Setup** | **Project Scaffolding** | `specs/03-architecture-and-tech-stack.md` | ✅ DONE |
| | | Initialize project with `src/automake` layout, `pyproject.toml`, and `uv`. | `specs/03-architecture-and-tech-stack.md` | ✅ DONE |
| | | Set up pre-commit hooks for `black` and `ruff`. | `specs/03-architecture-and-tech-stack.md` | ✅ DONE |
| | **Configuration & Logging** | Implement `config.toml` creation and reading logic. | `specs/04-configuration-management.md` | ✅ DONE |
| | | Implement file-based logging with rotation and `config.toml` level setting. | `specs/06-logging-strategy.md` | ✅ DONE |
| | **Packaging Configuration** | Configure `pyproject.toml` with dependencies and script entry points for `uvx`. | `specs/07-packaging-and-distribution.md` | ✅ DONE |
| 2 | **Core Engine** | **Makefile Reader** | Implement a robust function to find and read the `Makefile` in the current directory. | `specs/01-core-functionality.md` | ✅ DONE |
| | **Ollama Client** | Create `ollama_client.py` to manage connection, model selection, and API calls. | `specs/01-core-functionality.md` | ✅ DONE |
| | **AI Core (`smolagent`)** | Implement the `smolagent` responsible for command interpretation. | `specs/01-core-functionality.md`, `specs/05-ai-prompting.md` | TBD |
| | | Integrate system and user prompts with dynamic content (`Makefile`, user command). | `specs/05-ai-prompting.md` | TBD |
| | | Implement robust JSON parsing and validation for the LLM's response. | `specs/05-ai-prompting.md` | TBD |
| | **Execution Engine** | Implement subprocess logic to run the selected `make` command and stream its output. | `specs/01-core-functionality.md` | TBD |
| 3 | **User Interface** | **CLI Scaffolding** | Create the `Typer` app with the primary command argument and basic usage text. | `specs/02-cli-and-ux.md` | ✅ DONE |
| | **Interactive Sessions** | Integrate `questionary` for the interactive command selection UI. | `specs/10-interactive-sessions.md` | TBD |
| | | Implement the confidence check logic to trigger the interactive session. | `specs/10-interactive-sessions.md` | TBD |
| | **End-to-End Wiring** | Integrate all components: CLI -> Config -> Logging -> Makefile -> AI Core -> Execution/Interaction. | All | TBD |
| 4 | **Quality & Automation** | **Testing** | Write unit tests for config, logging, CLI parsing, and execution. | `specs/03-architecture-and-tech-stack.md` | ✅ DONE |
| | | Write integration tests for the AI Core with a mocked Ollama client. | `specs/03-architecture-and-tech-stack.md` | TBD |
| | **CI/CD Pipeline** | Implement GitHub Actions workflow for automated testing and coverage checks. | `specs/08-cicd-pipeline.md` | ✅ DONE |
| | **Documentation** | Write a comprehensive `README.md` with setup, usage, and configuration instructions. | All | TBD |
| | | Add CI status and coverage badges to `README.md`. | `specs/08-cicd-pipeline.md` | TBD |
| 5 | **Advanced Features** | **MCP Integration** | Implement the MCP-compliant interface for autonomous tool discovery and use. | `specs/09-model-context-protocol.md` | TBD |
