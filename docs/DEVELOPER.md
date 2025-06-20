# AutoMake Developer Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Agent Implementation Patterns](#agent-implementation-patterns)
5. [Testing Strategies](#testing-strategies)
6. [Contributing Guidelines](#contributing-guidelines)
7. [Debugging and Troubleshooting](#debugging-and-troubleshooting)
8. [Release Process](#release-process)

## Project Overview

AutoMake is a Python-based, agent-first command-line tool built on the `smolagents` framework. The project has evolved from a simple Makefile wrapper into a sophisticated multi-agent AI assistant capable of interpreting and executing complex natural language commands.

### Key Technologies

- **Python 3.11+**: Core language
- **smolagents**: Multi-agent framework
- **uv**: Package management and virtual environments
- **Rich**: Terminal UI and formatting
- **Typer**: CLI framework
- **Pydantic v2**: Data validation and settings
- **pytest**: Testing framework

### Architecture Philosophy

- **Agent-First Design**: Everything revolves around the multi-agent system
- **Delegation Pattern**: Manager Agent orchestrates specialist agents
- **Security by Design**: Sandboxed execution and user confirmation
- **Local-First**: Ollama integration for privacy and offline capability
- **Test-Driven Development**: Comprehensive test coverage for reliability

## Development Environment Setup

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- [Ollama](https://ollama.com/) for local LLM support
- Git for version control

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/auto-make.git
cd auto-make

# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Install pre-commit hooks (if available)
pre-commit install

# Run tests to verify setup
uv run pytest

# Initialize AutoMake
uv run automake init
```

### Development Tools

**Recommended IDE Setup:**
- VS Code with Python extension
- PyCharm Professional or Community
- Vim/Neovim with Python LSP

**Essential Extensions/Plugins:**
- Python language server (Pylsp, Pyright, or similar)
- Black formatter
- isort import sorter
- mypy type checker
- pytest test runner

## Project Structure

```
auto-make/
├── automake/                    # Main package
│   ├── __init__.py             # Package initialization
│   ├── __main__.py             # Entry point for python -m automake
│   ├── agent/                  # Multi-agent system
│   │   ├── __init__.py
│   │   ├── manager.py          # Manager Agent orchestration
│   │   ├── specialists.py      # Specialist agent implementations
│   │   └── ui/                 # Agent UI components
│   │       ├── __init__.py
│   │       └── session.py      # Interactive session management
│   ├── cli/                    # Command-line interface
│   │   ├── __init__.py
│   │   ├── app.py              # Main CLI application
│   │   ├── commands/           # CLI command implementations
│   │   ├── display/            # UI display components
│   │   ├── error_handler.py    # Global error handling
│   │   └── logs.py             # Logging CLI commands
│   ├── config/                 # Configuration management
│   │   ├── __init__.py
│   │   ├── defaults.py         # Default configuration values
│   │   └── manager.py          # Configuration manager
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── ai_agent.py         # Legacy AI agent (deprecated)
│   │   ├── command_runner.py   # Command execution utilities
│   │   ├── interactive.py      # Interactive session handling
│   │   └── makefile_reader.py  # Makefile parsing utilities
│   ├── logging/                # Logging system
│   │   ├── __init__.py
│   │   ├── handlers.py         # Custom log handlers
│   │   └── setup.py            # Logging configuration
│   └── utils/                  # Utility modules
│       ├── __init__.py
│       ├── animation.py        # Text animation utilities
│       ├── model_selector.py   # Model selection UI
│       ├── ollama_manager.py   # Ollama integration
│       └── output/             # Output formatting
│           ├── __init__.py
│           ├── formatter.py    # Rich formatting utilities
│           ├── live_box.py     # Live updating UI components
│           └── types.py        # Output type definitions
├── tests/                      # Test suite
│   ├── agent/                  # Agent system tests
│   ├── cli/                    # CLI tests
│   ├── config/                 # Configuration tests
│   ├── core/                   # Core functionality tests
│   ├── integration/            # Integration tests
│   ├── logging/                # Logging tests
│   ├── project/                # Project-level tests
│   └── utils/                  # Utility tests
├── docs/                       # Documentation
├── specs/                      # Technical specifications
├── pyproject.toml              # Project configuration
├── uv.lock                     # Dependency lock file
└── README.md                   # Project overview
```

### Key Modules Explained

**`automake/agent/`**: The heart of the multi-agent system
- `manager.py`: Contains the `ManagerAgent` that orchestrates all operations
- `specialists.py`: Implements all specialist agents (Terminal, Coding, Web, etc.)
- `ui/session.py`: Manages interactive chat sessions with rich UI

**`automake/cli/`**: Command-line interface implementation
- `app.py`: Main Typer application with command routing
- `commands/`: Individual command implementations (agent, config, init, etc.)
- `error_handler.py`: Global exception handling and user-friendly error messages

**`automake/config/`**: Configuration management system
- `manager.py`: Handles loading, saving, and validating configuration
- `defaults.py`: Default configuration values and schema

**`automake/utils/`**: Shared utilities and components
- `ollama_manager.py`: Manages Ollama model installation and communication
- `output/`: Rich-based output formatting and live UI components

## Agent Implementation Patterns

### Creating a New Specialist Agent

When adding a new specialist agent, follow this pattern:

```python
from smolagents import tool, CodeAgent, ManagedAgent
from typing import List, Optional

# 1. Define tools for the agent
@tool
def my_custom_tool(parameter: str, optional_param: Optional[str] = None) -> str:
    """
    Tool description that will be used by the LLM.

    Args:
        parameter: Description of required parameter
        optional_param: Description of optional parameter

    Returns:
        Description of return value
    """
    # Implementation
    try:
        result = perform_operation(parameter, optional_param)
        return f"Operation completed: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def another_tool(items: List[str]) -> str:
    """Another tool for the agent."""
    # Implementation
    pass

# 2. Create the agent
def create_my_specialist_agent() -> ManagedAgent:
    """Create and configure the custom specialist agent."""

    # Create the underlying CodeAgent with tools
    agent_logic = CodeAgent(
        tools=[my_custom_tool, another_tool],
        model="qwen3:0.6b",  # Will be overridden by configuration
        max_iterations=3
    )

    # Wrap in ManagedAgent with metadata
    return ManagedAgent(
        agent=agent_logic,
        name="my_specialist",
        description="Handles custom operations and specialized tasks"
    )

# 3. Register with ManagerAgent (in manager.py)
def setup_manager_agent() -> ManagerAgent:
    # ... existing code ...
    my_agent = create_my_specialist_agent()

    managed_agents = [
        # ... existing agents ...
        my_agent
    ]

    return ManagerAgent(
        managed_agents=managed_agents,
        # ... other configuration ...
    )
```

### Tool Development Best Practices

**1. Type Hints and Documentation**
```python
@tool
def well_documented_tool(
    required_param: str,
    optional_param: Optional[int] = None,
    list_param: List[str] = None
) -> str:
    """
    Clear, concise description of what the tool does.

    Args:
        required_param: Clear description of this parameter
        optional_param: What this optional parameter controls
        list_param: What items in this list represent

    Returns:
        Description of the return value format

    Raises:
        ValueError: When invalid parameters are provided
        FileNotFoundError: When required files don't exist
    """
    # Validate inputs
    if not required_param.strip():
        raise ValueError("required_param cannot be empty")

    # Implementation with proper error handling
    try:
        result = process_data(required_param, optional_param, list_param or [])
        return f"Success: {result}"
    except Exception as e:
        logger.error(f"Tool failed: {e}")
        return f"Error: {str(e)}"
```

**2. Error Handling**
```python
@tool
def robust_tool(file_path: str) -> str:
    """Tool with comprehensive error handling."""
    try:
        # Validate inputs
        if not file_path:
            return "Error: file_path is required"

        path = Path(file_path)
        if not path.exists():
            return f"Error: File {file_path} does not exist"

        # Perform operation
        content = path.read_text()
        result = process_content(content)

        return f"Processed {len(content)} characters successfully"

    except PermissionError:
        return f"Error: Permission denied accessing {file_path}"
    except UnicodeDecodeError:
        return f"Error: Cannot decode file {file_path} as text"
    except Exception as e:
        logger.exception("Unexpected error in robust_tool")
        return f"Unexpected error: {str(e)}"
```

**3. Security Considerations**
```python
@tool
def secure_file_operation(file_path: str, content: str) -> str:
    """Secure file operation with path validation."""
    try:
        # Validate and sanitize file path
        path = Path(file_path).resolve()

        # Prevent path traversal attacks
        cwd = Path.cwd().resolve()
        if not str(path).startswith(str(cwd)):
            return "Error: File path must be within current directory"

        # Check permissions before writing
        if path.exists() and not os.access(path, os.W_OK):
            return f"Error: No write permission for {file_path}"

        # Perform operation safely
        path.write_text(content)
        return f"Successfully wrote {len(content)} characters to {file_path}"

    except Exception as e:
        return f"Error: {str(e)}"
```

### Agent Configuration

Agents can be configured through the configuration system:

```python
# In your agent implementation
def create_configured_agent(config: ConfigManager) -> ManagedAgent:
    """Create agent with configuration support."""

    # Access agent-specific configuration
    agent_config = config.get("agents.my_specialist", {})
    timeout = agent_config.get("timeout", 300)
    max_retries = agent_config.get("max_retries", 3)

    # Configure tools with settings
    configured_tools = [
        create_tool_with_config(timeout, max_retries)
    ]

    agent_logic = CodeAgent(
        tools=configured_tools,
        model=config.get("ollama.model", "qwen3:0.6b")
    )

    return ManagedAgent(
        agent=agent_logic,
        name="my_specialist",
        description="Configured specialist agent"
    )
```

## Testing Strategies

### Test Organization

AutoMake uses a comprehensive testing strategy with different test types:

**Unit Tests**: Test individual components in isolation
```python
# tests/agent/test_specialists.py
import pytest
from automake.agent.specialists import create_terminal_agent

def test_terminal_agent_creation():
    """Test that terminal agent is created correctly."""
    agent = create_terminal_agent()

    assert agent.name == "terminal_agent"
    assert "Execute shell commands" in agent.description
    assert len(agent.agent.tools) > 0

def test_terminal_agent_tool_execution():
    """Test terminal agent tool execution."""
    agent = create_terminal_agent()

    # Test with safe command
    result = agent.agent.tools[0]("echo 'test'")
    assert "test" in result
```

**Integration Tests**: Test component interaction
```python
# tests/integration/test_agent_integration.py
import pytest
from automake.agent.manager import ManagerAgent
from automake.config.manager import ConfigManager

@pytest.fixture
def manager_agent():
    """Create a manager agent for testing."""
    config = ConfigManager()
    return ManagerAgent.from_config(config)

def test_manager_agent_delegation(manager_agent):
    """Test that manager agent properly delegates to specialists."""
    # Test delegation to terminal agent
    response = manager_agent.run("list files in current directory")
    assert "ls" in response or "dir" in response

    # Test delegation to coding agent
    response = manager_agent.run("calculate 2 + 2 in python")
    assert "4" in response
```

**Functional Tests**: Test complete user workflows
```python
# tests/cli/test_agent_commands.py
from click.testing import CliRunner
from automake.cli.app import app

def test_agent_command_execution():
    """Test agent command execution through CLI."""
    runner = CliRunner()

    # Test non-interactive mode
    result = runner.invoke(app, ["agent", "echo hello world"])
    assert result.exit_code == 0
    assert "hello world" in result.output

    # Test with confirmation disabled
    result = runner.invoke(app, [
        "config", "set", "agent.require_confirmation", "false"
    ])
    assert result.exit_code == 0
```

### Testing Agent Functionality

**Mocking External Dependencies**:
```python
import pytest
from unittest.mock import patch, MagicMock
from automake.agent.specialists import create_web_agent

@patch('automake.agent.specialists.DuckDuckGoSearchRun')
def test_web_agent_search(mock_search):
    """Test web agent search functionality."""
    # Setup mock
    mock_search_instance = MagicMock()
    mock_search_instance.run.return_value = "Test search results"
    mock_search.return_value = mock_search_instance

    # Test agent
    agent = create_web_agent()
    result = agent.agent.tools[0]("test query")

    assert "Test search results" in result
    mock_search_instance.run.assert_called_once_with("test query")
```

**Testing Configuration Integration**:
```python
def test_agent_respects_configuration(tmp_path):
    """Test that agents respect configuration settings."""
    # Create temporary config
    config_file = tmp_path / "config.toml"
    config_file.write_text("""
    [agent]
    require_confirmation = true
    timeout = 60

    [ollama]
    model = "test-model"
    """)

    # Load configuration
    config = ConfigManager(config_path=config_file)

    # Test agent creation
    agent = ManagerAgent.from_config(config)
    assert agent.require_confirmation == True
    assert agent.timeout == 60
```

### Test Utilities

**Common Test Fixtures**:
```python
# tests/conftest.py
import pytest
import tempfile
from pathlib import Path
from automake.config.manager import ConfigManager

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def test_config(temp_dir):
    """Create a test configuration."""
    config_file = temp_dir / "config.toml"
    config_file.write_text("""
    [agent]
    require_confirmation = false

    [ollama]
    model = "qwen3:0.6b"
    base_url = "http://localhost:11434"
    """)

    return ConfigManager(config_path=config_file)

@pytest.fixture
def mock_ollama():
    """Mock Ollama for testing."""
    with patch('automake.utils.ollama_manager.requests') as mock_requests:
        mock_response = MagicMock()
        mock_response.json.return_value = {"models": [{"name": "qwen3:0.6b"}]}
        mock_requests.get.return_value = mock_response
        yield mock_requests
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=automake --cov-report=html

# Run specific test categories
uv run pytest tests/agent/          # Agent tests only
uv run pytest tests/integration/    # Integration tests only

# Run tests matching pattern
uv run pytest -k "test_agent"

# Run tests with verbose output
uv run pytest -v

# Run tests and stop on first failure
uv run pytest -x
```

## Contributing Guidelines

### Code Style and Standards

**Python Style**:
- Follow PEP 8 style guide
- Use Black for code formatting
- Use isort for import sorting
- Maximum line length: 88 characters
- Use type hints for all function parameters and return values

**Naming Conventions**:
- Classes: `PascalCase`
- Functions/Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private attributes: `_leading_underscore`

**Documentation**:
- Use Google-style docstrings
- Document all public functions and classes
- Include type information in docstrings
- Provide usage examples for complex functions

### Git Workflow

**Branch Naming**:
- Features: `feature/description-of-feature`
- Bug fixes: `fix/description-of-fix`
- Documentation: `docs/description-of-change`
- Refactoring: `refactor/description-of-change`

**Commit Messages**:
```
type(scope): short description

Longer description if needed explaining what and why,
not how. Wrap at 72 characters.

- List any breaking changes
- Reference issues: Fixes #123
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Pull Request Process**:
1. Create feature branch from `main`
2. Implement changes with tests
3. Ensure all tests pass
4. Update documentation if needed
5. Submit pull request with clear description
6. Address review feedback
7. Squash and merge when approved

### Adding New Features

**1. Planning**:
- Create or update specifications in `specs/`
- Discuss approach in GitHub issues
- Consider impact on existing functionality

**2. Implementation**:
- Follow TDD approach (tests first)
- Implement in small, focused commits
- Maintain backward compatibility when possible
- Update configuration schema if needed

**3. Documentation**:
- Update relevant documentation files
- Add examples to user guide
- Update CLI help text if applicable
- Update CHANGELOG.md

**4. Testing**:
- Write comprehensive unit tests
- Add integration tests for new workflows
- Test CLI commands and help text
- Verify examples in documentation work

### Code Review Guidelines

**For Authors**:
- Keep pull requests focused and small
- Provide clear description and context
- Include tests for all new functionality
- Update documentation and examples
- Self-review code before submitting

**For Reviewers**:
- Check code quality and style
- Verify test coverage and quality
- Test functionality manually if needed
- Review documentation updates
- Provide constructive feedback

## Debugging and Troubleshooting

### Debugging Agent Issues

**Enable Debug Logging**:
```bash
# Set debug level in configuration
automake config set logging.level DEBUG

# Or use environment variable
export AUTOMAKE_LOG_LEVEL=DEBUG
automake agent "your command"
```

**Agent Execution Tracing**:
```python
# In your agent code
import logging
logger = logging.getLogger(__name__)

@tool
def debug_tool(parameter: str) -> str:
    """Tool with debug logging."""
    logger.debug(f"Tool called with parameter: {parameter}")

    try:
        result = process_parameter(parameter)
        logger.debug(f"Tool result: {result}")
        return result
    except Exception as e:
        logger.error(f"Tool failed: {e}", exc_info=True)
        raise
```

**Interactive Debugging**:
```python
# Add breakpoints in agent code
import pdb; pdb.set_trace()

# Or use rich debugging
from rich import print as rprint
rprint(f"Debug info: {variable}", style="bold red")
```

### Common Issues and Solutions

**Agent Not Responding**:
1. Check Ollama is running: `ollama list`
2. Verify model is available: `automake config show`
3. Check network connectivity to Ollama
4. Review logs: `automake logs view`

**Tool Execution Failures**:
1. Check tool parameter types and validation
2. Verify required dependencies are installed
3. Test tools in isolation
4. Check for permission issues

**Configuration Issues**:
1. Validate configuration: `automake config show`
2. Reset to defaults: `automake config reset`
3. Check file permissions on config file
4. Verify TOML syntax is correct

**Performance Issues**:
1. Monitor resource usage during execution
2. Check for memory leaks in long-running sessions
3. Profile agent execution times
4. Optimize tool implementations

### Development Tools

**Logging Analysis**:
```bash
# View recent logs
automake logs view

# Filter logs by level
grep "ERROR" ~/.local/share/automake/logs/automake_*.log

# Monitor logs in real-time
tail -f ~/.local/share/automake/logs/automake_*.log
```

**Configuration Debugging**:
```bash
# Show current configuration
automake config show

# Test configuration changes
automake config set logging.level DEBUG
automake agent "test command"
automake config reset
```

**Performance Profiling**:
```python
# Add to agent code for profiling
import time
import cProfile

def profile_agent_execution():
    """Profile agent execution."""
    profiler = cProfile.Profile()
    profiler.enable()

    # Run agent code
    result = agent.run("test command")

    profiler.disable()
    profiler.dump_stats("agent_profile.prof")

    return result
```

## Release Process

### Version Management

AutoMake uses semantic versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Release Checklist

**Pre-Release**:
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Version number is bumped in `pyproject.toml`
- [ ] Examples and demos work correctly

**Release**:
- [ ] Create release branch: `release/v1.2.3`
- [ ] Final testing and validation
- [ ] Create GitHub release with changelog
- [ ] Tag release: `git tag v1.2.3`
- [ ] Build and publish to PyPI (if applicable)

**Post-Release**:
- [ ] Merge release branch to main
- [ ] Update development dependencies
- [ ] Plan next release cycle

### Continuous Integration

The project uses GitHub Actions for CI/CD:

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install uv
      run: pip install uv

    - name: Install dependencies
      run: uv sync

    - name: Run tests
      run: uv run pytest --cov=automake

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

This developer documentation provides a comprehensive guide for contributing to AutoMake. For questions or clarifications, please open an issue on GitHub or contact the maintainers.
