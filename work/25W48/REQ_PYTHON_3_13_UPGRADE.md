# Implementation Plan: Update all .github/scripts to Python 3.13

**Status**: ✅ Completed

## Overview
Update all Python scripts in `.github/scripts/` to require Python 3.13, update the Python version installed in GitHub Actions workflows to match, and ensure all dependencies are compatible with Python 3.13.

## Checklist Summary

### Phase 1: Update pyproject.toml Files
- [x] 6/6 tasks completed

### Phase 2: Update .python-version Files
- [x] 6/6 tasks completed

### Phase 3: Update GitHub Actions Workflows
- [x] 1/1 tasks completed

### Phase 4: Regenerate uv.lock Files
- [x] 3/3 tasks completed

### Phase 5: Verify and Test
- [x] 1/1 tasks completed

## Context
**Reference**: `plan/25W48/REQ_PYTHON_3_13_UPGRADE.md`

**Current State**:
- All 6 scripts in `.github/scripts/` have `requires-python = ">=3.11"` in their `pyproject.toml` files
- Only `.github/scripts/release-notes/.python-version` exists and specifies `3.12`
- The `.github/workflows/pull_request.yaml` workflow installs Python `3.11` via `actions/setup-python` for the pre-commit job
- Scripts are executed in workflows using `uv run python -m ...` which respects the `requires-python` constraint
- Three scripts have `uv.lock` files that need to be regenerated: `pr-labels/`, `release-notes/`, and `release-version/`

**Affected Scripts**:
- `.github/scripts/coverage-summary/`
- `.github/scripts/create-checksum/`
- `.github/scripts/pr-labels/`
- `.github/scripts/release-notes/`
- `.github/scripts/release-version/`
- `.github/scripts/test-summary/`

**Workflows Using Python**:
- `.github/workflows/pull_request.yaml` (explicit Python setup for pre-commit)
- `.github/workflows/release-build.yaml` (uses scripts via `uv run`)
- `.github/workflows/release-version.yaml` (uses scripts via `uv run`)
- `.github/workflows/pr-label.yml` (uses scripts via `uv run`)

## Goals
- Update all `pyproject.toml` files to require Python 3.13
- Create or update `.python-version` files to specify Python 3.13 for all scripts
- Update GitHub Actions workflow to install Python 3.13 instead of 3.11
- Regenerate `uv.lock` files to ensure dependencies are resolved for Python 3.13
- Verify all scripts work correctly with Python 3.13

## Non-Goals
- Updating Python code to use Python 3.13-specific features (this is a version requirement update only)
- Changing dependency versions unless required for Python 3.13 compatibility
- Modifying script functionality or behavior

## Design Decisions

- **Standardize on Python 3.13 across all scripts**: All scripts will use the same Python version requirement for consistency and maintainability.
  - **Rationale**: Consistency simplifies development, CI/CD, and local development setup. Using the latest stable version ensures access to performance improvements and security updates.
  - **Alternatives Considered**: Using different Python versions per script was rejected as it adds complexity and maintenance burden.
  - **Trade-offs**: None - Python 3.13 is backward compatible with code written for 3.11+.

- **Create .python-version files for all scripts**: Add `.python-version` files to scripts that don't currently have them.
  - **Rationale**: These files help local development tooling (like `pyenv` and `uv`) automatically select the correct Python version, improving developer experience.
  - **Alternatives Considered**: Not creating these files was rejected as it reduces consistency and developer experience.
  - **Trade-offs**: None - these files are small and provide clear benefits.

- **Regenerate uv.lock files**: Update lock files for scripts that have them to ensure dependencies are resolved for Python 3.13.
  - **Rationale**: Lock files ensure reproducible builds and must be updated when Python version requirements change to reflect the correct dependency resolution for Python 3.13.
  - **Alternatives Considered**: Not regenerating lock files was rejected as it could lead to dependency resolution issues.
  - **Trade-offs**: None - this is a standard practice when updating Python version requirements.

## Implementation Steps

### Phase 1: Update pyproject.toml Files

