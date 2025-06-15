# 14. Agent Interaction Scaffolding Specification

## 1. Purpose
This document specifies the design for a standardized scaffolding to manage interactive, multi-turn agent sessions. The goal is to create a reusable, maintainable, and consistent framework for handling the UI/UX of conversations between the user and the agent, including the complexities of streaming thoughts, tool calls, and results.

## 2. Core Component: `InteractiveSession` ABC
The heart of this scaffolding will be an Abstract Base Class (ABC) named `InteractiveSession`. This class will define the contract for any component that manages a live, interactive agent conversation.

### 2.1. Abstract Methods and Properties
The `InteractiveSession` ABC will define the following:
- **`__init__(self, agent: CodeAgent)`**: Constructor to link the session with a `smolagents` agent instance.
- **`start(self)`**: The main entry point to begin the interactive session. It will manage the main conversation loop.
- **`render(self, content: Any)` (abstract)**: A method responsible for rendering agent output (thoughts, tool calls, final answers) and user input within the `LiveBox` UI.
- **`get_user_input(self)` (abstract)**: A method to capture input from the user.
- **`update_state(self, new_state: str, tool_call: dict = None)` (abstract)**: A method to update and render the agent's current status (e.g., "Thinking...", "Executing tool...").

### 2.2. Concrete Implementation: `RichInteractiveSession`
A concrete class, `RichInteractiveSession`, will implement the `InteractiveSession` ABC using the `rich` library.
- It will use `rich.live.Live` to manage the dynamic display area.
- `render()` will update the `Live` display with formatted agent output, conversation history, and status updates.
- `get_user_input()` will use `rich.prompt.Prompt` to capture user input seamlessly within the live display.

## 3. Architecture & Data Flow
1.  **Instantiation**: An instance of `RichInteractiveSession` is created, linked to the `ManagerAgent`.
2.  **Session Start**: The `start()` method is called, which initializes the `rich.live.Live` context and enters the main loop.
3.  **User Input**: The loop waits for user input via `get_user_input()`.
4.  **Agent Invocation**: The user's prompt is passed to `agent.run(prompt, stream=True)`.
5.  **Streaming & Rendering**: The session manager iterates through the generator returned by `agent.run()`:
    - For each item yielded by the agent (e.g., `Thought`, `Action`, `Observation`), it calls `update_state()` and `render()` to update the `LiveBox` in real-time. This provides a transparent view into the agent's process.
6.  **Loop Continuation**: After the agent finishes and the final output is rendered, the loop returns to step 3, waiting for the next user input.
7.  **Session End**: The loop terminates when the user types `exit` or `quit`.

## 4. State Management
The `InteractiveSession` will manage the state of the conversation, including:
- **`history`**: A list of all messages exchanged between the user and the agent.
- **`status`**: The current status of the agent (e.g., `WAITING_FOR_INPUT`, `THINKING`, `EXECUTING_TOOL`).
- **`last_tool_call`**: Information about the last tool call for detailed rendering.

## 5. Implementation Notes
- The `InteractiveSession` and its `rich` implementation will be located in the `automake.agent.ui` module.
- The scaffolding should be designed to be decoupled from the agent's core logic. Its sole responsibility is to manage the user-facing interaction layer.
- This scaffolding will replace any ad-hoc implementation of the interactive loop for the `automake agent` command.

## 6. Acceptance Criteria
- An `InteractiveSession` ABC is defined in the codebase.
- A `RichInteractiveSession` class implements the ABC using `rich`.
- The `automake agent` command uses the `RichInteractiveSession` to manage the chat.
- The UI clearly shows the agent's thoughts, tool calls, and final responses in a structured manner.

## 7. Out of Scope
- Non-CLI-based UIs (e.g., web interfaces). The focus is on a `rich`-based terminal experience.
- Persistence of conversation history between sessions.
