# Graceful Shutdown and Signal Handling Specification

## 1. Purpose
This specification defines the application's behavior for handling POSIX signals, specifically `SIGINT` (Ctrl+C) and `EOF` (Ctrl+D), to ensure a graceful shutdown of all components, including the main application, the agent manager, and any specialist agents.

## 2. Functional Requirements
- **`Ctrl+C` (`SIGINT`) Handling**:
  - The application MUST intercept the `SIGINT` signal.
  - Upon receiving `SIGINT`, the application MUST initiate a graceful shutdown sequence.
  - This sequence includes:
    - Stopping any active agent sessions.
    - Terminating any child processes spawned by agents (e.g., `uv` sandboxed processes).
    - Cleaning up temporary resources.
    - Printing a clear "Shutting down..." message to the user.
    - Exiting with a non-zero status code to indicate termination by signal.

- **`Ctrl+D` (`EOF`) Handling**:
  - In interactive modes (e.g., `automake agent`), `Ctrl+D` should be interpreted as a request to end the session.
  - The application MUST detect the `EOFError` that typically results from a `Ctrl+D` in input streams.
  - Upon detection, the application will:
    - Gracefully terminate the interactive session.
    - Exit with a status code of 0.

## 3. Architecture & Data Flow
- A central signal handler will be registered at the application entry point (in `automake/cli/app.py` or `automake/__main__.py`).
- This handler will be responsible for coordinating the shutdown across different components.
- The `AgentManager` will expose a `shutdown()` method that can be called by the signal handler.
- The `AgentManager.shutdown()` method will be responsible for stopping all managed agents and their subprocesses.
- Interactive session components (like `RichInteractiveSession`) will handle `KeyboardInterrupt` (raised from `Ctrl+C`) and `EOFError` (from `Ctrl+D`) within their input loops and trigger the shutdown process.

## 4. Implementation Notes
- Standard Python libraries `signal` and `atexit` can be used.
- The `signal` module can be used to register custom handlers for `SIGINT`.
- The main input loop in interactive sessions should be wrapped in a `try...except` block to catch `KeyboardInterrupt` and `EOFError`.
- Care must be taken to ensure that child processes created by agents are properly terminated to avoid zombie processes. Process groups (`os.setpgrp`) might be useful here.

## 5. Acceptance Criteria
- Pressing `Ctrl+C` at any point while the application is running (either in interactive mode or during a non-interactive command) causes the application to exit cleanly within a few seconds.
- Pressing `Ctrl+D` in the interactive agent chat causes the session to end and the application to exit.
- No zombie processes are left running after the application terminates.
- A user-friendly message is displayed upon shutdown.
