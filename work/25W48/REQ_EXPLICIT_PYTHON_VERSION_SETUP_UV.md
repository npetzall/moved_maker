# Implementation Plan: Explicitly Set Python 3.13 in All `setup-uv` Actions

**Status**: ✅ Complete

## Overview
Add explicit `python-version: "3.13"` to all 8 instances of `setup-uv` actions across 4 GitHub Actions workflow files to ensure consistent and reliable Python version usage.

## Checklist Summary

### Phase 1: Update pull_request.yaml
- [x] 3/3 tasks completed

### Phase 2: Update release-build.yaml
- [x] 3/3 tasks completed

### Phase 3: Update release-version.yaml
- [x] 1/1 tasks completed

### Phase 4: Update pr-label.yml
- [x] 1/1 tasks completed

## Context
Reference: `plan/25W48/REQ_EXPLICIT_PYTHON_VERSION_SETUP_UV.md`

Currently, all 8 instances of `setup-uv` actions across 4 workflow files do not explicitly specify the Python version. While `uv` can detect Python versions from `.python-version` files and `requires-python` constraints in `pyproject.toml`, explicit specification in `setup-uv` actions provides better reliability, explicitness, and follows CI/CD best practices.

**Current format:**
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@d7d33e16d4ecbbea0da49ecb6fcc16df877ddac8  # v5
```

**Target format:**
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@d7d33e16d4ecbbea0da49ecb6fcc16df877ddac8  # v5
  with:
    python-version: "3.13"
```

## Goals
- Add explicit `python-version: "3.13"` to all 8 `setup-uv` action instances
- Ensure consistent Python version specification across all workflows
- Improve CI/CD reliability by avoiding potential version detection issues
- Maintain existing workflow behavior (no functional changes)

## Non-Goals
- Changing the Python version (already 3.13)
- Modifying other workflow steps
- Updating documentation (not required per REQ)
- Manual testing (handled post-implementation)

## Design Decisions

**Explicit Python Version Specification**: Add `python-version: "3.13"` to all `setup-uv` actions
  - **Rationale**: Explicit specification ensures the correct Python version is used even if automatic detection has issues. This follows CI/CD best practices and provides better reliability.
  - **Alternatives Considered**:
    - Relying on automatic detection from `.python-version` files: Rejected - explicit specification is more reliable
    - Relying on `requires-python` constraint in `pyproject.toml`: Rejected - `setup-uv` needs the version before `uv run` can read `pyproject.toml`
    - Using `uv run --python 3.13`: Rejected - `setup-uv` should install the correct Python version upfront
  - **Trade-offs**: None - this is a straightforward improvement with no downsides

## Implementation Steps

### Phase 1: Update pull_request.yaml

**Objective**: Add explicit Python version to all 3 `setup-uv` actions in the pull request workflow

- [x] **Task 1**: Update `setup-uv` in `test-ubuntu` job
  - [x] Read `.github/workflows/pull_request.yaml` to verify current state
  - [x] Locate `setup-uv` action at line 74 (in `test-ubuntu` job)
  - [x] Add `with:` section with `python-version: "3.13"` to the action
  - [x] Verify YAML syntax is correct
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: None
  - **Testing**: Verify YAML syntax with a linter or parser
  - **Notes**: This is the first `setup-uv` instance in the file, before test-summary generation

- [x] **Task 2**: Update `setup-uv` in `test-macos` job
  - [x] Locate `setup-uv` action at line 119 (in `test-macos` job)
  - [x] Add `with:` section with `python-version: "3.13"` to the action
  - [x] Verify YAML syntax is correct
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: None
  - **Testing**: Verify YAML syntax with a linter or parser
  - **Notes**: This is the second `setup-uv` instance in the file, before test-summary generation

- [x] **Task 3**: Update `setup-uv` in `coverage` job
  - [x] Locate `setup-uv` action at line 198 (in `coverage` job)
  - [x] Add `with:` section with `python-version: "3.13"` to the action
  - [x] Verify YAML syntax is correct
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: None
  - **Testing**: Verify YAML syntax with a linter or parser
  - **Notes**: This is the third `setup-uv` instance in the file, before coverage-summary generation

### Phase 2: Update release-build.yaml

**Objective**: Add explicit Python version to all 3 `setup-uv` actions in the release build workflow

- [x] **Task 1**: Update `setup-uv` in `coverage` job
  - [x] Read `.github/workflows/release-build.yaml` to verify current state
  - [x] Locate `setup-uv` action at line 140 (in `coverage` job)
  - [x] Add `with:` section with `python-version: "3.13"` to the action
  - [x] Verify YAML syntax is correct
  - **Files**: `.github/workflows/release-build.yaml`
  - **Dependencies**: None
  - **Testing**: Verify YAML syntax with a linter or parser
  - **Notes**: This is the first `setup-uv` instance in the file, before coverage-summary generation

- [x] **Task 2**: Update `setup-uv` in `build-and-release` job
  - [x] Locate `setup-uv` action at line 192 (in `build-and-release` job)
  - [x] Add `with:` section with `python-version: "3.13"` to the action
  - [x] Verify YAML syntax is correct
  - **Files**: `.github/workflows/release-build.yaml`
  - **Dependencies**: None
  - **Testing**: Verify YAML syntax with a linter or parser
  - **Notes**: This is the second `setup-uv` instance in the file, before test-summary generation

