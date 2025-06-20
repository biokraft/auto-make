# AutoMake Architecture Documentation

## Overview

AutoMake is built on a sophisticated multi-agent architecture using the `smolagents` framework. This document provides a comprehensive overview of the system design, data flow, and implementation details.

## Multi-Agent System Overview

### Core Philosophy

AutoMake follows a **delegation-based architecture** where a central Manager Agent orchestrates specialized agents to accomplish user tasks. This design provides:

- **Specialization**: Each agent is optimized for specific types of tasks
- **Modularity**: Agents can be developed and updated independently
- **Scalability**: New agents can be added without affecting existing ones
- **Reliability**: Agent failures are isolated and don't crash the entire system
- **Transparency**: All agent actions are logged and visible to users

### Agent Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                    Manager Agent                            │
│                  (Central Orchestrator)                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ├── Terminal Agent (Shell Commands)
                  ├── Coding Agent (Python Execution)
                  ├── Web Agent (Internet Search)
                  ├── Makefile Agent (Build Operations)
                  └── FileSystem Agent (File Operations)
```

## Manager Agent Responsibilities

The Manager Agent acts as the central coordinator and is responsible for:

### 1. Request Analysis
- Parsing natural language user inputs
- Determining task complexity and scope
- Identifying required capabilities and resources

### 2. Agent Selection and Delegation
- Choosing the most appropriate specialist agent(s)
- Breaking down complex tasks into manageable subtasks
- Coordinating multi-agent workflows

### 3. Workflow Orchestration
- Managing task execution order and dependencies
- Handling inter-agent communication
- Aggregating results from multiple agents

### 4. User Interface Management
- Streaming real-time progress updates
- Handling user confirmations and approvals
- Providing transparent feedback on agent decisions

### 5. Error Handling and Recovery
- Detecting and handling agent failures
- Implementing retry logic and fallback strategies
- Providing meaningful error messages to users

## Specialist Agent Descriptions

### Terminal Agent

**Purpose**: Execute shell commands and system operations

**Implementation**:
- Uses `subprocess.run()` with security constraints
- 5-minute timeout for command execution
- Captures both stdout and stderr
- Returns structured output with return codes

**Capabilities**:
- Execute arbitrary shell commands
- Handle complex command pipelines
- Process file system operations
- Manage environment variables

**Security Model**:
- Runs in user context (no privilege escalation)
- Command timeout prevents runaway processes
- Output sanitization for safe display

### Coding Agent

**Purpose**: Execute Python code in secure, isolated environments

**Implementation**:
- Creates temporary `uv` virtual environments per execution
- Automatic dependency management
- Sandboxed execution with cleanup
- Support for complex data analysis and scripting

**Capabilities**:
- Execute Python scripts with custom dependencies
- Perform data analysis and calculations
- Generate and run code solutions dynamically
- Handle file I/O operations through code

**Security Model**:
- Complete isolation using `uv` virtual environments
- Temporary directory cleanup after execution
- No access to host system beyond execution directory
- Dependency installation limited to specified packages

### Web Agent

**Purpose**: Search the internet and gather web-based information

**Implementation**:
- Integrates with DuckDuckGo Search API
- Structured result parsing and formatting
- Rate limiting and error handling
- Privacy-focused search (no tracking)

**Capabilities**:
- Perform web searches for current information
- Research technical topics and documentation
- Find solutions to development problems
- Gather market research and trends

**Security Model**:
- No data storage or caching of search results
- Uses privacy-focused search engine
- Rate limiting to prevent abuse
- No cookies or tracking mechanisms

### Makefile Agent

**Purpose**: Handle build system operations and Makefile targets

**Implementation**:
- Parses Makefile structure and targets
- Executes make commands with proper error handling
- Integrates with project build systems
- Provides intelligent target recommendations

**Capabilities**:
- List and describe available make targets
- Execute specific build targets with dependencies
- Handle complex build workflows
- Provide build status and error reporting

**Security Model**:
- Executes in project directory context
- Validates Makefile existence before operations
- Timeout protection for long-running builds
- Safe handling of build artifacts

### FileSystem Agent

**Purpose**: Manage files and directories with safety checks

**Implementation**:
- Path validation and sanitization
- Atomic file operations where possible
- Backup creation for destructive operations
- Permission checking and error handling

**Capabilities**:
- Read and write files with encoding detection
- Create and modify directory structures
- Perform file operations with safety checks
- Generate file and directory reports

**Security Model**:
- User confirmation required for destructive operations
- Path traversal attack prevention
- Permission validation before operations
- Automatic backup creation for file modifications

## Data Flow and Interaction Patterns

### Request Processing Flow

```
1. User Input → CLI Parser → Manager Agent
2. Manager Agent → Task Analysis → Intent Classification
3. Intent Classification → Agent Selection → Specialist Agent(s)
4. Specialist Agent(s) → Task Execution → Result Generation
5. Result Generation → Manager Agent → Response Formatting
6. Response Formatting → User Interface → Real-time Display
```

### Inter-Agent Communication

**Direct Delegation Model**:
- Manager Agent directly invokes specialist agents
- No peer-to-peer communication between specialists
- All coordination flows through the Manager Agent
- Results are aggregated by the Manager Agent

**Message Format**:
```python
{
    "agent_name": "terminal_agent",
    "action": "run_shell_command",
    "parameters": {"command": "ls -la"},
    "context": {"working_directory": "/project"},
    "confirmation_required": true
}
```

### State Management

**Session State**:
- Manager Agent maintains conversation context
- Interactive sessions preserve multi-turn context
- Non-interactive sessions are stateless
- Agent state is isolated per execution

**Configuration State**:
- Global configuration managed by ConfigManager
- Agent-specific settings stored in config.toml
- Runtime configuration changes propagated to agents
- Configuration validation on startup

## Security Model and Sandboxing

### Multi-Layer Security Architecture

**Layer 1: Input Validation**
- User input sanitization and validation
- Command injection prevention
- Path traversal attack mitigation

**Layer 2: Agent Isolation**
- Each agent runs in isolated context
- No shared state between agent executions
- Resource limits and timeouts

**Layer 3: Execution Sandboxing**
- Python code runs in temporary `uv` environments
- Shell commands executed with user permissions only
- File operations restricted to project scope

**Layer 4: User Confirmation**
- Configurable confirmation requirements
- Transparent action disclosure
- User approval for destructive operations

### Sandboxing Implementation

**Python Code Execution**:
```python
# Create isolated environment
temp_dir = tempfile.mkdtemp(prefix="automake_python_")
venv_path = temp_dir / "venv"
subprocess.run(["uv", "venv", str(venv_path)])

