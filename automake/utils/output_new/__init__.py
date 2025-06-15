"""Output formatting utilities for AutoMake.

This package provides consistent, beautiful console output formatting
that matches the style of Typer's error boxes.
"""

from .formatter import (
    OutputFormatter,
    get_formatter,
    print_box,
    print_error_box,
    print_status,
)
from .live_box import LiveBox
from .types import MessageType

__all__ = [
    "MessageType",
    "LiveBox",
    "OutputFormatter",
    "get_formatter",
    "print_box",
    "print_error_box",
    "print_status",
]
