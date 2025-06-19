# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.4.4 - Enhanced Model Management & Python 3.13 Support

### ✨ Added
- 🧠 Hardware-aware model recommendation system for optimal performance based on user hardware capabilities
- 🛡️ Graceful shutdown procedures for agent operations with improved signal handling
- 📋 Enhanced first-time setup guidance with better model selection instructions
- 🔧 New specifications for hardware-aware model recommendation and signal handling

### 🛠️ Improved
- ⚡ Enhanced model management and initialization process with better error handling
- 🎯 Improved user experience during agent initialization with clearer feedback
- 📚 Updated help command image to reflect recent CLI enhancements
- 🧪 Expanded test coverage for help display and agent functionality

### 🔧 Fixed
- ✅ Better error handling in agent manager for model availability checks
- 🔄 Improved subprocess management for cleaner agent operations

### ⚠️ Breaking Changes
- 🐍 **Python 3.13+ now required** - Updated minimum Python version requirement from 3.11+ to 3.13+

## v0.4.3 - Non-Interactive Agent Mode & CLI Enhancement

### ✨ Added
- 🤖 Primary interface `automake "prompt"` for direct natural language command execution
- 📦 LiveBox integration for real-time feedback during command execution and agent initialization
- 🧪 Comprehensive test coverage for non-interactive mode and CLI behavior
- 📚 Phase 4 implementation documentation with detailed technical specifications

### 🛠️ Improved
- 🎯 Enhanced CLI architecture maintaining backward compatibility while improving user experience
- 📋 Updated help system to prominently feature new usage patterns and examples
- 🔧 Streamlined command execution flow with better real-time feedback

## v0.4.2 - Documentation & Configuration Enhancement

### 🛠️ Improved
- 📚 Enhanced README with clearer `run` command usage examples and configuration guidance
- ⚙️ Improved configuration command error messages with better user guidance
- 🎯 Updated configuration examples for AI model setup and parameter management
- 📋 Enhanced help display functionality for better user experience

### ✨ Added
- 🧪 Expanded test coverage for configuration commands with success and error scenarios
- 💡 Future enhancement suggestions for making `run` the default subcommand

## v0.4.1 - Interactive Session Enhancement

### ✨ Added
- 🎯 `RichInteractiveSession` class for improved user interaction in agent commands
- ⚙️ Agent confirmation configuration options for enhanced user control
- 🧪 Comprehensive test coverage for new session architecture with timeout support

### 🛠️ Improved
- 🤖 Streamlined agent command execution process with better session management
- 📋 Enhanced test infrastructure with `pytest-timeout` for custom test timeouts
- 🔧 Refined agent UI components for better user experience

### 🔧 Fixed
- ✅ Robust error handling in interactive session functionality

## v0.4.0 - Major Architecture Refactoring & Modular Design

### ✨ Added
- 🏗️ Complete modular CLI architecture with organized command structure
- 🤖 Enhanced agent specifications with multi-agent system design
- 📚 Comprehensive refactoring documentation in `/docs/refactoring-vibes/`
- 🔧 Interactive model configuration command for easier setup
- 🧪 Expanded test coverage with improved mocking and CLI command testing
- 📋 New agent specifications: RAG, Project Init, Codebase Exploration, and Concurrent Sessions

### 🛠️ Improved
- 🎯 Decomposed monolithic CLI into modular command structure (`commands/`, `display/`, `config/`, `logging/`)
- 📦 Reorganized project structure for better maintainability and future extensibility
- 🔄 Enhanced configuration management with better defaults and organization
- 📖 Updated README with comprehensive installation and usage guidelines
- 🎨 Improved output formatting and display handling with dedicated modules

### 🔧 Fixed
- ✅ Removed obsolete test files and updated project configuration
- 🧹 Cleaned up migration artifacts and phase completion documents
- 🔗 Updated specifications to reflect new modular architecture

## v0.3.5 - UI/UX Enhancement & LiveBox Integration

### ✨ Added
- 🎨 LiveBox integration for dynamic CLI output and improved visual feedback
- 📋 Enhanced test coverage for LiveBox functionality and output consistency
- 🤖 Autonomous agent mode specification and implementation planning

### 🛠️ Improved
- 🎯 CLI help handling with cleaner user experience for subcommands
- 📊 Consistent emoji formatting across error, success, and informational messages
- 📚 Updated project specifications reflecting completion of Phase 1 UI components
- 🔧 Output consistency improvements across different CLI scenarios

### 🔧 Fixed
- ✅ Test assertions updated for improved clarity and accuracy
- 🎨 Help command display consistency across logs and config subcommands

## v0.3.4 - UVX Distribution Enhancement

### ✨ Added
- 🚀 Additional `automake-cli` script entry point for direct uvx execution
- 📦 Enhanced version detection using importlib.metadata for installed packages

### 🛠️ Improved
- 🔧 Version handling now works correctly when package is installed via uvx
- 📋 Dual entry points: both `automake` and `automake-cli` commands available

### 🔧 Fixed
- ✅ Version reporting accuracy in installed packages
- 🎯 UVX compatibility for `uvx automake-cli` direct execution
- 🔗 Corrected GitHub repository links in README badges

