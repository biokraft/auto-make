#!/usr/bin/env python3

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, ".")

from typer.testing import CliRunner

from automake.cli.app import app

runner = CliRunner()
test_command = "deploy the application to staging environment"
makefile_content = "all:\n\techo 'Hello World'"

with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = Path(temp_dir)
    makefile_path = temp_path / "Makefile"
    makefile_path.write_text(makefile_content)

    with (
        patch("automake.config.get_config") as mock_get_config,
        patch("automake.logging.setup_logging") as mock_setup_logging,
        patch("automake.logging.get_logger") as mock_get_logger,
        patch("automake.logging.log_config_info") as mock_log_config_info,
        patch("automake.logging.log_command_execution") as mock_log_command_execution,
        patch("automake.utils.output.get_formatter") as mock_get_formatter,
        patch("automake.core.ai_agent.create_ai_agent") as mock_create_agent,
        patch("automake.core.command_runner.CommandRunner") as mock_runner,
        patch("automake.core.makefile_reader.Path.cwd", return_value=temp_path),
    ):
        # Mock config
        mock_config = MagicMock()
        mock_config.interactive_threshold = 70
        mock_get_config.return_value = mock_config

        # Mock logging
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger
        mock_get_logger.return_value = mock_logger

        # Mock output formatter
        mock_formatter = MagicMock()
        mock_live_box = MagicMock()
        mock_formatter.live_box.return_value.__enter__.return_value = mock_live_box
        mock_formatter.live_box.return_value.__exit__.return_value = None
        mock_formatter.ai_thinking_box.return_value.__enter__.return_value = (
            mock_live_box
        )
        mock_formatter.ai_thinking_box.return_value.__exit__.return_value = None
        mock_formatter.command_execution_box.return_value.__enter__.return_value = (
            mock_live_box
        )
        mock_formatter.command_execution_box.return_value.__exit__.return_value = None
        mock_formatter.print_ai_reasoning_streaming = MagicMock()
        mock_formatter.print_command_chosen_animated = MagicMock()
        mock_get_formatter.return_value = mock_formatter

        # Mock AI agent response
        mock_agent = MagicMock()
        mock_response = MagicMock()
        mock_response.reasoning = "The user wants to deploy"
        mock_response.command = "all"
        mock_response.confidence = 85
        mock_response.alternatives = []
        mock_agent.interpret_command.return_value = mock_response
        mock_create_agent.return_value = (mock_agent, False)

        # Mock command runner
        mock_runner_instance = MagicMock()
        mock_runner.return_value = mock_runner_instance

        result = runner.invoke(app, ["run", test_command])

print(f"Exit code: {result.exit_code}")
print(f"Output: {result.output}")
print(f"Exception: {result.exception}")
if result.exception:
    import traceback

    traceback.print_exception(
        type(result.exception), result.exception, result.exception.__traceback__
    )