# Install dependencies in isolation
subprocess.run(["uv", "pip", "install", "--python", python_exe, dependency])

# Execute code with cleanup
try:
    result = subprocess.run([python_exe, script_path], ...)
finally:
    shutil.rmtree(temp_dir)  # Always cleanup
```

**Shell Command Execution**:
```python
# Execute with timeout and capture
result = subprocess.run(
    command,
    shell=True,
    capture_output=True,
    text=True,
    timeout=300,  # 5 minute limit
)
```

## Configuration Management Architecture

### Configuration Hierarchy

```
1. Default Configuration (hardcoded)
2. User Configuration (~/.config/automake/config.toml)
3. Project Configuration (./automake.toml)
4. Environment Variables (AUTOMAKE_*)
5. CLI Arguments (highest priority)
```

### Configuration Categories

**Agent Settings**:
```toml
[agent]
require_confirmation = true
max_concurrent = 3
timeout = 300
```

**Model Configuration**:
```toml
[ollama]
base_url = "http://localhost:11434"
model = "qwen3:0.6b"
```

**Logging Configuration**:
```toml
[logging]
level = "INFO"
max_files = 10
cleanup_on_startup = true
```

### Dynamic Configuration Updates

- Configuration changes applied immediately
- Agent instances receive updated configuration
- Validation ensures configuration integrity
- Rollback capability for invalid configurations

## Performance Considerations

### Agent Startup Optimization

**Lazy Loading**:
- Agents initialized only when needed
- Tool imports deferred until execution
- Configuration loaded on-demand

**Connection Pooling**:
- Ollama connection reuse across requests
- Web search client connection pooling
- Database connections (if applicable) managed efficiently

### Execution Optimization

**Parallel Execution**:
- Multiple agents can run concurrently
- I/O-bound operations parallelized
- CPU-intensive tasks queued appropriately

**Resource Management**:
- Memory usage monitoring and limits
- Temporary file cleanup automation
- Process lifecycle management

### Scalability Patterns

**Horizontal Scaling**:
- Agent instances can be distributed
- Load balancing across multiple Ollama instances
- Stateless design enables easy scaling

**Vertical Scaling**:
- Resource allocation per agent type
- Memory and CPU limits configurable
- Graceful degradation under resource pressure

## Error Handling and Resilience

### Error Categories

**User Errors**:
- Invalid input or malformed requests
- Permission or access issues
- Configuration problems

**System Errors**:
- Network connectivity issues
- Resource exhaustion
- External service failures

**Agent Errors**:
- Tool execution failures
- Timeout conditions
- Unexpected exceptions

### Recovery Strategies

**Graceful Degradation**:
- Fallback to simpler approaches when complex ones fail
- Alternative agent selection when primary choice unavailable
- Partial results when complete execution impossible

**Retry Logic**:
- Exponential backoff for transient failures
- Circuit breaker pattern for persistent failures
- User notification of retry attempts

**Error Reporting**:
- Structured error messages with context
- Actionable suggestions for resolution
- Debug information for troubleshooting

## Extension and Customization

### Adding New Agents

**Agent Interface**:
```python
from smolagents import tool, ManagedAgent, CodeAgent

