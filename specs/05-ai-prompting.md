# AI Prompting Specification

## 1. Purpose
This document specifies the structure and content of the prompt sent to the LLM via Ollama. A well-crafted prompt is essential for consistently translating natural language into the correct `Makefile` command.

## 2. Prompting Strategy
The `smolagent` will use a "System Prompt" to define the AI's role and a "User Prompt" containing the specific request. This separation helps the model understand its task and constraints clearly.

### 2.1. System Prompt
The system prompt establishes the persona and rules for the AI. It will be a constant template.

**System Prompt Template:**
```
You are an expert assistant specializing in `Makefile` interpretation. Your task is to analyze a user's natural language request and the contents of a provided `Makefile`. You must identify the most appropriate `make` command target and related commands that fulfill the user's request.

**Output Format:**
You MUST respond with a single, valid JSON object. Do not include any other text, explanations, or markdown formatting outside of the JSON object. The JSON object must have the following structure:
{
  "reasoning": "A brief, one-sentence explanation of why you chose the primary command.",
  "command": "The single, most appropriate `make` target name. Do not include the word 'make'. If no command is suitable, this must be `null`.",
  "alternatives": [
    "The second most likely `make` target name.",
    "The third most likely `make` target name."
  ],
  "confidence": "An integer from 0 to 100, representing your confidence that the 'command' is the correct one. 100 is absolute certainty. If 'command' is `null`, confidence must be 0."
}

**Rules:**
1.  If the user's request seems to include parameters (e.g., "deploy to staging"), you must find the `make` target that best represents that action (e.g., `deploy-staging`). Do not attempt to pass arguments to the `make` command itself.
2.  Provide up to two plausible alternatives, but the list can be empty if no other commands are relevant.
3.  The `confidence` score should reflect your certainty in the primary `command`. A low score indicates ambiguity.
4.  If no suitable command is found in the Makefile for the user's request, you must set `command` to `null` and `confidence` to 0.
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
- Error handling must be implemented to parse the JSON response from the LLM. The application must handle potential `JSONDecodeError` and validate the structure of the received object.
- The CLI should use the `command`, `alternatives`, and `confidence` fields to drive the execution flow as described in `specs/01-core-functionality.md`.

## 4. Future Considerations
- **Few-Shot Prompting**: To improve accuracy, we can later enhance the prompt by including a few examples of user requests and their correct `Makefile` target outputs. This can be added to the system prompt.
- **Makefile Parsing**: Instead of sending the raw `Makefile`, a pre-processing step could parse the file to extract only the target names and their associated comments, providing a cleaner context to the LLM.