- [x] **Task 3**: Update `setup-uv` in `release` job
  - [x] Locate `setup-uv` action at line 269 (in `release` job)
  - [x] Add `with:` section with `python-version: "3.13"` to the action
  - [x] Verify YAML syntax is correct
  - **Files**: `.github/workflows/release-build.yaml`
  - **Dependencies**: None
  - **Testing**: Verify YAML syntax with a linter or parser
  - **Notes**: This is the third `setup-uv` instance in the file, before release-notes generation

### Phase 3: Update release-version.yaml

**Objective**: Add explicit Python version to the `setup-uv` action in the release version workflow

- [x] **Task 1**: Update `setup-uv` in `version` job
  - [x] Read `.github/workflows/release-version.yaml` to verify current state
  - [x] Locate `setup-uv` action at line 47 (in `version` job)
  - [x] Add `with:` section with `python-version: "3.13"` to the action
  - [x] Verify YAML syntax is correct
  - **Files**: `.github/workflows/release-version.yaml`
  - **Dependencies**: None
  - **Testing**: Verify YAML syntax with a linter or parser
  - **Notes**: This is the only `setup-uv` instance in the file, before release-version script execution

### Phase 4: Update pr-label.yml

**Objective**: Add explicit Python version to the `setup-uv` action in the PR label workflow

- [x] **Task 1**: Update `setup-uv` in `label` job
  - [x] Read `.github/workflows/pr-label.yml` to verify current state
  - [x] Locate `setup-uv` action at line 19 (in `label` job)
  - [x] Add `with:` section with `python-version: "3.13"` to the action
  - [x] Verify YAML syntax is correct
  - **Files**: `.github/workflows/pr-label.yml`
  - **Dependencies**: None
  - **Testing**: Verify YAML syntax with a linter or parser
  - **Notes**: This is the only `setup-uv` instance in the file, before pr-labels script execution

## Files to Modify/Create
- **Modified Files**:
  - `.github/workflows/pull_request.yaml` - Add `python-version: "3.13"` to 3 `setup-uv` actions (lines 74, 119, 198)
  - `.github/workflows/release-build.yaml` - Add `python-version: "3.13"` to 3 `setup-uv` actions (lines 140, 192, 269)
  - `.github/workflows/release-version.yaml` - Add `python-version: "3.13"` to 1 `setup-uv` action (line 47)
  - `.github/workflows/pr-label.yml` - Add `python-version: "3.13"` to 1 `setup-uv` action (line 19)

## Testing Strategy
- **YAML Syntax Validation**: Verify all modified workflow files have valid YAML syntax
  - Use `yamllint` or similar tool if available
  - Check for proper indentation and structure
- **Workflow File Structure**: Verify that all `setup-uv` actions now include the `with:` section with `python-version: "3.13"`
  - Use `grep` or similar to verify all instances are updated
  - Count occurrences to ensure all 8 instances are modified
- **Manual Testing**: (Informational only - not part of AI tasks)
  - Verify all affected workflows run successfully in GitHub Actions
  - Test PR workflow (test-ubuntu, test-macos, coverage jobs)
  - Test release-build workflow (coverage, build-and-release, release jobs)
  - Test release-version workflow (version job)
  - Test pr-label workflow (label job)

## Breaking Changes
None - workflows will continue to function identically, just with explicit version specification.

## Migration Guide
N/A - No breaking changes.

## Documentation Updates
- [ ] No documentation updates required (per REQ document)

## Success Criteria
- All 8 instances of `setup-uv` actions have explicit `python-version: "3.13"` specified
- All modified workflow files have valid YAML syntax
- No functional changes to workflow behavior (Python 3.13 was already the target version)
- Consistent format across all workflow files

## Risks and Mitigations
- **Risk**: YAML syntax errors could break workflow files
  - **Mitigation**: Verify YAML syntax after each change, use proper indentation (2 spaces for YAML)
- **Risk**: Incorrect line numbers if files have changed since REQ was written
  - **Mitigation**: Read files first to verify current state, locate `setup-uv` actions by searching for the action name rather than relying solely on line numbers
- **Risk**: Python 3.13 might not be available on GitHub Actions runners
  - **Mitigation**: Python 3.13 is a stable release and should be available. The REQ document confirms this is already the target version, so this is low risk.

## References
- Related REQ_ document: `plan/25W48/REQ_EXPLICIT_PYTHON_VERSION_SETUP_UV.md`
- Related to:
  - Python 3.13 upgrade work (`plan/25W48/REQ_PYTHON_3_13_UPGRADE.md`)
  - Remove uv sync from workflows (`plan/XX_Backlog/REQ_REMOVE_UV_SYNC_FROM_WORKFLOWS.md`)
- External references:
  - [setup-uv action documentation](https://github.com/astral-sh/setup-uv)
  - [uv issue #6285 - .python-version detection](https://github.com/astral-sh/uv/issues/6285)
