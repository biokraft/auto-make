# 17. Codebase Exploration Agent Specification

## 1. Purpose
To create a sophisticated coding agent capable of understanding and interacting with a codebase in a manner similar to a human developer. This agent will use dynamic exploration and on-the-fly analysis rather than relying on static, pre-indexed vector embeddings (RAG). Its goal is to provide high-quality, context-aware assistance for complex development tasks like implementation, debugging, and refactoring.

## 2. Functional Requirements
- The agent must be able to explore the file system to understand project structure.
- It must be able to read and parse source code files to understand their content and structure.
- It must trace dependencies by following imports and function calls across multiple files.
- The agent will build a dynamic, in-memory understanding of the codebase relevant to the current task, rather than relying on a static index.
- It should be able to answer questions about the code, implement new features, and fix bugs based on its exploration.

## 3. Non-functional Requirements / Constraints
- **Performance**: The agent's exploration must be efficient to provide timely responses. Caching of file contents and analysis results should be used where appropriate.
- **Scalability**: The approach must be scalable to large, real-world codebases without a significant degradation in performance.
- **Extensibility**: The agent's toolset for exploration (e.g., parsers for different languages, dependency analyzers) should be extensible.
- **Accuracy**: The agent's understanding must be accurate and reflect the current state of the codebase.

## 4. Architecture & Data Flow
The Codebase Exploration Agent will be a specialist agent orchestrated by the `ManagerAgent`. It will be equipped with a suite of tools for dynamic code analysis.

1.  **User Query**: A user asks for a code-related task (e.g., "Implement feature X," "Why is function Y failing?").
2.  **Agent Invocation**: The `ManagerAgent` delegates the task to the `CodebaseExplorationAgent`.
3.  **Dynamic Exploration Loop**: The agent performs a series of actions to build context:
    - **`list_directory`**: To understand the project layout.
    - **`read_file`**: To inspect specific files.
    - **`analyze_dependencies`**: A new tool that uses static analysis (e.g., parsing ASTs) to identify imports, function definitions, and calls within a file.
    - **`follow_path`**: The agent decides which file to read next based on the analysis of the current file (e.g., following an import).
4.  **Context Building**: The agent synthesizes the information from its exploration into a coherent context map within its memory. This map is dynamic and tailored to the specific query.
5.  **Solution Generation**: Using the dynamically-built context, the agent generates code, explanations, or debugging suggestions.
6.  **Execution & Feedback (Optional)**: For implementation tasks, the agent can use existing tools (like the `CodingAgent`) to execute or test its generated code, creating an iterative refinement loop.

This approach avoids the pitfalls of RAG by building high-quality, relevant context on demand, mirroring the workflow of a senior developer.

## 5. Implementation Notes
- A new set of tools for code analysis needs to be developed (e.g., `analyze_dependencies`). These can leverage existing libraries for AST parsing (e.g., Python's `ast` module).
- The agent's core logic will be a loop that reasons about which tool to use next to expand its understanding of the codebase.
- The agent should be integrated into both the non-interactive (`automake "<prompt>"`) and interactive (`automake agent`) modes.

## 6. Out of Scope
- Full-blown static analysis for all programming languages. The initial implementation will focus on Python.
- Pre-emptive, whole-codebase indexing. Analysis is always on-demand.
