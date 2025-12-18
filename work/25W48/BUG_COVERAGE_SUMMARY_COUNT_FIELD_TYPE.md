# Implementation Plan: Fix Coverage Summary Count Field Type Parsing

**Status**: ✅ Complete

## Overview
Fix the coverage summary parser to correctly handle the actual JSON structure from `cargo llvm-cov report --json`, where `count` is an integer (not a dictionary) and file metrics are under `summary` (not directly under the file object).

## Checklist Summary

### Phase 1: Fix Parser Implementation
- [x] 2/2 tasks completed

### Phase 2: Update Test Fixtures
- [x] 2/2 tasks completed

### Phase 3: Verification
- [x] 1/1 tasks completed

## Context
Reference to corresponding BUG_ document: `plan/25W48/BUG_COVERAGE_SUMMARY_COUNT_FIELD_TYPE.md`

The parser currently expects:
- `totals.*.count` to be a dictionary with `covered`, `partial`, `missed` keys
- File metrics to be directly under `files[].lines`, `files[].branches`, etc.

But the actual `cargo llvm-cov report --json` output has:
- `totals.*.count` as an integer (total count)
- `totals.*.covered` as a direct field (covered count)
- File metrics under `files[].summary.lines`, `files[].summary.branches`, etc.

## Goals
- Fix `extract_metrics()` to handle integer `count` and direct `covered` field
- Fix `extract_file_metrics()` to access metrics from `summary` key
- Update test fixtures to match actual cargo-llvm-cov JSON structure
- Ensure all existing tests pass with corrected structure

## Non-Goals
- Changing the CoverageMetrics dataclass structure
- Modifying the generator or other parts of the coverage-summary tool
- Adding new features or functionality

## Design Decisions

**Decision 1**: Handle integer `count` and direct `covered` field in totals
  - **Rationale**: The actual cargo-llvm-cov output uses `count` as an integer representing total items, and `covered` as a separate field. The `count` field IS the total, not a dictionary.
  - **Alternatives Considered**: Could have tried to support both formats, but the actual format is well-defined and consistent.
  - **Trade-offs**: This is a breaking change for test fixtures, but aligns with reality.

**Decision 2**: Access file metrics from `summary` key
  - **Rationale**: Files have a `summary` object containing `lines`, `branches`, and `functions` metrics, not directly on the file object.
  - **Alternatives Considered**: Could check both locations, but the structure is consistent in cargo-llvm-cov output.
  - **Trade-offs**: Requires updating all test fixtures, but ensures correctness.

**Decision 3**: Calculate total from `count` directly for totals
  - **Rationale**: For totals, `count` is the total number of items. For branches, we may need to handle `notcovered` field.
  - **Alternatives Considered**: Could calculate from `covered + partial + missed`, but `count` is authoritative.
  - **Trade-offs**: Simpler logic, aligns with actual data structure.

## Implementation Steps

### Phase 1: Fix Parser Implementation

**Objective**: Update parser to handle actual cargo-llvm-cov JSON structure

- [x] **Task 1**: Fix `extract_metrics()` function for totals
  - [x] Update line 112: Change `count = metric_data.get("count", {})` to `count = int(metric_data.get("count", 0))`
  - [x] Update line 113: Change `covered = int(count.get("covered", 0))` to `covered = int(metric_data.get("covered", 0))`
  - [x] Update line 114: Change total calculation to use `count` directly (for lines/functions) or handle `notcovered` for branches
  - **Files**: `.github/scripts/coverage-summary/src/coverage_summary/parser.py`
  - **Dependencies**: None
  - **Testing**: Run parser tests after fixture updates
  - **Notes**: For branches, check if `notcovered` field exists, otherwise use `count - covered`

- [x] **Task 2**: Fix `extract_file_metrics()` function for files
  - [x] Update line 134: Check for `summary` key in `file_data` instead of direct `file_key`
  - [x] Update line 137: Access `metric_data` from `file_data["summary"][file_key]` instead of `file_data[file_key]`
  - [x] Update lines 139-145: Use same logic as totals (integer `count`, direct `covered`)
  - **Files**: `.github/scripts/coverage-summary/src/coverage_summary/parser.py`
  - **Dependencies**: None
  - **Testing**: Run parser tests after fixture updates
  - **Notes**: Return zero metrics if `summary` key is missing

