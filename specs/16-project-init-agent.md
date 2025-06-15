# 16. Project Initialization Agent Specification (High-Level Sketch)

## 1. Purpose
This document provides a high-level sketch for a Project Initialization Agent (`ProjectInitAgent`). The purpose of this agent is to automate the setup and scaffolding of new software projects based on high-level user descriptions, incorporating best practices and common tooling.

## 2. Vision
A developer should be able to bootstrap a new, well-structured project with a single command, moving from idea to code in seconds.
- `automake "scaffold a new fastapi project named 'my-api'"`
- `automake "create a new python cli tool with typer and add ruff for linting"`
- `automake "add a Dockerfile for a basic flask app to the current project"`

## 3. Core Components

### 3.1. The `ProjectInitAgent`
- This will be a new `ManagedAgent` available to the `ManagerAgent`.
- The `ManagerAgent` will be trained to recognize "scaffolding" or "initialization" commands and delegate them to this specialist.

### 3.2. Core Tools
The `ProjectInitAgent` will be equipped with tools that generate and modify project structures. These tools will heavily leverage the existing `FileSystemAgent` and `CodingAgent`.

1.  **`scaffold_project(project_name: str, project_type: str, style: str = "src") -> str`**:
    - **Function**: Creates a complete, standard directory structure for a given project type (e.g., "fastapi", "flask", "cli"). This includes creating `pyproject.toml`, a `src` layout, a `tests` directory, and a `.gitignore` file.
    - **Example**: `project_type="fastapi"` would generate boilerplate for a basic FastAPI application.

2.  **`add_tool_to_config(tool_name: str, config_path: str = "pyproject.toml") -> str`**:
    - **Function**: Intelligently modifies the specified configuration file to add boilerplate for common development tools.
    - **Example**: `tool_name="ruff"` would add the `[tool.ruff]` and `[tool.ruff.lint]` tables to `pyproject.toml`.

3.  **`create_dockerfile(app_type: str) -> str`**:
    - **Function**: Generates a multi-stage `Dockerfile` optimized for a specific application framework (e.g., "fastapi", "flask").

## 4. High-Level Architecture
1.  **Invocation**: The user runs a command like `automake "start a new flask app called 'hello-world' with docker support"`.
2.  **Delegation**: The `ManagerAgent` identifies the intent and delegates the task to the `ProjectInitAgent`.
3.  **Orchestration**: The `ProjectInitAgent`'s internal logic calls its specialist tools in sequence:
    - It first calls `scaffold_project(project_name="hello-world", project_type="flask")`.
    - Then, it calls `create_dockerfile(app_type="flask")`.
4.  **Execution**: Each tool uses the underlying `FileSystemAgent` to create directories and files, and the `CodingAgent` to generate the boilerplate content.
5.  **Reporting**: The `ProjectInitAgent` reports the successful creation of the project structure back to the user.

## 5. Implementation Notes
- This agent represents a significant step towards `automake` becoming a true developer companion.
- The templates for different project types and tools should be stored in a structured and easily extendable way within the `automake` package.
- This agent's tools are high-impact and will rely on the action confirmation feature for safety.

## 6. Out of Scope (for initial version)
- Support for languages other than Python.
- Highly customized or obscure project layouts. The focus will be on widely accepted community standards.
