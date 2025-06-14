# Logging Strategy Specification

## 1. Purpose
This document defines the logging strategy for the AutoMake application. The goal is to capture essential information for debugging and monitoring while managing log file size and retention.

## 2. Functional Requirements
- The application must log events to a file.
- Log files will be stored in a platform-specific user log directory (e.g., `~/.local/state/automake/logs` on Linux, `~/Library/Logs/automake` on macOS).
- Logging should be configured with a rotation policy: a new log file is created for each day.
- Log files older than 7 days must be automatically deleted.

## 3. Log Levels and Content
The application will use standard log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
- **`INFO`**: High-level information about the application's flow.
    - Example: "Interpreting user command: '...'", "Executing command: 'make ...'".
- **`DEBUG`**: Detailed information for developers, including the full prompt sent to the LLM and the raw response received. This should be disabled by default but configurable.
- **`ERROR`**: Used when the application encounters a critical error.
    - Example: "Could not connect to Ollama server at ...", "Makefile not found".

## 4. Implementation Notes
- The standard Python `logging` module should be used.
- The `logging.handlers.TimedRotatingFileHandler` is perfectly suited for implementing the daily rotation and backup count (which directly translates to the retention period).
- The `appdirs` library or a similar utility can be used to reliably determine the correct cross-platform log directory.
- A configuration setting in `config.toml` should allow the user to enable `DEBUG` level logging for troubleshooting.

**Example `config.toml` addition:**
```toml
# ... existing config ...

[logging]
# Set log level to "DEBUG" for verbose output for troubleshooting.
# Accepted values: "INFO", "DEBUG", "WARNING", "ERROR"
level = "INFO"
```

## 5. Log Format
Logs should be structured to be easily parsable. A good default format is:
`%(asctime)s - %(name)s - %(levelname)s - %(message)s`

**Example Log Entry:**
`2023-10-27 10:00:00,123 - automake.core - INFO - Executing command: make build`

## 6. Out of Scope
- Sending logs to a remote aggregation service (e.g., Datadog, Splunk).
- A special CLI command for viewing or tailing logs. Users will access the files directly. 