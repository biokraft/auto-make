# Logging Strategy Specification

## 1. Purpose
This document defines the logging strategy for the AutoMake application. The goal is to capture essential information for debugging and monitoring while ensuring robust support for concurrent application instances.

## 2. Functional Requirements
- The application must log events to a file.
- Log files will be stored in a platform-specific user log directory (e.g., `~/.local/state/automake/logs` on Linux, `~/Library/Logs/automake` on macOS).
- **Concurrent Session Support**: To prevent conflicts when multiple instances of AutoMake run simultaneously, each session will generate a unique log file.
  - Log filenames will be based on the process ID (PID) and the current date, following the pattern: `automake_YYYY-MM-DD_PID.log`.
- **Log Retention**: Log files older than 7 days must be automatically deleted. This cleanup process will run at application startup.

## 3. Log Levels and Content
The application will use standard log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
- **`INFO`**: High-level information about the application's flow.
    - Example: "Interpreting user command: '...'", "Executing command: 'make ...'".
- **`DEBUG`**: Detailed information for developers, including the full prompt sent to the LLM and the raw response received. This should be disabled by default but configurable.
- **`ERROR`**: Used when the application encounters a critical error.
    - Example: "Could not connect to Ollama server at ...", "Makefile not found".

## 4. Implementation Notes
- The standard Python `logging` module is used.
- A custom `setup_logging` function handles the creation of PID-based log files and the startup-based cleanup of old logs.
- The `appdirs` library is used to reliably determine the correct cross-platform log directory.
- A configuration setting in `config.toml` allows the user to set the log level.

**Example `config.toml` addition:**
```toml
# ... existing config ...

[logging]
# Set log level for troubleshooting.
# Accepted values: "INFO", "DEBUG", "WARNING", "ERROR"
level = "INFO"
```

## 5. Log Format
Logs are structured to be easily parsable. The format is:
`%(asctime)s - %(name)s - %(levelname)s - %(message)s`

**Example Log Entry:**
`2023-10-27 10:00:00,123 - automake - INFO - Executing command: make build`

## 6. Out of Scope
- Sending logs to a remote aggregation service (e.g., Datadog, Splunk).
- A special CLI command for viewing or tailing logs. Users will access the files directly.
