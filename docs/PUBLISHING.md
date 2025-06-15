# Publishing Guide

This document explains how to publish new versions of the `automake-cli` package to PyPI using GitHub Actions.

## Overview

The project uses GitHub Actions with **Trusted Publishing** to securely publish packages to PyPI. This eliminates the need to store PyPI tokens as secrets and provides better security.

## Workflows

### 1. Production Publishing (`publish.yml`)

**Trigger:** When a new GitHub release is published
**Target:** PyPI (https://pypi.org)

This workflow:
- ✅ Verifies the package version matches the release tag
- ✅ Runs the full test suite
- ✅ Builds the package
- ✅ Verifies both `automake` and `automake-cli` entry points work
- ✅ Publishes to PyPI using trusted publishing
- ✅ Verifies the package is available on PyPI

### 2. Test Publishing (`publish-test.yml`)

**Trigger:** Manual workflow dispatch
**Target:** TestPyPI (https://test.pypi.org)

This workflow:
- ✅ Adds a test suffix to the version (e.g., `0.3.4.dev1`)
- ✅ Runs the same validation as production
- ✅ Publishes to TestPyPI for testing
- ✅ Verifies installation from TestPyPI

## Setup Requirements

### 1. PyPI Trusted Publishing Setup

You need to configure trusted publishing for both PyPI and TestPyPI:

#### For PyPI (Production):
1. Go to https://pypi.org/manage/account/publishing/
2. Add a new trusted publisher with:
   - **PyPI Project Name:** `automake-cli`
   - **Owner:** `seanbaufeld` (your GitHub username)
   - **Repository name:** `auto-make`
   - **Workflow filename:** `publish.yml`
   - **Environment name:** `pypi`

#### For TestPyPI (Testing):
1. Go to https://test.pypi.org/manage/account/publishing/
2. Add a new trusted publisher with:
   - **PyPI Project Name:** `automake-cli`
   - **Owner:** `seanbaufeld`
   - **Repository name:** `auto-make`
   - **Workflow filename:** `publish-test.yml`
   - **Environment name:** `testpypi`

### 2. GitHub Environment Setup

Create two environments in your GitHub repository settings:

#### Environment: `pypi`
- **Protection rules:** Require reviewers (recommended)
- **Deployment branches:** Only `main` branch
- **Secrets:** None needed (uses trusted publishing)

#### Environment: `testpypi`
- **Protection rules:** None required
- **Deployment branches:** Any branch
- **Secrets:** None needed (uses trusted publishing)

## Publishing Process

### Testing a Release (Recommended First Step)

1. **Test on TestPyPI first:**
   ```bash
   # Go to GitHub Actions tab
   # Run "Test Publish to TestPyPI" workflow manually
   # Optionally specify a test version suffix (default: "dev1")
   ```

2. **Verify the test publication:**
   ```bash
   # Check TestPyPI: https://test.pypi.org/project/automake-cli/
   # Test installation:
   pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ automake-cli==0.3.4.dev1
   ```

### Production Release

1. **Ensure version is updated:**
   ```bash
   # Update version in pyproject.toml
   version = "0.3.5"  # New version

   # Update CHANGELOG.md with new version
   # Commit and push changes
   ```

2. **Create a GitHub Release:**
   ```bash
   # Go to GitHub repository
   # Click "Releases" → "Create a new release"
   # Tag version: v0.3.5 (must match pyproject.toml version)
   # Release title: v0.3.5 - Your Release Title
   # Add release notes
   # Click "Publish release"
   ```

3. **Monitor the workflow:**
   - The `publish.yml` workflow will automatically trigger
   - Monitor progress in GitHub Actions tab
   - Verify publication on PyPI: https://pypi.org/project/automake-cli/

4. **Verify the release:**
   ```bash
   # Test installation from PyPI
   uvx automake-cli --version
   uvx --from automake-cli automake --version
   ```

## Version Management

### Version Format
- **Production:** `X.Y.Z` (e.g., `0.3.4`)
- **Test:** `X.Y.Z.suffix` (e.g., `0.3.4.dev1`, `0.3.4.rc1`)

### Version Synchronization
The workflows automatically verify that:
- Package version in `pyproject.toml` matches the release tag
- Both entry points (`automake` and `automake-cli`) report the same version
- Version is correctly embedded in the installed package

## Troubleshooting

### Common Issues

1. **Version Mismatch Error:**
   ```
   ❌ Version mismatch: package version (0.3.4) does not match release tag (0.3.5)
   ```
   **Solution:** Update `pyproject.toml` version to match your release tag.

2. **Trusted Publishing Not Configured:**
   ```
   Error: Trusted publishing exchange failure
   ```
   **Solution:** Set up trusted publishing on PyPI/TestPyPI as described above.

3. **Environment Protection Rules:**
   ```
   Error: Required reviewers not met
   ```
   **Solution:** Get required approvals or adjust environment protection rules.

4. **Package Already Exists:**
   ```
   Error: File already exists
   ```
   **Solution:** You cannot overwrite existing versions. Increment the version number.

### Debugging Steps

1. **Check workflow logs** in GitHub Actions for detailed error messages
2. **Verify trusted publishing setup** on PyPI/TestPyPI
3. **Test locally** before creating a release:
   ```bash
   uv build
   uvx --from ./dist/automake_cli-X.Y.Z-py3-none-any.whl automake-cli --version
   ```

## Security Notes

- ✅ **No secrets required:** Trusted publishing eliminates the need for PyPI tokens
- ✅ **Environment protection:** Production releases can require manual approval
- ✅ **Audit trail:** All publications are logged and traceable
- ✅ **Minimal permissions:** Workflows only have necessary permissions

## Manual Publishing (Emergency)

If GitHub Actions are unavailable, you can publish manually:

```bash
# Install publishing tools
uv add --dev twine

# Build package
uv build

# Upload to PyPI (requires API token)
uv run twine upload dist/*

# Or upload to TestPyPI
uv run twine upload --repository testpypi dist/*
```

**Note:** Manual publishing requires PyPI API tokens and is less secure than trusted publishing.
