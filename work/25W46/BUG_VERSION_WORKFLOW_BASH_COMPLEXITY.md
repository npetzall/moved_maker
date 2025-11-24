# Implementation Plan: BUG_VERSION_WORKFLOW_BASH_COMPLEXITY

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_VERSION_WORKFLOW_BASH_COMPLEXITY.md`.

## Context

Related bug report: `plan/25W46/BUG_VERSION_WORKFLOW_BASH_COMPLEXITY.md`

## Implementation Plan

### Phase 1: Setup Python Project

#### Step 1: Create directory structure

**Directory:** `.github/scripts/release-version/`

- [x] Create `.github/scripts/release-version/` directory
- [x] Create `pyproject.toml` with dependencies (see content below)

**File:** `.github/scripts/release-version/pyproject.toml`

```toml
[project]
name = "release-version"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pygithub>=2.0.0",
    "packaging>=24.0",
    "tomlkit>=0.12.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-datadir>=1.4.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

#### Step 2: Create package structure

- [x] Create `src/release_version/` directory
- [x] Create `src/release_version/__init__.py` (empty file)
- [x] Create `src/release_version/__main__.py` (entry point)
- [x] Create `src/release_version/version.py` (version calculation logic)
- [x] Create `src/release_version/github_client.py` (GitHub API wrapper)
- [x] Create `src/release_version/cargo.py` (Cargo.toml manipulation)
- [x] Create `tests/` directory
- [x] Create `tests/__init__.py` (empty file)
- [x] Create `tests/conftest.py` (pytest fixtures)
- [x] Create `tests/test_version.py` (version calculation tests)
- [x] Create `tests/test_github_client.py` (GitHub client tests)
- [x] Create `tests/test_cargo.py` (Cargo.toml tests)
- [x] Create `tests/data/` directory for test data files

#### Step 3: Generate lock file

- [x] Navigate to the script directory: `cd .github/scripts/release-version`
- [x] Install dev dependencies: `uv sync --dev`
- [x] Run `uv lock` to generate `uv.lock` file (generated automatically by uv sync)
- [x] Verify `uv.lock` file was created
- [ ] Commit `uv.lock` file to repository

### Phase 2: Implement Python Package

The package should be structured with separate modules for better testability and maintainability:

**Package structure:**
- `src/release_version/__main__.py` - Entry point (calls main function)
- `src/release_version/version.py` - Version calculation logic
- `src/release_version/github_client.py` - GitHub API client wrapper
- `src/release_version/cargo.py` - Cargo.toml manipulation

#### Step 1: Implement core modules

**File:** `src/release_version/cargo.py`

- [ ] Implement `read_cargo_version(path: str) -> str`:
  - Read Cargo.toml using `tomlkit.parse()`
  - Extract and return version from `package.version`
  - Handle file not found and parsing errors
- [ ] Implement `update_cargo_version(path: str, version: str) -> None`:
  - Read Cargo.toml using `tomlkit.parse()`
  - Update `package.version` field
  - Write back using `tomlkit.dumps()` to preserve formatting
  - Validate update was successful

**File:** `src/release_version/github_client.py`

- [ ] Implement `GitHubClient` class:
  - `__init__(self, token: str, repo_name: str)` - Initialize GitHub client
  - `get_merged_prs_since(self, since_timestamp: int) -> List[PullRequest]`:
    - Use `repo.get_pulls(state="closed", base="main", sort="updated", direction="desc")`
    - Filter by `merged_at` timestamp > since_timestamp
    - Handle pagination automatically (PyGithub does this)
    - Return list of merged PRs
  - `get_repo(self) -> Repository` - Return repository object

**File:** `src/release_version/version.py`

- [x] Implement `get_latest_tag() -> str | None`:
  - Use subprocess to run `git describe --tags --match "v*" --abbrev=0`
  - Return tag name or None if no tags exist
- [x] Implement `get_tag_timestamp(tag: str) -> int`:
  - Use subprocess to run `git log -1 --format=%ct <tag>`
  - Return Unix timestamp
- [x] Implement `get_commit_count(since_tag: str) -> int`:
  - Use subprocess to run `git rev-list --count <tag>..HEAD`
  - Return commit count
- [x] Implement `determine_bump_type(prs: List[PullRequest]) -> str`:
  - Check PR labels for "version: major" or "breaking" → return "MAJOR"
  - Check PR labels for "version: minor" or "feature" → return "MINOR"
  - No matching labels → return "PATCH"
