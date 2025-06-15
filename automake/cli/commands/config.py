"""Config command implementation for AutoMake CLI.

This module contains all configuration management commands.
"""

import os
import subprocess

import typer

from automake.config import get_config
from automake.utils.output import MessageType, get_formatter


def _convert_config_value(value: str) -> str | int | bool:
    """Convert string value to appropriate type for configuration.

    Args:
        value: String value to convert

    Returns:
        Converted value (str, int, or bool)
    """
    # Try to convert to boolean
    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    # Try to convert to integer
    try:
        return int(value)
    except ValueError:
        pass

    # Return as string
    return value


def config_show_command(
    section: str = typer.Argument(
        None,
        help="Show only a specific section (optional)",
    ),
) -> None:
    """Show current configuration."""
    output = get_formatter()
    try:
        config = get_config()

        if section:
            # Show specific section
            section_data = config.get_all_sections().get(section)
            if section_data is None:
                with output.live_box(
                    "Configuration Error", MessageType.ERROR
                ) as error_box:
                    error_box.update(
                        f"❌ Section '{section}' not found in configuration.\n\n"
                        "💡 Hint: Use 'automake config show' to see all available "
                        "sections."
                    )
                raise typer.Exit(1)

            # Format section data
            content = f"\\[{section}]\n"
            for key, value in section_data.items():
                if isinstance(value, str):
                    content += f'{key} = "{value}"\n'
                else:
                    content += f"{key} = {value}\n"

            with output.live_box(
                f"Configuration - {section}", MessageType.INFO, transient=False
            ) as config_box:
                config_box.update(content.strip())
        else:
            # Show all configuration
            all_config = config.get_all_sections()
            content = ""

            for section_name, section_data in all_config.items():
                content += f"\\[{section_name}]\n"
                for key, value in section_data.items():
                    if isinstance(value, str):
                        content += f'{key} = "{value}"\n'
                    else:
                        content += f"{key} = {value}\n"
                content += "\n"

            with output.live_box(
                "Configuration", MessageType.INFO, transient=False
            ) as config_box:
                config_box.update(content.strip())

    except Exception as e:
        with output.live_box("Configuration Error", MessageType.ERROR) as error_box:
            error_box.update(f"❌ Error reading configuration: {e}")
        raise typer.Exit(1) from e


def config_set_command(
    key_path: str = typer.Argument(
        ..., help="Configuration key path (e.g., 'ollama.model', 'logging.level')"
    ),
    value: str = typer.Argument(..., help="Value to set"),
) -> None:
    """Set a configuration value."""
    output = get_formatter()
    try:
        config = get_config()

        # Parse the key path (e.g., "ollama.model" -> section="ollama", key="model")
        if "." not in key_path:
            # Provide more specific guidance based on common mistakes
            if key_path in ["ollama", "logging", "agent"]:
                raise ValueError(
                    f"Invalid key path '{key_path}'. Missing key name after section.\n"
                    f"Use format 'section.key', for example:\n"
                    f"  • 'ollama.model' to set the AI model\n"
                    f"  • 'ollama.base_url' to set the Ollama server URL\n"
                    f"  • 'logging.level' to set the log level"
                )
            else:
                raise ValueError(
                    f"Invalid key path '{key_path}'. Use format 'section.key' "
                    "(e.g., 'ollama.model', 'logging.level')"
                )

        section, key = key_path.split(".", 1)

        # Convert value to appropriate type
        converted_value = _convert_config_value(value)

        # Set the configuration value
        config.set(section, key, converted_value)

        # Special handling for model changes
        if section == "ollama" and key == "model":
            with output.live_box(
                "Model Configuration Updated", MessageType.SUCCESS
            ) as success_box:
                success_box.update(
                    f"✅ Ollama model updated to: {converted_value}\n\n"
                    "💡 Configuration has been saved to file.\n\n"
                    "⚠️  Important: Run 'automake init' to initialize the new model "
                    "before using AutoMake commands."
                )
        else:
            with output.live_box(
                "Configuration Updated", MessageType.SUCCESS
            ) as success_box:
                success_box.update(
                    f"✅ Set {section}.{key} = {converted_value}\n\n"
                    "💡 Configuration has been saved to file."
                )

    except Exception as e:
        with output.live_box("Configuration Error", MessageType.ERROR) as error_box:
            error_box.update(
                f"❌ Error setting configuration: {e}\n\n"
                "💡 Hint: Check that the section and key names are valid."
            )
        raise typer.Exit(1) from e