**Objective**: Update all `pyproject.toml` files to require Python 3.13 instead of 3.11.

- [x] **Task 1**: Update coverage-summary pyproject.toml
  - [x] Change `requires-python = ">=3.11"` to `requires-python = ">=3.13"` in `.github/scripts/coverage-summary/pyproject.toml`
  - **Files**: `.github/scripts/coverage-summary/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify the file contains the updated requirement
  - **Notes**: Simple string replacement

- [x] **Task 2**: Update create-checksum pyproject.toml
  - [x] Change `requires-python = ">=3.11"` to `requires-python = ">=3.13"` in `.github/scripts/create-checksum/pyproject.toml`
  - **Files**: `.github/scripts/create-checksum/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify the file contains the updated requirement
  - **Notes**: Simple string replacement

- [x] **Task 3**: Update pr-labels pyproject.toml
  - [x] Change `requires-python = ">=3.11"` to `requires-python = ">=3.13"` in `.github/scripts/pr-labels/pyproject.toml`
  - **Files**: `.github/scripts/pr-labels/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify the file contains the updated requirement
  - **Notes**: Simple string replacement; this script has a `uv.lock` file that will be updated in Phase 4

- [x] **Task 4**: Update release-notes pyproject.toml
  - [x] Change `requires-python = ">=3.11"` to `requires-python = ">=3.13"` in `.github/scripts/release-notes/pyproject.toml`
  - **Files**: `.github/scripts/release-notes/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify the file contains the updated requirement
  - **Notes**: Simple string replacement; this script has a `uv.lock` file that will be updated in Phase 4

- [x] **Task 5**: Update release-version pyproject.toml
  - [x] Change `requires-python = ">=3.11"` to `requires-python = ">=3.13"` in `.github/scripts/release-version/pyproject.toml`
  - **Files**: `.github/scripts/release-version/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify the file contains the updated requirement
  - **Notes**: Simple string replacement; this script has a `uv.lock` file that will be updated in Phase 4

- [x] **Task 6**: Update test-summary pyproject.toml
  - [x] Change `requires-python = ">=3.11"` to `requires-python = ">=3.13"` in `.github/scripts/test-summary/pyproject.toml`
  - **Files**: `.github/scripts/test-summary/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify the file contains the updated requirement
  - **Notes**: Simple string replacement

### Phase 2: Update .python-version Files

**Objective**: Create or update `.python-version` files to specify Python 3.13 for all scripts.

- [x] **Task 1**: Create coverage-summary .python-version
  - [x] Create `.github/scripts/coverage-summary/.python-version` with content `3.13`
  - **Files**: `.github/scripts/coverage-summary/.python-version` (new file)
  - **Dependencies**: None
  - **Testing**: Verify the file exists and contains `3.13`
  - **Notes**: New file creation

- [x] **Task 2**: Create create-checksum .python-version
  - [x] Create `.github/scripts/create-checksum/.python-version` with content `3.13`
  - **Files**: `.github/scripts/create-checksum/.python-version` (new file)
  - **Dependencies**: None
  - **Testing**: Verify the file exists and contains `3.13`
  - **Notes**: New file creation

- [x] **Task 3**: Create pr-labels .python-version
  - [x] Create `.github/scripts/pr-labels/.python-version` with content `3.13`
  - **Files**: `.github/scripts/pr-labels/.python-version` (new file)
  - **Dependencies**: None
  - **Testing**: Verify the file exists and contains `3.13`
  - **Notes**: New file creation

- [x] **Task 4**: Update release-notes .python-version
  - [x] Change content from `3.12` to `3.13` in `.github/scripts/release-notes/.python-version`
  - **Files**: `.github/scripts/release-notes/.python-version`
  - **Dependencies**: None
  - **Testing**: Verify the file contains `3.13`
  - **Notes**: Update existing file

- [x] **Task 5**: Create release-version .python-version
  - [x] Create `.github/scripts/release-version/.python-version` with content `3.13`
  - **Files**: `.github/scripts/release-version/.python-version` (new file)
  - **Dependencies**: None
  - **Testing**: Verify the file exists and contains `3.13`
  - **Notes**: New file creation

