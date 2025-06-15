# Configuration Management Specification

## 1. Purpose
This document specifies how users will configure the AutoMake tool, particularly for connecting to the Ollama service and selecting a language model. The goal is to provide flexibility while maintaining ease of use.

## 2. Functional Requirements
- AutoMake will look for a configuration file named `config.toml` in a platform-specific user configuration directory (e.g., `~/.config/automake/` on Linux, `%APPDATA%/automake/` on Windows).
- If the configuration file does not exist upon first run, the tool shall create it with default values and inform the user.
- The configuration will allow the user to specify:
    - The base URL of their local Ollama server.
    - The name of the LLM model they wish to use (e.g., `qwen3:0.6b`, `phi3`, etc.).
- The tool must read this configuration at runtime to connect to the correct Ollama instance and use the specified model.

## 3. Configuration File Format
The `config.toml` file will use the TOML format for simplicity and readability.

**Example `config.toml`:**
```toml
# Configuration for AutoMake

[ollama]
# The base URL for the local Ollama server.
base_url = "http://localhost:11434"

# The model to use for interpreting commands.
# The user must ensure this model is available on their Ollama server.
model = "qwen3:0.6b"

[agent]
# If true, require user confirmation before every action.
require_confirmation = true
```

## 4. Default Behavior
- If `config.toml` is not found, AutoMake will create it with the default `base_url` (`http://localhost:11434`) and a sensible default `model` (e.g., `qwen3:0.6b`).
- If the `base_url` or `model` keys are missing from the file, the tool will use the same default values.
- If the tool cannot connect to the specified `base_url`, it will exit with a clear error message instructing the user to check if their Ollama server is running and if the configuration is correct.

## 5. Implementation Notes
- A dedicated module should be responsible for locating, reading, and validating the configuration file.
- The popular `tomli` library can be used for parsing the TOML file in Python < 3.11, while the standard library `tomllib` is available in Python 3.11+. Given our stack, `tomllib` is preferred.
- The application should provide a clear message to the user about where the configuration file is located.

## 6. Interactive Model Configuration

### 6.1. Command: `automake config model`
- A new CLI command, `automake config model`, will be introduced to provide a user-friendly way to set the Ollama model.
- This command removes the need for users to manually edit the `config.toml` file for model selection.

### 6.2. Interactive UI
- Upon running the command, the tool will query the local Ollama API to get a list of all downloaded models.
- It will then present an interactive selection list using a `rich`-based component (similar to `specs/10-interactive-sessions.md`).
- The list of models will be appended with a final option: "Search for a new model online...".

### 6.3. Online Model Search
- If the user selects the "Search..." option, they will be prompted to enter a search query.
- The tool will then query the Ollama online model registry (or a suitable API) to find matching models.
- The search results will be presented in a new interactive list.
- Upon selection, the chosen model name (e.g., `llama3:8b`) will be captured.

### 6.4. Configuration Update
- Once a model is selected (either from the local list or the online search), its identifier will be written to the `model` key in the `config.toml` file.
- The tool will inform the user that the configuration has been updated and remind them to run `automake init` if they selected a new model that needs to be downloaded.

## 7. Agent Behavior Configuration

### 7.1. Action Confirmation
- A new section, `[agent]`, will be added to the `config.toml` file.
- It will contain a boolean key, `require_confirmation`, which defaults to `true`.
- When `true`, the agent will always ask for user confirmation before executing any action (e.g., running a terminal command, executing a `Makefile` target).

**Example `config.toml` with agent settings:**
```toml
[ollama]
base_url = "http://localhost:11434"
model = "qwen3:0.6b"

[agent]
# If true, require user confirmation before every action.
require_confirmation = true
```

## 8. Out of Scope
- A CLI command to directly edit other configuration values like the `base_url`.
- Per-project configuration files. The configuration remains global for the user.
