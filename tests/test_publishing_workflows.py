"""Tests for publishing workflows configuration."""

from pathlib import Path

import yaml


class TestPublishingWorkflows:
    """Test publishing workflow configurations."""

    def test_publish_workflow_exists(self) -> None:
        """Test that the publish workflow file exists."""
        workflow_path = Path(".github/workflows/publish.yml")
        assert workflow_path.exists(), "publish.yml workflow should exist"

    def test_publish_test_workflow_exists(self) -> None:
        """Test that the publish-test workflow file exists."""
        workflow_path = Path(".github/workflows/publish-test.yml")
        assert workflow_path.exists(), "publish-test.yml workflow should exist"

    def test_publish_workflow_configuration(self) -> None:
        """Test the publish workflow configuration."""
        workflow_path = Path(".github/workflows/publish.yml")
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)

        # Test basic structure
        assert workflow["name"] == "Publish to PyPI"
        # YAML parser converts 'on:' to boolean True, so we access it that way
        workflow_on = workflow[True]
        assert "release" in workflow_on
        assert workflow_on["release"]["types"] == ["published"]

        # Test job configuration
        publish_job = workflow["jobs"]["publish"]
        assert publish_job["runs-on"] == "ubuntu-latest"
        assert publish_job["environment"]["name"] == "pypi"
        assert publish_job["environment"]["url"] == "https://pypi.org/p/automake-cli"

        # Test permissions
        permissions = publish_job["permissions"]
        assert permissions["id-token"] == "write"
        assert permissions["contents"] == "read"

        # Test steps
        step_names = [step["name"] for step in publish_job["steps"]]
        expected_steps = [
            "Checkout code",
            "Set up Python",
            "Install uv",
            "Verify version matches release tag",
            "Install dependencies",
            "Run tests",
            "Build package",
            "Verify package contents",
            "Publish to PyPI",
            "Verify PyPI publication",
        ]

        for expected_step in expected_steps:
            assert expected_step in step_names, (
                f"Step '{expected_step}' should be present"
            )

        # Test PyPI publish action
        publish_step = next(
            step for step in publish_job["steps"] if step["name"] == "Publish to PyPI"
        )
        assert publish_step["uses"] == "pypa/gh-action-pypi-publish@release/v1"
        assert publish_step["with"]["print-hash"] is True
        assert publish_step["with"]["verbose"] is True

    def test_publish_test_workflow_configuration(self) -> None:
        """Test the publish-test workflow configuration."""
        workflow_path = Path(".github/workflows/publish-test.yml")
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)

        # Test basic structure
        assert workflow["name"] == "Test Publish to TestPyPI"
        # YAML parser converts 'on:' to boolean True, so we access it that way
        workflow_on = workflow[True]
        assert "workflow_dispatch" in workflow_on
        assert "test_version" in workflow_on["workflow_dispatch"]["inputs"]

        # Test job configuration
        test_publish_job = workflow["jobs"]["test-publish"]
        assert test_publish_job["runs-on"] == "ubuntu-latest"
        assert test_publish_job["environment"]["name"] == "testpypi"
        assert (
            test_publish_job["environment"]["url"]
            == "https://test.pypi.org/p/automake-cli"
        )

        # Test permissions
        permissions = test_publish_job["permissions"]
        assert permissions["id-token"] == "write"
        assert permissions["contents"] == "read"

        # Test steps
        step_names = [step["name"] for step in test_publish_job["steps"]]
        expected_steps = [
            "Checkout code",
            "Set up Python",
            "Install uv",
            "Modify version for test",
            "Install dependencies",
            "Run tests",
            "Build package",
            "Verify package contents",
            "Publish to TestPyPI",
            "Verify TestPyPI publication",
            "Test uvx installation",
        ]

        for expected_step in expected_steps:
            assert expected_step in step_names, (
                f"Step '{expected_step}' should be present"
            )

        # Test TestPyPI publish action
        publish_step = next(
            step
            for step in test_publish_job["steps"]
            if step["name"] == "Publish to TestPyPI"
        )
        assert publish_step["uses"] == "pypa/gh-action-pypi-publish@release/v1"
        assert publish_step["with"]["repository-url"] == "https://test.pypi.org/legacy/"
        assert publish_step["with"]["print-hash"] is True
        assert publish_step["with"]["verbose"] is True

    def test_workflow_python_version_consistency(self) -> None:
        """Test that both workflows use the same Python version."""
        publish_path = Path(".github/workflows/publish.yml")
        test_publish_path = Path(".github/workflows/publish-test.yml")

        with open(publish_path) as f:
            publish_workflow = yaml.safe_load(f)

        with open(test_publish_path) as f:
            test_publish_workflow = yaml.safe_load(f)

        publish_python_version = publish_workflow["env"]["PYTHON_VERSION"]
        test_publish_python_version = test_publish_workflow["env"]["PYTHON_VERSION"]

        assert publish_python_version == test_publish_python_version, (
            "Both workflows should use the same Python version"
        )

    def test_workflow_uses_uv_setup(self) -> None:
        """Test that workflows use the uv setup action."""
        workflows = [
            Path(".github/workflows/publish.yml"),
            Path(".github/workflows/publish-test.yml"),
        ]

        for workflow_path in workflows:
            with open(workflow_path) as f:
                workflow = yaml.safe_load(f)

            # Find uv setup step
            job = list(workflow["jobs"].values())[0]  # Get first job
            uv_setup_step = next(
                (step for step in job["steps"] if step["name"] == "Install uv"),
                None,
            )

            assert uv_setup_step is not None, (
                f"uv setup step should exist in {workflow_path.name}"
            )
            assert uv_setup_step["uses"] == "astral-sh/setup-uv@v4"
            assert uv_setup_step["with"]["version"] == "latest"

    def test_workflow_includes_entry_point_verification(self) -> None:
        """Test that workflows verify both entry points work."""
        workflows = [
            Path(".github/workflows/publish.yml"),
            Path(".github/workflows/publish-test.yml"),
        ]

        for workflow_path in workflows:
            with open(workflow_path) as f:
                workflow = yaml.safe_load(f)

            job = list(workflow["jobs"].values())[0]  # Get first job
            verify_step = next(
                (
                    step
                    for step in job["steps"]
                    if "Verify package contents" in step["name"]
                ),
                None,
            )

            assert verify_step is not None, (
                f"Package verification step should exist in {workflow_path.name}"
            )

            # Check that the step tests both entry points
            run_script = verify_step["run"]
            assert "automake --version" in run_script
            assert "automake-cli --version" in run_script

    def test_publishing_documentation_exists(self) -> None:
        """Test that publishing documentation exists."""
        docs_path = Path("docs/PUBLISHING.md")
        assert docs_path.exists(), "Publishing documentation should exist"

        with open(docs_path) as f:
            content = f.read()

        # Check for key sections
        assert "# Publishing Guide" in content
        assert "Trusted Publishing" in content
        assert "PyPI" in content
        assert "TestPyPI" in content
        assert "GitHub Actions" in content
