"""Makefile reader module for AutoMake.

This module provides functionality to find and read Makefiles from the current
directory, supporting common naming conventions and providing clear error handling.
"""

import re
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
        self._content = None
        self._targets = None
        self._targets_with_descriptions = None

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
        if self._content is not None:
            return self._content

        makefile_path = self.find_makefile()

        try:
            self._content = makefile_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try with latin-1 encoding as fallback for older Makefiles
            try:
                self._content = makefile_path.read_text(encoding="latin-1")
            except UnicodeDecodeError as e:
                raise OSError(f"Could not read Makefile {makefile_path}: {e}") from e
        except OSError as e:
            raise OSError(f"Could not read Makefile {makefile_path}: {e}") from e

        return self._content

    def extract_targets_with_descriptions(self) -> dict[str, str]:
        """Extract target names and their help descriptions from the Makefile.

        Returns:
            Dictionary mapping target names to their descriptions.
            Targets without descriptions will have empty string values.
        """
        if self._targets_with_descriptions is not None:
            return self._targets_with_descriptions

        content = self.read_makefile()
        targets_with_descriptions = {}

        # Pattern to match targets with help descriptions (target: ## description)
        help_pattern = re.compile(r"^([a-zA-Z0-9_.-]+)\s*:.*?##\s*(.*)$", re.MULTILINE)

        # Pattern to match all target definitions
        target_pattern = re.compile(r"^([a-zA-Z0-9_.-]+)\s*:", re.MULTILINE)

        # First, collect all targets with descriptions
        for match in help_pattern.finditer(content):
            target_name = match.group(1).strip()
            description = match.group(2).strip()

            # Skip special targets and variables
            if not target_name.startswith(".") and "=" not in target_name:
                targets_with_descriptions[target_name] = description

        # Then, collect all other targets without descriptions
        for match in target_pattern.finditer(content):
            target_name = match.group(1).strip()

            # Skip special targets and variables
            if (
                not target_name.startswith(".")
                and "=" not in target_name
                and target_name not in targets_with_descriptions
            ):
                targets_with_descriptions[target_name] = ""

        self._targets_with_descriptions = targets_with_descriptions
        return self._targets_with_descriptions

    def extract_targets(self) -> list[str]:
        """Extract target names from the Makefile content.

        Returns:
            List of target names found in the Makefile.
        """
        if self._targets is not None:
            return self._targets

        # Use the targets with descriptions method and extract just the keys
        targets_dict = self.extract_targets_with_descriptions()
        self._targets = list(targets_dict.keys())
        return self._targets

    def get_target_description(self, target_name: str) -> str:
        """Get the description for a specific target.

        Args:
            target_name: Name of the target to get description for.

        Returns:
            Description of the target, or empty string if no description found.
        """
        targets_dict = self.extract_targets_with_descriptions()
        return targets_dict.get(target_name, "")

    def get_targets_with_descriptions(self) -> list[tuple[str, str]]:
        """Get a list of tuples containing target names and descriptions.

        Returns:
            List of (target_name, description) tuples.
        """
        targets_dict = self.extract_targets_with_descriptions()
        return [(target, desc) for target, desc in targets_dict.items()]

    @property
    def targets(self) -> list[str]:
        """Get the list of targets from the Makefile.

        Returns:
            List of target names.
        """
        return self.extract_targets()

    @property
    def targets_with_descriptions(self) -> dict[str, str]:
        """Get the dictionary of targets with their descriptions.

        Returns:
            Dictionary mapping target names to descriptions.
        """
        return self.extract_targets_with_descriptions()

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
