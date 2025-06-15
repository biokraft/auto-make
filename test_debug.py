"""Debug test for CLI argument parsing."""

from typer.testing import CliRunner

from automake.cli.app import app


def test_cli_parsing():
    """Test CLI argument parsing."""
    runner = CliRunner()

    print("Testing agent command help...")
    result = runner.invoke(app, ["agent", "--help"])
    print(f"Help exit code: {result.exit_code}")
    print(f"Help output: {result.output}")

    print("\nTesting agent command with prompt...")
    result = runner.invoke(app, ["agent", "test prompt"], catch_exceptions=False)
    print(f"Agent exit code: {result.exit_code}")
    print(f"Agent output: {result.output}")
    if result.exception:
        print(f"Exception: {result.exception}")
        import traceback

        traceback.print_exception(
            type(result.exception), result.exception, result.exception.__traceback__
        )


if __name__ == "__main__":
    test_cli_parsing()