- [x] **Task 6**: Create test-summary .python-version
  - [x] Create `.github/scripts/test-summary/.python-version` with content `3.13`
  - **Files**: `.github/scripts/test-summary/.python-version` (new file)
  - **Dependencies**: None
  - **Testing**: Verify the file exists and contains `3.13`
  - **Notes**: New file creation

### Phase 3: Update GitHub Actions Workflows

**Objective**: Update the GitHub Actions workflow to install Python 3.13 instead of 3.11.

- [x] **Task 1**: Update pull_request.yaml workflow
  - [x] Change `python-version: '3.11'` to `python-version: '3.13'` in `.github/workflows/pull_request.yaml` (line 226)
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: None
  - **Testing**: Verify the workflow file contains the updated Python version
  - **Notes**: This is in the pre-commit job; other workflows use `uv` which will automatically respect the `requires-python` constraint

### Phase 4: Regenerate uv.lock Files

**Objective**: Regenerate `uv.lock` files for scripts that have them to ensure dependencies are resolved for Python 3.13.

- [x] **Task 1**: Regenerate pr-labels uv.lock
  - [x] Run `uv lock` in `.github/scripts/pr-labels/` directory to regenerate the lock file for Python 3.13
  - **Files**: `.github/scripts/pr-labels/uv.lock`
  - **Dependencies**: Phase 1 Task 3 (pyproject.toml must be updated first)
  - **Testing**: Verify the lock file is updated and dependencies resolve correctly for Python 3.13
  - **Notes**: Requires `uv` to be installed; lock file will be automatically regenerated based on updated `requires-python` constraint

- [x] **Task 2**: Regenerate release-notes uv.lock
  - [x] Run `uv lock` in `.github/scripts/release-notes/` directory to regenerate the lock file for Python 3.13
  - **Files**: `.github/scripts/release-notes/uv.lock`
  - **Dependencies**: Phase 1 Task 4 (pyproject.toml must be updated first)
  - **Testing**: Verify the lock file is updated and dependencies resolve correctly for Python 3.13
  - **Notes**: Requires `uv` to be installed; lock file will be automatically regenerated based on updated `requires-python` constraint

- [x] **Task 3**: Regenerate release-version uv.lock
  - [x] Run `uv lock` in `.github/scripts/release-version/` directory to regenerate the lock file for Python 3.13
  - **Files**: `.github/scripts/release-version/uv.lock`
  - **Dependencies**: Phase 1 Task 5 (pyproject.toml must be updated first)
  - **Testing**: Verify the lock file is updated and dependencies resolve correctly for Python 3.13
  - **Notes**: Requires `uv` to be installed; lock file will be automatically regenerated based on updated `requires-python` constraint

### Phase 5: Verify and Test

**Objective**: Verify all changes are correct and scripts can run with Python 3.13.

- [x] **Task 1**: Verify all changes
  - [x] Verify all 6 `pyproject.toml` files have `requires-python = ">=3.13"`
  - [x] Verify all 6 `.python-version` files exist and contain `3.13`
  - [x] Verify `.github/workflows/pull_request.yaml` has `python-version: '3.13'`
  - [x] Verify all 3 `uv.lock` files have been regenerated (check modification timestamps or content)
  - **Files**: All files modified in previous phases
  - **Dependencies**: All previous phases must be complete
  - **Testing**: Use `grep` or file reading to verify changes
  - **Notes**: This is a verification step to ensure all changes were applied correctly

## Files to Modify/Create
- **New Files**:
  - `.github/scripts/coverage-summary/.python-version` - Python version specification for local development
  - `.github/scripts/create-checksum/.python-version` - Python version specification for local development
  - `.github/scripts/pr-labels/.python-version` - Python version specification for local development
  - `.github/scripts/release-version/.python-version` - Python version specification for local development
  - `.github/scripts/test-summary/.python-version` - Python version specification for local development
