"""AutoMake - AI-powered Makefile command execution.

A command-line tool that leverages a local Large Language Model (LLM) to interpret
natural language commands and execute corresponding Makefile targets.
"""

__version__ = "0.2.0"  # Match version in pyproject.toml
__author__ = "Sean Baufeld"
__email__ = "sean.baufeld@protonmail.com"

# Core functionality exports
from automake.core.makefile_reader import MakefileNotFoundError, MakefileReader
from automake.utils.output import MessageType, OutputFormatter, get_formatter

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "MakefileReader",
    "MakefileNotFoundError",
    "MessageType",
    "OutputFormatter",
    "get_formatter",
]
