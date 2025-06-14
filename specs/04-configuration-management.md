# Configuration Management Specification

## 1. Purpose
This document specifies how users will configure the AutoMake tool, particularly for connecting to the Ollama service and selecting a language model. The goal is to provide flexibility while maintaining ease of use.

## 2. Functional Requirements
- AutoMake will look for a configuration file named `config.toml` in a platform-specific user configuration directory (e.g., `~/.config/automake/` on Linux, `%APPDATA%/automake/` on Windows).
- If the configuration file does not exist upon first run, the tool shall create it with default values and inform the user.
- The configuration will allow the user to specify:
    - The base URL of their local Ollama server.
    - The name of the LLM model they wish to use (e.g., `gemma3:4b`, `phi3`, etc.).
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
model = "gemma3:4b"
```

## 4. Default Behavior
- If `config.toml` is not found, AutoMake will create it with the default `base_url` (`http://localhost:11434`) and a sensible default `model` (e.g., `gemma3:4b`).
- If the `base_url` or `model` keys are missing from the file, the tool will use the same default values.
- If the tool cannot connect to the specified `base_url`, it will exit with a clear error message instructing the user to check if their Ollama server is running and if the configuration is correct.

## 5. Implementation Notes
- A dedicated module should be responsible for locating, reading, and validating the configuration file.
- The popular `tomli` library can be used for parsing the TOML file in Python < 3.11, while the standard library `tomllib` is available in Python 3.11+. Given our stack, `tomllib` is preferred.
- The application should provide a clear message to the user about where the configuration file is located.

## 6. Out of Scope
- A CLI command to directly edit the configuration (e.g., `automake config set model=phi3`). Users will edit the file manually.
- Per-project configuration files. The configuration is global for the user.
