#!/usr/bin/env python3
"""Comprehensive demonstration of the enhanced AutoMake UX.

This script showcases the complete user experience with LiveBox integration
throughout the AI command interpretation and execution flow.
"""

import time

from rich.console import Console

from automake.utils.output import MessageType, OutputFormatter


def demo_ai_thinking_process() -> None:
    """Demonstrate the AI thinking process with LiveBox."""
    console = Console()
    formatter = OutputFormatter(console)

    console.print("\n[bold blue]🧠 Demo: AI Command Analysis Process[/bold blue]")

    with formatter.ai_thinking_box("AI Command Analysis") as thinking_box:
        # The first message is already animated by ai_thinking_box

        thinking_box.update("🧠 Processing Makefile targets...")
        time.sleep(0.8)

        thinking_box.update("🔍 Finding best match...")
        time.sleep(0.6)

        thinking_box.update("✅ Analysis complete!")
        time.sleep(0.5)


def demo_ai_reasoning_streaming() -> None:
    """Demonstrate AI reasoning with streaming effect."""
    console = Console()
    formatter = OutputFormatter(console)

    console.print("\n[bold blue]💭 Demo: AI Reasoning Stream[/bold blue]")

    reasoning = (
        "The user wants to build the project. Looking at the available Makefile "
        "targets, I can see 'build', 'compile', and 'make-all' options. The 'build' "
        "target appears to be the most appropriate match as it directly corresponds "
        "to the user's intent and is a common convention for project compilation."
    )

    formatter.print_ai_reasoning_streaming(reasoning, 92)


def demo_command_selection_animation() -> None:
    """Demonstrate animated command selection."""
    console = Console()
    formatter = OutputFormatter(console)

    console.print("\n[bold blue]🎯 Demo: Command Selection Animation[/bold blue]")

    # High confidence command
    formatter.print_command_chosen_animated("build", 92)
    time.sleep(1.5)

    # Low confidence scenario
    formatter.print_command_chosen_animated(None, 35)


def demo_interactive_session() -> None:
    """Demonstrate interactive session introduction."""
    console = Console()
    formatter = OutputFormatter(console)

    console.print("\n[bold blue]🤝 Demo: Interactive Session Introduction[/bold blue]")

    from automake.utils.output import MessageType

    with formatter.live_box(
        "Interactive Command Selection", MessageType.WARNING
    ) as live_box:
        live_box.update("🤔 AI confidence is below threshold...")
        time.sleep(0.8)

        live_box.update(
            "🤔 AI confidence is below threshold...\n🎯 Preparing command options..."
        )
        time.sleep(0.6)

        live_box.update(
            "🤔 AI confidence is below threshold...\n"
            "🎯 Preparing command options...\n"
            "📋 Ready for your selection!"
        )
        time.sleep(1.0)


def demo_command_execution() -> None:
    """Demonstrate command execution with real-time output."""
    console = Console()
    formatter = OutputFormatter(console)

    console.print(
        "\n[bold blue]🚀 Demo: Command Execution with Live Output[/bold blue]"
    )

    with formatter.command_execution_box("build") as execution_box:
        execution_box.update("🚀 Starting execution of make build...")
        time.sleep(0.5)

        # Simulate build output
        build_steps = [
            "Checking dependencies...",
            "Compiling source files...",
            "  - main.c",
            "  - utils.c",
            "  - config.c",
            "Linking objects...",
            "Creating executable...",
            "Build completed successfully!",
        ]

        output_buffer = ""
        for step in build_steps:
            output_buffer += f"{step}\n"
            execution_box.update(
                f"🚀 Executing: make build\n\n[dim]{output_buffer}[/dim]"
            )
            time.sleep(0.4)

        # Final success message
        execution_box.update(
            f"✅ Command completed successfully: make build\n\n"
            f"[dim]{output_buffer}[/dim]"
        )
        time.sleep(1.0)


