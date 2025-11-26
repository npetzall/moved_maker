# REQ: Update all .github/scripts to Python 3.13

**Status**: ✅ Completed

## Overview
Update all Python scripts in `.github/scripts/` to require Python 3.13, and update the Python version installed in GitHub Actions workflows to match.

## Motivation
Python 3.13 is the latest stable version and provides performance improvements, new features, and security updates. Standardizing on Python 3.13 across all scripts and workflows ensures consistency, takes advantage of the latest language features, and maintains compatibility with the most recent Python ecosystem.

## Current Behavior
- All `.github/scripts/*/pyproject.toml` files specify `requires-python = ">=3.11"`
- Only `.github/scripts/release-notes/.python-version` exists and specifies `3.12`; other scripts do not have `.python-version` files
- The `.github/workflows/pull_request.yaml` workflow installs Python `3.11` via `actions/setup-python`
- Scripts are executed in workflows using `uv run python -m ...` which respects the `requires-python` constraint

**Affected scripts:**
- `.github/scripts/coverage-summary/`
- `.github/scripts/create-checksum/`
- `.github/scripts/pr-labels/`
- `.github/scripts/release-notes/`
- `.github/scripts/release-version/`
- `.github/scripts/test-summary/`

**Workflows using Python:**
- `.github/workflows/pull_request.yaml` (explicit Python setup for pre-commit)
- `.github/workflows/release-build.yaml` (uses scripts via `uv run`)
- `.github/workflows/release-version.yaml` (uses scripts via `uv run`)
- `.github/workflows/pr-label.yml` (uses scripts via `uv run`)

## Proposed Behavior
- Update all `requires-python = ">=3.11"` to `requires-python = ">=3.13"` in all `pyproject.toml` files
- Update `.github/scripts/release-notes/.python-version` from `3.12` to `3.13`
- Add `.python-version` files containing `3.13` to all scripts that don't currently have them:
  - `.github/scripts/coverage-summary/.python-version`
  - `.github/scripts/create-checksum/.python-version`
  - `.github/scripts/pr-labels/.python-version`
  - `.github/scripts/release-version/.python-version`
  - `.github/scripts/test-summary/.python-version`
- Update `.github/workflows/pull_request.yaml` to install Python `3.13` instead of `3.11`
- Ensure all workflows that use `uv` will automatically use Python 3.13 based on the `requires-python` constraint

## Use Cases
- Developers working locally with Python 3.13 will have consistent behavior with CI/CD
- CI/CD pipelines will use the latest stable Python version for improved performance and features
- All scripts will benefit from Python 3.13 improvements (performance, type system enhancements, etc.)

## Implementation Considerations
- Verify that all dependencies used by the scripts are compatible with Python 3.13
- Test all scripts in workflows to ensure they work correctly with Python 3.13
- Update `uv.lock` files if they exist (currently in `pr-labels/`, `release-notes/`, and `release-version/`)
- Consider if any scripts use Python features that might have changed between 3.11/3.12 and 3.13
- Ensure GitHub Actions runners support Python 3.13 (should be available as it's a stable release)
- Create `.python-version` files for consistency across all scripts (helps with local development tooling like `pyenv` and `uv`)

## Alternatives Considered
- **Stay on Python 3.11**: Rejected - misses out on performance improvements and new features in 3.13
- **Upgrade to Python 3.12**: Rejected - 3.13 is the latest stable version and provides more benefits
- **Use different Python versions per script**: Rejected - consistency is important for maintainability and developer experience

## Impact
- **Breaking Changes**: No - Python 3.13 is backward compatible with code written for 3.11+
- **Documentation**: Update any README files in script directories that mention Python version requirements
- **Testing**: Run all script tests with Python 3.13 to verify compatibility
- **Dependencies**: May need to regenerate `uv.lock` files to ensure dependencies are resolved for Python 3.13

## References
- Related issues: None
- Related PRs: None
- External references:
  - [Python 3.13 Release Notes](https://docs.python.org/3.13/whatsnew/3.13.html)
  - [GitHub Actions setup-python](https://github.com/actions/setup-python)
