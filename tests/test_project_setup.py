"""Tests for project setup and configuration."""

import tomllib
from pathlib import Path


class TestProjectSetup:
    """Test cases for project setup and configuration files."""

    def test_pyproject_toml_exists(self) -> None:
        """Test that pyproject.toml exists."""
        pyproject_path = Path("pyproject.toml")
        assert pyproject_path.exists(), "pyproject.toml file should exist"

    def test_pyproject_toml_valid(self) -> None:
        """Test that pyproject.toml is valid TOML."""
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)
        assert isinstance(config, dict)

    def test_pyproject_build_system(self) -> None:
        """Test that build system is configured correctly."""
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)

        assert "build-system" in config
        build_system = config["build-system"]
        assert "requires" in build_system
        assert "hatchling" in build_system["requires"]
        assert build_system["build-backend"] == "hatchling.build"

    def test_pyproject_project_metadata(self) -> None:
        """Test that project metadata is configured correctly."""
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)

        assert "project" in config
        project = config["project"]

        # Required fields
        assert project["name"] == "automake-cli"
        assert project["version"]
        assert project["description"] == "AI-powered Makefile command execution"
        assert project["requires-python"] == ">=3.11"

        # Dependencies
        assert "dependencies" in project
        dependencies = project["dependencies"]
        assert any("typer" in dep for dep in dependencies)
        assert any("smolagents" in dep for dep in dependencies)
        assert any("requests" in dep for dep in dependencies)

    def test_pyproject_scripts_entry_point(self) -> None:
        """Test that CLI entry point is configured."""
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)

        assert "project" in config
        assert "scripts" in config["project"]
        scripts = config["project"]["scripts"]
        assert "automake" in scripts
        assert scripts["automake"] == "automake.cli.main:app"

    def test_pyproject_dev_dependencies(self) -> None:
        """Test that development dependencies are configured."""
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)

        assert "project" in config
        assert "optional-dependencies" in config["project"]
        optional_deps = config["project"]["optional-dependencies"]
        assert "dev" in optional_deps

        dev_deps = optional_deps["dev"]
        assert any("pytest" in dep for dep in dev_deps)
        assert any("pre-commit" in dep for dep in dev_deps)
        assert any("ruff" in dep for dep in dev_deps)

    def test_pyproject_ruff_configuration(self) -> None:
        """Test that Ruff is configured correctly."""
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)

        assert "tool" in config
        assert "ruff" in config["tool"]
        ruff_config = config["tool"]["ruff"]

        assert ruff_config["line-length"] == 88
        assert ruff_config["target-version"] == "py311"
        assert ruff_config["fix"] is True

    def test_pyproject_pytest_configuration(self) -> None:
        """Test that pytest is configured correctly."""
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)

        assert "tool" in config
        assert "pytest" in config["tool"]
        pytest_config = config["tool"]["pytest"]["ini_options"]

        assert "tests" in pytest_config["testpaths"]
        assert "--cov=automake" in pytest_config["addopts"]

    def test_precommit_config_exists(self) -> None:
        """Test that pre-commit configuration exists."""
        precommit_path = Path(".pre-commit-config.yaml")
        assert precommit_path.exists(), ".pre-commit-config.yaml should exist"

    def test_precommit_config_valid(self) -> None:
        """Test that pre-commit configuration is valid YAML."""
        import yaml

        with open(".pre-commit-config.yaml") as f:
            config = yaml.safe_load(f)

        assert isinstance(config, dict)
        assert "repos" in config
        assert isinstance(config["repos"], list)

    def test_precommit_ruff_hooks(self) -> None:
        """Test that Ruff hooks are configured in pre-commit."""
        import yaml

        with open(".pre-commit-config.yaml") as f:
            config = yaml.safe_load(f)

        ruff_repo = None
        for repo in config["repos"]:
            if "ruff-pre-commit" in repo["repo"]:
                ruff_repo = repo
                break

        assert ruff_repo is not None, "Ruff pre-commit repo should be configured"
        assert "hooks" in ruff_repo

        hook_ids = [hook["id"] for hook in ruff_repo["hooks"]]
        assert "ruff" in hook_ids
        assert "ruff-format" in hook_ids

    def test_directory_structure(self) -> None:
        """Test that required directories exist."""
        required_dirs = ["automake", "tests", "docs"]

        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            assert dir_path.exists(), f"Directory {dir_name} should exist"
            assert dir_path.is_dir(), f"{dir_name} should be a directory"

    def test_package_init_files(self) -> None:
        """Test that __init__.py files exist in packages."""
        init_files = [
            "automake/__init__.py",
            "tests/__init__.py",
        ]

        for init_file in init_files:
            init_path = Path(init_file)
            assert init_path.exists(), f"{init_file} should exist"

    def test_gitignore_exists(self) -> None:
        """Test that .gitignore exists."""
        gitignore_path = Path(".gitignore")
        assert gitignore_path.exists(), ".gitignore should exist"

    def test_readme_exists(self) -> None:
        """Test that README.md exists."""
        readme_path = Path("README.md")
        assert readme_path.exists(), "README.md should exist"

    def test_license_exists(self) -> None:
        """Test that LICENSE exists."""
        license_path = Path("LICENSE")
        assert license_path.exists(), "LICENSE should exist"
