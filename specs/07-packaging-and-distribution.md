# Packaging and Distribution Specification

## 1. Purpose
This document specifies how the AutoMake tool will be packaged for distribution. The primary goal is to enable easy, one-command installation using `uvx` for end-users, without requiring them to clone the source code repository.

## 2. Functional Requirements
- The project must be packaged as a standard Python wheel.
- The package must be installable from a Git repository (and eventually from PyPI).
- Installation must create an executable script named `automake` in the user's environment.
- The tool must be directly executable via `uvx` from a Git repository.

## 3. `pyproject.toml` Configuration
To achieve this, the `pyproject.toml` file must be configured with a `[project.scripts]` entry point. This links the `automake` command to a function within the Python source code.

**Example `pyproject.toml` additions:**
```toml
[project]
name = "automake-cli"
version = "0.1.0"
description = "AI-powered Makefile command execution"
requires-python = ">=3.11"
dependencies = [
    "typer[all]",
    "smolagents",
    "requests", # Or a dedicated ollama client
    "tomli; python_version < '3.11'",
    "appdirs"
]

[project.urls]
Homepage = "https://github.com/your-repo/automake" # To be updated
Repository = "https://github.com/your-repo/automake" # To be updated

# This section is critical for creating the CLI command
[project.scripts]
automake = "automake.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```
*Note: The `automake = "automake.main:app"` line assumes the `Typer` app object is named `app` inside a `main.py` file within the `src/automake` directory.*

## 4. Installation and Execution
With the `pyproject.toml` configured correctly, users can install and run the tool as follows.

### Using `uvx` (Recommended)
This command temporarily installs the package from GitHub and runs it in an isolated environment.

```bash
# To be updated with the final repository URL
uvx git+https://github.com/your-repo/automake -- automake "build the project"
```

### Using `uv pip install`
This command installs the package into the current environment persistently.

```bash
# To be updated with the final repository URL
uv pip install git+https://github.com/your-repo/automake

# After installation, the user can run the command directly
automake "run all the tests"
```

## 5. Out of Scope
- Publishing to PyPI (this can be a future consideration).
- Creating binary packages for different operating systems (e.g., via PyInstaller).
- Homebrew, `apt`, or other system-level package manager installations. 