- **Modified Files**:
  - `.github/scripts/coverage-summary/pyproject.toml` - Update `requires-python` to `>=3.13`
  - `.github/scripts/create-checksum/pyproject.toml` - Update `requires-python` to `>=3.13`
  - `.github/scripts/pr-labels/pyproject.toml` - Update `requires-python` to `>=3.13`
  - `.github/scripts/pr-labels/uv.lock` - Regenerate for Python 3.13
  - `.github/scripts/release-notes/pyproject.toml` - Update `requires-python` to `>=3.13`
  - `.github/scripts/release-notes/.python-version` - Update from `3.12` to `3.13`
  - `.github/scripts/release-notes/uv.lock` - Regenerate for Python 3.13
  - `.github/scripts/release-version/pyproject.toml` - Update `requires-python` to `>=3.13`
  - `.github/scripts/release-version/uv.lock` - Regenerate for Python 3.13
  - `.github/scripts/test-summary/pyproject.toml` - Update `requires-python` to `>=3.13`
  - `.github/workflows/pull_request.yaml` - Update Python version from `3.11` to `3.13`

## Testing Strategy
- **Unit Tests**: Not applicable - this is a configuration change, not a code change
- **Integration Tests**: Verify that scripts can be executed with Python 3.13:
  - Run `uv sync` in each script directory to verify dependencies resolve correctly
  - Run `uv run python -m <module_name>` for each script to verify they execute without errors
  - Verify that workflows will use Python 3.13 (workflows using `uv` will automatically respect the `requires-python` constraint)
- **Manual Testing**:
  - Run the workflows in GitHub Actions to verify they work correctly with Python 3.13
  - Verify that all scripts execute successfully in CI/CD pipelines
  - Check that pre-commit hooks work with Python 3.13

## Breaking Changes
None - Python 3.13 is backward compatible with code written for Python 3.11+. This change only updates version requirements and does not modify any Python code.

## Migration Guide
Not applicable - no breaking changes. The upgrade is transparent to users and developers. Developers working locally should ensure they have Python 3.13 installed (or use `pyenv`/`uv` which will automatically use the version specified in `.python-version` files).

## Documentation Updates
- [ ] Check if any README files in script directories mention Python version requirements and update them if necessary
- [ ] Verify that no other documentation references Python 3.11 or 3.12 as the required version

## Success Criteria
- All 6 `pyproject.toml` files specify `requires-python = ">=3.13"`
- All 6 scripts have `.python-version` files containing `3.13`
- The `.github/workflows/pull_request.yaml` workflow installs Python 3.13
- All 3 `uv.lock` files have been regenerated for Python 3.13
- All scripts can be executed successfully with Python 3.13 (verified via `uv run`)
- All workflows execute successfully in GitHub Actions with Python 3.13

## Risks and Mitigations
- **Risk**: Dependencies may not be compatible with Python 3.13
  - **Mitigation**: Check dependency compatibility before updating. Most modern Python packages support Python 3.13. If any dependencies are incompatible, they will need to be updated or replaced.

- **Risk**: GitHub Actions runners may not have Python 3.13 available
  - **Mitigation**: Python 3.13 is a stable release and should be available in GitHub Actions. Verify availability before implementation. If not available, wait for GitHub Actions to add support or use a different approach.

- **Risk**: Scripts may use Python features that changed between 3.11/3.12 and 3.13
  - **Mitigation**: Python 3.13 is backward compatible with 3.11+. Review Python 3.13 release notes for any deprecations. Test all scripts after the upgrade to ensure they work correctly.

- **Risk**: Local developers may not have Python 3.13 installed
  - **Mitigation**: The `.python-version` files will help tools like `pyenv` and `uv` automatically use the correct version. Developers can install Python 3.13 using their preferred method. This is a standard upgrade process.

## References
- Related REQ_ document: `plan/25W48/REQ_PYTHON_3_13_UPGRADE.md`
- Related issues: None
- Related PRs: None
- External references:
  - [Python 3.13 Release Notes](https://docs.python.org/3.13/whatsnew/3.13.html)
  - [GitHub Actions setup-python](https://github.com/actions/setup-python)
  - [uv documentation](https://github.com/astral-sh/uv)
