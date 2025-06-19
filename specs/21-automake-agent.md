# 21. `AutoMakeAgent`: Self-Referential Command Execution

## Purpose
To provide a specialized agent capable of interpreting natural language commands and translating them into executable `automake` CLI commands. This enables users to interact with `automake`'s own features using natural language, creating a self-referential and more intuitive user experience.

## Functional Requirements
- The `AutoMakeAgent` shall be responsible for handling user prompts that are explicitly directed at controlling the `automake` tool itself.
- It must be able to translate natural language queries into valid `automake` subcommands and arguments (e.g., "start an agent session" -> `automake agent`).
- The `ManagerAgent` must be equipped with a routing mechanism to identify and delegate such prompts to the `AutoMakeAgent`.
- To ensure it generates valid commands, the agent's context must be populated with a dynamically generated list of all available `automake` commands. This can be achieved by parsing the output of `automake --help`.

## Non-functional Requirements / Constraints
- **Accuracy**: The agent must exhibit a high degree of accuracy in translating user intent into the correct `automake` command.
- **Performance**: The overhead of routing and translation by the `AutoMakeAgent` should be minimal to maintain a responsive user experience.
- **Extensibility**: The agent's design should easily accommodate the addition of new `automake` commands in the future.

## Architecture & Data Flow
1. The user provides a prompt, such as `automake "show me the logs"`.
2. The main CLI entry point forwards the prompt to the `ManagerAgent`.
3. The `ManagerAgent`'s initial routing prompt asks the LLM to classify the user's intent. If the intent is to execute an `automake` command, it selects the `AutoMakeAgent`.
4. The `ManagerAgent` invokes the `AutoMakeAgent` with the user's prompt. The `AutoMakeAgent` is provided with system context that includes the full `automake --help` output.
5. The `AutoMakeAgent` processes the prompt and returns a single, executable `automake` command string.
6. The `ManagerAgent` receives the command string.
7. The command is then executed by the appropriate specialist (e.g., `TerminalAgent`).

## Implementation Notes
- A new specialist agent, `AutoMakeAgent`, will be created.
- The `ManagerAgent`'s routing logic will be updated to include the `AutoMakeAgent` as a potential delegate.
- A mechanism to capture the output of `automake --help` and inject it into the `AutoMakeAgent`'s context will be implemented.

## Acceptance Criteria
- Running `automake "start a new agent session"` should successfully launch the interactive agent mode.
- Running `automake "check the logs"` should execute the `automake logs` command.
- Prompts not related to `automake`'s functionality (e.g., `automake "what is in the current directory"`) should be routed to other appropriate agents, not the `AutoMakeAgent`.

## Out of Scope
- Chaining multiple `automake` commands from a single prompt.
- Interactive dialogues to clarify ambiguous `automake` commands. The agent should aim to execute the most likely command based on the prompt.

## Risks & Mitigations
- **Risk**: The agent may misinterpret the user's intent and generate an incorrect or harmful `automake` command.
  - **Mitigation**: The agent's prompt will be carefully engineered for accuracy. The action confirmation feature (`agent.require_confirmation = true`) can be enabled by the user to require approval before execution.
- **Risk**: Changes to the CLI (new or modified commands) could make the agent's knowledge outdated.
  - **Mitigation**: The agent's context is built dynamically from the `automake --help` output at runtime, ensuring it always has up-to-date command information.

## Future Considerations
- Enhance the agent to support more complex interactions, such as guiding a user through the `automake init` process.
- Allow the agent to query the user for clarification if a prompt is ambiguous.
