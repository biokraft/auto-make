"""Agent module for AutoMake.

This module implements the multi-agent architecture using smolagents framework.
"""

from .manager import ManagerAgentRunner, create_manager_agent
from .specialists import (
    get_all_specialist_tools,
    get_coding_tools,
    get_filesystem_tools,
    get_makefile_tools,
    get_terminal_tools,
    get_web_tools,
)

__all__ = [
    "create_manager_agent",
    "ManagerAgentRunner",
    "get_all_specialist_tools",
    "get_coding_tools",
    "get_filesystem_tools",
    "get_makefile_tools",
    "get_terminal_tools",
    "get_web_tools",
]
