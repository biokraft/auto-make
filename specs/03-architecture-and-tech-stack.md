# Architecture & Tech Stack Specification

## 1. Purpose
This document defines the overall system architecture, technology stack, and development standards for the AutoMake project. It ensures that development aligns with the established best practices found in the `.cursor/rules`.

## 2. Technology Stack
- **Language**: Python 3.11+
- **CLI Framework**: `Typer`
- **AI Framework**: `smolagents`
- **LLM Interaction**: `Ollama` via direct HTTP requests or a dedicated client library.
- **Dependency Management**: `uv`, as specified in `.cursor/rules/python/01-deps-management.mdc`.

## 3. Architecture
The system is a monolithic command-line application with three primary logical components:
1.  **CLI Layer**: Built with `Typer`, this is the entry point for the user. Its responsibility is to parse the command-line arguments and orchestrate the other components. (See `specs/02-cli-and-ux.md`)
2.  **AI Core Layer**: Built with `smolagents`, this component is responsible for all AI-related tasks. It takes the natural language query and `Makefile` contents, interacts with the Ollama service, and produces the target `make` command. (See `specs/01-core-functionality.md`)
3.  **Execution Layer**: A simple module that takes the command string from the AI Core and executes it as a subprocess, streaming the output back to the CLI Layer.

## 4. Project Structure
The project will adhere to the structure defined in `.cursor/rules/python/02-project-structure.mdc`. This includes a `src/automake` layout for the main application code and a separate `tests/` directory.

## 5. Code Style & Quality
- **Formatting**: Code will be formatted using `black` and `ruff`.
- **Linting**: Linting will be performed with `ruff`.
- **Pre-commit**: Pre-commit hooks will be used to enforce style and quality standards, as defined in `.cursor/rules/python/05-pre-commit.mdc`.
- These standards are derived from `.cursor/rules/python/03-style.mdc`.

## 6. Testing
- Testing practices will follow the guidelines in `.cursor/rules/python/testing/01-best-practices.mdc`.
- The primary focus will be on unit tests for the CLI layer (e.g., argument parsing) and the execution layer.
- Integration tests will cover the interaction between the AI Core and a mocked Ollama service. End-to-end tests against a live Ollama instance will be considered.

## 7. Out of Scope
- Any web-based or API component.
- A graphical user interface (GUI).
- Persistent storage or databases.

## 8. Future Considerations
- **Third-Party Agent Ecosystem**: Explore supporting a framework like Google's Agent-to-Agent (A2A) communication protocol to allow external developers to create and integrate their own specialist agents into the AutoMake ecosystem. This would enable a plug-and-play architecture, expanding the tool's capabilities beyond the core set of agents.
