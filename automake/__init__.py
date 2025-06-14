"""AutoMake - AI-powered Makefile command execution.

A command-line tool that leverages a local Large Language Model (LLM) to interpret
natural language commands and execute corresponding Makefile targets.
"""

import tomllib  # noqa: UP036
from pathlib import Path

# Core functionality exports
from automake.core.makefile_reader import MakefileNotFoundError, MakefileReader
from automake.utils.output import MessageType, OutputFormatter, get_formatter


def _get_version() -> str:
    """Get version from pyproject.toml.

    Returns:
        Version string from pyproject.toml, or fallback version if not found.
    """
    try:
        # Get the path to pyproject.toml relative to this file
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomllib.load(f)
                return pyproject_data["project"]["version"]
    except Exception:
        # Fallback if we can't read the version
        pass

    return "0.2.1"  # Fallback version


__version__ = _get_version()
__author__ = "Sean Baufeld"
__email__ = "sean.baufeld@protonmail.com"

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
