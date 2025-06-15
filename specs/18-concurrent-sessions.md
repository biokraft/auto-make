# 18. Concurrent Session Support Specification

## 1. Purpose
This document specifies the necessary changes to allow multiple `automake` processes to run concurrently without causing state conflicts. This is essential for enabling workflows where a user might have several `automake` agent sessions active in different terminal windows or panes.

## 2. The Challenge: State Conflicts
Analysis of the existing architecture reveals two potential sources of conflict:
1.  **Logging**: The current strategy (`specs/06-logging-strategy.md`) uses a single daily log file. Multiple processes writing to this file simultaneously would result in corrupted, interleaved log entries, making debugging impossible.
2.  **File System Operations**: The `FileSystemAgent` (`specs/12-autonomous-agent-mode.md`) can be instructed to write to files. While this is a user-directed action, concurrent writes to the same file from different agent sessions could lead to data loss.

The file system conflict is an inherent risk of the tool's power and is mitigated by the user confirmation step. Therefore, this specification will focus exclusively on resolving the logging conflict.

## 3. Functional Requirements

### 3.1. Process-Isolated Logging
- Each `automake` process instance MUST write its logs to a unique file.
- The log filename MUST incorporate the Process ID (PID) to guarantee uniqueness.

### 3.2. Log Filename Convention
- Log files shall be named using the format: `automake_YYYY-MM-DD_PID.log`.
- Example: `automake_2024-07-30_12345.log`

### 3.3. Log Retention and Cleanup
- The existing requirement to retain logs for 7 days remains.
- The previous log rotation mechanism (`TimedRotatingFileHandler`) is no longer suitable for managing a variable number of log files.
- Instead, a new startup-based cleanup mechanism shall be implemented:
    - On every `automake` invocation, before logging is initialized, the application will scan the log directory.
    - It will delete any log files (`automake_*.log`) whose creation date is older than 7 days.

## 4. Implementation Notes
- The logging setup logic must be modified to generate the unique, PID-based log filename for the current process.
- The `TimedRotatingFileHandler` should be replaced with a standard `logging.FileHandler` pointed at the unique log file.
- A new function should be created and called on startup to perform the log cleanup task. This function will list files in the log directory, check their creation timestamp (or last modified, though creation is more accurate for this purpose), and delete them if they are too old.
- This change deprecates the daily rotation and backup count feature in favor of a simpler, more robust cleanup process that is compatible with concurrent execution.

## 5. Out of Scope
- A locking mechanism for file system writes. This remains the user's responsibility, supported by the action confirmation feature.
