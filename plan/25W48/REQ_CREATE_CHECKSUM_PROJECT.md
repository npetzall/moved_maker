# REQ: Convert create-checksum.py to Project Structure

**Status**: ✅ Completed

## Overview
Convert `create-checksum.py` from a standalone script to a proper Python project structure matching the other projects in `.github/scripts` (pr-labels, release-notes, release-version, test-summary).

## Motivation
Currently, `create-checksum.py` is a standalone script file, while other Python projects in `.github/scripts` follow a proper project structure with `pyproject.toml`, organized source code, tests, and proper packaging. Converting it to match this structure will improve maintainability, enable proper testing, and provide consistency across all script projects.

## Current Behavior
`create-checksum.py` exists as a single standalone Python script in `.github/scripts/` with no project structure, no tests, and no `pyproject.toml` configuration. It currently uses positional arguments: `binary` and `output`.

## Proposed Behavior
Convert `create-checksum.py` to a project structure similar to other projects:
- Create a `create-checksum/` directory
- Move script code to `src/create_checksum/` with proper module structure
- Add `pyproject.toml` with project metadata and dependencies
- Create `tests/` directory with test files
- Add `README.md` documenting the project
- Update CLI interface to use named arguments: `--file`, `--algo`, and `--output`
- Implement algorithm selection (currently only sha256, but extensible for future algorithms)
- Improve file writing handling to prevent data corruption issues (atomic writes, proper error handling, create parent directories)
- Update any references to the script in workflows or documentation
- Update usage instructions to reflect the new project structure and invocation method

The new structure should match the pattern:
```
create-checksum/
  pyproject.toml
  README.md
  src/
    create_checksum/
      __init__.py
      __main__.py
      checksum.py (or similar module name)
  tests/
    __init__.py
    test_checksum.py
```

## Use Cases
- Maintain consistency across all Python projects in `.github/scripts`
- Enable proper testing of checksum functionality
- Improve code organization and maintainability
- Allow for future enhancements with proper project structure
- Enable dependency management through pyproject.toml

## Implementation Considerations
- Extract main logic into a proper module structure
- Create `__main__.py` to maintain CLI entry point
- Add `pyproject.toml` with appropriate project metadata
- Update CLI interface to use named arguments: `--file`, `--algo`, and `--output`
- Implement algorithm selection with validation (currently only sha256 supported)
- Implement atomic file writing to prevent data corruption (write to temporary file, then rename)
- Create parent directories for output file if they don't exist
- Add proper error handling for file operations (reading input, writing output)
- Write tests for checksum calculation, algorithm selection, and file handling
- Update any GitHub Actions workflows that reference the script with new CLI arguments
- Update usage instructions and documentation to reflect new project structure and invocation
- Follow the same patterns used in other script projects (pr-labels, release-notes, etc.)

## Alternatives Considered
- **Keep as standalone script**: Rejected - inconsistent with other projects and lacks testing capability
- **Minimal project structure**: Rejected - should match the full structure of other projects for consistency
- **Different project name**: Rejected - `create-checksum` matches the naming pattern of other projects

## Impact
- **Breaking Changes**: Yes - CLI interface changes from positional arguments to named arguments (`--file`, `--algo`, `--output`). Workflow references must be updated to use new argument format.
- **Documentation**: Update any documentation referencing the script path, update usage instructions to reflect new project structure and CLI arguments, add README.md for the new project
- **Testing**: Add comprehensive tests for checksum functionality, algorithm selection, and file writing (including atomic write behavior)
- **Dependencies**: No new dependencies required (uses standard library only)
- **File Writing Improvements**: Atomic writes prevent partial file corruption, parent directory creation ensures output file can be written successfully

## References
- Related projects: pr-labels, release-notes, release-version, test-summary (for structure reference)
- Current script: `.github/scripts/create-checksum.py`
