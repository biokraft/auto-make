# AutoMake User Guide

Welcome to AutoMake, your AI-powered command-line assistant! This guide will help you master the multi-agent system and get the most out of your AI-native shell experience.

## Table of Contents
1. [Getting Started with Agents](#getting-started-with-agents)
2. [Understanding the Multi-Agent Architecture](#understanding-the-multi-agent-architecture)
3. [Interactive vs Non-Interactive Modes](#interactive-vs-non-interactive-modes)
4. [Configuration Options for Agents](#configuration-options-for-agents)
5. [Best Practices for Prompting Agents](#best-practices-for-prompting-agents)
6. [Troubleshooting Common Agent Issues](#troubleshooting-common-agent-issues)
7. [Advanced Usage Patterns and Workflows](#advanced-usage-patterns-and-workflows)

## Getting Started with Agents

AutoMake transforms your command line into an intelligent, agent-driven environment. Instead of memorizing commands and flags, you simply describe what you want to accomplish in natural language.

### The Manager Agent

The **Manager Agent** is your primary interface. It:
- Receives your natural language requests
- Analyzes the intent and complexity
- Decides which specialist agent(s) to use
- Orchestrates multi-step workflows
- Provides you with real-time feedback

### Specialist Agents

The Manager Agent coordinates with several specialist agents, each optimized for specific tasks:

#### 🖥️ Terminal Agent
- **Purpose**: Execute shell commands and system operations
- **Example prompts**: `"show me the current directory contents"`

#### 🐍 Coding Agent
- **Purpose**: Execute Python code in secure, isolated environments
- **Example prompts**: `"calculate the factorial of 20"`

#### 🌐 Web Agent
- **Purpose**: Search the internet and gather web-based information
- **Example prompts**: `"search for Python 3.13 new features"`

#### 🔨 Makefile Agent
- **Purpose**: Handle build system operations and Makefile targets
- **Example prompts**: `"show me all available make targets"`

#### 📁 FileSystem Agent
- **Purpose**: Manage files and directories
- **Example prompts**: `"read the contents of config.toml"`

## Interactive vs Non-Interactive Modes

AutoMake offers two primary modes of operation, each suited for different use cases.

### Non-Interactive Mode

Perfect for quick, one-off tasks where you know exactly what you want to accomplish.

**Syntax**: `automake "your request here"`

**When to use**:
- Quick system queries
- Simple file operations
- Running known commands
- Automation scripts
- CI/CD pipelines

### Interactive Mode

Ideal for complex, multi-step tasks, exploration, and iterative problem-solving.

**Syntax**: `automake agent`

**Features**:
- Persistent conversation context
- Multi-step task execution
- Clarification and refinement
- Exploratory workflows
- Learning and explanation

**When to use**:
- Complex problem-solving
- Learning new technologies
- Exploratory data analysis
- Multi-step workflows
- When you need explanations

## Configuration Options for Agents

AutoMake provides extensive configuration options to customize agent behavior.

### Core Agent Settings

```bash
# View current configuration
automake config show

# Set agent confirmation requirements
automake config set agent.require_confirmation true

# Configure interaction threshold for complex tasks
automake config set ai.interactive_threshold 80
```

## Best Practices for Prompting Agents

Effective prompting is key to getting the best results from AutoMake's agents.

### Be Specific and Clear

❌ **Poor**: `"fix my code"`
✅ **Good**: `"review my Python script for syntax errors and suggest improvements"`

### Leverage Agent Specialization

Understand which agent is best for your task:

```bash
# Terminal Agent tasks
automake "show system resource usage"

# Coding Agent tasks
automake "create a data visualization from this CSV"

# Web Agent tasks
automake "find the latest Python security advisories"

# FileSystem Agent tasks
automake "organize my downloads folder by file type"

# Makefile Agent tasks
automake "show all build targets and their descriptions"
```

## Troubleshooting Common Agent Issues

### Agent Startup Problems

**Issue**: Agent fails to initialize
```bash
# Check Ollama status
ollama serve
ollama list

# Reinitialize AutoMake
automake init
```

### Agent Performance Issues

**Issue**: Slow responses
```bash
# Switch to a faster model
automake config set ollama.model "qwen3:0.6b"
automake init
```

## Advanced Usage Patterns and Workflows

### Workflow 1: Project Analysis and Documentation

```bash
# Start interactive session for complex analysis
automake agent

# In interactive mode:
# 1. "analyze the project structure and identify main components"
# 2. "review the codebase for documentation coverage"
# 3. "generate a comprehensive README based on the code"
```

### Workflow 2: Automated Testing and Quality Assurance

```bash
# Non-interactive approach for CI/CD
automake "run all tests and generate coverage report"
automake "check code style and formatting issues"
```

## Tips for Maximum Productivity

1. **Start Simple**: Begin with basic commands and gradually explore more complex workflows
2. **Use Interactive Mode**: For learning and exploration, interactive mode provides the best experience
3. **Leverage Confirmation**: Keep `agent.require_confirmation` enabled for safety
4. **Monitor Logs**: Use `automake logs` to understand agent decision-making
5. **Experiment**: Try different phrasings to see how agents interpret your requests

---

Ready to become an AutoMake power user? Start with simple commands and gradually explore the full potential of your AI-powered command line assistant!
