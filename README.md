# 🤖 auto-make
*Makefiles without writing Makefiles.*

[![Latest Version](https://img.shields.io/pypi/v/automake-cli?label=latest&logo=pypi&logoColor=white)](https://pypi.org/project/automake-cli/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white)](https://github.com/seanbaufeld/auto-make)
[![Build Status](https://github.com/seanbaufeld/auto-make/actions/workflows/ci.yml/badge.svg)](https://github.com/seanbaufeld/auto-make/actions/workflows/ci.yml)
[![codecov](https://img.shields.io/badge/coverage->85%-brightgreen?logo=codecov)](https://codecov.io/gh/seanbaufeld/auto-make)
[![PyPI version](https://badge.fury.io/py/automake-cli.svg)](https://badge.fury.io/py/automake-cli)


[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-black.svg)](https://github.com/astral-sh/ruff)
[![tested with pytest](https://img.shields.io/badge/tested%20with-pytest-0A9B7B.svg?logo=pytest)](https://pytest.org)

---

![AutoMake Help Command](./docs/help_cmd.png)

---

**auto-make** is a Python-based command-line tool that leverages a local Large Language autModel (LLM) to interpret your natural language commands and execute the correct `Makefile` target.

Tired of `grep "deploy" Makefile`? Just run `automake "deploy the app to staging"` and let the AI do the work.

## ✨ Key Features
- **Natural Language Commands**: Run `make` targets using plain English. No more memorizing target names.
- **Local First**: Integrates with local LLMs via [Ollama](https://ollama.ai/) for privacy and offline access.
- **User-Friendly CLI**: A clean, simple interface built with `Typer`.
- **Configurable**: Set your preferred LLM model and other options in a simple `config.toml` file.
- **Modern Python Stack**: Built with `uv`, `smolagents`, and `pre-commit` for a robust development experience.

## ⚙️ How It Works
`auto-make` follows a simple, powerful workflow to translate your instructions into actions:

1.  **Parse Command**: The CLI captures your natural language instruction.
2.  **Read Makefile**: It finds and reads the `Makefile` in your current directory.
3.  **Consult AI**: It sends the `Makefile` contents and your instruction to a local LLM (via Ollama).
4.  **Identify Target**: The LLM analyzes the context and identifies the single most likely `make` command to run.
5.  **Execute**: The identified command is executed, and its output is streamed directly to your terminal.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended for installation)
- An active [Ollama](https://ollama.ai/) server with a running model (e.g., `ollama run qwen3:0.6b`).

### Installation
Install `auto-make` using `uvx` (the `uv` equivalent of `npx`):
```bash
uvx automake-cli
```
This command temporarily installs and runs the `automake` CLI tool in an isolated environment.

### First-Time Setup
After installation, run the initialization command once to set up Ollama and download the required model:
```bash
automake init
```
This command will:
- Verify that Ollama is installed and running
- Download the configured LLM model if not already available
- Ensure everything is ready for natural language command interpretation

## ✍️ Usage
To use `auto-make`, simply pass your command as a string argument:

```bash
automake "run the tests and generate a coverage report"
```

The tool will find the corresponding target in your `Makefile` and execute it.

For detailed usage information and available options, run:
```bash
automake help
```

## 🛠️ Configuration
On first run, `auto-make` will create a `config.toml` file in your user configuration directory. You can edit this file to change the default Ollama model or other settings.

Example `config.toml`:
```toml
# Default configuration for auto-make
[ollama]
model = "qwen3:0.6b" # Specify the Ollama model you want to use
```

## 🎬 Demos
Want to see some UI/UX demos?
Just run `uv run make demo-all`
or use automake: `automake "show all demos"`

> **Note:** Running demos with automake may cause animation display issues. For the best demo experience, use the direct `uv run make demo-all` command.

## 🗺️ Project Roadmap
For a detailed breakdown of the project roadmap, implementation phases, and technical specifications, see [SPECS.md](SPECS.md).

## 🚀 Development & Publishing

### For Contributors
This project uses modern Python tooling and automated publishing:

- **Package Management**: [UV](https://github.com/astral-sh/uv) for fast dependency management
- **Code Quality**: Pre-commit hooks with Ruff for linting and formatting
- **Testing**: Pytest with comprehensive test coverage
- **CI/CD**: GitHub Actions for automated testing and publishing

### Publishing Process
The project uses **GitHub Actions with Trusted Publishing** for secure, automated releases:

- **Production**: Automatically publishes to PyPI when a GitHub release is created
- **Testing**: Manual workflow to test publishing on TestPyPI before production releases

For detailed publishing instructions, see [docs/PUBLISHING.md](docs/PUBLISHING.md).

### Installation Methods
```bash
# Direct execution (recommended for users)
uvx automake-cli

# Alternative with explicit package name
uvx --from automake-cli automake

# Traditional pip installation
pip install automake-cli
```
