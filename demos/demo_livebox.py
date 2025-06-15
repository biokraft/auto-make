#!/usr/bin/env python3
"""Demonstration script for the LiveBox component.

This script shows how to use the LiveBox for real-time streaming output,
simulating AI model token streaming and other dynamic content updates.
"""

import time

from rich.console import Console

from automake.utils.output import MessageType, OutputFormatter


def demo_basic_livebox() -> None:
    """Demonstrate basic LiveBox functionality."""
    console = Console()
    formatter = OutputFormatter(console)

    console.print("\n[bold blue]Demo 1: Basic LiveBox with streaming text[/bold blue]")

    with formatter.live_box("AI Token Stream", MessageType.INFO) as live_box:
        # Simulate streaming AI tokens
        tokens = [
            "I",
            " understand",
            " that",
            " you",
            " want",
            " to",
            " build",
            " the",
            " project.",
            " Let",
            " me",
            " help",
            " you",
            " with",
            " that.",
            " I'll",
            " run",
            " the",
            " appropriate",
            " make",
            " command",
            " for",
            " building",
            "...",
        ]

        for token in tokens:
            live_box.append_text(token)
            time.sleep(0.1)  # Simulate streaming delay

    console.print("[green]✅ Streaming complete![/green]\n")


def demo_different_message_types() -> None:
    """Demonstrate LiveBox with different message types."""
    console = Console()
    formatter = OutputFormatter(console)

    console.print("[bold blue]Demo 2: Different message types[/bold blue]")

    # Info type
    with formatter.live_box("Processing", MessageType.INFO) as live_box:
        for i in range(1, 6):
            live_box.update(f"Processing step {i}/5...")
            time.sleep(0.3)

    # Success type
    with formatter.live_box("Success", MessageType.SUCCESS) as live_box:
        live_box.update("✅ All steps completed successfully!")
        time.sleep(1)

    # Warning type
    with formatter.live_box("Warning", MessageType.WARNING) as live_box:
        live_box.update("⚠️ Some warnings were encountered during processing")
        time.sleep(1)

    # Error type
    with formatter.live_box("Error", MessageType.ERROR) as live_box:
        live_box.update("❌ An error occurred during the operation")
        time.sleep(1)

    console.print("[green]✅ Message type demo complete![/green]\n")


def demo_dynamic_title_updates() -> None:
    """Demonstrate dynamic title updates."""
    console = Console()
    formatter = OutputFormatter(console)

    console.print("[bold blue]Demo 3: Dynamic title updates[/bold blue]")

    with formatter.live_box("Initializing", MessageType.INFO) as live_box:
        live_box.update("Starting process...")
        time.sleep(1)

        live_box.set_title("Downloading")
        live_box.update("Downloading dependencies...")
        time.sleep(1)

        live_box.set_title("Building")
        live_box.update("Compiling source code...")
        time.sleep(1)

        live_box.set_title("Testing")
        live_box.update("Running test suite...")
        time.sleep(1)

        live_box.set_title("Complete")
        live_box.update("✅ All operations completed successfully!")
        time.sleep(1)

    console.print("[green]✅ Dynamic title demo complete![/green]\n")


def demo_concurrent_updates() -> None:
    """Demonstrate thread-safe concurrent updates."""
    import threading

    console = Console()
    formatter = OutputFormatter(console)

    console.print("[bold blue]Demo 4: Concurrent updates (thread safety)[/bold blue]")

    with formatter.live_box("Multi-threaded Processing", MessageType.INFO) as live_box:
        live_box.update("Starting concurrent operations...\n")

        def worker(worker_id: int) -> None:
            for i in range(5):
                live_box.append_text(f"Worker {worker_id}: Step {i + 1}\n")
                time.sleep(0.2)

        # Start multiple worker threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i + 1,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        live_box.append_text("\n✅ All workers completed!")
        time.sleep(1)

    console.print("[green]✅ Concurrent updates demo complete![/green]\n")


def demo_non_transient_box() -> None:
    """Demonstrate non-transient LiveBox that persists after completion."""
    console = Console()
    formatter = OutputFormatter(console)

    console.print(
        "[bold blue]Demo 5: Non-transient box (persists after completion)[/bold blue]"
    )

    with formatter.live_box(
        "Persistent Output", MessageType.SUCCESS, transient=False
    ) as live_box:
        live_box.update("This box will remain visible after completion...")
        time.sleep(2)
        live_box.update("This box will remain visible after completion...\n✅ Done!")
        time.sleep(1)

    console.print("Notice how the box above remains visible!\n")


def main() -> None:
    """Run all LiveBox demonstrations."""
    console = Console()

    console.print(
        "[bold magenta]🎭 AutoMake LiveBox Component Demonstration[/bold magenta]"
    )
    console.print("This demo showcases the real-time streaming output capabilities.\n")

    try:
        demo_basic_livebox()
        demo_different_message_types()
        demo_dynamic_title_updates()
        demo_concurrent_updates()
        demo_non_transient_box()

        console.print(
            "[bold green]🎉 All demonstrations completed successfully![/bold green]"
        )
        console.print(
            "The LiveBox component is ready for integration with AI model streaming!"
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo failed with error: {e}[/red]")


if __name__ == "__main__":
    main()
