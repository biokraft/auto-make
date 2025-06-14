# 🤖 auto-make
*Makefiles without writing Makefiles.*

[![CI/CD Pipeline](https://github.com/seanbaufeld/auto-make/actions/workflows/main.yml/badge.svg)](https://github.com/seanbaufeld/auto-make/actions/workflows/main.yml)
[![PyPI version](https://badge.fury.io/py/automake-cli.svg)](https://badge.fury.io/py/automake-cli)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

---

**auto-make** is a Python-based command-line tool that leverages a local Large Language Model (LLM) to interpret your natural language commands and execute the correct `Makefile` target.

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
- An active [Ollama](https://ollama.ai/) server with a running model (e.g., `ollama run llama3`).

### Installation
Install `auto-make` using `uvx` (the `uv` equivalent of `npx`):
```bash
uvx automake-cli
```
This command temporarily installs and runs the `automake` CLI tool in an isolated environment.

## ✍️ Usage
To use `auto-make`, simply pass your command as a string argument:

```bash
automake "run the tests and generate a coverage report"
```

The tool will find the corresponding target in your `Makefile` and execute it.

## 🛠️ Configuration
On first run, `auto-make` will create a `config.toml` file in your user configuration directory. You can edit this file to change the default Ollama model or other settings.

Example `config.toml`:
```toml
# Default configuration for auto-make
[ollama]
model = "llama3" # Specify the Ollama model you want to use
```

## 🗺️ Project Roadmap
This project is actively developed. Here is the current implementation status based on our defined specifications:

| Phase | Focus Area | Key Deliverables | Status |
| :--- | :--- | :--- | :--- |
| 1 | Project Setup | Initialize project structure, `pyproject.toml` with `uv`, and pre-commit hooks. | ✅ DONE |
| 2 | Config & Logging Setup | Implement logic to create/read `config.toml` and set up file-based logging. | TBD |
| 3 | CLI Scaffolding | Create the basic `Typer` application, argument parsing, and help text. | ✅ DONE |
| 4 | Makefile Reader | Implement the logic to find and read the `Makefile` from the current directory. | TBD |
| 5 | Ollama Integration | Create a module to handle communication with the local Ollama server. | TBD |
| 6 | Smolagent Core | Develop the `smolagent` with a precise prompt for reliable command interpretation. | TBD |
| 7 | Execution Engine | Implement the subprocess logic to run the `make` command and stream output. | TBD |
| 8 | End-to-End Wiring | Integrate all components into a seamless workflow. | TBD |
| 9 | Unit & Integration Tests | Write tests for all core components and interactions. | 🔄 IN PROGRESS |
| 10 | CI/CD Pipeline | Implement GitHub Actions workflow for automated testing and coverage. | TBD |
| 11 | Packaging & Distribution | Configure `pyproject.toml` for `uvx` distribution. | ✅ DONE |
| 12 | Documentation | Write comprehensive `README.md` and user guides. | 🔄 IN PROGRESS |

## 🔮 Future Work
We have many exciting features planned for future releases:

- **Ambiguity Resolution**: Prompt the user with the top 3 likely targets when a command is unclear.
- **Dry-Run Mode**: Add a `--dry-run` flag to show the interpreted command without executing it.
- **Failure Detection**: Intelligently detect when the LLM or the executed command fails.
- **Makefile Generation**: Add `automake makefile` to intelligently scan a repo and generate a `Makefile`.
- **Multi-Provider LLM Support**: Add support for OpenAI, Anthropic, and other major LLM providers.

---

Made with ❤️ by [Sean Baufeld](https://github.com/seanbaufeld).
