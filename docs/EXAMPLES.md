# AutoMake Examples and Tutorials

## Table of Contents

1. [Basic Agent Usage Patterns](#basic-agent-usage-patterns)
2. [Complex Multi-Step Workflows](#complex-multi-step-workflows)
3. [Integration with Development Tools](#integration-with-development-tools)
4. [Real-World Use Case Scenarios](#real-world-use-case-scenarios)
5. [Performance Optimization Tips](#performance-optimization-tips)

## Basic Agent Usage Patterns

### Getting Started with AutoMake

AutoMake operates through a multi-agent system where a Manager Agent orchestrates specialist agents to accomplish your tasks. Here are the fundamental usage patterns:

#### Non-Interactive Mode (Quick Commands)

Execute single commands directly:

```bash
# File operations
automake "list all python files in the current directory"
automake "create a new file called hello.py with a simple hello world function"
automake "show me the contents of the README file"

# Build and development tasks
automake "build the project using make"
automake "run all tests"
automake "install the project dependencies"

# System operations
automake "check the current git status"
automake "show me the disk usage of this directory"
automake "find all files modified in the last 24 hours"

# Web research
automake "search for the latest Python best practices"
automake "find documentation for the requests library"
```

#### Interactive Mode (Chat Session)

Start an interactive session for complex, multi-turn conversations:

```bash
# Start interactive mode
automake agent

# Then in the chat session:
You: "I need to set up a new Python project"
Agent: "I'll help you set up a new Python project. Let me create the basic structure..."

You: "Add a requirements.txt file with common dependencies"
Agent: "I'll add a requirements.txt file with commonly used Python dependencies..."

You: "Now create a simple test file"
Agent: "I'll create a basic test file using pytest..."
```

### Understanding Agent Specialization

Each specialist agent has specific capabilities:

#### Terminal Agent Examples
```bash
# System administration
automake "show me all running Python processes"
automake "check if port 8000 is available"
automake "create a backup of the current directory"

# Git operations
automake "commit all changes with message 'Update documentation'"
automake "create a new branch called feature/new-agent"
automake "show me the git log for the last 5 commits"
```

#### Coding Agent Examples
```bash
# Code analysis and execution
automake "calculate the factorial of 10 using Python"
automake "analyze this CSV file and show me basic statistics"
automake "create a simple web scraper for a given URL"

# Data processing
automake "read the data.json file and convert it to CSV format"
automake "generate a random password with specific criteria"
```

#### Web Agent Examples
```bash
# Research and information gathering
automake "find the current weather in San Francisco"
automake "search for recent news about artificial intelligence"
automake "look up the documentation for FastAPI"

# Technical research
automake "find best practices for Python testing"
automake "search for solutions to Docker memory issues"
```

#### Makefile Agent Examples
```bash
# Build system operations
automake "show me all available make targets"
automake "run the test target from the Makefile"
automake "build the docker image using make"

# Project management
automake "clean the build artifacts"
automake "deploy the application to staging"
```

#### FileSystem Agent Examples
```bash
# File management
automake "organize all images in this directory by date"
automake "find and delete all .pyc files recursively"
automake "create a directory structure for a new web project"

# Content analysis
automake "count the lines of code in all Python files"
automake "find all TODO comments in the codebase"
```

## Complex Multi-Step Workflows

### Project Setup Workflow

```bash
# Start interactive session for complex setup
automake agent

# Multi-step project initialization
You: "I want to create a new FastAPI project with testing setup"

Agent: "I'll help you create a complete FastAPI project. Let me start by creating the project structure..."

# The agent will:
# 1. Create directory structure
# 2. Set up virtual environment
# 3. Install FastAPI and dependencies
# 4. Create main application file
# 5. Set up testing framework
# 6. Create configuration files
# 7. Initialize git repository

You: "Add Docker support to this project"

Agent: "I'll add Docker support with a Dockerfile and docker-compose.yml..."

You: "Create a simple CRUD API for users"

Agent: "I'll create a complete CRUD API with models, routes, and tests..."
```

### Code Analysis and Refactoring

```bash
automake agent

You: "Analyze the code quality of my Python project"

Agent: "I'll analyze your Python project for code quality issues..."
# Agent runs linting tools, analyzes complexity, checks test coverage

You: "Fix the linting issues you found"

Agent: "I'll fix the linting issues by updating the code..."
# Agent applies automatic fixes for style and simple issues

You: "Add type hints to all functions that are missing them"

Agent: "I'll add type hints to improve code quality..."
# Agent analyzes functions and adds appropriate type annotations
```

### CI/CD Pipeline Setup

```bash
automake "set up a complete CI/CD pipeline for this Python project"

# The agent will:
# 1. Create GitHub Actions workflow files
# 2. Set up testing pipeline
# 3. Configure code quality checks
# 4. Add deployment steps
# 5. Create necessary configuration files
```

## Integration with Development Tools

### Git Workflow Integration

```bash
# Intelligent git operations
automake "create a feature branch and switch to it"
automake "stage all Python files and commit with a descriptive message"
automake "merge the current branch to main and clean up"

# Code review preparation
automake "show me what files have changed since last commit"
automake "create a summary of changes for code review"
```

### Database Operations

```bash
# Database management
automake "create a simple SQLite database with a users table"
automake "backup the database to a timestamped file"
automake "run database migrations if any exist"

# Data analysis
automake "connect to the database and show me user statistics"
automake "export the users table to a CSV file"
```

### Docker and Containerization

```bash
# Container management
automake "build and run the Docker container for this project"
automake "show me the logs from the running container"
automake "create a docker-compose file for this application"

# Container debugging
automake "inspect the running container and show resource usage"
automake "connect to the running container and check the environment"
```

### Testing and Quality Assurance

```bash
# Test management
automake "run all tests and generate a coverage report"
automake "create unit tests for the new functions I added"
automake "run only the failing tests from last run"

# Code quality
automake "run all linting tools and fix what can be auto-fixed"
automake "check for security vulnerabilities in dependencies"
automake "generate documentation from docstrings"
```

## Real-World Use Case Scenarios

### Scenario 1: Bug Investigation

```bash
automake agent

You: "I'm getting a 500 error in my web application. Help me debug it."

Agent: "I'll help you investigate the 500 error. Let me start by checking the logs..."

# Agent will:
# 1. Check application logs
# 2. Examine error traces
# 3. Test API endpoints
# 4. Check database connections
# 5. Suggest fixes

You: "The error seems to be in the database connection. Can you check the config?"

Agent: "Let me examine the database configuration and test the connection..."
```

### Scenario 2: Performance Optimization

```bash
You: "My Python script is running slowly. Can you help optimize it?"

Agent: "I'll analyze your script for performance bottlenecks..."

# Agent will:
# 1. Profile the code execution
# 2. Identify slow functions
# 3. Suggest optimizations
# 4. Implement improvements
# 5. Benchmark the results
```

### Scenario 3: Deployment Preparation

```bash
You: "I need to deploy this application to production. What do I need to do?"

Agent: "I'll help you prepare for production deployment..."

# Agent will:
# 1. Check for production readiness
# 2. Create deployment scripts
# 3. Set up environment configurations
# 4. Create monitoring setup
# 5. Generate deployment documentation
```

### Scenario 4: Code Migration

```bash
You: "I need to migrate this project from Python 3.8 to 3.12"

Agent: "I'll help you migrate to Python 3.12. Let me check compatibility..."

# Agent will:
# 1. Analyze current dependencies
# 2. Check for compatibility issues
# 3. Update configuration files
# 4. Test the migration
# 5. Update documentation
```

### Scenario 5: Security Audit

```bash
You: "Can you perform a security audit of my web application?"

Agent: "I'll conduct a security audit of your application..."

# Agent will:
# 1. Scan for vulnerable dependencies
# 2. Check for common security issues
# 3. Analyze authentication mechanisms
# 4. Review file permissions
# 5. Generate security report
```

## Performance Optimization Tips

### Efficient Agent Usage

**1. Use Specific Commands**
```bash
# Instead of: "do something with files"
# Use: "list all Python files modified in the last week"

# Instead of: "fix the code"
# Use: "fix PEP 8 style issues in the main.py file"
```

**2. Break Complex Tasks into Steps**
```bash
# For complex workflows, use interactive mode
automake agent

# Then break down the task:
You: "First, analyze the current code structure"
You: "Now, identify the main issues"
You: "Finally, implement the fixes one by one"
```

**3. Leverage Agent Specialization**
```bash
# Let each agent do what it does best
automake "search for Python best practices"  # Web Agent
automake "run the test suite"                # Terminal Agent
automake "calculate data statistics"         # Coding Agent
automake "organize project files"           # FileSystem Agent
```

### Configuration Optimization

**1. Adjust Confirmation Settings**
```bash
# For trusted environments, disable confirmations
automake config set agent.require_confirmation false

# For sensitive operations, keep confirmations enabled
automake config set agent.require_confirmation true
```

**2. Optimize Model Selection**
```bash
# Use faster models for simple tasks
automake config set ollama.model "qwen3:0.6b"

# Use more capable models for complex reasoning
automake config set ollama.model "qwen3:8b"
```

**3. Enable Debug Mode for Troubleshooting**
```bash
# Enable detailed logging
automake config set logging.level DEBUG

# Check logs for performance insights
automake logs view
```

### Best Practices for Large Projects

**1. Use Project-Specific Configuration**
```bash
# Create project-specific config
echo '[agent]
require_confirmation = false
timeout = 600

[ollama]
model = "qwen3:8b"' > automake.toml
```

**2. Organize Commands by Complexity**
```bash
# Simple commands: use non-interactive mode
automake "run tests"

# Complex workflows: use interactive mode
automake agent
# Then have a conversation about the complex task
```

**3. Document Agent Workflows**
```bash
# Create scripts for common agent workflows
echo '#!/bin/bash
# Development workflow
automake "check git status"
automake "run all tests"
automake "check code quality"
automake "build the project"' > dev-check.sh
```

### Troubleshooting Common Issues

**1. Agent Not Responding**
```bash
# Check Ollama status
ollama list

# Verify configuration
automake config show

# Check logs
automake logs view
```

**2. Slow Performance**
```bash
# Use a faster model
automake config set ollama.model "qwen3:0.6b"

# Check system resources
automake "show system resource usage"
```

**3. Unexpected Results**
```bash
# Enable debug mode
automake config set logging.level DEBUG

# Use more specific commands
# Instead of: "fix this"
# Use: "fix the syntax error on line 25 of main.py"
```

---

These examples demonstrate the power and flexibility of AutoMake's multi-agent system. Start with simple commands and gradually explore more complex workflows as you become familiar with the system. The agents are designed to understand natural language, so feel free to describe your tasks in your own words!
