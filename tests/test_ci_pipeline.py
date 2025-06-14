"""Tests for CI/CD pipeline configuration."""

from pathlib import Path

import yaml


class TestCIPipeline:
    """Test cases for CI/CD pipeline configuration."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.workflow_file = self.project_root / ".github" / "workflows" / "ci.yml"

    def test_ci_workflow_file_exists(self) -> None:
        """Test that the CI workflow file exists."""
        assert self.workflow_file.exists(), (
            "CI workflow file should exist at .github/workflows/ci.yml"
        )

    def test_ci_workflow_valid_yaml(self) -> None:
        """Test that the CI workflow file is valid YAML."""
        with open(self.workflow_file) as f:
            workflow_config = yaml.safe_load(f)

        assert isinstance(workflow_config, dict), (
            "Workflow file should contain valid YAML"
        )
        assert "name" in workflow_config, "Workflow should have a name"
        # PyYAML interprets 'on' as boolean True, so we check for True key
        assert True in workflow_config or "on" in workflow_config, (
            "Workflow should have trigger conditions"
        )
        assert "jobs" in workflow_config, "Workflow should have jobs defined"

    def test_ci_workflow_triggers(self) -> None:
        """Test that the CI workflow has correct triggers."""
        with open(self.workflow_file) as f:
            workflow_config = yaml.safe_load(f)

        # PyYAML interprets 'on' as boolean True
        triggers = workflow_config.get(True) or workflow_config.get("on")
        assert triggers is not None, "Should have trigger conditions"
        assert "push" in triggers, "Should trigger on push"
        assert "pull_request" in triggers, "Should trigger on pull request"

        # Check branch configuration
        assert triggers["push"]["branches"] == ["main"], (
            "Should trigger on push to main branch"
        )
        assert triggers["pull_request"]["branches"] == ["main"], (
            "Should trigger on PR to main branch"
        )

    def test_ci_workflow_jobs_structure(self) -> None:
        """Test that the CI workflow has the required jobs."""
        with open(self.workflow_file) as f:
            workflow_config = yaml.safe_load(f)

        jobs = workflow_config["jobs"]
        required_jobs = ["lint", "test", "security", "build", "integration"]

        for job in required_jobs:
            assert job in jobs, f"Job '{job}' should be defined in the workflow"

    def test_lint_job_configuration(self) -> None:
        """Test that the lint job is properly configured."""
        with open(self.workflow_file) as f:
            workflow_config = yaml.safe_load(f)

        lint_job = workflow_config["jobs"]["lint"]
        assert lint_job["runs-on"] == "ubuntu-latest", (
            "Lint job should run on ubuntu-latest"
        )

        # Check steps
        steps = lint_job["steps"]
        step_names = [step.get("name", "") for step in steps]

        assert "Checkout code" in step_names, "Should checkout code"
        assert "Set up Python" in step_names, "Should set up Python"
        assert "Install uv" in step_names, "Should install uv"
        assert "Install dependencies" in step_names, "Should install dependencies"
        assert "Run pre-commit hooks on all files" in step_names, (
            "Should run pre-commit hooks"
        )

    def test_test_job_configuration(self) -> None:
        """Test that the test job is properly configured."""
        with open(self.workflow_file) as f:
            workflow_config = yaml.safe_load(f)

        test_job = workflow_config["jobs"]["test"]
        assert test_job["runs-on"] == "ubuntu-latest", (
            "Test job should run on ubuntu-latest"
        )

        # Check Python version matrix
        strategy = test_job["strategy"]
        assert strategy["fail-fast"] is False, "Should not fail fast"
        matrix = strategy["matrix"]
        assert "3.11" in matrix["python-version"], "Should test Python 3.11"
        assert "3.12" in matrix["python-version"], "Should test Python 3.12"

        # Check steps
        steps = test_job["steps"]
        step_names = [step.get("name", "") for step in steps]

        assert "Checkout code" in step_names, "Should checkout code"
        assert "Run tests with coverage" in step_names, "Should run tests with coverage"
        assert "Upload coverage to Codecov" in step_names, "Should upload coverage"
        assert "Upload test results" in step_names, "Should upload test results"

    def test_build_job_configuration(self) -> None:
        """Test that the build job is properly configured."""
        with open(self.workflow_file) as f:
            workflow_config = yaml.safe_load(f)

        build_job = workflow_config["jobs"]["build"]
        assert build_job["runs-on"] == "ubuntu-latest", (
            "Build job should run on ubuntu-latest"
        )
        assert build_job["needs"] == ["lint", "test"], (
            "Build job should depend on lint and test jobs"
        )

        # Check steps
        steps = build_job["steps"]
        step_names = [step.get("name", "") for step in steps]

        assert "Build package" in step_names, "Should build package"
        assert "Upload build artifacts" in step_names, "Should upload build artifacts"

    def test_integration_job_configuration(self) -> None:
        """Test that the integration job is properly configured."""
        with open(self.workflow_file) as f:
            workflow_config = yaml.safe_load(f)

        integration_job = workflow_config["jobs"]["integration"]
        assert integration_job["runs-on"] == "ubuntu-latest", (
            "Integration job should run on ubuntu-latest"
        )
        assert integration_job["needs"] == ["build"], (
            "Integration job should depend on build job"
        )

        # Check steps
        steps = integration_job["steps"]
        step_names = [step.get("name", "") for step in steps]

        assert "Download build artifacts" in step_names, (
            "Should download build artifacts"
        )
        assert "Create test environment and install package" in step_names, (
            "Should install package"
        )
        assert "Test CLI installation" in step_names, "Should test CLI installation"

    def test_uv_usage_in_workflow(self) -> None:
        """Test that the workflow uses uv for dependency management."""
        with open(self.workflow_file) as f:
            workflow_content = f.read()

        assert "astral-sh/setup-uv@v4" in workflow_content, "Should use uv setup action"
        assert "uv sync --dev" in workflow_content, (
            "Should use uv sync for dependencies"
        )
        assert "uv run pytest" in workflow_content, "Should use uv run for pytest"
        assert "uv run --with pre-commit" in workflow_content, (
            "Should use uv run for pre-commit"
        )
        assert "uv build" in workflow_content, (
            "Should use uv build for package building"
        )

    def test_coverage_requirements(self) -> None:
        """Test that coverage requirements are properly configured."""
        with open(self.workflow_file) as f:
            workflow_content = f.read()

        assert "--cov=automake" in workflow_content, (
            "Should measure coverage for automake package"
        )
        assert "--cov-fail-under=80" in workflow_content, (
            "Should enforce 80% coverage threshold"
        )
        assert "--cov-report=xml" in workflow_content, (
            "Should generate XML coverage report"
        )
        assert "codecov/codecov-action@v4" in workflow_content, (
            "Should upload to Codecov"
        )

    def test_python_versions_supported(self) -> None:
        """Test that the workflow supports the required Python versions."""
        with open(self.workflow_file) as f:
            workflow_config = yaml.safe_load(f)

        # Check environment variable
        env = workflow_config.get("env", {})
        assert env.get("PYTHON_VERSION_MAIN") == "3.12", (
            "Should set main Python version to 3.12"
        )

        # Check test matrix
        test_job = workflow_config["jobs"]["test"]
        python_versions = test_job["strategy"]["matrix"]["python-version"]
        assert "3.11" in python_versions, "Should support Python 3.11"
        assert "3.12" in python_versions, "Should support Python 3.12"

    def test_security_job_exists(self) -> None:
        """Test that security scanning is included."""
        with open(self.workflow_file) as f:
            workflow_config = yaml.safe_load(f)

        security_job = workflow_config["jobs"]["security"]
        assert security_job["runs-on"] == "ubuntu-latest", (
            "Security job should run on ubuntu-latest"
        )

        # Check steps
        steps = security_job["steps"]
        step_names = [step.get("name", "") for step in steps]

        assert "Run safety check" in step_names, "Should run security checks"

    def test_workflow_name(self) -> None:
        """Test that the workflow has the correct name."""
        with open(self.workflow_file) as f:
            workflow_config = yaml.safe_load(f)

        assert workflow_config["name"] == "CI Pipeline", (
            "Workflow should be named 'CI Pipeline'"
        )

    def test_artifact_uploads(self) -> None:
        """Test that artifacts are properly uploaded."""
        with open(self.workflow_file) as f:
            workflow_content = f.read()

        assert "actions/upload-artifact@v4" in workflow_content, (
            "Should use upload-artifact action"
        )
        assert "actions/download-artifact@v4" in workflow_content, (
            "Should use download-artifact action"
        )
        assert "test-results-" in workflow_content, "Should upload test results"
        assert "name: dist" in workflow_content, "Should upload dist artifacts"