def demo_model_streaming() -> None:
    """Demonstrate AI model response streaming."""
    console = Console()
    formatter = OutputFormatter(console)

    console.print("\n[bold blue]🤖 Demo: AI Model Response Streaming[/bold blue]")

    with formatter.model_streaming_box("AI Response Generation") as streaming_box:
        streaming_box.update("🤖 Generating response...")
        time.sleep(0.5)

        # Simulate token streaming
        response_tokens = [
            "Based",
            " on",
            " your",
            " request",
            " to",
            " 'build",
            " the",
            " project',",
            " I",
            " have",
            " identified",
            " the",
            " most",
            " appropriate",
            " command",
            " from",
            " your",
            " Makefile.",
            " The",
            " 'build'",
            " target",
            " will",
            " compile",
            " all",
            " source",
            " files",
            " and",
            " create",
            " the",
            " executable.",
            " This",
            " is",
            " the",
            " standard",
            " approach",
            " for",
            " project",
            " compilation.",
        ]

        current_response = ""
        for token in response_tokens:
            current_response += token
            streaming_box.update(f"🤖 AI Response:\n\n{current_response}")
            time.sleep(0.08)

        time.sleep(1.0)


def demo_error_handling() -> None:
    """Demonstrate error handling with LiveBox."""
    console = Console()
    formatter = OutputFormatter(console)

    console.print("\n[bold blue]❌ Demo: Error Handling with LiveBox[/bold blue]")

    with formatter.command_execution_box("test") as execution_box:
        execution_box.update("🚀 Starting execution of make test...")
        time.sleep(0.5)

        execution_box.update(
            "🚀 Executing: make test\n\n"
            "[dim]Running test suite...\n"
            "test_config.py ✓\n"
            "test_utils.py ✓\n"
            "test_main.py ✗[/dim]"
        )
        time.sleep(1.0)

        # Simulate error
        execution_box.update(
            "❌ Command failed with exit code 1\n\n"
            "[red]Error: test_main.py::test_invalid_input FAILED\n"
            "AssertionError: Expected 'success' but got 'error'\n"
            "1 failed, 2 passed in 2.34s[/red]"
        )
        time.sleep(1.5)


def demo_complete_workflow() -> None:
    """Demonstrate a complete AutoMake workflow."""
    console = Console()
    formatter = OutputFormatter(console)

    console.print("\n[bold magenta]🎭 Demo: Complete AutoMake Workflow[/bold magenta]")
    console.print("Simulating: [cyan]automake run 'build the project'[/cyan]\n")

    # Step 1: Command received
    formatter.print_box(
        "Natural language command: [cyan]'build the project'[/cyan]",
        MessageType.INFO,
        "Command Received",
    )
    time.sleep(0.5)

    # Step 2: AI Analysis
    with formatter.ai_thinking_box("AI Command Analysis") as thinking_box:
        # The first message is already animated by ai_thinking_box
        thinking_box.update("🧠 Processing Makefile targets...")
        time.sleep(0.6)
        thinking_box.update("🔍 Finding best match...")
        time.sleep(0.4)

    # Step 3: AI Reasoning
    reasoning = (
        "The user wants to build the project. The 'build' target is the most "
        "appropriate match."
    )
    formatter.print_ai_reasoning_streaming(reasoning, 95)
    time.sleep(0.5)

    # Step 4: Command Selection
    formatter.print_command_chosen_animated("build", 95)
    time.sleep(0.5)

    # Step 5: Execution
    with formatter.command_execution_box("build") as execution_box:
        execution_box.update("🚀 Starting execution of make build...")
        time.sleep(0.3)

        steps = ["Compiling...", "Linking...", "Success!"]
        output = ""
        for step in steps:
            output += f"{step}\n"
            execution_box.update(f"🚀 Executing: make build\n\n[dim]{output}[/dim]")
            time.sleep(0.5)

        execution_box.update(
            f"✅ Command completed successfully: make build\n\n[dim]{output}[/dim]"
        )
        time.sleep(1.0)

    formatter.print_box(
        "Project built successfully! 🎉", MessageType.SUCCESS, "Workflow Complete"
    )


def main() -> None:
    """Run all UX demonstrations."""
    console = Console()

    console.print("[bold magenta]🎨 AutoMake Enhanced UX Demonstration[/bold magenta]")
    console.print("Showcasing the beautiful new LiveBox-powered user experience!\n")

    try:
        demo_ai_thinking_process()
        time.sleep(1)

        demo_ai_reasoning_streaming()
        time.sleep(1)

        demo_command_selection_animation()
        time.sleep(1)

        demo_interactive_session()
        time.sleep(1)

        demo_command_execution()
        time.sleep(1)

        demo_model_streaming()
        time.sleep(1)

        demo_error_handling()
        time.sleep(1)

        demo_complete_workflow()

        console.print("\n[bold green]🎉 All UX demonstrations completed![/bold green]")
        console.print("The enhanced AutoMake experience is ready for users! ✨")

    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user.[/yellow]")


if __name__ == "__main__":
    main()