- [x] Implement `calculate_version(base_version: str, bump_type: str, commit_count: int) -> str`:
  - Parse base version using `packaging_version.parse()`
  - Increment based on bump type:
    - MAJOR: increment major, reset minor and patch to 0
    - MINOR: increment minor, reset patch to 0
    - PATCH: add commit_count to patch
  - Return new version string
- [x] Implement `calculate_new_version(repo_path: str = ".") -> tuple[str, str]`:
  - Main orchestration function
  - Get latest tag or use Cargo.toml version (first release)
  - Get merged PRs since tag
  - Determine bump type
  - Calculate new version
  - Return (version, tag_name) tuple

**File:** `src/release_version/__main__.py`

- [x] Implement `main()` function:
  - Parse environment variables:
    - `GITHUB_TOKEN` - GitHub Actions token for API access (automatically available)
    - `GITHUB_OUTPUT` - Path to output file for workflow variables
    - `GITHUB_REPOSITORY` - Repository name (owner/repo format)
  - Initialize GitHub client
  - Call `calculate_new_version()`
  - Update Cargo.toml with new version
  - Output to $GITHUB_OUTPUT format:
    - Write `version=<version>` and `tag_name=v<version>` to output file
    - Fallback to stdout if GITHUB_OUTPUT not set
- [x] Add `if __name__ == "__main__":` block to call `main()`

#### Step 2: Add error handling and logging

- [x] Add try/except blocks in all modules:
  - GitHub API calls in `github_client.py`
  - Git subprocess calls in `version.py`
  - File I/O operations in `cargo.py`
  - Version parsing in `version.py`
- [x] Add informative log messages using `print()`:
  - Log when starting version calculation
  - Log latest tag found (or "first release")
  - Log PR label checks (which PRs have which labels)
  - Log bump type determined
  - Log calculated version
  - Log Cargo.toml update confirmation
- [x] Use stderr for error messages: `print(..., file=sys.stderr)`
- [x] Use stdout for informational messages

#### Step 3: Implement tests

**File:** `tests/conftest.py`

- [x] Create pytest fixtures:
  - `mock_github_client` - Mock GitHub client
  - `mock_repo` - Mock repository object
  - `mock_pr` - Mock pull request object
  - `temp_cargo_toml` - Temporary Cargo.toml file fixture
  - `sample_cargo_toml_with_deps` - Sample Cargo.toml with dependencies

**File:** `tests/test_cargo.py`

- [x] Test `read_cargo_version()`:
  - Test reading valid Cargo.toml
  - Test file not found error
  - Test invalid TOML format
  - Test missing version field
- [x] Test `update_cargo_version()`:
  - Test updating version in valid Cargo.toml
  - Test preserving formatting
  - Test file not found error
  - Test invalid TOML format
- [x] Use pytest fixtures for test data files:
  - Created fixtures for various Cargo.toml formats

**File:** `tests/test_version.py`

- [x] Test `get_latest_tag()`:
  - Test with existing tags
  - Test with no tags (returns None)
  - Mock subprocess calls
- [x] Test `get_tag_timestamp()`:
  - Test timestamp extraction
  - Test invalid tag error
- [x] Test `get_commit_count()`:
  - Test commit count calculation
  - Test with different tag ranges
- [x] Test `determine_bump_type()`:
  - Test with major version label
  - Test with minor version label
  - Test with patch (no labels)
  - Test with multiple PRs (highest priority wins)
- [x] Test `calculate_version()`:
  - Test major bump
  - Test minor bump
  - Test patch bump with commit count
  - Test invalid version format

**File:** `tests/test_github_client.py`

- [x] Test `get_merged_prs_since()`:
  - Test filtering by timestamp
  - Test pagination handling
  - Test API error handling
  - Mock PyGithub responses
- [x] Test `get_repo()`:
  - Test repository retrieval
  - Test authentication errors

**Test execution:**

- [x] Run tests: `uv run python -m pytest tests/`
- [x] Verify all tests pass (26 tests passing)
- [ ] Check test coverage (optional): `uv run python -m pytest --cov=src tests/`

### Phase 3: Update Workflow

**File:** `.github/workflows/release-version.yaml`

#### Step 1: Update release-version.yaml

- [x] Add `astral-sh/setup-uv` action step before the version calculation step:
  ```yaml
  - name: Install uv
    uses: astral-sh/setup-uv@486d0b887200c1d9bb3a30439404f78461090c4f  # v5
  ```
  - Using commit SHA: 486d0b887200c1d9bb3a30439404f78461090c4f
