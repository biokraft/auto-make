"""Tests for Phase 1 agent implementation.

This module tests the core agent functionality including:
- Manager agent creation and initialization
- Specialist agent tools
- CLI integration with agent commands
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from automake.agent.manager import ManagerAgentRunner, create_manager_agent
from automake.agent.specialists import (
    coding_agent,
    edit_file,
    filesystem_agent,
    get_makefile_targets,
    list_directory,
    makefile_agent,
    python_interpreter,
    read_file,
    run_makefile_target,
    run_shell_command,
    terminal_agent,
    web_agent,
)
from automake.cli.app import app
from automake.config import Config


def create_test_config():
    """Create a test configuration instance."""
    temp_dir = Path(tempfile.mkdtemp())
    config = Config(config_dir=temp_dir)
    return config


class TestSpecialistAgentTools:
    """Test the individual tools used by specialist agents."""

    def test_list_directory_current(self):
        """Test listing current directory."""
        result = list_directory(".")
        assert "Contents of '.'" in result
        assert "[DIR]" in result or "[FILE]" in result

    def test_list_directory_nonexistent(self):
        """Test listing non-existent directory."""
        result = list_directory("/nonexistent/path")
        assert "ERROR: Directory does not exist" in result

    def test_read_file_success(self):
        """Test reading a file successfully."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Hello, World!")
            temp_path = f.name

        try:
            result = read_file(temp_path)
            assert result == "Hello, World!"
        finally:
            Path(temp_path).unlink()

    def test_read_file_nonexistent(self):
        """Test reading non-existent file."""
        result = read_file("/nonexistent/file.txt")
        assert "ERROR: File does not exist" in result

    def test_edit_file_success(self):
        """Test editing a file successfully."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_path = f.name

        try:
            result = edit_file(temp_path, "New content")
            assert "SUCCESS" in result

            # Verify the content was written
            content = Path(temp_path).read_text()
            assert content == "New content"
        finally:
            Path(temp_path).unlink()

    def test_run_shell_command_success(self):
        """Test running a successful shell command."""
        result = run_shell_command("echo 'Hello, World!'")
        assert "Hello, World!" in result
        assert "Return code: 0" in result

    def test_run_shell_command_failure(self):
        """Test running a failing shell command."""
        result = run_shell_command("false")  # Command that always fails
        assert "Return code: 1" in result

    @patch("subprocess.run")
    def test_python_interpreter_success(self, mock_run):
        """Test Python interpreter with successful execution."""
        # Mock the subprocess calls for uv venv creation and python execution
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # uv venv
            Mock(
                returncode=0, stdout="Hello from Python!", stderr=""
            ),  # python execution
        ]

        with (
            patch("tempfile.mkdtemp") as mock_mkdtemp,
            patch("shutil.rmtree") as mock_rmtree,
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.write_text"),
            patch("os.path.exists", return_value=True),
        ):
            mock_mkdtemp.return_value = "/tmp/test_dir"

            result = python_interpreter("print('Hello from Python!')")

            assert "Hello from Python!" in result
            assert "Return code: 0" in result
            mock_rmtree.assert_called_once()

    @patch("subprocess.run")
    def test_python_interpreter_with_dependencies(self, mock_run):
        """Test Python interpreter with dependencies."""
        # Mock the subprocess calls
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # uv venv
            Mock(returncode=0, stdout="", stderr=""),  # pip install requests
            Mock(
                returncode=0, stdout="Requests installed!", stderr=""
            ),  # python execution
        ]

        with (
            patch("tempfile.mkdtemp") as mock_mkdtemp,
            patch("shutil.rmtree"),
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.write_text"),
            patch("os.path.exists", return_value=True),
        ):
            mock_mkdtemp.return_value = "/tmp/test_dir"

            result = python_interpreter("print('Requests installed!')", ["requests"])

            assert "Requests installed!" in result
            assert "Return code: 0" in result
            # Should have called uv venv, pip install, and python execution
            assert mock_run.call_count == 3

    @patch("automake.agent.specialists.MakefileReader")
    def test_get_makefile_targets_success(self, mock_reader_class):
        """Test getting Makefile targets successfully."""
        mock_reader = Mock()
        mock_reader.targets_with_descriptions = {
            "build": "Build the application",
            "test": "Run all tests",
            "clean": "",
        }
        mock_reader_class.return_value = mock_reader

        result = get_makefile_targets()

        assert "Available Makefile targets:" in result
        assert "build: Build the application" in result
        assert "test: Run all tests" in result
        assert "clean: (no description)" in result

    @patch("automake.agent.specialists.MakefileReader")
    @patch("subprocess.run")
    def test_run_makefile_target_success(self, mock_run, mock_reader_class):
        """Test running a Makefile target successfully."""
        # Mock the MakefileReader
        mock_reader = Mock()
        mock_reader.targets_with_descriptions = {"build": "Build the project"}
        mock_reader_class.return_value = mock_reader

        # Mock the subprocess run
        mock_run.return_value = Mock(
            returncode=0, stdout="Build successful!", stderr=""
        )

        result = run_makefile_target("build")

        assert "Build successful!" in result
        assert "Return code: 0" in result
        mock_run.assert_called_once()

    @patch("automake.agent.specialists.MakefileReader")
    def test_run_makefile_target_not_found(self, mock_reader_class):
        """Test running a non-existent Makefile target."""
        mock_reader = Mock()
        mock_reader.targets_with_descriptions = {"build": "Build the application"}
        mock_reader_class.return_value = mock_reader

        result = run_makefile_target("nonexistent")

        assert "ERROR: Target 'nonexistent' not found" in result
        assert "Available targets: ['build']" in result


class TestSpecialistAgents:
    """Test the specialist agent instances."""

    def test_terminal_agent_structure(self):
        """Test terminal agent has correct structure."""
        assert terminal_agent.name == "terminal_agent"
        assert "shell commands" in terminal_agent.description
        assert len(terminal_agent.tools) == 2  # run_shell_command, list_directory

    def test_coding_agent_structure(self):
        """Test coding agent has correct structure."""
        assert coding_agent.name == "coding_agent"
        assert (
            "Execute Python code with dependency management" == coding_agent.description
        )
        assert len(coding_agent.tools) == 1  # python_interpreter

    def test_filesystem_agent_structure(self):
        """Test filesystem agent has correct structure."""
        assert filesystem_agent.name == "filesystem_agent"
        assert (
            "Read from and write to files, explore directories"
            == filesystem_agent.description
        )
        assert len(filesystem_agent.tools) == 3  # read_file, edit_file, list_directory

    def test_makefile_agent_structure(self):
        """Test makefile agent has correct structure."""
        assert makefile_agent.name == "makefile_agent"
        assert "Makefile targets" in makefile_agent.description
        assert (
            len(makefile_agent.tools) == 2
        )  # get_makefile_targets, run_makefile_target

    def test_web_agent_structure(self):
        """Test web agent has correct structure."""
        assert web_agent.name == "web_agent"
        assert "Search the internet using DuckDuckGo" == web_agent.description
        assert len(web_agent.tools) == 1  # DuckDuckGoSearchTool


class TestManagerAgent:
    """Test the manager agent functionality."""

    @patch("automake.agent.manager.LiteLLMModel")
    @patch("automake.agent.manager.ToolCallingAgent")
    def test_create_manager_agent_success(self, mock_agent_class, mock_model_class):
        """Test successful manager agent creation."""
        config = create_test_config()

        # Mock the model and agent
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        # This test just verifies that the function can be called without errors
        # and returns the expected types
        with patch("automake.agent.manager.ensure_ollama_running") as mock_ollama:
            mock_ollama.return_value = (True, False)  # (is_running, was_started)

            agent, ollama_started = create_manager_agent(config)

            # Verify return types
            assert agent is not None
            assert isinstance(ollama_started, bool)
            assert ollama_started is False

            # Verify the model was created with correct parameters
            mock_model_class.assert_called_once_with(
                model_id=f"ollama/{config.ollama_model}",
                base_url=config.ollama_base_url,
            )

    @patch("automake.agent.manager.LiteLLMModel")
    @patch("automake.agent.manager.ToolCallingAgent")
    def test_create_manager_agent_ollama_started(
        self, mock_agent_class, mock_model_class
    ):
        """Test manager agent creation when Ollama needs to be started."""
        config = create_test_config()

        # Mock the model and agent
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        with patch("automake.agent.manager.ensure_ollama_running") as mock_ollama:
            mock_ollama.return_value = (True, True)  # (is_running, was_started)

            agent, ollama_started = create_manager_agent(config)

            # Verify return types
            assert agent is not None
            assert isinstance(ollama_started, bool)
            assert ollama_started is True

    def test_manager_agent_runner_initialization(self):
        """Test ManagerAgentRunner initialization."""
        config = create_test_config()

        runner = ManagerAgentRunner(config)

        assert runner.config == config
        assert runner.agent is None
        assert runner.ollama_was_started is False

    @patch("automake.agent.manager.create_manager_agent")
    def test_manager_agent_runner_initialize(self, mock_create):
        """Test ManagerAgentRunner initialize method."""
        mock_agent = Mock()
        mock_create.return_value = (mock_agent, True)

        config = create_test_config()

        runner = ManagerAgentRunner(config)
        ollama_started = runner.initialize()

        assert runner.agent == mock_agent
        assert ollama_started is True
        assert runner.ollama_was_started is True

    def test_manager_agent_runner_run_not_initialized(self):
        """Test ManagerAgentRunner run method when not initialized."""
        config = create_test_config()

        runner = ManagerAgentRunner(config)

        with pytest.raises(RuntimeError, match="Agent not initialized"):
            runner.run("test prompt")

    @patch("automake.agent.manager.create_manager_agent")
    def test_manager_agent_runner_run_success(self, mock_create):
        """Test ManagerAgentRunner run method success."""
        mock_agent = Mock()
        mock_agent.run.return_value = "Agent response"
        mock_create.return_value = (mock_agent, False)

        config = create_test_config()

        runner = ManagerAgentRunner(config)
        runner.initialize()

        result = runner.run("test prompt")

        assert result == "Agent response"
        mock_agent.run.assert_called_once_with("test prompt")

    @patch("automake.agent.manager.create_manager_agent")
    def test_manager_agent_runner_run_streaming(self, mock_create):
        """Test ManagerAgentRunner run method with streaming."""
        mock_agent = Mock()
        mock_agent.run.return_value = ["chunk1", "chunk2", "chunk3"]
        mock_create.return_value = (mock_agent, False)

        config = create_test_config()

        runner = ManagerAgentRunner(config)
        runner.initialize()

        result = runner.run("test prompt", stream=True)

        assert result == ["chunk1", "chunk2", "chunk3"]
        mock_agent.run.assert_called_once_with("test prompt", stream=True)


class TestCLIIntegration:
    """Test CLI integration with the agent system."""

    def test_agent_command_available(self):
        """Test that the agent command is available in the CLI."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "agent" in result.stdout

    @patch("automake.cli.commands.agent.ManagerAgentRunner")
    @patch("automake.config.get_config")
    @patch("automake.logging.setup_logging")
    @patch("automake.utils.output.get_formatter")
    @patch("automake.logging.log_command_execution")
    @patch("automake.logging.log_config_info")
    @patch("automake.logging.get_logger")
    def test_agent_command_non_interactive(
        self,
        mock_get_logger,
        mock_log_config,
        mock_log_cmd,
        mock_get_formatter,
        mock_logging,
        mock_config,
        mock_runner_class,
    ):
        """Test agent command in non-interactive mode."""
        # Setup mocks
        mock_config.return_value = Mock()
        mock_logging.return_value = Mock()
        mock_get_logger.return_value = Mock()

        # Mock the output formatter
        mock_formatter = Mock()
        mock_live_box = Mock()
        mock_live_box.__enter__ = Mock(return_value=mock_live_box)
        mock_live_box.__exit__ = Mock(return_value=None)
        mock_formatter.live_box.return_value = mock_live_box
        mock_get_formatter.return_value = mock_formatter

        mock_runner = Mock()
        mock_runner.initialize.return_value = False
        mock_runner.run.return_value = "Agent executed successfully"
        mock_runner_class.return_value = mock_runner

        runner = CliRunner()
        result = runner.invoke(app, ["agent", "test prompt"])

        assert result.exit_code == 0
        mock_runner.initialize.assert_called_once()
        mock_runner.run.assert_called_once_with("test prompt")

    @patch("automake.cli.commands.run.ManagerAgentRunner")
    @patch("automake.config.get_config")
    @patch("automake.logging.setup_logging")
    @patch("automake.utils.output.get_formatter")
    @patch("automake.logging.log_command_execution")
    @patch("automake.logging.log_config_info")
    @patch("automake.logging.get_logger")
    def test_run_command_with_agent(
        self,
        mock_get_logger,
        mock_log_config,
        mock_log_cmd,
        mock_get_formatter,
        mock_logging,
        mock_config,
        mock_runner_class,
    ):
        """Test run command using the new agent architecture."""
        # Setup mocks
        mock_config.return_value = Mock()
        mock_logging.return_value = Mock()
        mock_get_logger.return_value = Mock()

        # Mock the output formatter
        mock_formatter = Mock()
        mock_live_box = Mock()
        mock_live_box.__enter__ = Mock(return_value=mock_live_box)
        mock_live_box.__exit__ = Mock(return_value=None)
        mock_formatter.live_box.return_value = mock_live_box
        mock_get_formatter.return_value = mock_formatter

        mock_runner = Mock()
        mock_runner.initialize.return_value = False
        mock_runner.run.return_value = "Command executed successfully"
        mock_runner_class.return_value = mock_runner

        runner = CliRunner()
        result = runner.invoke(app, ["run", "build the project"])

        assert result.exit_code == 0
        mock_runner.initialize.assert_called_once()
        mock_runner.run.assert_called_once_with("build the project")

    def test_no_command_shows_help(self):
        """Test that running automake with no command shows help."""
        runner = CliRunner()
        result = runner.invoke(app, [])

        assert result.exit_code == 0
        # Check for the ASCII art banner or help text
        assert "automake" in result.stdout.lower() or "usage" in result.stdout.lower()


