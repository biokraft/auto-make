"""Makefile reader module for AutoMake.

This module provides functionality to find and read Makefiles from the current
directory, supporting common naming conventions and providing clear error handling.
"""

from pathlib import Path


class MakefileNotFoundError(Exception):
    """Raised when no Makefile is found in the current directory."""

    pass


class MakefileReader:
    """Handles finding and reading Makefiles from the filesystem."""

    # Common Makefile naming conventions, in order of preference
    MAKEFILE_NAMES = ["Makefile", "makefile", "GNUmakefile"]

    def __init__(self, directory: Path | None = None) -> None:
        """Initialize the MakefileReader.

        Args:
            directory: Directory to search for Makefiles. Defaults to current directory.
        """
        self.directory = directory or Path.cwd()

    def find_makefile(self) -> Path:
        """Find a Makefile in the specified directory.

        Returns:
            Path to the found Makefile.

        Raises:
            MakefileNotFoundError: If no Makefile is found in the directory.
        """
        for makefile_name in self.MAKEFILE_NAMES:
            makefile_path = self.directory / makefile_name
            if makefile_path.exists() and makefile_path.is_file():
                return makefile_path

        raise MakefileNotFoundError(
            f"No Makefile found in directory: {self.directory}\n"
            f"Looked for: {', '.join(self.MAKEFILE_NAMES)}"
        )

    def read_makefile(self) -> str:
        """Read the contents of the Makefile.

        Returns:
            The contents of the Makefile as a string.

        Raises:
            MakefileNotFoundError: If no Makefile is found.
            OSError: If there's an error reading the file.
        """
        makefile_path = self.find_makefile()

        try:
            return makefile_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try with latin-1 encoding as fallback for older Makefiles
            try:
                return makefile_path.read_text(encoding="latin-1")
            except UnicodeDecodeError as e:
                raise OSError(f"Could not read Makefile {makefile_path}: {e}") from e
        except OSError as e:
            raise OSError(f"Could not read Makefile {makefile_path}: {e}") from e

    def get_makefile_info(self) -> dict[str, str]:
        """Get information about the found Makefile.

        Returns:
            Dictionary containing Makefile information including path and size.

        Raises:
            MakefileNotFoundError: If no Makefile is found.
        """
        makefile_path = self.find_makefile()
        stat = makefile_path.stat()

        return {
            "path": str(makefile_path),
            "name": makefile_path.name,
            "size": str(stat.st_size),
            "directory": str(self.directory),
        }


def read_makefile_from_directory(directory: Path | None = None) -> str:
    """Convenience function to read a Makefile from a directory.

    Args:
        directory: Directory to search for Makefiles. Defaults to current directory.

    Returns:
        The contents of the Makefile as a string.

    Raises:
        MakefileNotFoundError: If no Makefile is found.
        OSError: If there's an error reading the file.
    """
    reader = MakefileReader(directory)
    return reader.read_makefile()
