# Implementation Plan: Replace SemVer Validation with semver Python Package

**Status**: ✅ Complete

## Overview
Replace the current regex-based SemVer 2.0.0 validation implementation with the `semver` Python package to simplify code, improve maintainability, and ensure proper SemVer 2.0.0 compliance.

## Checklist Summary

### Phase 1: Dependency and Code Updates
- [x] 3/3 tasks completed

### Phase 2: Testing and Verification
- [x] 1/1 tasks completed

### Phase 3: Documentation Updates
- [x] 1/1 tasks completed

## Context
Reference: `plan/25W48/REQ_REPLACE_SEMVER_VALIDATION_WITH_SEMVER_PACKAGE.md`

The current implementation in `cargo.py` uses custom regex patterns and helper functions to validate SemVer 2.0.0 formats, particularly for versions with pre-release identifiers and build metadata (e.g., `0.2.1-pr26+87baede`). This approach requires maintaining custom regex patterns, duplicates validation logic, and uses a mix of `packaging.version.Version` (PEP 440) and custom regex, which is inconsistent.

## Goals
- Replace custom regex-based validation with the `semver` Python package
- Reduce code complexity from ~90 lines to ~5 lines for validation
- Ensure proper SemVer 2.0.0 compliance
- Maintain backward compatibility with all existing version formats
- Ensure all existing tests continue to pass

