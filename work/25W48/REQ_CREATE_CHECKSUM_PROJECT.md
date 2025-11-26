# Implementation Plan: Convert create-checksum.py to Project Structure

**Status**: ✅ Completed

## Overview
Convert `create-checksum.py` from a standalone script to a proper Python project structure matching the pattern used by other projects in `.github/scripts` (pr-labels, release-notes, release-version, test-summary, coverage-summary). This will improve maintainability, enable proper testing, and provide consistency across all script projects.

## Checklist Summary

### Phase 1: Project Structure Setup
- [x] 3/3 tasks completed

### Phase 2: Code Refactoring and Module Organization
- [x] 2/2 tasks completed

### Phase 3: Testing Infrastructure
- [x] 2/2 tasks completed

### Phase 4: Documentation and Integration Updates
- [x] 3/3 tasks completed

## Context
**Reference**: `plan/25W48/REQ_CREATE_CHECKSUM_PROJECT.md`

Currently, `create-checksum.py` exists as a standalone script in `.github/scripts/` with no project structure, no tests, and no `pyproject.toml` configuration. Other Python projects in `.github/scripts` follow a proper project structure with organized source code, tests, and proper packaging. This inconsistency makes maintenance harder and prevents proper testing of the checksum functionality.

The script is currently used in `.github/workflows/release-build.yaml` with positional arguments. There have been previous issues with data being written incorrectly, which motivates improvements to the CLI interface (using named arguments for clarity) and file writing handling (atomic writes to prevent corruption).

The CLI interface will be updated to use named arguments (`--file`, `--algo`, `--output`) to prevent argument order mistakes and improve clarity. File writing will be improved with atomic writes (write to temporary file, then rename) to prevent partial file corruption if the process is interrupted.

## Goals
- Convert `create-checksum.py` to a proper Python project structure matching other script projects
- Update CLI interface to use named arguments: `--file`, `--algo`, and `--output`
- Implement algorithm selection (currently only sha256, but extensible for future algorithms)
- Improve file writing handling to prevent data corruption (atomic writes, proper error handling)
- Enable comprehensive testing of checksum functionality
- Improve code organization and maintainability
- Enable dependency management through `pyproject.toml`
- Update workflow references to use the new project structure and CLI arguments

## Non-Goals
- Adding new hash algorithms beyond sha256 (infrastructure supports it, but only sha256 is implemented)
- Adding external dependencies (script uses only standard library)
- Modifying other script projects

## Design Decisions

**Project Structure**: Following the established pattern from other script projects
- **Rationale**: Consistency across all script projects improves maintainability and reduces cognitive load when working with multiple projects
- **Alternatives Considered**: Minimal structure (just `pyproject.toml`), different directory layout
- **Trade-offs**: Slightly more files, but matches existing patterns exactly

**Module Organization**: Extract logic into `checksum.py` module with `__main__.py` as entry point
- **Rationale**: Separates business logic from CLI interface, enables better testing, follows Python best practices
- **Alternatives Considered**: Keep all logic in `__main__.py`, split into multiple modules
- **Trade-offs**: More files but better separation of concerns

**CLI Interface**: Change from positional arguments to named arguments (`--file`, `--algo`, `--output`)
- **Rationale**: Named arguments are clearer, prevent argument order mistakes, and enable future extensibility. Addresses previous issues with data being written incorrectly by making the interface explicit.
- **Alternatives Considered**: Keep positional arguments, use different argument names
- **Trade-offs**: Breaking change for workflow, but improves usability and prevents errors

**Testing Framework**: Use pytest with standard library only (no external test dependencies)
- **Rationale**: Matches pattern from `test-summary` project, keeps dependencies minimal
- **Alternatives Considered**: Use unittest, add pytest plugins
- **Trade-offs**: Standard pytest is sufficient for this simple script

