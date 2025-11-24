# Implementation Plan: BUG_RELEASE_NOTES_NOT_FOUND

**Status**: ✅ Complete

## Overview
Fix the GitHub Release creation failure by updating the release notes Python script to write the `release_notes.md` file to the workspace root instead of the script's current working directory. The script will use a recursive function to find the workspace root by traversing up the directory tree looking for `Cargo.toml` as a marker file.

## Checklist Summary

### Phase 1: Implement workspace root detection
- [x] 2/2 tasks completed

### Phase 2: Update file writing logic
- [x] 1/1 tasks completed

### Phase 3: Testing and verification
- [x] 1/2 tasks completed (unit tests done, manual verification is informational)

## Context

Related bug report: `plan/25W48/BUG_RELEASE_NOTES_NOT_FOUND.md`

**Current State**: The release notes script writes `release_notes.md` using a relative path, which causes the file to be created in `.github/scripts/release-notes/` directory when the workflow changes directory before running the script. The `gh release create` command expects the file at the workspace root and fails with "no such file or directory" error.

**Root Cause**: Working directory mismatch - the script uses `Path("release_notes.md")` which creates the file relative to the current working directory, not the workspace root.

## Goals
- Fix the release notes file path issue so releases can be created successfully
- Make the script resilient to working directory changes
- Make the script resilient to script relocation (no hardcoded path depths)
- Use `GITHUB_WORKSPACE` environment variable when available (automatically set by GitHub Actions)
- Provide clear error messages if workspace root cannot be determined

## Non-Goals
- Modifying the GitHub Actions workflow (no workflow changes needed)
- Changing the script's directory structure
- Adding new dependencies

## Design Decisions

- **Recursive workspace root detection**: Use a recursive function to traverse up the directory tree looking for `Cargo.toml` as a marker file
  - **Rationale**: This approach is resilient to script relocation and doesn't rely on hardcoded path depths. It works regardless of where the script is located in the repository structure.
  - **Alternatives Considered**:
    - Hardcoded path calculation (e.g., `Path.cwd().parent.parent.parent`) - rejected because it breaks if script is moved
    - Using `Path.cwd()` to find workspace root - rejected because it depends on current working directory which changes in the workflow
  - **Trade-offs**: Slightly more complex than hardcoded paths, but much more robust

- **Primary use of GITHUB_WORKSPACE environment variable**: Check `GITHUB_WORKSPACE` first before falling back to recursive search
  - **Rationale**: `GITHUB_WORKSPACE` is automatically set by GitHub Actions and points directly to the workspace root, making it the most reliable source. It's also faster than traversing the directory tree.
  - **Alternatives Considered**:
    - Always use recursive search - rejected because it's less efficient when `GITHUB_WORKSPACE` is available
    - Require `GITHUB_WORKSPACE` to be set - rejected because we want the script to work in local development environments
  - **Trade-offs**: None - this is the best of both worlds

- **Using `__file__` instead of `Path.cwd()`**: Determine script location using `__file__` for the fallback search
  - **Rationale**: `__file__` always points to the script's actual location, independent of the current working directory. This ensures the recursive search starts from the correct location.
  - **Alternatives Considered**:
    - Using `Path.cwd()` - rejected because it depends on where the script is executed from
  - **Trade-offs**: None

- **Error handling with RuntimeError**: Raise `RuntimeError` with descriptive message if workspace root cannot be determined
  - **Rationale**: Provides clear feedback about what went wrong and how to fix it. Allows the script to fail gracefully with a non-zero exit code.
  - **Alternatives Considered**:
    - Return None and handle silently - rejected because silent failures are harder to debug
    - Use a default path - rejected because writing to the wrong location would cause the same bug
  - **Trade-offs**: None

## Implementation Steps

### Phase 1: Implement workspace root detection

**Objective**: Add helper functions to detect the workspace root directory using `GITHUB_WORKSPACE` environment variable and recursive `Cargo.toml` search.

- [x] **Task 1**: Add `find_workspace_root()` recursive function
  - [x] Add function before `main()` function in `__main__.py`
  - [x] Implement recursive traversal up directory tree
  - [x] Check for `Cargo.toml` marker file at each level
  - [x] Handle base case (filesystem root reached)
  - [x] Add docstring with function description, args, and return value
  - [x] Add type hints (`start_path: Path` -> `Path | None`)
  - **Files**: `.github/scripts/release-notes/src/release_notes/__main__.py`
  - **Dependencies**: None
  - **Testing**: Verify function finds workspace root when `Cargo.toml` exists, returns `None` when not found
  - **Notes**: Function should use `Path.resolve()` to handle symlinks and relative paths

- [x] **Task 2**: Add `get_workspace_root()` function
  - [x] Add function before `main()` function in `__main__.py`
  - [x] Check `GITHUB_WORKSPACE` environment variable first
  - [x] Validate that `GITHUB_WORKSPACE` path exists and is a directory
  - [x] Fallback to recursive search using `__file__` to get script location
  - [x] Raise `RuntimeError` with descriptive message if workspace root cannot be found
  - [x] Add docstring with function description, priority order, return value, and exceptions
  - [x] Add type hints (returns `Path`, raises `RuntimeError`)
  - **Files**: `.github/scripts/release-notes/src/release_notes/__main__.py`
  - **Dependencies**: `find_workspace_root()` function from Task 1
  - **Testing**: Verify function uses `GITHUB_WORKSPACE` when set, falls back to recursive search when not set, raises error when neither works
  - **Notes**: Should print warning to stderr if `GITHUB_WORKSPACE` is set but points to non-existent directory