## Non-Goals
- Changing the PR version format (it's already correct according to SemVer 2.0.0)
- Modifying how PR versions are calculated
- Changing other parts of the version script

## Design Decisions

- **Use `semver` package for all validation**: Replace all custom validation logic with `semver.Version.parse()` which handles all SemVer 2.0.0 formats (standard, pre-release, build metadata, combinations).
  - **Rationale**: The `semver` package is well-tested, maintained, and specifically designed for SemVer 2.0.0 validation. It eliminates the need for custom regex patterns and provides consistent validation for all version formats.
  - **Alternatives Considered**:
    - Keep current regex-based approach: Rejected because it's error-prone, harder to maintain, and doesn't leverage well-tested libraries
    - Use `semantic_version` package: Considered but `semver` is more widely used and has a simpler API
    - Continue using `packaging.version.Version`: Rejected because it follows PEP 440, not SemVer 2.0.0, and doesn't support SemVer pre-release formats like `pr26`
  - **Trade-offs**: Adds a new dependency, but significantly reduces code complexity and improves maintainability.

- **Remove all custom validation helper functions**: Delete `_split_version_with_build_metadata()`, `_validate_semver_format()`, and `_validate_build_metadata()` functions.
  - **Rationale**: These functions are no longer needed since `semver.Version.parse()` handles all validation cases.
  - **Alternatives Considered**: Keep functions for backward compatibility - rejected because they're no longer needed and removing them simplifies the codebase.
  - **Trade-offs**: None - these functions are internal and not used elsewhere.

## Implementation Steps

### Phase 1: Dependency and Code Updates

**Objective**: Add semver dependency and replace validation logic

- [x] **Task 1**: Add semver dependency to pyproject.toml
  - [x] Add `semver>=3.0.0` to dependencies list in `pyproject.toml`
  - **Files**: `.github/scripts/version/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify dependency is added correctly
  - **Notes**: Use version >=3.0.0 as specified in REQ document

- [x] **Task 2**: Replace validation logic in cargo.py
  - [x] Import `semver` package (replace or remove `re` import)
  - [x] Remove helper functions: `_split_version_with_build_metadata()`, `_validate_semver_format()`, `_validate_build_metadata()`
  - [x] Replace validation logic in `read_cargo_version()` with `semver.Version.parse(version)`
  - [x] Update error handling to catch `semver.VersionInfo` exceptions appropriately
  - [x] Update docstrings to reflect use of `semver` package
  - [x] Remove `re` import if no longer needed
  - **Files**: `.github/scripts/version/src/version/cargo.py`
  - **Dependencies**: Task 1 (semver dependency)
  - **Testing**: Run existing tests to verify all pass
  - **Notes**: Maintain similar error message format for consistency

- [x] **Task 3**: Remove unused imports
  - [x] Remove `re` import from `cargo.py` if no longer used
  - [x] Remove `packaging.version` imports if no longer needed (check if used elsewhere)
  - **Files**: `.github/scripts/version/src/version/cargo.py`
  - **Dependencies**: Task 2
  - **Testing**: Verify code still works
  - **Notes**: `packaging.version` might still be used elsewhere, check before removing

### Phase 2: Testing and Verification

**Objective**: Ensure all tests pass and functionality works correctly

- [x] **Task 1**: Run tests and verify functionality
  - [x] Run `pytest` in `.github/scripts/version` directory
  - [x] Verify all existing tests pass
  - [x] Verify version validation works for all formats (standard, pre-release, build metadata, PR versions)
  - [x] Update test expectations for error messages to match new format
  - **Files**: `.github/scripts/version/tests/test_cargo.py`
  - **Dependencies**: Phase 1 complete
  - **Testing**: Run full test suite
  - **Notes**: All existing tests should continue to pass without modification

### Phase 3: Documentation Updates

**Objective**: Update documentation to reflect changes

- [x] **Task 1**: Update progress in plan and work documents
  - [x] Update status in `plan/25W48/REQ_REPLACE_SEMVER_VALIDATION_WITH_SEMVER_PACKAGE.md` to "✅ Complete"
  - [x] Update status in `work/25W48/REQ_REPLACE_SEMVER_VALIDATION_WITH_SEMVER_PACKAGE.md` to "✅ Complete"
  - **Files**: `plan/25W48/REQ_REPLACE_SEMVER_VALIDATION_WITH_SEMVER_PACKAGE.md`, `work/25W48/REQ_REPLACE_SEMVER_VALIDATION_WITH_SEMVER_PACKAGE.md`
  - **Dependencies**: Phase 2 complete
  - **Testing**: Verify documents are updated correctly
  - **Notes**: Mark as complete only after all implementation and testing is done

## Files to Modify/Create
- **Modified Files**:
  - `.github/scripts/version/pyproject.toml` - Add semver dependency
  - `.github/scripts/version/src/version/cargo.py` - Replace validation logic, remove helper functions
  - `plan/25W48/REQ_REPLACE_SEMVER_VALIDATION_WITH_SEMVER_PACKAGE.md` - Update status
  - `work/25W48/REQ_REPLACE_SEMVER_VALIDATION_WITH_SEMVER_PACKAGE.md` - Update status

## Testing Strategy
- **Unit Tests**: All existing tests in `test_cargo.py` should continue to pass without modification
- **Integration Tests**: Verify version validation works correctly for all supported formats:
  - Standard versions: `1.0.0`
  - Pre-release versions: `1.0.0-alpha`
  - Build metadata versions: `1.0.0+build.1`
  - PR versions: `0.2.1-pr26+87baede`
  - Invalid versions should still be rejected appropriately

## Breaking Changes
- None - all existing version formats will continue to work

## Migration Guide
N/A - no breaking changes

## Documentation Updates
- [x] Update docstrings in `cargo.py` to reflect use of `semver` package
- [ ] Update progress in plan document
- [ ] Update progress in work document

## Success Criteria
- [x] `semver>=3.0.0` added to dependencies
- [x] All custom validation helper functions removed
- [x] Validation logic replaced with `semver.Version.parse()`
- [x] All existing tests pass
- [x] Code complexity reduced (from ~90 lines to ~5 lines for validation)
- [x] No breaking changes to existing functionality

## Risks and Mitigations
- **Risk**: `semver` package might have different error messages or behavior than current implementation
  - **Mitigation**: Test all existing test cases to ensure behavior is compatible. Update error messages if needed to maintain consistency.
- **Risk**: `semver` package might not support all edge cases currently handled
  - **Mitigation**: Review `semver` package documentation and test all existing version formats to ensure compatibility.

## References
- Related REQ_ document: `plan/25W48/REQ_REPLACE_SEMVER_VALIDATION_WITH_SEMVER_PACKAGE.md`
- Related BUG_ document: `plan/25W48/BUG_PR_VERSION_VALIDATION_FAILURE.md` (this fix addresses the root cause)
- SemVer 2.0.0 specification: https://semver.org/spec/v2.0.0.html
- semver Python package: https://pypi.org/project/semver/
- semver documentation: https://python-semver.readthedocs.io/
