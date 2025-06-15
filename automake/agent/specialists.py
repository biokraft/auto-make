"""Specialist agents for AutoMake.

This module defines the specialist agents that are managed by the ManagerAgent.
Each agent is a ManagedAgent instance with specific tools and capabilities.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from smolagents import DuckDuckGoSearchTool, tool

from ..core.makefile_reader import MakefileReader
from ..logging import get_logger

logger = get_logger()


@tool
def run_shell_command(command: str) -> str:
    """Execute a shell command and return its output.

    Args:
        command: The shell command to execute

    Returns:
        The combined stdout and stderr output from the command
    """
    try:
        logger.info(f"Executing shell command: {command}")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        output += f"Return code: {result.returncode}"

        logger.info(f"Command completed with return code: {result.returncode}")
        return output

    except subprocess.TimeoutExpired:
        error_msg = f"Command timed out after 300 seconds: {command}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
    except Exception as e:
        error_msg = f"Error executing command '{command}': {str(e)}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"


@tool
def python_interpreter(code: str, dependencies: list[str] = None) -> str:
    """Execute Python code in a temporary, isolated uv environment.

    This tool creates a new virtual environment for each execution, installs any
    specified dependencies, runs the code, captures the output, and tears down
    the environment, ensuring a clean and secure execution context.

    Args:
        code: The Python code to execute
        dependencies: A list of pip packages to install before execution

    Returns:
        The standard output and standard error of the executed code
    """
    if dependencies is None:
        dependencies = []

    temp_dir = None
    try:
        # Create a secure temporary directory
        temp_dir = tempfile.mkdtemp(prefix="automake_python_")
        temp_path = Path(temp_dir)

        logger.info(f"Created temporary directory: {temp_dir}")

        # Create virtual environment using uv
        venv_path = temp_path / "venv"
        logger.info("Creating virtual environment with uv")

        result = subprocess.run(
            ["uv", "venv", str(venv_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            return f"ERROR: Failed to create virtual environment: {result.stderr}"

        # Determine the python executable path
        if os.name == "nt":  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
        else:  # Unix-like
            python_exe = venv_path / "bin" / "python"

        if not python_exe.exists():
            return f"ERROR: Python executable not found at {python_exe}"

        # Install dependencies if provided
        if dependencies:
            logger.info(f"Installing dependencies: {dependencies}")
            for dep in dependencies:
                result = subprocess.run(
                    ["uv", "pip", "install", "--python", str(python_exe), dep],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if result.returncode != 0:
                    return (
                        f"ERROR: Failed to install dependency '{dep}': {result.stderr}"
                    )

        # Write the code to a temporary script file
        script_path = temp_path / "script.py"
        script_path.write_text(code, encoding="utf-8")

        # Execute the script
        logger.info("Executing Python code")
        result = subprocess.run(
            [str(python_exe), str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=str(temp_path),
        )

        # Combine output
        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        output += f"Return code: {result.returncode}"

        logger.info(
            f"Python code execution completed with return code: {result.returncode}"
        )
        return output

    except subprocess.TimeoutExpired:
        error_msg = "Python code execution timed out after 300 seconds"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
    except Exception as e:
        error_msg = f"Error executing Python code: {str(e)}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(
                    f"Failed to clean up temporary directory {temp_dir}: {e}"
                )


@tool
def read_file(path: str) -> str:
    """Read the entire content of a file and return it as a string.

    Args:
        path: The file path to read

    Returns:
        The file content as a string
    """
    try:
        file_path = Path(path)
        if not file_path.exists():
            return f"ERROR: File does not exist: {path}"

        if not file_path.is_file():
            return f"ERROR: Path is not a file: {path}"

        logger.info(f"Reading file: {path}")
        content = file_path.read_text(encoding="utf-8")
        logger.info(f"Successfully read file: {path} ({len(content)} characters)")
        return content

    except Exception as e:
        error_msg = f"Error reading file '{path}': {str(e)}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"


@tool
def edit_file(path: str, new_content: str) -> str:
    """Overwrite a file with new content. Use with extreme caution.

    Args:
        path: The file path to write to
        new_content: The new content to write to the file

    Returns:
        Success or error message
    """
    try:
        file_path = Path(path)

        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Writing to file: {path}")
        file_path.write_text(new_content, encoding="utf-8")
        logger.info(
            f"Successfully wrote to file: {path} ({len(new_content)} characters)"
        )
        return (
            f"SUCCESS: File '{path}' has been updated with "
            f"{len(new_content)} characters"
        )

    except Exception as e:
        error_msg = f"Error writing to file '{path}': {str(e)}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"


@tool
def list_directory(path: str = ".") -> str:
    """List the contents of a directory.

    Args:
        path: The directory path to list (defaults to current directory)

    Returns:
        A formatted list of directory contents
    """
    try:
        dir_path = Path(path)
        if not dir_path.exists():
            return f"ERROR: Directory does not exist: {path}"

        if not dir_path.is_dir():
            return f"ERROR: Path is not a directory: {path}"

        logger.info(f"Listing directory: {path}")

        items = []
        for item in sorted(dir_path.iterdir()):
            if item.is_dir():
                items.append(f"[DIR]  {item.name}/")
            else:
                size = item.stat().st_size
                items.append(f"[FILE] {item.name} ({size} bytes)")

        if not items:
            return f"Directory '{path}' is empty"

        result = f"Contents of '{path}':\n" + "\n".join(items)
        logger.info(f"Listed {len(items)} items in directory: {path}")
        return result

    except Exception as e:
        error_msg = f"Error listing directory '{path}': {str(e)}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"


@tool
def get_makefile_targets() -> str:
    """Get available Makefile targets and their descriptions.

    Returns:
        A formatted list of Makefile targets with descriptions
    """
    try:
        logger.info("Reading Makefile targets")
        reader = MakefileReader()
        reader.read_makefile()

        targets_with_desc = reader.targets_with_descriptions

        if not targets_with_desc:
            return "No Makefile targets found"

        result = "Available Makefile targets:\n"
        for target, description in targets_with_desc.items():
            if description:
                result += f"  {target}: {description}\n"
            else:
                result += f"  {target}: (no description)\n"

        logger.info(f"Found {len(targets_with_desc)} Makefile targets")
        return result

    except Exception as e:
        error_msg = f"Error reading Makefile targets: {str(e)}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"


@tool
def run_makefile_target(target: str) -> str:
    """Execute a specific Makefile target.

    Args:
        target: The Makefile target to execute

    Returns:
        The output from executing the make command
    """
    try:
        logger.info(f"Executing Makefile target: {target}")

        # First check if the target exists
        reader = MakefileReader()
        reader.read_makefile()

        if target not in reader.targets_with_descriptions:
            available_targets = list(reader.targets_with_descriptions.keys())
            return (
                f"ERROR: Target '{target}' not found. "
                f"Available targets: {available_targets}"
            )

        # Execute the make command
        command = f"make {target}"
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout for make commands
        )

        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        output += f"Return code: {result.returncode}"

        logger.info(
            f"Make target '{target}' completed with return code: {result.returncode}"
        )
        return output

    except subprocess.TimeoutExpired:
        error_msg = f"Make target '{target}' timed out after 600 seconds"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
    except Exception as e:
        error_msg = f"Error executing make target '{target}': {str(e)}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"


# Specialist tool collections for the manager agent
def get_terminal_tools():
    """Get tools for terminal operations."""
    return [run_shell_command, list_directory]


def get_coding_tools():
    """Get tools for Python code execution."""
    return [python_interpreter]


def get_filesystem_tools():
    """Get tools for file system operations."""
    return [read_file, edit_file, list_directory]


def get_makefile_tools():
    """Get tools for Makefile operations."""
    return [get_makefile_targets, run_makefile_target]


def get_web_tools():
    """Get tools for web search operations."""
    return [DuckDuckGoSearchTool()]


def get_all_specialist_tools():
    """Get all specialist tools for the manager agent."""
    tools = []
    tools.extend(get_terminal_tools())
    tools.extend(get_coding_tools())
    tools.extend(get_filesystem_tools())
    tools.extend(get_makefile_tools())
    tools.extend(get_web_tools())

    # Remove duplicates (like list_directory which appears in multiple categories)
    seen = set()
    unique_tools = []
    for tool_item in tools:
        tool_name = tool_item.name if hasattr(tool_item, "name") else str(tool_item)
        if tool_name not in seen:
            seen.add(tool_name)
            unique_tools.append(tool_item)

    return unique_tools


# For backward compatibility, create simple objects that represent the
# specialist capabilities
class SpecialistAgent:
    """Simple representation of a specialist agent's capabilities."""

    def __init__(self, name: str, description: str, tools: list):
        self.name = name
        self.description = description
        self.tools = tools


# Create specialist agent representations
terminal_agent = SpecialistAgent(
    name="terminal_agent",
    description="Execute shell commands and list directory contents",
    tools=get_terminal_tools(),
)

coding_agent = SpecialistAgent(
    name="coding_agent",
    description="Execute Python code with dependency management",
    tools=get_coding_tools(),
)

filesystem_agent = SpecialistAgent(
    name="filesystem_agent",
    description="Read from and write to files, explore directories",
    tools=get_filesystem_tools(),
)

makefile_agent = SpecialistAgent(
    name="makefile_agent",
    description="List and execute Makefile targets",
    tools=get_makefile_tools(),
)

web_agent = SpecialistAgent(
    name="web_agent",
    description="Search the internet using DuckDuckGo",
    tools=get_web_tools(),
)