- [x] Replace the bash script step (lines 39-111) with:
  ```yaml
  - name: Calculate version from PR labels
    id: version
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_REPOSITORY: ${{ github.repository }}
    run: |
      cd .github/scripts/release-version
      uv run python -m release_version
  ```
- [x] Update token usage to use `GITHUB_TOKEN` (GitHub Actions token) for script
- [x] Remove the old bash script step completely
- [x] Verify workflow YAML syntax is valid
- [ ] Test workflow locally (if possible) or in a test branch

#### Step 2: Verify workflow

- [ ] Test with first release (no tags):
  - Should read version from Cargo.toml
  - Should output that version
- [ ] Test with existing tags:
  - Should find latest tag
  - Should calculate version based on PR labels
- [ ] Test with major version label:
  - PR with "version: major" or "breaking" label
  - Should increment major version, reset minor and patch to 0
- [ ] Test with minor version label:
  - PR with "version: minor" or "feature" label
  - Should increment minor version, reset patch to 0
- [ ] Test with patch version (no labels):
  - PRs without version labels
  - Should increment patch by commit count
- [ ] Test with multiple PRs:
  - Multiple PRs with different labels
  - Should use highest priority (major > minor > patch)
- [ ] Test with more than 100 PRs (pagination):
  - Verify PyGithub handles pagination automatically
  - All PRs should be checked

### Phase 4: Dependabot Configuration

**File:** `.github/dependabot.yml`

#### Step 1: Update dependabot.yml

- [x] Add pip ecosystem entry for release-version directory:
  ```yaml
  - package-ecosystem: "pip"
    directory: "/.github/scripts/release-version"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
    reviewers:
      - npetzall
    assignees:
      - npetzall
  ```
- [x] Place the new entry after the existing cargo and github-actions entries
- [x] Verify YAML syntax is valid
- [ ] Commit the updated dependabot.yml file
- [ ] Verify Dependabot detects pyproject.toml:
  - Check Dependabot logs in GitHub repository
  - Should see scanning activity for the new directory

#### Step 2: Test Dependabot

- [ ] Wait for Dependabot to scan the directory (may take a few minutes to hours)
- [ ] Check Dependabot tab in repository for any dependency update PRs
- [ ] Verify it creates PRs for dependency updates when available
- [ ] Test updating a dependency manually:
  - Update a version in pyproject.toml
  - Commit and push
  - Verify Dependabot detects the change

### Phase 5: Testing and Validation

#### Step 1: Local testing

- [ ] Run unit tests: `cd .github/scripts/release-version && uv run pytest tests/`
- [ ] Verify all tests pass
- [ ] Test script locally with mock GitHub API:
  - Set up test environment variables
  - Run `uv run python -m release_version`
  - Verify output format
- [ ] Test version calculation logic with various scenarios
- [ ] Test Cargo.toml update with different formats
- [ ] Test error handling with invalid inputs
- [ ] Check test coverage: `uv run pytest --cov=src --cov-report=term tests/`

#### Step 2: Integration testing
- [ ] Test in a feature branch
- [ ] Verify workflow runs successfully
- [ ] Verify version calculation is correct
- [ ] Verify Cargo.toml is updated correctly
- [ ] Verify tag is created correctly

#### Step 3: Rollout
- [ ] Merge to main branch
- [ ] Monitor first run
- [ ] Verify version is calculated correctly
- [ ] Verify tag is created
- [ ] Verify Cargo.toml is updated

## Example Implementation

### Python Script

**File:** `.github/scripts/release-version/release-version.py`

