# 25. TDV (Test-Driven Vibing) Agent Specification

## 1. Purpose
To provide an autonomous agent that implements software features using a strict Test-Driven Development (TDD) workflow. This agent takes a specific development phase from a `SPECS.md` file and executes it, ensuring that all code is test-covered and developed incrementally.

## 2. Functional Requirements
- **Phase Ingestion:** The agent must be able to read `SPECS.md` and understand the deliverables for a given implementation phase.
- **Plan Generation:** The agent's first step must be to create a detailed `plan.md` file that breaks down the phase into a series of TDD cycles. It must wait for user approval of this plan.
- **TDD Cycle Execution:** The agent must rigorously follow the Red-Green-Refactor cycle:
    1.  Write a failing test.
    2.  Run tests to confirm failure.
    3.  Write the minimum implementation code to make the test pass.
    4.  Run tests to confirm success.
    5.  Refactor the code.
- **Plan Management:** The agent must update the `plan.md` file after each successful cycle.
- **Cleanup:** Upon completion of all tasks in `plan.md`, the agent must ask the user for permission to delete the file.

## 3. Architecture & Data Flow
1.  **Invocation**: The user asks `automake` to implement a phase (e.g., `automake "implement phase 1 from SPECS.md"`).
2.  **Delegation**: The `ManagerAgent` recognizes the "implementation" intent and delegates to the `TDVAgent`.
3.  **Planning**: The `TDVAgent` reads `@SPECS.md`, creates a `plan.md`, and asks for user approval.
4.  **Execution**: The `TDVAgent` uses the `CodingAgent` to write test and implementation files, and the `CommandRunner` to execute test commands. It follows the TDD cycle until the plan is complete.
5.  **Reporting**: The agent provides real-time feedback to the user, showing test outputs and code changes.

## 4. Implementation Notes
- This will be a new `ManagedAgent` that heavily utilizes the `CodingAgent` and a `CommandRunner` tool.
- The agent needs a state machine to track its progress through the TDD cycle (Red, Green, Refactor).
- The `refresh` command from the original TDV mode should be implemented as a standard capability to re-orient the agent.

## 5. Out of Scope
- Generating specifications; it only consumes them.
- Deviating from the approved `plan.md` without explicit user consent.
