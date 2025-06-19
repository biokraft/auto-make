"""Init command implementation for AutoMake CLI.

This module contains the initialization functionality for AutoMake.
"""

import subprocess

import typer

from automake.config import get_config
from automake.utils.ollama_manager import (
    OllamaManagerError,
    get_available_models,
    is_model_available,
)
from automake.utils.output import MessageType, get_formatter


def init_command() -> None:
    """Initialize AutoMake by ensuring Ollama and the configured model are ready."""
    output = get_formatter()
    try:
        # Load configuration
        config = get_config()

        # Use LiveBox for initialization process
        with output.live_box("AutoMake Initialization", MessageType.INFO) as init_box:
            init_box.update("🚀 Starting AutoMake initialization...")

            # Check if Ollama is installed by trying to run ollama --version
            try:
                init_box.update("🔍 Checking Ollama installation...")
                result = subprocess.run(
                    ["ollama", "--version"], capture_output=True, text=True, timeout=10
                )
                if result.returncode != 0:
                    raise FileNotFoundError("Ollama command failed")

                init_box.update("✅ Ollama installation verified")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                with output.live_box(
                    "Installation Error", MessageType.ERROR
                ) as error_box:
                    error_box.update(
                        "❌ Ollama is not installed or not available in your PATH.\n\n"
                        "💡 Hint: Please install Ollama from https://ollama.ai/ "
                        "and ensure it's in your PATH."
                    )
                raise typer.Exit(1) from None

            # Check if Ollama server is running and start if needed
            init_box.update("🔍 Checking Ollama server status...")
            try:
                # Try to get available models to test connection
                get_available_models(config.ollama_base_url)
                init_box.update("✅ Ollama server is running")
            except Exception:
                init_box.update("🚀 Starting Ollama server...")
                try:
                    # Start Ollama server in background
                    subprocess.Popen(
                        ["ollama", "serve"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    # Give it a moment to start
                    import time

                    time.sleep(2)

                    # Test connection again
                    get_available_models(config.ollama_base_url)  # noqa: F841
                    init_box.update("✅ Ollama server started successfully")
                except Exception as e:
                    with output.live_box(
                        "Server Error", MessageType.ERROR
                    ) as error_box:
                        error_box.update(
                            f"❌ Failed to start Ollama server: {e}\n\n"
                            "💡 Hint: Try running 'ollama serve' manually "
                            "in another terminal."
                        )
                    raise typer.Exit(1) from e

            # Ensure the configured model is available
            init_box.update(f"🔍 Checking model availability: {config.ollama_model}")

            # Check if model is already available
            if is_model_available(config.ollama_base_url, config.ollama_model):
                init_box.update(
                    f"✅ Model '{config.ollama_model}' is already available and ready."
                )
            else:
                # Model needs to be downloaded
                init_box.update(f"📥 Downloading model: {config.ollama_model}")

                try:
                    # Use subprocess to pull the model with better progress indication
                    import threading
                    import time

                    # Start the ollama pull process
                    process = subprocess.Popen(
                        ["ollama", "pull", config.ollama_model],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        universal_newlines=True,
                    )

                    # Show progress animation while downloading
                    def show_progress():
                        dots = 0
                        while process.poll() is None:
                            dots = (dots + 1) % 4
                            progress_text = (
                                "📥 Downloading model: " + "." * dots + " " * (3 - dots)
                            )
                            init_box.update(
                                f"🔍 Checking model availability: {config.ollama_model}\n\n"  # noqa: E501
                                f"{progress_text}\n\n"
                                "💡 This may take several minutes for large models..."
                            )
                            time.sleep(0.5)

                    # Start progress animation in background
                    progress_thread = threading.Thread(
                        target=show_progress, daemon=True
                    )
                    progress_thread.start()

                    # Wait for the process to complete
                    stdout, stderr = process.communicate()

                    if process.returncode == 0:
                        init_box.update(
                            f"✅ Model '{config.ollama_model}' has been downloaded and is now ready."  # noqa: E501
                        )
                    else:
                        raise subprocess.CalledProcessError(
                            process.returncode, "ollama pull", stderr
                        )

                except subprocess.CalledProcessError as e:
                    with output.live_box(
                        "Model Pull Error", MessageType.ERROR
                    ) as error_box:
                        error_box.update(
                            f"❌ Failed to pull model '{config.ollama_model}': {e.stderr}\n\n"  # noqa: E501
                            f"💡 Hint: Check if '{config.ollama_model}' is a valid model name. "  # noqa: E501
                            f"You can see available models at https://ollama.ai/library"
                        )
                    raise typer.Exit(1) from e
                except Exception as e:
                    with output.live_box(
                        "Download Error", MessageType.ERROR
                    ) as error_box:
                        error_box.update(
                            f"❌ Unexpected error during model download: {e}\n\n"
                            f"💡 Hint: Try running 'ollama pull {config.ollama_model}' manually."  # noqa: E501
                        )
                    raise typer.Exit(1) from e

            # Show available models
            try:
                init_box.update("📋 Fetching available models...")
                available_models = get_available_models(config.ollama_base_url)
                if available_models:
                    models_text = "Available models:\n" + "\n".join(
                        f"• {model}" for model in available_models[:10]
                    )
                    if len(available_models) > 10:
                        models_text += f"\n... and {len(available_models) - 10} more"

                    init_box.update(models_text)
            except Exception:
                # Don't fail if we can't list models, the main goal is achieved
                init_box.update("⚠️ Could not fetch available models list")

        # Final success message with LiveBox
        with output.live_box("Ready", MessageType.SUCCESS) as success_box:
            success_box.update(
                "🎉 AutoMake is ready to use!\n\n"
                'Try running: automake run "your command here"'
            )

    except OllamaManagerError as e:
        if "not installed" in str(e).lower() or "not found" in str(e).lower():
            with output.live_box("Installation Error", MessageType.ERROR) as error_box:
                error_box.update(
                    "❌ Ollama is not installed or not available in your "
                    "PATH.\n\n"
                    "💡 Hint: Please install Ollama from https://ollama.ai/ "
                    "and ensure it's in your PATH."
                )
        elif "Connection" in str(e) or "connect" in str(e).lower():
            with output.live_box("Connection Error", MessageType.ERROR) as error_box:
                error_box.update(
                    f"❌ Could not connect to Ollama server at "
                    f"{config.ollama_base_url}.\n\n"
                    "💡 Hint: Make sure Ollama is running. Try: ollama serve"
                )
        elif "pull" in str(e).lower() or "model" in str(e).lower():
            with output.live_box("Model Error", MessageType.ERROR) as error_box:
                error_box.update(
                    f"❌ Failed to pull model '{config.ollama_model}': {e}\n\n"
                    f"💡 Hint: Check if '{config.ollama_model}' is a valid "
                    f"model name. You can see available models at "
                    f"https://ollama.ai/library"
                )
        else:
            with output.live_box(
                "Initialization Error", MessageType.ERROR
            ) as error_box:
                error_box.update(
                    f"❌ Initialization failed: {e}\n\n"
                    "💡 Hint: Check your Ollama setup and configuration."
                )
        raise typer.Exit(1) from e
    except Exception as e:
        with output.live_box("Unexpected Error", MessageType.ERROR) as error_box:
            error_box.update(
                f"❌ An unexpected error occurred during initialization: {e}"
            )
        raise typer.Exit(1) from e
