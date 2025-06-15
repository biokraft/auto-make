# 12. Autonomous Agent Mode Specification

## 1. Purpose
This document specifies the requirements for a new autonomous agent mode in AutoMake. This mode provides an interactive chat session within the CLI, allowing users to collaborate with an AI agent that can execute terminal commands, run code, and access the internet to accomplish complex tasks, guided by the principles of the `smolagents` framework.

## 2. Functional Requirements

### 2.1. Invocation
- The agent mode shall be accessible via the `automake agent` command.
- If invoked with a prompt (e.g., `automake agent "list all python files"`), the agent will execute the task non-interactively and exit.
- If invoked without a prompt (i.e., `automake agent`), the agent will launch an interactive chat session within the terminal.

### 2.2. Interactive Chat Session
- The chat interface will be built using the `rich` library to ensure a seamless and polished user experience consistent with the existing AutoMake CLI.
- The interface will support a continuous conversation loop, maintaining context throughout the session.
- Users can exit the session by typing `exit` or `quit`.

### 2.3. Agent Capabilities & Architecture
AutoMake will adopt a multi-agent architecture, a pattern that yields better performance through specialization. This will be orchestrated by a central **Manager Agent** that delegates tasks to a suite of specialized agents.

The agent ecosystem, powered by `smolagents`, will be comprised of:
- **Manager Agent**: The primary `CodeAgent` that interacts with the user. It analyzes requests and orchestrates the specialist agents to fulfill the user's goal. It does not execute tasks directly.
- **Terminal Agent**: A `ManagedAgent` equipped with tools to run arbitrary shell commands (e.g., `ls`, `git status`).
- **Coding Agent**: A `ManagedAgent` with a sandboxed Python environment to execute generated code for calculations, file I/O, or scripting tasks.
- **Web Agent**: A `ManagedAgent` that uses the `DuckDuckGoSearchTool` to query the internet.
- **Makefile Agent**: A `ManagedAgent` with tools to list and execute `Makefile` targets, preserving AutoMake's core function.

### 2.4. Core Logic: Code Agents & the ReAct Loop
- The system will be built on `smolagents.CodeAgent`. This approach, where the LLM writes actions as Python code snippets, is more natural and flexible than JSON-based tool calling. It provides superior composability, object management, and generality.
- The agent will operate autonomously using the **ReAct (Reason-Act)** framework. At each step, it will:
    1.  **Reason**: Analyze the task and its memory to decide on the next best action.
    2.  **Act**: Generate a Python code snippet to call the appropriate specialist agent (e.g., `terminal_agent.run("ls -l")`).
- The agent's thought process and the actions it takes will be streamed to the user for full transparency.

## 3. Non-functional Requirements / Constraints
- **Security**: Code execution must be strictly sandboxed. The `Coding Agent` will be configured with `executor_type="docker"` to isolate file system and network access from the host machine. This is a core security feature of `smolagents`.
- **Performance**: Agent response time should be optimized for a fluid conversational experience.
- **UI/UX**: The chat interface must be intuitive and visually consistent with the AutoMake CLI. It must not rely on external web UIs like Gradio.

## 4. Architecture & Data Flow
- The feature will be built on the `smolagents` library, utilizing a `ManagerAgent` (`CodeAgent`) and several `ManagedAgent` instances.
- The CLI will be updated in `automake/cli/main.py` to include the `agent` command.
- A new module, `automake.agent`, will be created with the following structure:
  - `manager.py`: Contains the factory function to initialize the main `ManagerAgent`.
  - `specialists.py`: Defines the specialist agents (`TerminalAgent`, `CodingAgent`, etc.) as `ManagedAgent` instances, encapsulating their respective tools.
  - `ui.py`: Manages the `rich`-based interactive session.
- The `smolagents` framework follows a clear execution cycle:
    1. **Initialization**: The system prompt is stored in a `SystemPromptStep` and the user query in a `TaskStep`.
    2. **ReAct Loop**:
        - The agent's memory (a log of all previous steps) is written to a list of messages via `agent.write_memory_to_messages()`.
        - These messages are sent to the LLM.
        - The LLM's response (a code snippet) is parsed into an `ActionStep`.
        - The action is executed, and the result is logged to memory.
    This loop continues until the task is complete.

## 5. Implementation Notes
- The interactive UI in `automake/agent/ui.py` will use `rich.live.Live` and `rich.prompt.Prompt`.
- The UI loop will iterate over the `manager_agent.run(prompt, stream=True)` generator to display the agent's step-by-step reasoning and actions.
- `automake/agent/specialists.py` will define each specialist. For example:
  ```python
  from smolagents import CodeAgent, ManagedAgent, tool

  @tool
  def run_shell_command(command: str) -> str:
      """Executes a shell command and returns its output."""
      # ... implementation ...

  terminal_agent_logic = CodeAgent(tools=[run_shell_command], executor_type="docker")
  terminal_agent = ManagedAgent(
      agent=terminal_agent_logic,
      name="terminal_agent",
      description="Use this agent to execute shell commands in the user's terminal."
  )
  ```
- The main `ManagerAgent` will be initialized with a list of these `ManagedAgent` instances in its `managed_agents` parameter.

## 6. Acceptance Criteria
- Running `automake agent` opens a `rich`-based chat window.
- The user can ask the agent to perform tasks (e.g., "what's in the current directory?").
- The manager agent correctly delegates the task to the `terminal_agent`, which executes `ls` and displays the output.
- The agent can answer a web-based question by delegating to the `web_agent`.
- The agent can execute a `Makefile` target by delegating to the `makefile_agent`.
- Running `automake agent "create a file named test.txt"` delegates to the `coding_agent` to create the file, then exits.

## 7. Out of Scope
- Multi-user sessions.
- Long-term memory or persistence of conversation history between sessions.
