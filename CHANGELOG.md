# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.4.7 - CI Compatibility & Animation Fixes

### 🔧 Fixed
- 🐛 Resolved CI environment animation timeout issues by automatically disabling animations in CI/CD pipelines
- 🧪 Enhanced test compatibility across GitHub Actions, GitLab CI, Travis, CircleCI, and Jenkins environments
- ⚡ Improved deployment reliability for automated publishing workflows

### 🛠️ Improved
- 🎯 Smarter animation detection that respects CI environment variables
- 📦 More robust package publishing process with better error handling

## v0.4.6 - Enhanced User Experience & Interactive Configuration

### ✨ Added
- 🎬 Typewriter-style text animation across `RichInteractiveSession`, `LiveBox`, and `OutputFormatter` components
- ⚙️ Interactive `config model` command for streamlined Ollama model selection and configuration
- 🎯 `ModelSelector` utility for both local and online model options with enhanced user experience
- 📋 Animation configuration settings allowing users to enable/disable animations and adjust speed

### 🛠️ Improved
- 🎨 Enhanced visual feedback with consistent animated text display throughout the application
- 🔧 Comprehensive configuration management with better model selection workflow
- 📚 Updated specifications documentation with new animated text display requirements

### 🔧 Fixed
- ✅ Enhanced error handling for animation features and model configuration processes
- 🧪 Expanded test coverage ensuring robust functionality across animation and configuration components

## v0.4.5 - Agent System Enhancement & User Safety

### ✨ Added
- 🛡️ Action confirmation feature for enhanced user safety during agent operations
- 🤖 AutoMakeAgent specification for natural language command interpretation
- 📊 MermaidAgent specification for diagram generation from source code
- 🔧 Intelligent CLI error handling with AI-powered correction suggestions
- ⚙️ Configurable confirmation prompts via `agent.require_confirmation` setting

### 🛠️ Improved
- 🎯 Interactive agent mode with comprehensive session management
- 📚 Enhanced documentation with future considerations for third-party agent ecosystem
- 🔄 Agent routing logic for better task delegation and execution
- 🧪 Expanded test coverage for agent functionality and error handling scenarios

### 🔧 Fixed
- ✅ Enhanced error management across CLI operations with robust handling
- 🎨 Help display improvements with cleaner ASCII art presentation

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
- 🎯 Decomposed monolithic CLI into modular command structure (`commands/`, `display/`, `config/`, `