class TestErrorHandling:
    """Test error handling in the agent system."""

    @patch("automake.agent.manager.LiteLLMModel")
    @patch("automake.agent.manager.ToolCallingAgent")
    @patch("automake.agent.manager.ensure_ollama_running")
    def test_manager_agent_creation_failure(
        self, mock_ollama, mock_agent_class, mock_model_class
    ):
        """Test manager agent creation failure."""
        mock_ollama.side_effect = Exception("Ollama connection failed")

        config = create_test_config()

        with pytest.raises(Exception, match="Ollama connection failed"):
            create_manager_agent(config)

    @patch("automake.agent.manager.create_manager_agent")
    def test_manager_agent_runner_run_failure(self, mock_create):
        """Test ManagerAgentRunner run method failure."""
        mock_agent = Mock()
        mock_agent.run.side_effect = Exception("Agent execution failed")
        mock_create.return_value = (mock_agent, False)

        config = create_test_config()

        runner = ManagerAgentRunner(config)
        runner.initialize()

        with pytest.raises(Exception, match="Agent execution failed"):
            runner.run("test prompt")

    def test_tool_error_handling(self):
        """Test that tools handle errors gracefully."""
        # Test with invalid shell command
        result = run_shell_command("invalid_command_that_does_not_exist")
        assert "ERROR:" in result or "Return code:" in result

        # Test with invalid file path
        result = read_file("/invalid/path/file.txt")
        assert "ERROR:" in result

        # Test with invalid directory
        result = list_directory("/invalid/path")
        assert "ERROR:" in result
