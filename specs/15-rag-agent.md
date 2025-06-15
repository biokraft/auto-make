# 15. RAG Agent Specification (High-Level Sketch)

## 1. Purpose
This document provides a high-level sketch for a Retrieval-Augmented Generation (RAG) agent. The purpose of this agent is to provide the `automake` assistant with a deep understanding of the user's projects by indexing local directories into a persistent knowledge base and answering questions based on that content.

## 2. Vision
A user should be able to ask complex, context-aware questions about their codebase, and the agent should be able to answer them accurately.
- `automake "how is authentication handled in this fastapi app?"`
- `automake "summarize the purpose of the data_processing.py file"`
- `automake "index my project documentation located in the ./docs folder"`

## 3. Core Components

### 3.1. The `RAGAgent`
- This will be a new `ManagedAgent` available to the `ManagerAgent`.
- The `ManagerAgent` will learn to route knowledge-based questions to this specialist.

### 3.2. Local Vector Store
- To align with the project's "local-first" principle, the RAG system will use a file-based vector database (e.g., **LanceDB**, ChromaDB).
- The database will be stored in a dedicated directory within the user's configuration folder (e.g., `~/.config/automake/rag_db/`).
- This avoids the need for external services or servers.

### 3.3. Core Tools
The `RAGAgent` will be equipped with two primary tools:

1.  **`index_directory(path: str, recursive: bool = True) -> str`**:
    - **Function**: Scans a directory, reads supported files (`.py`, `.md`, `.txt`, etc.), splits them into text chunks, generates embeddings using the configured Ollama model, and stores them in the vector database.
    - **User Flow**: The user explicitly tells the agent to index a path.

2.  **`query_knowledge_base(question: str) -> str`**:
    - **Function**: Takes a user's question, generates an embedding, performs a similarity search on the vector DB to find relevant chunks, and then uses the main LLM to synthesize an answer based on those chunks.
    - **User Flow**: The `ManagerAgent` delegates a question to the `RAGAgent`, which then uses this tool.

## 4. High-Level Architecture
1.  **Indexing**: The user invokes the agent with a command like `automake "index this project"`. The `ManagerAgent` passes this to the `RAGAgent`, which uses the `index_directory` tool.
2.  **Querying**: The user asks `automake "how does the config loader work?"`. The `ManagerAgent` recognizes this as a knowledge query and delegates to the `RAGAgent`.
3.  **Retrieval & Generation**: The `RAGAgent` uses its `query_knowledge_base` tool. The retrieved context and the original question are sent to the LLM, which generates a final, informed answer for the user.

## 5. Implementation Notes
- This is a significant feature and should be implemented after the core agent functionality is stable.
- The choice of embedding model will be critical. Initially, it can default to the user's primary configured Ollama model.
- We will need to add dependencies for the chosen vector DB (`lancedb`) and potentially text-splitting libraries (`langchain-text-splitters`).

## 6. Out of Scope (for initial version)
- Automatic re-indexing on file changes. Indexing will be a manual user-triggered process.
- Complex data sources (e.g., PDFs, Word documents). The initial focus is on plain text and code files.
- Multiple, separate knowledge bases. A single, global knowledge base will be used initially.