### Phase 2: Update Test Fixtures

**Objective**: Update test fixtures to match actual cargo-llvm-cov JSON structure

- [x] **Task 1**: Update `conftest.py` fixtures
  - [x] Update `sample_coverage_json_high`: Change `count` from dict to int, add `covered` as direct field, move file metrics under `summary`
  - [x] Update `sample_coverage_json_low`: Same changes
  - [x] Update `sample_coverage_json_no_branches`: Same changes, handle `notcovered` for branches
  - [x] Update `sample_coverage_json_empty`: Same changes
  - **Files**: `.github/scripts/coverage-summary/tests/conftest.py`
  - **Dependencies**: Parser fixes must be complete
  - **Testing**: Run all parser tests to verify
  - **Notes**: Ensure test expectations match new structure (e.g., total = count, not covered + partial + missed)

- [x] **Task 2**: Create or update fixture file if needed
  - [x] Check if `tests/fixtures/coverage.json` exists (referenced in `test_parse_coverage_json_dict_format`)
  - [x] Create fixture file with correct structure if missing, or update if exists
  - **Files**: `.github/scripts/coverage-summary/tests/fixtures/coverage.json` (if needed)
  - **Dependencies**: Parser fixes must be complete
  - **Testing**: Run `test_parse_coverage_json_dict_format` test
  - **Notes**: Use same structure as updated conftest fixtures

### Phase 3: Verification

**Objective**: Ensure all tests pass and parser works correctly

- [x] **Task 1**: Run tests and verify fixes
  - [x] Run `pytest tests/test_parser.py` to verify all tests pass
  - [x] Verify parser correctly handles integer `count` and `summary` structure
  - [x] Check that test expectations match actual calculated values
  - **Files**: All test files
  - **Dependencies**: All previous tasks complete
  - **Testing**: Full test suite
  - **Notes**: May need to adjust test expectations if total calculation changed

## Files to Modify/Create
- **Modified Files**:
  - `.github/scripts/coverage-summary/src/coverage_summary/parser.py` - Fix parsing logic for totals and files
  - `.github/scripts/coverage-summary/tests/conftest.py` - Update test fixtures to match actual structure
  - `.github/scripts/coverage-summary/tests/fixtures/coverage.json` - Create or update fixture file (if needed)

## Testing Strategy
- **Unit Tests**: All existing parser tests should pass with updated fixtures
- **Integration Tests**: Verify parser works with actual cargo-llvm-cov JSON output structure
- **Manual Testing**: Test in GitHub Actions workflow to ensure coverage summary generates correctly

## Breaking Changes
- Test fixtures are updated to match actual cargo-llvm-cov output (breaking for tests only, not for production)

## Migration Guide
N/A - This is a bug fix, not a feature change

## Documentation Updates
- [x] Update parser docstring if needed to reflect actual JSON structure
- [x] Ensure comments in code match actual structure

## Success Criteria
- Parser successfully parses actual cargo-llvm-cov JSON output without errors
- All existing tests pass with updated fixtures
- Coverage summary generates correctly in GitHub Actions workflow
- Parser handles both integer `count` and direct `covered` fields correctly
- File metrics are correctly extracted from `summary` key

## Risks and Mitigations
- **Risk**: Test expectations may need adjustment if total calculation logic changed
  - **Mitigation**: Review test expectations carefully and update to match new calculation (total = count for lines/functions, count = covered + notcovered for branches)
- **Risk**: Missing edge cases (e.g., branches with `notcovered` field)
  - **Mitigation**: Check jq script for reference on how branches are handled, ensure parser matches

## References
- Related BUG_ document: `plan/25W48/BUG_COVERAGE_SUMMARY_COUNT_FIELD_TYPE.md`
- Related code: `.config/coverage-threshold-check.jq` (correctly uses `$s.lines.count` as integer)
- Related bug: `BUG_COVERAGE_SUMMARY_JSON_PARSING.md` (already fixed - addressed root structure)
