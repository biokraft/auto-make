"""Debug test for init_command directly."""

from unittest.mock import MagicMock, patch


def test_direct_init():
    """Test calling init_command directly."""
    print("Starting direct test...")

    with (
        patch("automake.cli.commands.init.get_config") as mock_get_config,
        patch("automake.utils.output.get_formatter") as mock_get_formatter,
        patch("subprocess.run") as mock_run,
        patch("automake.cli.commands.init.ensure_model_available") as mock_ensure_model,
        patch("automake.cli.commands.init.get_available_models") as mock_get_models,
    ):
        # Setup mocks
        mock_config = MagicMock()
        mock_config.ollama_base_url = "http://localhost:11434"
        mock_config.ollama_model = "llama2"
        mock_get_config.return_value = mock_config

        mock_formatter = MagicMock()
        mock_live_box = MagicMock()
        mock_formatter.live_box.return_value.__enter__.return_value = mock_live_box
        mock_formatter.live_box.return_value.__exit__.return_value = None
        mock_get_formatter.return_value = mock_formatter

        mock_run.return_value = MagicMock(returncode=0, stdout="ollama version 0.1.0")
        mock_ensure_model.return_value = (True, False)  # Available, not pulled
        mock_get_models.return_value = ["llama2", "codellama"]

        print("About to import init_command...")
        from automake.cli.commands.init import init_command

        print("About to call init_command...")
        try:
            init_command()
            print("init_command completed successfully")
        except Exception as e:
            print(f"init_command failed with: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_direct_init()
