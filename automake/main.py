"""Main CLI entry point for AutoMake."""

import typer

from automake import __version__

app = typer.Typer(
    name="automake",
    help="AI-powered Makefile command execution",
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"AutoMake version {__version__}")
        raise typer.Exit()


@app.command()
def main(
    command: str = typer.Argument(
        ...,
        help="Natural language command to execute",
        metavar="COMMAND",
    ),
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """Execute a natural language command using AI to interpret Makefile targets.

    Examples:
        automake "build the project"
        automake "run all tests"
        automake "deploy to staging"
    """
    # TODO: This is a placeholder implementation for Phase 1
    # The actual AI integration will be implemented in later phases
    typer.echo(f"🤖 AutoMake received command: {command}")
    typer.echo("⚠️  AI integration not yet implemented (Phase 1 complete)")
    typer.echo("📋 This will be implemented in Phase 6 (Smolagent Core)")


if __name__ == "__main__":
    app()
