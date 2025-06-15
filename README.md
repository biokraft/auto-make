# 🤖 automake: Your AI Command-Line Assistant
*The AI-native shell that turns natural language into actions.*

[![Latest Version](https://img.shields.io/pypi/v/automake-cli?label=latest&logo=pypi&logoColor=white)](https://pypi.org/project/automake-cli/)
[![Changelog](https://img.shields.io/badge/changelog-keep%20a%20changelog-blue)](CHANGELOG.md)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white)](https://github.com/biokraft/auto-make)
[![Build Status](https://github.com/biokraft/auto-make/actions/workflows/ci.yml/badge.svg)](https://github.com/biokraft/auto-make/actions/workflows/ci.yml)
[![codecov](https://img.shields.io/badge/coverage->85%-brightgreen?logo=codecov)](https://codecov.io/gh/biokraft/auto-make)
[![PyPI version](https://badge.fury.io/py/automake-cli.svg)](https://badge.fury.io/py/automake-cli)


[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-black.svg)](https://github.com/astral-sh/ruff)
[![tested with pytest](https://img.shields.io/badge/tested%20with-pytest-0A9B7B.svg?logo=pytest)](https://pytest.org)

---

![AutoMake Help Command](./docs/help_cmd.png)

---

**automake** is a Python-based, agent-first command-line tool that uses a powerful multi-agent system to interpret your natural language commands and execute them.

Forget remembering complex flags or exact `Makefile` targets. Just tell `automake` what you want to do.

## ✨ Key Features
- **AI-Native Commands**: Run terminal commands, execute `Makefile` targets, and perform other tasks using plain English.
- **Multi-Agent System**: A sophisticated `ManagerAgent` orchestrates a team of specialists (Terminal, Coding, Web, Makefile) to get the job done right.
- **Interactive Agent Mode**: Launch a chat session with `automake agent` for complex, multi-step tasks.
- **Local First**: Integrates with local LLMs via [Ollama](https://ollama.ai/) for privacy and offline access.
- **Intelligent Error Handling**: If you make a typo, the agent will analyze the error and suggest a correction.
- **User-Friendly & Configurable**: A clean CLI and a simple `config.toml` file for all your settings.

## ⚙️ How It Works
`automake` puts an AI agent at the heart of your command line, following a modern, agentic workflow:

1.  **Parse Prompt**: The CLI captures your natural language instruction (e.g., `automake "list all python files"`).
2.  **Invoke Agent**: Your prompt is sent directly to a central **Manager Agent**.
3.  **Reason & Delegate**: The agent analyzes your request and decides which specialist is best for the job—the `TerminalAgent` for shell commands, the `MakefileAgent` for `make` targets, etc.
4.  **Execute & Observe**: The specialist agent executes the task, and the result is observed.
5.  **Stream Output**: The results are streamed directly to your terminal in real-time.

This entire workflow is triggered by the `run` command. For example: `automake run "list all python files"`.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended for installation)
- An active [Ollama](https://ollama.ai/) server with a running model (e.g., `ollama run qwen3:0.6b`).

### Installation

There are several ways to install and run `automake`.

#### Recommended: `uv tool install`
For a permanent installation, we recommend using `uv tool install`. This makes the `automake` command available globally in a dedicated environment.

**1. From Git (Bleeding Edge)**
Install the very latest version directly from this repository:
```bash
# Install the latest version from the main branch
uv tool install git+https://github.com/biokraft/auto-make.git

# You can also install a specific tag or branch
uv tool install git+https://github.com/biokraft/auto-make.git@v0.4.1
```

**2. From PyPI (Stable)**
Install the latest stable release from PyPI:
```bash
uv tool install automake-cli
```

#### Temporary Execution: `uvx`
If you prefer not to install the tool, you can run it directly using `uvx` (similar to `npx`). This downloads and runs the package in a temporary environment.
```bash
uvx automake-cli run "your command here"
```

#### Traditional `pip`
You can also use `pip` for a standard installation:
```bash
pip install automake-cli
```

### First-Time Setup
After installation, run the initialization command once to set up Ollama and download the required model:
```bash
automake init
```
This command will:
- Verify that Ollama is installed and running.
- Download the configured LLM model if not already available.
- Ensure everything is ready for natural language command interpretation.

## ✍️ Usage

### Non-Interactive Commands
The primary way to use `automake` is with the `run` command, passing your request as a string argument:

```bash
# Run a terminal command
automake run "recursively find all files named README.md"

# Execute a Makefile target
automake run "run the tests and generate a coverage report"

# Build the project
automake run "build the project"
```

### Interactive Agent Session
For more complex tasks, start a chat with the agent:
```bash
automake agent
```

For detailed usage information and available options, run:
```bash
automake help
```

## 🛠️ Configuration
`automake` features a modern, user-friendly configuration system. On first run, it creates a `config.toml` file in your user configuration directory.

### Setting the AI Model
Configure your preferred Ollama model:
```bash
# Set a specific model
automake config set ollama.model "qwen2.5:7b"

# After changing the model, initialize it
automake init
```

**Important**: After changing the model, you must run `automake init` to download and initialize the new model if it's not already available locally.

### View and Modify Configuration
- **View current config**: `automake config show`
- **Set specific values**: `automake config set <section.key> <value>`
- **Edit manually**: `automake config edit`
- **Reset to defaults**: `automake config reset`

### Common Configuration Examples
```bash
# Set the AI model
automake config set ollama.model "qwen3:8b"

# Set the Ollama server URL
automake config set ollama.base_url "http://localhost:11434"

# Set logging level
automake config set logging.level "DEBUG"

# Set AI interaction threshold
automake config set ai.interactive_threshold 90
```

### Configuration Structure
Run `automake config show` to see the current configuration.
```toml
# Example from automake config show
[ollama]
base_url = "http://localhost:11434"
model = "qwen3:0.6b"

[logging]
level = "INFO"

[ai]
interactive_threshold = 80
```

## 🎬 Demos
Want to see some UI/UX demos?
Just run `uv run make demo-all`
or use automake: `automake run "show all demos"`

> **Note:** Running demos with automake may cause animation display issues. For the best demo experience, use the direct `uv run make demo-all` command.

## 🗺️ Project Roadmap
For a detailed breakdown of the project roadmap, implementation phases, and technical specifications, see [SPECS.md](SPECS.md).

## 📜 Changelog
All notable changes to this project are documented in the [CHANGELOG.md](CHANGELOG.md) file.

## 📄 License
This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.
