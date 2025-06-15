"""Pytest configuration file with timeout and performance monitoring."""

import time
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_config():
    """Fixture for a mock Config object."""
    config = MagicMock()
    config.ollama_base_url = "http://localhost:11434"
    config.ollama_model = "qwen3:0.6b"
    config.interactive_threshold = 90
    return config


def pytest_configure(config):
    """Configure pytest with custom timeout behavior."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "timeout(seconds): set a custom timeout for a test"
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """Monitor test execution time and collect performance data."""
    start_time = time.time()

    # Execute the test
    outcome = yield

    # Calculate duration
    duration = time.time() - start_time

    # Store duration for reporting
    item._test_duration = duration

    # Immediate warning for slow tests (but not timed out ones)
    if duration > 2.0 and not outcome.excinfo:
        print(f"\n⚠️  SLOW TEST WARNING: '{item.name}' took {duration:.2f}s")


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Enhanced terminal summary with performance insights."""
    # Collect timing data from all test reports
    slow_tests = []
    timeout_tests = []

    for phase in ["passed", "failed", "error"]:
        if phase in terminalreporter.stats:
            for report in terminalreporter.stats[phase]:
                if hasattr(report, "duration"):
                    if report.duration > 2.0:
                        slow_tests.append((report.nodeid, report.duration, phase))

                    # Check if it was a timeout failure
                    if (
                        hasattr(report, "longrepr")
                        and report.longrepr
                        and "timeout" in str(report.longrepr).lower()
                    ):
                        timeout_tests.append((report.nodeid, report.duration))

    # Report slow tests
    if slow_tests:
        terminalreporter.write_sep("=", "⚠️  PERFORMANCE WARNINGS", yellow=True)
        terminalreporter.write_line("The following tests took longer than 2 seconds:")
        terminalreporter.write_line("")

        for nodeid, duration, phase in sorted(
            slow_tests, key=lambda x: x[1], reverse=True
        ):
            status_emoji = {"passed": "✅", "failed": "❌", "error": "💥"}.get(
                phase, "❓"
            )
            terminalreporter.write_line(f"  {status_emoji} {nodeid}: {duration:.2f}s")

        terminalreporter.write_line("")
        terminalreporter.write_line("💡 Consider:")
        terminalreporter.write_line("   • Optimizing these tests")
        terminalreporter.write_line("   • Marking them with @pytest.mark.slow")
        terminalreporter.write_line("   • Using mocks for external dependencies")
        terminalreporter.write_line("")

    # Report timeout failures
    if timeout_tests:
        terminalreporter.write_sep("=", "🚨 TIMEOUT FAILURES", red=True)
        terminalreporter.write_line("The following tests exceeded the timeout limit:")
        terminalreporter.write_line("")

        for nodeid, duration in timeout_tests:
            terminalreporter.write_line(f"  💥 {nodeid}: {duration:.2f}s")

        terminalreporter.write_line("")
        terminalreporter.write_line("💡 To fix timeout issues:")
        terminalreporter.write_line(
            "   • Use @pytest.mark.timeout(N) for custom timeouts"
        )
        terminalreporter.write_line("   • Mock external API calls and I/O operations")
        terminalreporter.write_line(
            "   • Check for infinite loops or blocking operations"
        )
        terminalreporter.write_line("")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add timeout markers and warnings."""
    for item in items:
        # Check if test already has a timeout marker
        has_timeout = any(mark.name == "timeout" for mark in item.iter_markers())

        if not has_timeout:
            # Check if test is marked as slow and give it more time
            if any(mark.name == "slow" for mark in item.iter_markers()):
                item.add_marker(pytest.mark.timeout(30))  # 30s for slow tests
            # Integration tests get more time
            elif any(mark.name == "integration" for mark in item.iter_markers()):
                item.add_marker(pytest.mark.timeout(15))  # 15s for integration tests
