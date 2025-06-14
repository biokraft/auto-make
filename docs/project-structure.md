# Project Structure

This document describes the organization and structure of the AutoMake project.

## Directory Structure

```
auto-make/
├── automake/                    # Main package directory
│   ├── __init__.py             # Package initialization and exports
│   ├── __main__.py             # Entry point for module execution
│   ├── cli/                    # Command-line interface components
│   │   ├── __init__.py         # CLI module initialization
│   │   ├── main.py             # Main CLI application logic
│   │   └── ascii_art.txt       # ASCII art for CLI display
│   ├── core/                   # Core business logic
│   │   ├── __init__.py         # Core module initialization
│   │   └── makefile_reader.py  # Makefile reading and parsing
│   └── utils/                  # Utility modules
│       ├── __init__.py         # Utils module initialization
│       └── output.py           # Output formatting utilities
├── tests/                      # Test suite
│   ├── __init__.py             # Test package initialization
│   ├── test_main.py            # CLI tests
│   ├── test_makefile_reader.py # Makefile reader tests
│   ├── test_output.py          # Output formatting tests
│   ├── test_package.py         # Package structure tests
│   ├── test_project_setup.py   # Project configuration tests
│   └── test_ci_pipeline.py     # CI/CD pipeline tests
├── docs/                       # Documentation
│   ├── README.md               # Basic documentation
│   └── project-structure.md    # This file
├── specs/                      # Technical specifications
│   └── *.md                    # Various specification documents
├── .github/                    # GitHub workflows and templates
├── .cursor/                    # Cursor IDE configuration
├── pyproject.toml              # Project configuration and dependencies
├── README.md                   # Main project README
├── CHANGELOG.md                # Version history
├── SPECS.md                    # Specifications overview
├── LICENSE                     # Project license
└── .gitignore                  # Git ignore patterns
```

## Module Organization

### Core Modules (`automake/core/`)
Contains the core business logic and domain-specific functionality:
- `makefile_reader.py`: Handles finding, reading, and parsing Makefiles

### CLI Modules (`automake/cli/`)
Contains command-line interface components:
- `main.py`: Main CLI application using Typer
- `ascii_art.txt`: ASCII art displayed in CLI

### Utility Modules (`automake/utils/`)
Contains utility functions and helper classes:
- `output.py`: Console output formatting and styling

## Import Structure

The package follows a hierarchical import structure:

```python
# Main package exports core functionality
from automake import MakefileReader, MessageType, OutputFormatter

# Direct module imports for specific functionality
from automake.core.makefile_reader import MakefileReader
from automake.utils.output import MessageType, OutputFormatter
from automake.cli.main import app
```

## Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Hierarchical Organization**: Related functionality is grouped into logical subdirectories
3. **Clear Dependencies**: Import paths clearly indicate module relationships
4. **Testability**: Structure supports comprehensive testing with clear module boundaries
5. **Extensibility**: New features can be added without disrupting existing organization

## Entry Points

- **CLI Application**: `automake.cli.main:app` (configured in `pyproject.toml`)
- **Module Execution**: `python -m automake` (via `__main__.py`)
- **Package Import**: `import automake` (via `__init__.py`)

## Testing Strategy

Tests are organized to mirror the package structure:
- `test_main.py`: Tests for CLI functionality
- `test_makefile_reader.py`: Tests for core Makefile reading logic
- `test_output.py`: Tests for output formatting utilities
- `test_package.py`: Tests for package structure and imports
- `test_project_setup.py`: Tests for project configuration
- `test_ci_pipeline.py`: Tests for CI/CD pipeline functionality

This structure follows Python packaging best practices and supports the project's growth and maintainability.
