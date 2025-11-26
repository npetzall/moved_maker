# REQ: Explicitly Set Python 3.13 in All `setup-uv` Actions

**Status**: ✅ Complete

## Overview
Add explicit `python-version: "3.13"` to all `setup-uv` actions in GitHub Actions workflows to ensure consistent and reliable Python version usage.

## Motivation
While `uv` can detect Python versions from `.python-version` files and `requires-python` constraints in `pyproject.toml`, explicitly setting the Python version in `setup-uv` actions provides:
- **Reliability**: Ensures the correct Python version is used even if automatic detection has issues
- **Explicitness**: Makes the required Python version clear in workflow files
- **Consistency**: Standardizes Python version specification across all workflows
- **Best practices**: Follows CI/CD best practices of being explicit about dependencies
- **Future-proofing**: Protects against potential changes in `uv`'s version detection behavior

There have been reported issues with `uv run` not always detecting `.python-version` files correctly (see [uv issue #6285](https://github.com/astral-sh/uv/issues/6285)), making explicit version specification a safer approach.

## Current Behavior

All 8 instances of `setup-uv` across 4 workflow files do not explicitly set the Python version:

1. **`.github/workflows/pull_request.yaml`** (3 instances):
   - Line 74: `setup-uv` in `test-ubuntu` job (before test-summary)
   - Line 119: `setup-uv` in `test-macos` job (before test-summary)
   - Line 198: `setup-uv` in `coverage` job (before coverage-summary)

2. **`.github/workflows/release-build.yaml`** (3 instances):
   - Line 140: `setup-uv` in `coverage` job (before coverage-summary)
   - Line 192: `setup-uv` in `build-and-release` job (before test-summary)
   - Line 269: `setup-uv` in `release` job (before release-notes)

3. **`.github/workflows/release-version.yaml`** (1 instance):
   - Line 47: `setup-uv` in `version` job (before release-version script)

4. **`.github/workflows/pr-label.yml`** (1 instance):
   - Line 19: `setup-uv` in `label` job (before pr-labels script)

**Current format:**
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@d7d33e16d4ecbbea0da49ecb6fcc16df877ddac8  # v5
```

**Context:**
- All scripts have `.python-version` files specifying `3.13`
- All `pyproject.toml` files have `requires-python = ">=3.13"`
- `uv run` should detect Python 3.13 automatically, but explicit specification is more reliable

## Proposed Behavior

Add `python-version: "3.13"` to the `with` section of all `setup-uv` actions.

**New format:**
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@d7d33e16d4ecbbea0da49ecb6fcc16df877ddac8  # v5
  with:
    python-version: "3.13"
```

**Changes required:**

1. **`.github/workflows/pull_request.yaml`**:
   - Add `python-version: "3.13"` to `setup-uv` at line 74 (test-ubuntu job)
   - Add `python-version: "3.13"` to `setup-uv` at line 119 (test-macos job)
   - Add `python-version: "3.13"` to `setup-uv` at line 198 (coverage job)

2. **`.github/workflows/release-build.yaml`**:
   - Add `python-version: "3.13"` to `setup-uv` at line 140 (coverage job)
   - Add `python-version: "3.13"` to `setup-uv` at line 192 (build-and-release job)
   - Add `python-version: "3.13"` to `setup-uv` at line 269 (release job)

3. **`.github/workflows/release-version.yaml`**:
   - Add `python-version: "3.13"` to `setup-uv` at line 47 (version job)

4. **`.github/workflows/pr-label.yml`**:
   - Add `python-version: "3.13"` to `setup-uv` at line 19 (label job)

## Use Cases
- **Workflow execution**: All workflows will consistently use Python 3.13, reducing version-related issues
- **CI/CD reliability**: Explicit version specification prevents potential detection failures
- **Maintainability**: Clear Python version requirements in workflow files
- **Developer clarity**: Makes it obvious which Python version is required

## Implementation Considerations
- **Verification**: Test all affected workflows to ensure they run correctly with explicit Python version
- **Compatibility**: Verify that Python 3.13 is available on all GitHub Actions runners (should be available as it's a stable release)
- **Consistency**: All workflows will use the same explicit version specification pattern
- **No breaking changes**: This change should not affect workflow behavior since Python 3.13 is already the target version

## Alternatives Considered
- **Rely on automatic detection from `.python-version` files**: Rejected - explicit specification is more reliable and follows CI/CD best practices
- **Rely on `requires-python` constraint in `pyproject.toml`**: Rejected - `setup-uv` needs the version before `uv run` can read `pyproject.toml`
- **Use `uv run --python 3.13`**: Rejected - `setup-uv` should install the correct Python version upfront, and this would require changes to all `uv run` commands

## Impact
- **Breaking Changes**: No - workflows will continue to function identically, just with explicit version specification
- **Documentation**: No documentation updates required
- **Testing**:
  - Verify all affected workflows run successfully
  - Test PR workflow (test-ubuntu, test-macos, coverage jobs)
  - Test release-build workflow (coverage, build-and-release, release jobs)
  - Test release-version workflow (version job)
  - Test pr-label workflow (label job)
- **Dependencies**: No new dependencies required

## References
- Related to:
  - Python 3.13 upgrade work (`plan/25W48/REQ_PYTHON_3_13_UPGRADE.md`)
  - Remove uv sync from workflows (`plan/XX_Backlog/REQ_REMOVE_UV_SYNC_FROM_WORKFLOWS.md`)
- External references:
  - [setup-uv action documentation](https://github.com/astral-sh/setup-uv)
  - [uv issue #6285 - .python-version detection](https://github.com/astral-sh/uv/issues/6285)