### Phase 2: Update file writing logic

**Objective**: Replace the relative path file writing with absolute path using workspace root detection.

- [x] **Task 1**: Update file writing code to use workspace root
  - [x] Replace lines 100-103 in `__main__.py`
  - [x] Wrap workspace root detection and file writing in try/except block
  - [x] Call `get_workspace_root()` to get workspace root path
  - [x] Construct absolute path: `workspace_root / "release_notes.md"`
  - [x] Write release notes to the absolute path
  - [x] Add print statement showing where file was written
  - [x] Handle `RuntimeError` exception and return error code 1
  - [x] Print error message to stderr on failure
  - **Files**: `.github/scripts/release-notes/src/release_notes/__main__.py`
  - **Dependencies**: `get_workspace_root()` function from Phase 1
  - **Testing**: Verify file is written to workspace root, verify error handling works correctly
  - **Notes**: Should maintain existing behavior for `GITHUB_OUTPUT` writing (lines 91-98)

### Phase 3: Testing and verification

**Objective**: Verify the fix works correctly in different scenarios and doesn't break existing functionality.

- [x] **Task 1**: Create unit tests for workspace root detection functions
  - [x] Create test file for `find_workspace_root()` function
  - [x] Test finding workspace root when `Cargo.toml` exists
  - [x] Test returning `None` when `Cargo.toml` not found (reached filesystem root)
  - [x] Create test file for `get_workspace_root()` function
  - [x] Test using `GITHUB_WORKSPACE` when set and valid
  - [x] Test falling back to recursive search when `GITHUB_WORKSPACE` not set
  - [x] Test raising `RuntimeError` when workspace root cannot be determined
  - [x] Test warning message when `GITHUB_WORKSPACE` points to non-existent directory
  - **Files**: `.github/scripts/release-notes/tests/test_workspace_root.py` (new file)
  - **Dependencies**: Implementation from Phases 1 and 2
  - **Testing**: Run tests with `pytest` or `uv run pytest`
  - **Notes**: May need to use temporary directories and mock `__file__` for testing

- [ ] **Task 2**: Manual verification steps
  - [ ] Verify script runs successfully in local development environment
  - [ ] Verify script writes `release_notes.md` to workspace root when run from script directory
  - [ ] Verify script writes `release_notes.md` to workspace root when run from different directories
  - [ ] Verify script works when `GITHUB_WORKSPACE` environment variable is set
  - [ ] Verify script works when `GITHUB_WORKSPACE` environment variable is not set
  - [ ] Verify error handling when workspace root cannot be found
  - **Files**: N/A (manual testing)
  - **Dependencies**: Implementation from Phases 1 and 2
  - **Testing**: Run script manually from different directories, test with/without `GITHUB_WORKSPACE`
  - **Notes**: This is informational for manual verification after implementation

## Files to Modify/Create
- **Modified Files**:
  - `.github/scripts/release-notes/src/release_notes/__main__.py` - Add workspace root detection functions and update file writing logic
- **New Files**:
  - `.github/scripts/release-notes/tests/test_workspace_root.py` - Unit tests for workspace root detection functions

## Testing Strategy
- **Unit Tests**: Test `find_workspace_root()` and `get_workspace_root()` functions with various directory structures, with/without `GITHUB_WORKSPACE` set, and error cases
- **Integration Tests**: Verify the script writes `release_notes.md` to the correct location when run from different directories
- **Manual Testing**: Test in GitHub Actions workflow to verify release creation succeeds, test locally from different directories

## Breaking Changes
None - This is a bug fix that doesn't change the script's external interface or behavior from the user's perspective.

## Migration Guide
N/A - No breaking changes.

## Documentation Updates
- [x] Update docstrings in `__main__.py` to document the new workspace root detection behavior
- [x] Ensure existing docstrings are clear and complete

## Success Criteria
- Release notes file is created at workspace root (`release_notes.md`) regardless of current working directory
- Script works correctly when run from `.github/scripts/release-notes/` directory (current workflow behavior)
- Script works correctly when run from workspace root or any other directory
- Script uses `GITHUB_WORKSPACE` when available (GitHub Actions environment)
- Script falls back to recursive search when `GITHUB_WORKSPACE` is not set (local development)
- Script provides clear error messages if workspace root cannot be determined
- GitHub Release creation succeeds without "no such file or directory" error
- All existing functionality (GITHUB_OUTPUT writing) continues to work

## Risks and Mitigations
- **Risk**: Recursive search might be slow in very deep directory structures
  - **Mitigation**: Primary use of `GITHUB_WORKSPACE` avoids this in CI/CD. Recursive search is only a fallback for local development.

- **Risk**: Script might find wrong `Cargo.toml` if multiple exist in parent directories
  - **Mitigation**: The recursive search starts from the script's location and traverses up, so it will find the closest `Cargo.toml` to the script, which should be the workspace root. In practice, there should only be one `Cargo.toml` at the workspace root.

- **Risk**: Script might fail if `Cargo.toml` is missing (edge case)
  - **Mitigation**: Clear error message guides user to either set `GITHUB_WORKSPACE` or ensure `Cargo.toml` exists. This is an edge case that should not occur in normal usage.

## References
- Related BUG document: `plan/25W48/BUG_RELEASE_NOTES_NOT_FOUND.md`
- GitHub Actions `GITHUB_WORKSPACE` variable: https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables
- Python `pathlib.Path` documentation: https://docs.python.org/3/library/pathlib.html
- Python `__file__` variable: https://docs.python.org/3/reference/import.html#__file__
