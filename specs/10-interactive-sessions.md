# 10. Interactive Command Resolution

## 1. Purpose
This document specifies the functionality for an interactive command resolution session. This feature enhances `automake`'s robustness by allowing the user to clarify their intent when the LLM is not sufficiently confident in its interpretation of a natural language command.

## 2. Functional Requirements

### 2.1. Confidence Scoring and Trigger
- The LLM's response for a command interpretation request must include not only the most likely `make` command but also a confidence score (an integer between 0 and 100).
- The `automake` tool will define a confidence threshold in its configuration (e.g., `confidence_threshold = 90`).
- If the LLM's confidence score is at or above the threshold, the command is executed directly.
- If the confidence score is below the threshold, the interactive resolution mode is triggered.
- The interactive mode is also triggered if the `command` is `null` but the `alternatives` list is not empty.

### 2.2. Interactive Selection
- When triggered, the interactive mode will present the user with a list of the top 3 most likely `make` commands, as determined by the LLM.
- The user will be able to navigate this list using the arrow keys (up/down) and select a command by pressing Enter.
- An option to "Abort" or "Cancel" the operation must be included in the list.

### 2.3. User Flow
1. User runs `automake "..."`.
2. `automake` sends the request and the `Makefile` contents to the LLM.
3. The LLM returns a JSON object containing `{"command": "make ...", "confidence": 85, "alternatives": ["make ...", "make ..."]}`.
4. The tool checks `confidence` (85) against the `confidence_threshold` (90).
5. Since 85 < 90, interactive mode is triggered.
6. The CLI displays an interactive list:
   ```
   ? I'm not completely sure which command you meant. Please select one:
   > make deploy-staging
     make push
     make help
     [Abort]
   ```
7. User selects an option and presses Enter.
8. The selected command is executed, or the program exits if "Abort" is chosen.
9. If the LLM returns no primary `command` and no `alternatives`, the tool will display its standard help/usage message and exit, as defined in `specs/02-cli-and-ux.md`.

## 3. Technical Implementation

### 3.1. Recommended Library
- The interactive selection menu will be implemented using the `questionary` Python library. It provides the necessary `select` prompt type and is easy to integrate and test.

### 3.2. State Management
- The state for an interactive session is transient and should only persist for the duration of a single `automake` command invocation.
- No state regarding the interaction needs to be stored between different `automake` runs.

## 4. Non-functional Requirements
- The interaction must be fast and responsive.
- The UI must be clear and intuitive, guiding the user to a resolution.

## 5. Impact on Other Specifications
- `specs/01-core-functionality.md`: The core execution flow must be updated to include the confidence check and the branch for interactive resolution.
- `specs/05-ai-prompting.md`: The prompt sent to the LLM must be updated to require a confidence score and a list of alternatives in its response. The expected output format (JSON) must be clearly defined.
- `specs/03-architecture-and-tech-stack.md`: The `questionary` library should be added as a project dependency.
