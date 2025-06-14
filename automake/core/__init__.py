"""Core functionality for AutoMake.

This module contains the core business logic for reading and processing Makefiles.
"""

from automake.core.makefile_reader import MakefileNotFoundError, MakefileReader

__all__ = [
    "MakefileReader",
    "MakefileNotFoundError",
]
