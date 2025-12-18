# Implementation Plan: Fix Coverage Summary JSON Parsing

**Status**: ✅ Completed

## Overview
Fix the coverage summary script to correctly parse the JSON output from `cargo llvm-cov report --json`, which uses a dictionary structure with a `data` key containing the array, rather than a direct array. Additionally, update the workflow to use absolute paths via `${{ github.workspace }}` to ensure reliable file path resolution.

## Checklist Summary

### Phase 1: Fix Parser to Handle Actual JSON Format
- [x] 2/2 tasks completed

### Phase 2: Update Workflow to Use Absolute Paths
- [x] 1/1 tasks completed

### Phase 3: Add Test Data and Update Tests
- [x] 2/2 tasks completed

## Context
Reference to corresponding BUG_ document: `plan/25W48/BUG_COVERAGE_SUMMARY_JSON_PARSING.md`

**Current State**: The coverage summary parser expects a direct array format `[{...}]`, but `cargo llvm-cov report --json` actually outputs a dictionary format `{"data": [{...}]}`. The parser validation at line 74-77 in `parser.py` fails with "Invalid JSON structure: expected non-empty array, got <class 'dict'>". Additionally, the workflow uses relative paths (`../../../coverage.json`) which may cause issues with path resolution.

**Problem**:
1. The parser fails to parse the actual JSON format from cargo-llvm-cov
2. The workflow uses relative paths that may not resolve correctly in all contexts
3. No test data exists that matches the actual cargo-llvm-cov output format

**Evidence**: The jq script at `.config/coverage-threshold-check.jq` correctly uses `.data[0].totals`, confirming the actual structure has a `data` key.

## Goals
- Fix the parser to correctly handle the dictionary format with `data` key
- Update the workflow to use `${{ github.workspace }}` for absolute paths
- Add test coverage JSON file matching the actual cargo-llvm-cov format
- Update tests to validate the parser works with the actual format
- Ensure backward compatibility or clear migration path if format changes

## Non-Goals
- Changing the cargo-llvm-cov output format (we must adapt to it)
- Modifying the jq script (it already works correctly)
- Changing the overall structure of the coverage summary script

## Design Decisions

**Decision 1: Handle both dictionary and array formats for robustness**
- **Rationale**: While the current cargo-llvm-cov output uses the dictionary format, handling both formats makes the parser more robust to potential format changes or different versions
- **Alternatives Considered**:
  - Only support dictionary format: Simpler but less flexible
  - Only support array format: Would break with current cargo-llvm-cov
- **Trade-offs**: Slightly more complex validation logic, but provides better compatibility

**Decision 2: Use `${{ github.workspace }}` for absolute paths in workflow**
- **Rationale**: Absolute paths eliminate ambiguity and ensure files are found regardless of working directory changes in the workflow
- **Alternatives Considered**:
  - Keep relative paths: Simpler but error-prone if working directory changes
  - Use `$GITHUB_WORKSPACE` environment variable: Less explicit, requires shell variable expansion
- **Trade-offs**: Slightly more verbose workflow YAML, but more reliable

