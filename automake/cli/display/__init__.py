"""Display and presentation modules for AutoMake CLI.

This package contains modules responsible for user interface elements,
help systems, and visual presentation of information.
"""

from .callbacks import help_callback, help_command, version_callback
from .help import print_help_with_ascii, print_welcome, read_ascii_art

__all__ = [
    # Callbacks
    "version_callback",
    "help_callback",
    "help_command",
    # Help and ASCII art
    "print_welcome",
    "print_help_with_ascii",
    "read_ascii_art",
]