def config_reset_command(
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Reset configuration to defaults."""
    output = get_formatter()

    if not yes:
        with output.live_box("Confirm Reset", MessageType.WARNING) as warning_box:
            warning_box.update(
                "⚠️ This will reset ALL configuration to default values.\n\n"
                "This action cannot be undone."
            )

        if not typer.confirm("Are you sure you want to reset the configuration?"):
            with output.live_box("Operation Cancelled", MessageType.INFO) as info_box:
                info_box.update("🚫 Configuration reset cancelled.")
            raise typer.Exit()

    try:
        config = get_config()
        config.reset_to_defaults()

        with output.live_box("Configuration Reset", MessageType.SUCCESS) as success_box:
            success_box.update(
                "✅ Configuration has been reset to defaults.\n\n"
                "💡 All settings have been restored to their original values."
            )

    except Exception as e:
        with output.live_box("Configuration Error", MessageType.ERROR) as error_box:
            error_box.update(f"❌ Error resetting configuration: {e}")
        raise typer.Exit(1) from e


def config_edit_command() -> None:
    """Open configuration file in editor."""
    output = get_formatter()
    try:
        config = get_config()
        config_file = config.config_file_path

        # Determine which editor to use
        editor = os.environ.get("EDITOR", "nano")

        with output.live_box("Opening Editor", MessageType.INFO) as info_box:
            info_box.update(
                f"📝 Opening configuration file in {editor}...\n\nFile: {config_file}"
            )

        # Open the configuration file in the editor
        try:
            subprocess.run([editor, str(config_file)], check=True)

            with output.live_box("Editor Closed", MessageType.SUCCESS) as success_box:
                success_box.update(
                    "✅ Editor closed.\n\n"
                    "💡 If you made changes, they will take effect on the next "
                    "AutoMake command."
                )

        except subprocess.CalledProcessError as e:
            with output.live_box("Editor Error", MessageType.ERROR) as error_box:
                error_box.update(
                    f"❌ Error running editor '{editor}': {e}\n\n"
                    "💡 Hint: Try setting the EDITOR environment variable to "
                    "your preferred editor."
                )
            raise typer.Exit(1) from e
        except FileNotFoundError:
            # Try fallback to system open command
            try:
                with output.live_box("Trying Fallback", MessageType.INFO) as info_box:
                    info_box.update(
                        f"⚠️ Editor '{editor}' not found. Trying system open command..."
                    )

                subprocess.run(["open", str(config_file)], check=True)

                with output.live_box("File Opened", MessageType.SUCCESS) as success_box:
                    success_box.update(
                        "✅ Configuration file opened with system default application.\n\n"  # noqa: E501
                        "💡 If you made changes, they will take effect on the next "
                        "AutoMake command."
                    )
            except (subprocess.CalledProcessError, FileNotFoundError):
                with output.live_box(
                    "Editor Not Found", MessageType.ERROR
                ) as error_box:
                    error_box.update(
                        f"❌ Editor '{editor}' not found and fallback failed.\n\n"
                        "💡 Hint: Install the editor or set the EDITOR environment "
                        "variable to an available editor (e.g., 'nano', 'vim', 'code')."
                    )
                raise typer.Exit(1) from None

    except Exception as e:
        with output.live_box("Configuration Error", MessageType.ERROR) as error_box:
            error_box.update(f"❌ Error accessing configuration file: {e}")
        raise typer.Exit(1) from e


# Backward compatibility aliases for tests
config_show = config_show_command
config_set = config_set_command
config_reset = config_reset_command
config_edit = config_edit_command
