"""Model selection utility for interactive Ollama model configuration.

This module provides the ModelSelector class for handling interactive
model selection with both local and online model options.
"""

import questionary

from ..config import Config
from .ollama_manager import get_available_models


class ModelSelectorError(Exception):
    """Raised when there's an error during model selection."""

    pass


class ModelSelector:
    """Handles interactive model selection for Ollama configuration."""

    def __init__(self, config: Config):
        """Initialize the model selector.

        Args:
            config: Configuration object containing Ollama settings
        """
        self.config = config
        self.base_url = config.ollama_base_url

    def get_local_models(self) -> list[str]:
        """Get list of locally available models from Ollama.

        Returns:
            List of available model names

        Raises:
            ModelSelectorError: If unable to retrieve local models
        """
        try:
            return get_available_models(self.base_url)
        except Exception as e:
            raise ModelSelectorError(f"Failed to retrieve local models: {e}") from e

    def get_popular_models(self) -> list[str]:
        """Get list of popular Ollama models with descriptions.

        Returns:
            List of popular model names with descriptions
        """
        popular_models = [
            "llama3.2:3b",
            "llama3.2:1b",
            "mistral:7b",
            "phi3:mini",
            "codellama:7b",
            "gemma2:2b",
            "qwen2:7b",
            "deepseek-coder:6.7b",
            "nomic-embed-text",
            "llava:7b",
        ]
        return popular_models

    def format_model_info(self, model_name: str, description: str) -> str:
        """Format model name and description for display.

        Args:
            model_name: Name of the model
            description: Description of the model

        Returns:
            Formatted string for display
        """
        return f"{model_name} - {description}"

    def _format_model_info(self, model_name: str, description: str = None) -> str:
        """Format model name and description for display (private method).

        Args:
            model_name: Name of the model
            description: Description of the model (optional)

        Returns:
            Formatted string for display
        """
        if description:
            return f"{model_name} - {description}"
        return model_name

    def get_popular_models_with_descriptions(self) -> list[str]:
        """Get popular models with their descriptions formatted for display.

        Returns:
            List of formatted model choices
        """
        model_descriptions = {
            "llama3.2:3b": "Meta's Llama 3.2 3B - Efficient general-purpose model",
            "llama3.2:1b": "Meta's Llama 3.2 1B - Lightweight general-purpose model",
            "mistral:7b": "Mistral 7B - High-quality general-purpose model",
            "phi3:mini": "Microsoft Phi-3 Mini - Compact but capable model",
            "codellama:7b": "Code Llama 7B - Specialized for code generation",
            "gemma2:2b": "Google Gemma 2 2B - Efficient and capable",
            "qwen2:7b": "Alibaba Qwen2 7B - Multilingual capabilities",
            "deepseek-coder:6.7b": "DeepSeek Coder - Advanced code understanding",
            "nomic-embed-text": "Nomic Embed - Text embedding model",
            "llava:7b": "LLaVA 7B - Vision and language model",
        }

        formatted_choices = []
        for model in self.get_popular_models():
            description = model_descriptions.get(model, "Popular model")
            formatted_choices.append(self.format_model_info(model, description))

        return formatted_choices

    def select_model(self) -> str:
        """Present interactive model selection UI.

        Returns:
            Selected model name, or None if cancelled

        Raises:
            ModelSelectorError: If model selection fails or is cancelled
        """
        try:
            # Get local models
            local_models = self.get_local_models()

            # Prepare choices
            choices = local_models.copy()
            choices.append("Search for a new model online...")

            # Present selection UI
            selection = questionary.select("Select a model:", choices=choices).ask()

            if selection is None:
                return None

            if selection == "Search for a new model online...":
                return self.search_online_models()
            else:
                return selection

        except KeyboardInterrupt:
            raise ModelSelectorError("Model selection cancelled by user") from None

    def search_online_models(self) -> str:
        """Search for models online with popular suggestions.

        Returns:
            Selected model name from search or manual input, or None if cancelled/empty

        Raises:
            ModelSelectorError: If search fails or is cancelled
        """
        try:
            # Get popular models with descriptions
            popular_choices = self.get_popular_models_with_descriptions()

            # Add manual entry option
            popular_choices.append("✏️ Enter model name manually...")

            # Present popular models selection
            selection = questionary.select(
                "Choose from popular models or enter manually:", choices=popular_choices
            ).ask()

            if selection is None:
                return None

            if selection == "✏️ Enter model name manually...":
                # Manual input fallback
                model_name = questionary.text(
                    "Enter the model name (e.g., 'llama3.2:3b', 'mistral:7b'):"
                ).ask()

                # Handle empty or whitespace-only input
                if not model_name or not model_name.strip():
                    return None

                return model_name.strip()
            else:
                # Extract model name from formatted choice (before the " - " separator)
                if " - " in selection:
                    model_name = selection.split(" - ")[0]
                else:
                    # Handle unexpected selection format gracefully
                    return None
                return model_name

        except KeyboardInterrupt:
            return None

    def update_config(self, model: str) -> None:
        """Update the configuration with the selected model.

        Args:
            model: The model name to set in configuration

        Raises:
            ModelSelectorError: If configuration update fails
        """
        try:
            self.config.set("ollama", "model", model)
        except Exception as e:
            raise ModelSelectorError(f"Failed to update configuration: {e}") from e
