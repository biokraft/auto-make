"""Log management commands for AutoMake CLI."""

import subprocess
from pathlib import Path

import appdirs
import typer
from rich.console import Console
from rich.table import Table

from automake.config import get_config
from automake.utils.output import MessageType


def get_log_directory() -> Path:
    """Get the log directory path.

    Returns:
        Path to the log directory
    """
    if hasattr(appdirs, "user_log_dir"):
        return Path(appdirs.user_log_dir("automake"))
    else:
        # Fallback for older appdirs versions
        return Path(appdirs.user_data_dir("automake")) / "logs"


def get_log_files() -> list[Path]:
    """Get all log files in the log directory.

    Returns:
        List of log file paths, sorted by modification time (newest first)
    """
    log_dir = get_log_directory()
    if not log_dir.exists():
        return []

    # Find all log files with PID-based naming (automake_YYYY-MM-DD_PID.log)
    log_files = list(log_dir.glob("automake_*.log"))

    # Sort by modification time, newest first
    log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    return log_files


def show_logs_location(console: Console, output) -> None:
    """Show the location of log files."""
    log_dir = get_log_directory()

    if not log_dir.exists():
        output.print_box(
            f"Log directory does not exist yet: {log_dir}\n"
            "Logs will be created here when AutoMake runs.",
            MessageType.INFO,
            "Log Directory",
        )
        return

    log_files = get_log_files()

    if not log_files:
        output.print_box(
            f"Log directory exists but no log files found: {log_dir}",
            MessageType.INFO,
            "Log Directory",
        )
        return

    # Create a table showing log files
    table = Table(title="AutoMake Log Files")
    table.add_column("File", style="cyan")
    table.add_column("Size", justify="right", style="green")
    table.add_column("Modified", style="yellow")

    for log_file in log_files:
        stat = log_file.stat()
        size = format_file_size(stat.st_size)
        modified = format_timestamp(stat.st_mtime)
        table.add_row(log_file.name, size, modified)

    console.print(table)
    console.print(f"\nLog directory: [cyan]{log_dir}[/cyan]")


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def format_timestamp(timestamp: float) -> str:
    """Format timestamp in human-readable format."""
    import datetime

    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def view_log_content(
    console: Console,
    output,
    lines: int = 50,
    follow: bool = False,
    log_file: str | None = None,
) -> None:
    """View log content.

    Args:
        console: Rich console instance
        output: Output formatter
        lines: Number of lines to show
        follow: Whether to follow the log (tail -f behavior)
        log_file: Specific log file to view (defaults to current log)
    """
    log_files = get_log_files()

    if not log_files:
        output.print_box(
            "No log files found. Run AutoMake commands to generate logs.",
            MessageType.WARNING,
            "No Logs",
        )
        return

    # Determine which log file to view
    if log_file:
        target_file = get_log_directory() / log_file
        if not target_file.exists():
            output.print_box(
                f"Log file '{log_file}' not found.", MessageType.ERROR, "File Not Found"
            )
            return
    else:
        target_file = log_files[0]  # Most recent log file

    try:
        if follow:
            # Use tail -f for following logs
            output.print_box(
                f"Following log file: {target_file.name}\nPress Ctrl+C to stop",
                MessageType.INFO,
                "Tail Mode",
            )
            subprocess.run(["tail", "-f", str(target_file)], check=True)
        else:
            # Read and display the specified number of lines
            with open(target_file, encoding="utf-8") as f:
                all_lines = f.readlines()

            if len(all_lines) <= lines:
                display_lines = all_lines
                header = f"Showing all {len(all_lines)} lines from {target_file.name}"
            else:
                display_lines = all_lines[-lines:]
                header = f"Showing last {lines} lines from {target_file.name}"

            output.print_box(header, MessageType.INFO, "Log Content")

            # Print log content with syntax highlighting
            for line in display_lines:
                console.print(line.rstrip())

    except FileNotFoundError:
        output.print_box(
            f"Log file not found: {target_file}", MessageType.ERROR, "File Not Found"
        )
    except PermissionError:
        output.print_box(
            f"Permission denied reading log file: {target_file}",
            MessageType.ERROR,
            "Permission Error",
        )
    except KeyboardInterrupt:
        if follow:
            console.print("\n[yellow]Stopped following log file.[/yellow]")
        else:
            raise
    except Exception as e:
        output.print_box(
            f"Error reading log file: {e}", MessageType.ERROR, "Read Error"
        )


def clear_logs(console: Console, output, confirm: bool = False) -> None:
    """Clear all log files.

    Args:
        console: Rich console instance
        output: Output formatter
        confirm: Whether to skip confirmation prompt
    """
    log_files = get_log_files()

    if not log_files:
        output.print_box("No log files found to clear.", MessageType.INFO, "No Logs")
        return

    if not confirm:
        # Show what will be deleted
        output.print_box(
            f"This will delete {len(log_files)} log file(s):\n"
            + "\n".join(f"• {f.name}" for f in log_files),
            MessageType.WARNING,
            "Confirm Deletion",
        )

        if not typer.confirm("Are you sure you want to delete all log files?"):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

    # Delete log files
    deleted_count = 0
    errors = []

    for log_file in log_files:
        try:
            log_file.unlink()
            deleted_count += 1
        except Exception as e:
            errors.append(f"{log_file.name}: {e}")

    if errors:
        error_msg = (
            f"Deleted {deleted_count} files, but encountered errors:\n"
            + "\n".join(f"• {error}" for error in errors)
        )
        output.print_box(error_msg, MessageType.WARNING, "Partial Success")
    else:
        output.print_box(
            f"Successfully deleted {deleted_count} log file(s).",
            MessageType.SUCCESS,
            "Logs Cleared",
        )


def show_log_config(console: Console, output) -> None:
    """Show current logging configuration."""
    try:
        config = get_config()
        log_dir = get_log_directory()

        config_info = f"""Log Level: {config.log_level}
Log Directory: {log_dir}
Log File Pattern: automake_YYYY-MM-DD_PID.log
Cleanup: Startup-based (7 days retention)
Retention: 7 days
Format: %(asctime)s - %(name)s - %(levelname)s - %(message)s"""

        output.print_box(config_info, MessageType.INFO, "Logging Configuration")

    except Exception as e:
        output.print_box(
            f"Error reading logging configuration: {e}",
            MessageType.ERROR,
            "Configuration Error",
        )