**Decision 3: Add real format test data to tests/fixtures/**
- **Rationale**: Having actual format test data allows testing the parser with real-world data structure and serves as documentation of the expected format
- **Alternatives Considered**:
  - Only use in-memory fixtures: Less realistic, doesn't test file I/O
  - Generate dynamically in tests: More complex, less reproducible
- **Trade-offs**: Adds a file to the repository, but provides better test coverage and documentation

## Implementation Steps

### Phase 1: Fix Parser to Handle Actual JSON Format

**Objective**: Update the parser to correctly handle the dictionary format with `data` key that cargo-llvm-cov actually produces.

- [x] **Task 1**: Update parser validation logic to handle dictionary format
  - [x] Modify `parse_coverage_json` in `parser.py` to check if root is a dict with `data` key
  - [x] Extract the array from `data` key if present, otherwise use root directly (for backward compatibility)
  - [x] Update validation to check for non-empty array after extraction
  - [x] Update error messages to be more descriptive about expected formats
  - **Files**: `.github/scripts/coverage-summary/src/coverage_summary/parser.py`
  - **Dependencies**: None
  - **Testing**: Run existing tests, add new test for dictionary format
  - **Notes**: Should maintain backward compatibility with array format if possible

- [x] **Task 2**: Update parser docstring and error handling
  - [x] Update function docstring to document both supported formats
  - [x] Improve error messages to guide users if format is unexpected
  - [x] Add type hints and comments for clarity
  - **Files**: `.github/scripts/coverage-summary/src/coverage_summary/parser.py`
  - **Dependencies**: Task 1
  - **Testing**: Verify error messages are helpful
  - **Notes**: Error messages should help diagnose format issues

### Phase 2: Update Workflow to Use Absolute Paths

**Objective**: Replace relative paths with absolute paths using `${{ github.workspace }}` in the workflow.

- [x] **Task 1**: Update workflow step to use absolute paths
  - [x] Replace `../../../coverage.json` with `${{ github.workspace }}/coverage.json`
  - [x] Replace `../../../changed-files.txt` with `${{ github.workspace }}/changed-files.txt`
  - [x] Verify the `cd .github/scripts/coverage-summary` step doesn't interfere with absolute paths
  - [x] Test that paths resolve correctly
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: None
  - **Testing**: Verify workflow step can find files with absolute paths
  - **Notes**: The `cd` command changes working directory, but absolute paths should still work

### Phase 3: Add Test Data and Update Tests

**Objective**: Add real format test data and update tests to validate the parser works with actual cargo-llvm-cov format.

- [x] **Task 1**: Add test fixture file with actual format
  - [x] Create `tests/fixtures/coverage.json` with dictionary format matching cargo-llvm-cov output
  - [x] Use realistic coverage data matching the structure from the BUG document
  - [x] Ensure the file is properly formatted JSON
  - **Files**: `.github/scripts/coverage-summary/tests/fixtures/coverage.json`
  - **Dependencies**: None
  - **Testing**: Verify JSON is valid and matches expected structure
  - **Notes**: File already created, verify it matches actual format

- [x] **Task 2**: Add test case for dictionary format parsing
  - [x] Create test function `test_parse_coverage_json_dict_format` in `test_parser.py`
  - [x] Load and parse the fixture file from `tests/fixtures/coverage.json`
  - [x] Verify parser correctly extracts data from `data` key
  - [x] Verify all metrics are parsed correctly (lines, branches, functions)
  - [x] Verify file-level coverage is parsed correctly
  - **Files**: `.github/scripts/coverage-summary/tests/test_parser.py`
  - **Dependencies**: Task 1, Phase 1
  - **Testing**: Run pytest to verify test passes
  - **Notes**: This test validates the fix works with real format

## Files to Modify/Create
- **New Files**:
  - `.github/scripts/coverage-summary/tests/fixtures/coverage.json` - Test data matching actual cargo-llvm-cov format
- **Modified Files**:
  - `.github/scripts/coverage-summary/src/coverage_summary/parser.py` - Update to handle dictionary format with `data` key
  - `.github/scripts/coverage-summary/tests/test_parser.py` - Add test for dictionary format
  - `.github/workflows/pull_request.yaml` - Update to use `${{ github.workspace }}` for absolute paths

## Testing Strategy
- **Unit Tests**:
  - Add test case that loads the fixture file and verifies parsing works
  - Verify existing tests still pass (backward compatibility)
  - Test error handling for invalid formats
- **Integration Tests**:
  - Test the parser with the actual format from cargo-llvm-cov
  - Verify workflow step can find files using absolute paths
- **Manual Testing**:
  - Run the coverage summary script locally with a real coverage.json file
  - Verify the workflow step works in CI

## Breaking Changes
- None - the parser will support both formats (dictionary and array) for backward compatibility

## Migration Guide
N/A - No breaking changes. The parser will automatically detect and handle both formats.

## Documentation Updates
- [x] Update parser docstring to document both supported formats
- [ ] Update README if it mentions the expected JSON format
- [x] Add comments in parser code explaining the format handling

## Success Criteria
- Parser successfully parses JSON files with dictionary format (`{"data": [...]}`)
- Parser maintains backward compatibility with array format (`[...]`)
- Workflow uses absolute paths via `${{ github.workspace }}`
- Test coverage includes validation of dictionary format parsing
- All existing tests continue to pass
- Coverage summary generates successfully in CI workflow

## Risks and Mitigations
- **Risk**: Parser might break if cargo-llvm-cov format changes again
  - **Mitigation**: Support both formats, add clear error messages, and test with actual format
- **Risk**: Absolute paths might not work if `github.workspace` is not set
  - **Mitigation**: GitHub Actions always sets `github.workspace`, but we can add a fallback to relative paths if needed
- **Risk**: Tests might fail if fixture file format doesn't match actual output
  - **Mitigation**: Generate fixture from actual cargo-llvm-cov output and verify structure matches

## References
- Related BUG_ document: `plan/25W48/BUG_COVERAGE_SUMMARY_JSON_PARSING.md`
- Related code: `.config/coverage-threshold-check.jq` (correctly uses `.data[0].totals`)
- Related implementation: `work/25W48/REQ_CODE_COVERAGE_REPORTING.md` (original coverage summary implementation)