**File Writing**: Use atomic writes (write to temporary file, then rename) and create parent directories
- **Rationale**: Prevents partial file corruption if process is interrupted, ensures output directory exists
- **Alternatives Considered**: Direct write, only create parent directories
- **Trade-offs**: Slightly more complex, but prevents data corruption issues

## Implementation Steps

### Phase 1: Project Structure Setup

**Objective**: Create the directory structure and configuration files for the new project

- [x] **Task 1**: Create project directory structure
  - [x] Create `.github/scripts/create-checksum/` directory
  - [x] Create `src/create_checksum/` directory
  - [x] Create `tests/` directory
  - **Files**: New directories
  - **Dependencies**: None
  - **Testing**: Verify directories exist
  - **Notes**: Follow exact structure pattern from other projects

- [x] **Task 2**: Create `pyproject.toml` configuration
  - [x] Add project metadata (name, version, requires-python)
  - [x] Configure empty dependencies list (standard library only)
  - [x] Add dev dependencies (pytest)
  - [x] Configure build system (hatchling)
  - [x] Add pytest configuration
  - **Files**: `.github/scripts/create-checksum/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify `uv sync --extra dev` works
  - **Notes**: Match pattern from `test-summary/pyproject.toml` (simplest example)

- [x] **Task 3**: Create `__init__.py` files
  - [x] Create `src/create_checksum/__init__.py` (can be empty)
  - [x] Create `tests/__init__.py` (can be empty)
  - **Files**:
    - `.github/scripts/create-checksum/src/create_checksum/__init__.py`
    - `.github/scripts/create-checksum/tests/__init__.py`
  - **Dependencies**: Task 1 complete
  - **Testing**: Verify Python recognizes packages
  - **Notes**: Empty files are sufficient for package structure

### Phase 2: Code Refactoring and Module Organization

**Objective**: Extract and organize the script code into proper modules

- [x] **Task 1**: Create `checksum.py` module with core logic
  - [x] Move `calculate_sha256()` function to `checksum.py`
  - [x] Add algorithm selection function (currently only sha256, but extensible)
  - [x] Add function to calculate hash based on algorithm name
  - [x] Add proper module docstring
  - [x] Add function docstrings
  - [x] Ensure functions are properly exported
  - **Files**: `.github/scripts/create-checksum/src/create_checksum/checksum.py`
  - **Dependencies**: Phase 1 complete
  - **Testing**: Verify functions can be imported and work correctly
  - **Notes**: Keep hash calculation behavior identical, add algorithm validation

- [x] **Task 2**: Create `__main__.py` with CLI entry point
  - [x] Move `main()` function and argument parsing to `__main__.py`
  - [x] Update argument parser to use named arguments: `--file`, `--algo`, `--output`
  - [x] Add algorithm validation (currently only sha256 supported)
  - [x] Import hash calculation function from `checksum` module
  - [x] Implement atomic file writing (write to temp file, then rename)
  - [x] Create parent directories for output file if they don't exist
  - [x] Add proper error handling for all file operations
  - [x] Add proper module docstring
  - [x] Ensure `if __name__ == "__main__"` block works correctly
  - **Files**: `.github/scripts/create-checksum/src/create_checksum/__main__.py`
  - **Dependencies**: Task 1 complete
  - **Testing**: Verify CLI works with new argument format
  - **Notes**: CLI interface changes from positional to named arguments

### Phase 3: Testing Infrastructure

**Objective**: Create comprehensive tests for the checksum functionality

- [x] **Task 1**: Create test file structure
  - [x] Create `tests/test_checksum.py` for core logic tests
  - [x] Create `tests/conftest.py` for pytest fixtures (if needed)
  - **Files**:
    - `.github/scripts/create-checksum/tests/test_checksum.py`
    - `.github/scripts/create-checksum/tests/conftest.py` (if needed)
  - **Dependencies**: Phase 2 complete
  - **Testing**: Verify pytest can discover and run tests
  - **Notes**: Follow pattern from `test-summary/tests/`

- [x] **Task 2**: Write comprehensive tests
  - [x] Test hash calculation function with valid files
  - [x] Test hash calculation with different file sizes
  - [x] Test algorithm selection and validation (sha256 valid, invalid algorithms rejected)
  - [x] Test CLI with `--file`, `--algo`, `--output` arguments
  - [x] Test CLI with valid binary file
  - [x] Test CLI with missing binary file (error handling)
  - [x] Test CLI with unreadable file (error handling)
  - [x] Test CLI with invalid algorithm (error handling)
  - [x] Test CLI with missing required arguments (error handling)
  - [x] Test CLI with unwritable output path (error handling)
  - [x] Test atomic file writing (verify temp file is created and renamed)
  - [x] Test parent directory creation for output file
  - [x] Test checksum file output format (matches expected format)
  - [x] Test stdout output matches file output
  - [x] Test exit codes for success and error cases
  - **Files**: `.github/scripts/create-checksum/tests/test_checksum.py`
  - **Dependencies**: Task 1 complete
  - **Testing**: Run `uv run pytest -v` and verify all tests pass
  - **Notes**: Use temporary files for test fixtures, verify exact checksum format, test atomic write behavior

### Phase 4: Documentation and Integration Updates

**Objective**: Update documentation and workflow references to use new project structure

- [x] **Task 1**: Create `README.md` for the project
  - [x] Add project description
  - [x] Add installation instructions (using `uv`)
  - [x] Add usage instructions with new CLI interface (`--file`, `--algo`, `--output`)
  - [x] Document algorithm selection (currently only sha256)
  - [x] Add examples of CLI usage
  - [x] Add testing instructions
  - [x] Add constraints and requirements section
  - [x] Document dependencies (none, standard library only)
  - [x] Document atomic file writing behavior
  - **Files**: `.github/scripts/create-checksum/README.md`
  - **Dependencies**: Phase 2 complete
  - **Testing**: Verify README is accurate and complete
  - **Notes**: Follow pattern from `pr-labels/README.md` or `test-summary/README.md`

- [x] **Task 2**: Update workflow reference
  - [x] Update `.github/workflows/release-build.yaml` to use new project structure
  - [x] Change from `python3 .github/scripts/create-checksum.py` to `uv run python -m create_checksum` (or equivalent)
  - [x] Update CLI arguments from positional to named: `--file`, `--algo sha256`, `--output`
  - [x] Ensure working directory is set correctly if needed
  - [x] Verify workflow still works correctly
  - **Files**: `.github/workflows/release-build.yaml`
  - **Dependencies**: Phase 2 complete
  - **Testing**: Verify workflow step works (may need manual testing in CI)
  - **Notes**: CLI arguments change from positional to named format

- [x] **Task 3**: Remove old script file
  - [x] Delete `.github/scripts/create-checksum.py`
  - [x] Verify no other references exist
  - **Files**: `.github/scripts/create-checksum.py` (delete)
  - **Dependencies**: Task 2 complete and verified
  - **Testing**: Verify no broken references
  - **Notes**: Only delete after confirming new structure works

## Files to Modify/Create
- **New Files**:
  - `.github/scripts/create-checksum/pyproject.toml` - Project configuration
  - `.github/scripts/create-checksum/README.md` - Project documentation
  - `.github/scripts/create-checksum/src/create_checksum/__init__.py` - Package init
  - `.github/scripts/create-checksum/src/create_checksum/__main__.py` - CLI entry point
  - `.github/scripts/create-checksum/src/create_checksum/checksum.py` - Core checksum logic
  - `.github/scripts/create-checksum/tests/__init__.py` - Test package init
  - `.github/scripts/create-checksum/tests/test_checksum.py` - Test suite
  - `.github/scripts/create-checksum/tests/conftest.py` - Pytest fixtures (if needed)
- **Modified Files**:
  - `.github/workflows/release-build.yaml` - Update script invocation to use new project structure
- **Deleted Files**:
  - `.github/scripts/create-checksum.py` - Replaced by project structure

## Testing Strategy
- **Unit Tests**: Test `calculate_sha256()` function with various file inputs, verify correct hash calculation, test error handling
- **Integration Tests**: Test full CLI workflow with real files, verify output format, test error cases (missing file, unreadable file, unwritable output)
- **Manual Testing**: Verify workflow step works in GitHub Actions (informational only, not part of AI tasks)

## Breaking Changes
- **Workflow Update Required**: The workflow file must be updated to use the new project structure and invocation method (`uv run python -m create_checksum` instead of `python3 .github/scripts/create-checksum.py`)
- **CLI Interface Change**: The CLI interface changes from positional arguments to named arguments:
  - Old: `python3 create-checksum.py <binary> <output>`
  - New: `uv run python -m create_checksum --file <file> --algo sha256 --output <output>`
- **Output Format**: The checksum output format remains identical, ensuring compatibility with existing tools that read the checksum files

## Migration Guide
1. Update workflow file to use new invocation: `uv run python -m create_checksum` (from within `.github/scripts/create-checksum/` directory)
2. Update CLI arguments from positional to named format:
   - Old: `python3 create-checksum.py target/${{ matrix.target }}/release/${{ matrix.artifact_name }} target/${{ matrix.target }}/release/${{ matrix.artifact_name }}.sha256`
   - New: `uv run python -m create_checksum --file target/${{ matrix.target }}/release/${{ matrix.artifact_name }} --algo sha256 --output target/${{ matrix.target }}/release/${{ matrix.artifact_name }}.sha256`
3. Ensure `uv` is available in the workflow environment (should already be available if other script projects use it)
4. Verify the working directory is set correctly, or use absolute paths
5. Test the workflow step to ensure it works correctly

## Documentation Updates
- [x] Create `README.md` for create-checksum project
- [x] Update workflow file with new invocation method
- [x] Add doc comments to module and functions
- [x] No updates needed to main project documentation (internal script)

## Success Criteria
- Project structure matches pattern from other script projects (pr-labels, test-summary, etc.)
- CLI interface updated to use named arguments (`--file`, `--algo`, `--output`)
- Algorithm selection implemented (sha256 supported, extensible for future algorithms)
- Atomic file writing implemented to prevent data corruption
- Parent directory creation for output files implemented
- All original functionality preserved (hash calculation, behavior, output format)
- Comprehensive test coverage for checksum calculation, algorithm selection, and error handling
- Tests pass with `uv run pytest -v`
- Workflow updated with new CLI arguments and verified to work correctly
- README.md created with complete documentation including new CLI interface
- Old script file removed after migration verified

## Risks and Mitigations
- **Risk**: Workflow may fail if invocation method is incorrect
  - **Mitigation**: Test workflow step carefully, verify `uv` is available, check working directory
- **Risk**: CLI argument changes may cause workflow failures if not updated correctly
  - **Mitigation**: Update workflow with new named arguments, test with same file paths as original script, verify argument parsing
- **Risk**: Atomic file writing might fail on some filesystems or with permission issues
  - **Mitigation**: Test atomic write behavior, ensure proper error handling, fallback to direct write if atomic write fails (with warning)
- **Risk**: Import paths might not work correctly in package structure
  - **Mitigation**: Follow exact pattern from other projects, test imports locally before committing
- **Risk**: Algorithm validation might reject valid use cases
  - **Mitigation**: Only validate known algorithms, provide clear error messages for invalid algorithms

## References
- Related REQ_ document: `plan/25W48/REQ_CREATE_CHECKSUM_PROJECT.md`
- Reference projects:
  - `.github/scripts/pr-labels/` - Full project structure example
  - `.github/scripts/test-summary/` - Simple project structure example (no external deps)
  - `.github/scripts/release-notes/` - Another project structure example
- Current script: `.github/scripts/create-checksum.py`
- Workflow usage: `.github/workflows/release-build.yaml` (line 240)
