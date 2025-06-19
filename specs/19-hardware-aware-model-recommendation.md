# 19. Hardware-Aware Model Recommendation
## Purpose
To simplify the initial setup for users by automatically detecting their hardware capabilities and recommending the most powerful Ollama model their machine can comfortably run. This avoids manual configuration and ensures an optimal out-of-the-box experience.

## Functional Requirements
1.  **Post-`init` Hook**: After the standard `automake init` process successfully completes (Ollama is installed, running, and a default model is available), a new step will be initiated.
2.  **User Consent Prompt**: The user will be prompted with a clear question: `Would you like me to analyze your hardware and recommend the best model for your system? (y/N)`.
3.  **Hardware Analysis**:
    - If the user consents, the system will inspect the local hardware to determine:
        - Total system RAM (in GB).
        - Total VRAM of available GPUs (if any, in GB).
    - The analysis must be non-invasive and run quickly.
4.  **Model Selection Logic**:
    - A predefined mapping will be used to select the best model based on the detected VRAM and RAM. The logic prioritizes VRAM first, as it's the primary constraint for larger models.
    - **Tiering Example:**
      | VRAM       | RAM        | Recommended Model      |
      |------------|------------|------------------------|
      | > 32 GB    | > 32 GB    | `llama3:70b`           |
      | > 16 GB    | > 16 GB    | `llama3:13b`           |
      | > 8 GB     | > 8 GB     | `llama3:8b`            |
      | > 4 GB     | > 4 GB     | `gemma:7b`             |
      | (any)      | (any)      | `gemma:2b`             |
5.  **Slot Machine Animation**:
    - **Visual Design**: The animation will be displayed inside a `rich.panel.Panel` to match the tool's existing aesthetic. It will feature a single "reel" that cycles through model names. The panel's border color will transition from blue (info) during the fast spin to green (success) as it slows to reveal the result. Unicode characters (e.g., `🎰`) and consistent typography will be used to enhance the visual appeal.
    - **Animation Logic**: The animation will run for a configurable duration (e.g., 3 seconds). It will start with a rapid, random cycling of model names. In the final phase, the animation will visibly slow down, increasing anticipation before "landing" on the final recommended model. The animation speed will be controlled by adjusting the `time.sleep()` interval between frames.
    - **Dynamic Model List**: The list of models displayed in the animation will be sourced from a configurable list in `automake.config.defaults` to allow for easy future updates without code changes.
6.  **Revealing the Choice**:
    - Once the analysis is complete, the slot machine animation will conclude by displaying the chosen model clearly within the panel. A brief pause will follow to ensure the user registers the result.
7.  **Configuration Update**:
    - The system will then ask for final confirmation from the user to pull the model and update the configuration.
    - Upon confirmation, the chosen model will be pulled via `ollama pull`, and the `ollama_model` key in the user's `config.toml` will be updated.

## Non-functional Requirements / Constraints
- **Cross-Platform**: Hardware detection must work reliably on macOS, Windows, and Linux.
- **Performance**: The analysis should complete within a few seconds.
- **Graceful Failure**: If hardware information cannot be determined, the process should inform the user and exit gracefully without changing the existing configuration.
- **Dependencies**: The feature should use lightweight, cross-platform libraries like `psutil` for hardware detection.

## Architecture & Data Flow
1.  **Trigger**: `automake.cli.commands.init.init_command()` will invoke the hardware recommendation flow after its primary checks.
2.  **Hardware Detection Module**: A new utility, `automake.utils.hardware_profiler`, will be created to abstract the platform-specific logic for fetching RAM and VRAM.
3.  **UI Component**: The slot machine animation will be implemented as a new method within the `automake.utils.output.formatter.OutputFormatter` class. This ensures it inherits the existing `rich.console.Console` instance and aligns with current UI management patterns. It will leverage `rich.live.Live` for efficient, non-blocking terminal updates.
4.  **Configuration**: The model recommendation tiers and the list of models for the animation will be stored in `automake.config.defaults` to be easily accessible and modifiable.
5.  **Config Manager**: `automake.config.manager.set_config_value()` will be used to persist the new model name.

## Implementation Notes
- Hardware detection will use `psutil.virtual_memory().total` for RAM and platform-specific commands like `nvidia-smi` (with graceful fallbacks) for VRAM.
- The animation will be implemented within a `with Live(...)` context manager. The renderable function will generate a `Panel` containing the current model name.
- The animation sequence will be controlled by a `while` loop that tracks elapsed time. The `time.sleep()` duration between frames will be increased dynamically during the "slow down" phase.
- To ensure design consistency, the animation will reuse colors and styles defined in `automake.utils.output.types.MessageType`.

## Acceptance Criteria
- Running `automake init` on a fresh setup prompts the user for hardware analysis.
- Consenting (yes) triggers the slot machine animation.
- The animation resolves to a model appropriate for the user's hardware.
- The `config.toml` file is updated with the new model name after user confirmation.
- Declining (no) or failing to detect hardware gracefully exits the flow.

## Future Considerations
- **Advanced Hardware Profiling**: Incorporate CPU core count and architecture into the model selection logic.
- **Cloud/API Providers**: Extend the logic to recommend models from other providers (e.g., Anthropic, OpenAI) if the user has configured API keys.
