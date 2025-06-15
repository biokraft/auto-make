# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.3.5]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.3.5
[0.3.4]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.3.4
[0.3.3]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.3.3
[0.3.2]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.3.2
[0.3.1]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.3.1
[0.3.0]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.3.0
[0.2.1]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.2.1
[0.2.0]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.2.0
[0.1.0]: https://github.com/seanbaufeld/auto-make/releases/tag/v0.1.0