@tool
def custom_tool(parameter: str) -> str:
    """Custom tool implementation."""
    return f"Processed: {parameter}"

custom_agent_logic = CodeAgent(tools=[custom_tool])
custom_agent = ManagedAgent(
    agent=custom_agent_logic,
    name="custom_agent",
    description="Handles custom operations"
)
```

**Integration Steps**:
1. Define tools using `@tool` decorator
2. Create `CodeAgent` with tool list
3. Wrap in `ManagedAgent` with metadata
4. Register with Manager Agent
5. Update configuration schema

### Custom Tool Development

**Tool Requirements**:
- Type hints for all parameters and return values
- Comprehensive docstrings
- Error handling and validation
- Security considerations

**Best Practices**:
- Keep tools focused and single-purpose
- Implement proper timeout handling
- Use structured return formats
- Include logging for debugging

## Monitoring and Observability

### Logging Architecture

**Structured Logging**:
- JSON-formatted log entries
- Correlation IDs for request tracing
- Performance metrics collection
- Error tracking and aggregation

**Log Levels**:
- `DEBUG`: Detailed execution information
- `INFO`: General operational messages
- `WARNING`: Potential issues or degraded performance
- `ERROR`: Failures requiring attention

### Metrics Collection

**Performance Metrics**:
- Agent execution times
- Resource utilization
- Success/failure rates
- User satisfaction indicators

**Operational Metrics**:
- Request volume and patterns
- Error rates and types
- Configuration changes
- System health indicators

### Debugging Support

**Debug Mode**:
- Verbose logging enabled
- Intermediate results preserved
- Agent decision rationale exposed
- Performance profiling data

**Troubleshooting Tools**:
- Log analysis utilities
- Configuration validation
- Health check endpoints
- Performance profiling

## Future Architecture Considerations

### Planned Enhancements

**Agent Marketplace**:
- Plugin system for third-party agents
- Agent discovery and installation
- Version management and updates
- Security validation for external agents

**Advanced Orchestration**:
- Workflow definition language
- Conditional execution paths
- Loop and branching constructs
- State persistence across sessions

**Enhanced Security**:
- Role-based access control
- Agent capability restrictions
- Audit logging and compliance
- Secure communication channels

### Scalability Roadmap

**Distributed Architecture**:
- Agent execution across multiple nodes
- Load balancing and failover
- Shared state management
- Cross-node communication

**Cloud Integration**:
- Container orchestration support
- Auto-scaling capabilities
- Cloud-native monitoring
- Serverless execution options

This architecture provides a solid foundation for AutoMake's multi-agent system while maintaining flexibility for future enhancements and customizations.
