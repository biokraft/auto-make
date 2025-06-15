# 12. Autonomous Agent Mode Specification

## 1. Purpose
This document specifies the requirements for a new autonomous agent mode in AutoMake. This mode provides an interactive chat session within the CLI, allowing users to collaborate with an AI agent that can execute terminal commands, run code, and access the internet to accomplish complex tasks.

## 2. Functional Requirements

### 2.1. Invocation
- The agent mode shall be accessible via the `automake agent` command.
- If invoked with a prompt (e.g., `automake agent "list all python files"`), the agent will execute the task non-interactively and exit.
- If invoked without a prompt (i.e., `automake agent`), the agent will launch an interactive chat session within the terminal.

### 2.2. Interactive Chat Session
- The chat interface will be built using the `rich` library to ensure a seamless and polished user experience consistent with the existing AutoMake CLI.
- The interface will support a continuous conversation loop, maintaining context throughout the session.
- Users can exit the session by typing `exit` or `quit`.

### 2.3. Agent Capabilities & Tools
The agent, powered by `smolagents`, will be equipped with the following core tools:
- **Terminal Execution**: A tool to run arbitrary shell commands (e.g., `ls`, `git status`, `docker ps`).
- **Code Interpreter**: A sandboxed Python environment to execute generated code for calculations, file manipulation, or other scripting tasks.
- **Web Search**: A tool to query the internet for information, documentation, or troubleshooting steps.
- **Makefile Integration**: Tools to list and execute `Makefile` targets, preserving the core functionality of AutoMake.

### 2.4. Autonomy
- The agent will operate autonomously, deciding which tool to use based on the user's prompt and the ongoing conversation.
- It will follow the Reason-Act-Observe (ReAct) loop to break down complex tasks into smaller, executable steps.
- The agent's thought process and tool usage will be displayed to the user for transparency, likely within a collapsible or verbose-mode-gated section of the UI.

## 3. Non-functional Requirements / Constraints
- **Security**: All code and command execution must be sandboxed. The primary recommended method is using Docker via the `smolagents` `executor_type="docker"` parameter. This isolates file system and network access from the host machine, relying on a common developer tool. E2B is a viable but secondary alternative due to its external dependency.
- **Performance**: The agent's response time should be optimized for a fluid conversational experience. LLM and tool execution latency should be minimized.
- **UI/UX**: The chat interface must be intuitive, responsive, and visually consistent with the rest of the AutoMake CLI. It should not rely on web-based UIs like Gradio.

## 4. Architecture & Data Flow
- The feature will be built on the `smolagents` library, utilizing a `smolagents.CodeAgent`.
- The CLI will be updated in `automake/cli/main.py` to include the `agent` command with interactive and non-interactive invocation logic.
- A new module, `automake.agent`, will be created with the following structure:
  - `core.py`: Contains the factory function to initialize the `CodeAgent`.
  - `tools.py`: Defines custom tools for terminal and Makefile interaction using the `@tool` decorator.
  - `ui.py`: Manages the `rich`-based interactive session, handling user input and rendering agent output.
- The `smolagents` instance will inherently maintain the conversation memory for multi-turn interactions within a single session.

## 5. Implementation Notes
- The interactive UI in `automake/agent/ui.py` will be built using `rich.live.Live` for dynamic updates and `rich.prompt.Prompt` for user input.
- The core of the UI loop will iterate over the `agent.run(prompt, stream=True)` generator to display the agent's step-by-step reasoning and tool usage.
- Custom tools in `automake/agent/tools.py` will include:
  - `terminal_tool(command: str) -> str`: Executes a shell command and returns its output.
  - `makefile_tool(target: str = "") -> str`: Lists available `Makefile` targets or executes a specific one.
- The web search capability will be provided by importing and using the built-in `smolagents.DuckDuckGoSearchTool`.
- Security will be enforced by initializing the `CodeAgent` with `executor_type="docker"`.

## 6. Acceptance Criteria
- Running `automake agent` opens a `rich`-based chat window.
- The user can have a conversation with the agent (e.g., "what's in the current directory?").
- The agent correctly uses the terminal tool to execute `ls` and displays the output.
- The agent can answer a web-based question (e.g., "what's the latest version of flask?").
- The agent can execute a `Makefile` target when asked.
- Running `automake agent "create a file named test.txt"` creates the file and exits.

## 7. Out of Scope
- Multi-user sessions. The agent session is tied to the terminal instance that started it.
- Long-term memory or persistence of conversation history between sessions.
