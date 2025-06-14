# AI Prompting Specification

## 1. Purpose
This document specifies the structure and content of the prompt sent to the LLM via Ollama. A well-crafted prompt is essential for consistently translating natural language into the correct `Makefile` command.

## 2. Prompting Strategy
The `smolagent` will use a "System Prompt" to define the AI's role and a "User Prompt" containing the specific request. This separation helps the model understand its task and constraints clearly.

### 2.1. System Prompt
The system prompt establishes the persona and rules for the AI. It will be a constant template.

**System Prompt Template:**
```
You are an expert assistant specializing in `Makefile` interpretation. Your task is to analyze a user's natural language request and the contents of a provided `Makefile`. You must identify the single, most appropriate `make` command target that fulfills the user's request.

**Rules:**
1.  Your response must contain **only** the name of the `make` target.
2.  Do **not** include the word "make".
3.  Do **not** include any explanation, markdown formatting, or any other text.
4.  If the user's request seems to include parameters (e.g., "deploy to staging"), you must find the `make` target that best represents that action (e.g., `deploy-staging`). Do not attempt to pass arguments to the `make` command itself.
5.  If no suitable command is found, you must return the exact string "NO_COMMAND_FOUND".
```

### 2.2. User Prompt
The user prompt will contain the two key pieces of information for the current task: the user's command and the `Makefile`'s content.

**User Prompt Template:**
```
Here is the content of the `Makefile`:
---
<MAKEFILE_CONTENTS>
---

Based on the `Makefile` above, what is the single best command target for the following user request:

User Request: "<USER_COMMAND>"
```

## 3. Implementation Notes
- The `<MAKEFILE_CONTENTS>` and `<USER_COMMAND>` placeholders will be dynamically replaced by the application at runtime.
- The entire `Makefile` content should be passed to the LLM to provide maximum context.
- Error handling must be implemented to manage the `NO_COMMAND_FOUND` response from the LLM. The CLI should inform the user that their command could not be interpreted.

## 4. Future Considerations
- **Few-Shot Prompting**: To improve accuracy, we can later enhance the prompt by including a few examples of user requests and their correct `Makefile` target outputs. This can be added to the system prompt.
- **Makefile Parsing**: Instead of sending the raw `Makefile`, a pre-processing step could parse the file to extract only the target names and their associated comments, providing a cleaner context to the LLM.
