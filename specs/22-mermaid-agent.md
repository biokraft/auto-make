# 22. `MermaidAgent`: Diagram Generation Specialist

## Purpose
To provide a specialized agent capable of reading specified source files, understanding their structure or logic, and generating a corresponding diagram using Mermaid syntax. This agent will save the generated chart into a `.mmd` file.

## Functional Requirements
- The `MermaidAgent` shall be a specialist agent (`ManagedAgent`) within the multi-agent framework.
- It must be equipped with tools to:
    - Read the contents of one or more specified files.
    - Write content to a specified `.mmd` file.
- The agent's primary function is to process a user prompt like `"Create a sequence diagram of the login process described in auth.py and save it to login_flow.mmd"` and generate the correct Mermaid syntax.
- The `ManagerAgent` must be able to route diagramming-related tasks to the `MermaidAgent`.

## Non-functional Requirements / Constraints
- **Accuracy**: The generated Mermaid diagram should accurately represent the logic or structure of the source files.
- **Clarity**: The generated syntax must be clean, valid, and well-formatted.
- **Extensibility**: The agent should be designed to potentially support different diagram types (flowchart, sequence, class diagram, etc.) offered by Mermaid.

## Architecture & Data Flow
1. The user provides a prompt to the `ManagerAgent` (e.g., `automake "document the main function in cli/app.py as a flowchart"`).
2. The `ManagerAgent`, through its ReAct loop, identifies the task as a diagramming request and selects the `MermaidAgent`.
3. The `ManagerAgent` invokes the `MermaidAgent` with the user's prompt.
4. The `MermaidAgent` uses its file-reading tool to analyze the specified source code (`cli/app.py`).
5. Based on its analysis, the `MermaidAgent`'s LLM generates the appropriate Mermaid syntax for a flowchart.
6. The `MermaidAgent` uses its file-writing tool to save the generated syntax into a `.mmd` file (e.g., `app_flowchart.mmd`).
7. The `MermaidAgent` reports the successful creation of the file back to the `ManagerAgent`.
8. The `ManagerAgent` informs the user that the diagram has been created.

## Implementation Notes
- A new specialist agent, `MermaidAgent`, will be created.
- It will be equipped with file system tools, likely reusing the ones available to the `FileSystemAgent` (e.g., `read_file`, `edit_file`). The `edit_file` tool should be used carefully to create or overwrite `.mmd` files.
- The `ManagerAgent`'s system prompt may need to be updated to make it aware of this new capability.

## Acceptance Criteria
- Given a Python file with a simple function, the user can ask the agent to create a flowchart, and a valid `.mmd` file is created with the correct Mermaid syntax.
- The agent can handle requests specifying both the source file and the destination `.mmd` file.
- Non-diagramming tasks are not routed to the `MermaidAgent`.

## Out of Scope
- Rendering the Mermaid diagram into an image (e.g., PNG, SVG). The agent is only responsible for generating the `.mmd` source file.
- Automatically identifying which files to diagram without user input. The user must specify the target files.

## Risks & Mitigations
- **Risk**: The generated diagram may be inaccurate or incomplete.
  - **Mitigation**: The agent's prompt will be engineered to focus on accuracy. For complex code, the agent might generate a basic structure that the user can refine manually.
- **Risk**: The agent might overwrite existing files unintentionally.
  - **Mitigation**: The file-writing tool's description should be clear about its behavior (overwrite vs. append). User confirmation can be enforced for file-writing operations.

## Future Considerations
- Add a tool to validate the generated Mermaid syntax.
- Extend the agent to read multiple files to generate more complex, system-wide diagrams.
- Integrate with a rendering tool to provide a final image as output.