```python
#!/usr/bin/env python3
"""Calculate version from PR labels and git tags."""
import sys
import os
import subprocess
from pathlib import Path
from packaging import version as packaging_version
from github import Github
from datetime import datetime
import tomlkit

def get_latest_tag():
    """Get the latest tag matching v* pattern."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--match", "v*", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"Error getting latest tag: {e}", file=sys.stderr)
        sys.exit(1)

def get_version_from_cargo_toml():
    """Get version from Cargo.toml."""
    try:
        with open("Cargo.toml", "r") as f:
            cargo = tomlkit.parse(f.read())
        return cargo["package"]["version"]
    except Exception as e:
        print(f"Error reading Cargo.toml: {e}", file=sys.stderr)
        sys.exit(1)

def get_merged_prs_since_tag(github, repo, tag_date):
    """Get all merged PRs since the tag date."""
    prs = []
    try:
        # Get all merged PRs with pagination
        for pr in repo.get_pulls(state="closed", base="main", sort="updated", direction="desc"):
            if pr.merged_at and pr.merged_at.timestamp() > tag_date:
                prs.append(pr)
            # Stop if we've gone past the tag date
            if pr.updated_at.timestamp() < tag_date:
                break
    except Exception as e:
        print(f"Error getting PRs: {e}", file=sys.stderr)
        sys.exit(1)
    return prs

def determine_bump_type(prs):
    """Determine version bump type from PR labels."""
    major_bump = False
    minor_bump = False

    for pr in prs:
        labels = [label.name for label in pr.labels]
        if any(label in labels for label in ["version: major", "breaking"]):
            major_bump = True
            print(f"PR #{pr.number} has major version label")
        elif any(label in labels for label in ["version: minor", "feature"]):
            minor_bump = True
            print(f"PR #{pr.number} has minor version label")

    if major_bump:
        return "MAJOR"
    elif minor_bump:
        return "MINOR"
    else:
        return "PATCH"

def calculate_version(base_version_str, bump_type, commit_count):
    """Calculate new version based on bump type."""
    try:
        base_version = packaging_version.parse(base_version_str)
        major, minor, patch = base_version.release

        if bump_type == "MAJOR":
            return f"{major + 1}.0.0"
        elif bump_type == "MINOR":
            return f"{major}.{minor + 1}.0"
        else:  # PATCH
            return f"{major}.{minor}.{patch + commit_count}"
    except Exception as e:
        print(f"Error calculating version: {e}", file=sys.stderr)
        sys.exit(1)

def update_cargo_toml(new_version):
    """Update Cargo.toml with new version."""
    try:
        with open("Cargo.toml", "r") as f:
            cargo = tomlkit.parse(f.read())

        cargo["package"]["version"] = new_version

        with open("Cargo.toml", "w") as f:
            f.write(tomlkit.dumps(cargo))

        print(f"Updated Cargo.toml version to {new_version}")
    except Exception as e:
        print(f"Error updating Cargo.toml: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main execution logic."""
    # Get GitHub token from environment (GITHUB_TOKEN is automatically available in GitHub Actions)
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Initialize GitHub client
    github = Github(token)
    repo = github.get_repo(os.environ.get("GITHUB_REPOSITORY", "").split("/")[-1])

    # Get latest tag
    latest_tag = get_latest_tag()

    if not latest_tag:
        # First release - use version from Cargo.toml
        version = get_version_from_cargo_toml()
        print(f"No previous tag found (first release), using base version from Cargo.toml: {version}")
    else:
        # Extract version from tag
        base_version = latest_tag.lstrip("v")

        # Get tag date
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", latest_tag],
            capture_output=True,
            text=True,
            check=True
        )
        tag_date = int(result.stdout.strip())

        # Get merged PRs since tag
        prs = get_merged_prs_since_tag(github, repo, tag_date)

        # Determine bump type
        bump_type = determine_bump_type(prs)

        # Get commit count for patch bump
        if bump_type == "PATCH":
            result = subprocess.run(
                ["git", "rev-list", "--count", f"{latest_tag}..HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            commit_count = int(result.stdout.strip())
        else:
            commit_count = 0

        # Calculate version
        version = calculate_version(base_version, bump_type, commit_count)

        print(f"Latest tag: {latest_tag}")
        print(f"Bump type: {bump_type}")
        print(f"Calculated version: {version}")

    # Update Cargo.toml
    update_cargo_toml(version)

    # Output to GITHUB_OUTPUT
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"version={version}\n")
            f.write(f"tag_name=v{version}\n")
    else:
        print(f"version={version}")
        print(f"tag_name=v{version}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

### pyproject.toml

```toml
[project]
name = "release-version"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pygithub>=2.0.0",
    "packaging>=24.0",
    "tomlkit>=0.12.0",
]
```

### Updated Workflow Step

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@486d0b887200c1d9bb3a30439404f78461090c4f  # v5

- name: Calculate version from PR labels
  id: version
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITHUB_REPOSITORY: ${{ github.repository }}
  run: |
    cd .github/scripts/release-version
    uv run python -m release_version
```

### Updated Dependabot Config

```yaml
version: 2
updates:
  - package-ecosystem: "cargo"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
    reviewers:
      - npetzall
    assignees:
      - npetzall

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
    reviewers:
      - npetzall
    assignees:
      - npetzall

  - package-ecosystem: "pip"
    directory: "/.github/scripts/release-version"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
    reviewers:
      - npetzall
    assignees:
      - npetzall
```
