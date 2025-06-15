#!/usr/bin/env python3
"""Test script for rainbow ASCII art animation."""

from rich.console import Console

from automake.utils.output import OutputFormatter


def main():
    """Test the rainbow ASCII art animation."""
    console = Console()
    formatter = OutputFormatter(console)

    # Test ASCII art content (same as AutoMake's)
    test_art = """   ___       __                  __
  / _ |__ __/ /____  __ _  ___ _/ /_____
 / __ / // / __/ _ \/  ' \/ _ `/  '_/ -_)
/_/ |_\_,_/\__/\___/_/_/_/\_,_/_/\_\\__/"""

    print("🌈 Testing Rainbow ASCII Art Animation! 🌈")
    print("Watch the colors cycle through the rainbow...")
    print("Press Ctrl+C to stop early if needed.\n")

    # Show the rainbow animation for 5 seconds to make it clearly visible
    formatter.print_rainbow_ascii_art(test_art, duration=5.0)

    print("\n✨ Animation complete!")


if __name__ == "__main__":
    main()