## v0.3.3 - Enhanced UX & Testing Improvements

### ✨ Added
- 🎬 Comprehensive UX demonstration scripts for better user experience showcase
- 📊 Enhanced demo scripts with streaming capabilities and improved output handling
- 🧪 Improved test coverage for logs and command runner functionality

### 🛠️ Improved
- 🤖 Enhanced AI agent with better command interpretation and logging capabilities
- 📋 Makefile reader with improved functionality and error handling
- 🎯 LiveBox integration with better output handling and real-time updates
- 🔧 CommandRunner refactoring for cleaner output management

### 🔧 Fixed
- ✅ Test reliability improvements with better mocking for log file operations
- 🎨 Output handling consistency across different components

## v0.3.2 - Documentation & Demo Enhancements

### ✨ Added
- 🎬 LiveBox component demo script showcasing streaming capabilities and dynamic updates
- 📸 Help command screenshot for improved documentation
- 🚀 First-time setup instructions in README for better user onboarding

### 🛠️ Improved
- 🤖 Enhanced AI command response instructions for better JSON generation
- 📚 Cleaner README presentation with improved documentation structure
- 🧪 Expanded test coverage for LiveBox functionality and thread safety

## v0.3.1 - Enhanced User Experience & Configuration Management

### ✨ Added
- 🎬 Loading animations during AI command processing for better user feedback
- ⚙️ Configuration management commands for easier settings control
- 📦 LiveBox component for real-time output display
- 🔧 Ollama manager for improved model handling

### 🛠️ Improved
- 🎨 ASCII art display timing and visual experience
- 🤖 AI command interpretation with better JSON response handling
- 🔇 Cleaner output by suppressing unnecessary logs during AI processing
- 📋 Enhanced dependency management with tomli-w support
- 🎯 Updated default model to qwen3:0.6b for better performance

### 🔧 Fixed
- ⚡ Animation frame rates and cleanup processes
- 🔕 Pydantic serialization warnings suppression

## v0.3.0 - AI Core Implementation & Interactive Features

### ✨ Added
- 🤖 Complete AI agent implementation with Ollama integration for command interpretation
- 🎯 Interactive command selection with confidence-based prompting using questionary
- ⚙️ Comprehensive configuration management system with TOML support
- 📝 Advanced logging framework with file rotation and configurable levels
- 🏃 Command execution engine with real-time output streaming
- 🧪 Extensive test suite covering all core functionality

### 🛠️ Improved
- 📚 Enhanced project specifications with detailed implementation guidance
- 🔧 Dynamic version retrieval from pyproject.toml
- 📋 Makefile reading capabilities with better error handling
- 🎨 CLI interface with improved user experience and help system

### 🔧 Fixed
- ✅ Test coverage and linting compliance across all modules
- 🔗 Dependency management and lock file updates

## v0.2.1 - Documentation & Structure Improvements

### 🛠️ Improved
- 📊 Enhanced Codecov badge visibility and accuracy in README
- 🏗️ Refactored project structure with improved CLI entry point
- 📚 Updated documentation and CI configuration for better coverage reporting
- 🎨 Added welcome message with improved usage information

### 🔧 Fixed
- 🔗 Codecov integration and badge formatting issues
- 📈 Coverage reporting accuracy and token configuration

## v0.2.0 - Core Functionality & Enhanced Documentation

### ✨ Added
- 🎨 Welcome message functionality with ASCII art display
- 📁 Makefile reading functionality for target discovery
- 📋 Model Context Protocol specification documentation
- 🎯 Enhanced project documentation with ASCII art branding

### 🛠️ Improved
- 🔒 CI/CD security scanning (replaced Safety CLI with pip-audit)
- 🪝 Pre-commit hooks updated to version 5.0.0
- 📚 README and SPECS documentation enhancements
- 🧪 Expanded test coverage for new functionality

### 🔧 Fixed
- ✅ CI workflow authentication issues
- 📊 Test assertions and pipeline stability

## v0.1.0 - AI-Powered Makefile Assistant

### ✨ Added
- 🚀 Initial project setup with modern Python tooling (uv, pre-commit, pytest)
- 📋 Core CLI scaffolding with Typer for natural language command processing
- 🤖 Foundation for AI-powered Makefile target interpretation
- 📚 Comprehensive project specifications and documentation
- 🧪 Test suite with pytest and coverage reporting
- 🔧 Pre-commit hooks for code quality and formatting
- 📦 Package configuration for PyPI distribution via uvx

### 🛠️ Fixed
- ✅ Pre-commit hook compatibility issues
- 📏 Code formatting and linting compliance

[0.4.3]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.4.3
[0.4.2]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.4.2
[0.4.1]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.4.1
[0.4.0]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.4.0
[0.3.5]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.3.5
[0.3.4]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.3.4
[0.3.3]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.3.3
[0.3.2]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.3.2
[0.3.1]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.3.1
[0.3.0]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.3.0
[0.2.1]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.2.1
[0.2.0]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.2.0
[0.1.0]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.1.0
