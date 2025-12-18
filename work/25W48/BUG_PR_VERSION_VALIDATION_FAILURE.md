# Implementation Plan: BUG_PR_VERSION_VALIDATION_FAILURE

**Status**: ✅ Complete

## Overview
Fix the version validation in `read_cargo_version` to properly handle PR versions with build metadata (format: `X.Y.Z-prN+SHA`). The current implementation uses `packaging.version.Version` which follows PEP 440 and doesn't properly support the combination of pre-release identifiers with build metadata as specified in SemVer 2.0.0.

## Checklist Summary

### Phase 1: Update Version Validation Logic
- [x] 1/1 tasks completed

### Phase 2: Add Tests for PR Version Format
- [x] 1/1 tasks completed

## Context
Reference: `plan/25W48/BUG_PR_VERSION_VALIDATION_FAILURE.md`

The pull request workflow fails when updating Cargo.toml with PR versions that include build metadata (format: `X.Y.Z-prN+SHA`, e.g., `0.2.1-pr26+87baede`). The version validation in `read_cargo_version` uses `packaging.version.Version` which doesn't properly support the combination of pre-release identifiers with build metadata, even though this is valid according to SemVer 2.0.0.

The issue occurs when:
1. `update_cargo_version` is called with a PR version (e.g., `0.2.1-pr26+87baede`)
2. It calls `read_cargo_version(path)` on line 89 to get the current version
3. After updating, it calls `read_cargo_version(path)` again on line 111 to verify
4. `read_cargo_version` validates using `Version(version)` which fails for versions with both pre-release and build metadata

## Goals
- Fix `read_cargo_version` to accept valid SemVer 2.0.0 versions with pre-release identifiers and build metadata
- Maintain backward compatibility with existing version formats (standard versions, pre-release only, build metadata only)
- Ensure validation still rejects invalid version formats
- Add comprehensive tests for PR version format

## Non-Goals
- Changing the PR version format (it's already correct according to SemVer 2.0.0)
- Modifying `packaging.version.Version` or switching to a different versioning library
- Changing how PR versions are calculated

## Design Decisions

- **Split-based validation approach**: Instead of using `packaging.version.Version` directly on the full version string, we'll split the version into base version (with optional pre-release) and build metadata, then validate each part separately.
  - **Rationale**: `packaging.version.Version` follows PEP 440 which has different rules than SemVer 2.0.0. By splitting and validating separately, we can support SemVer 2.0.0 format while still using `packaging.version.Version` for the base version validation (which works correctly for standard versions and pre-release versions).
  - **Alternatives Considered**:
    - Using a different versioning library (e.g., `semver`): Rejected because it would require adding a new dependency and `packaging` is already used throughout the codebase
    - Using regex validation: Rejected because it's more error-prone and harder to maintain than using the existing `packaging.version.Version` for base validation
    - Removing validation for versions with build metadata: Rejected because we still want to validate that the base version is correct
  - **Trade-offs**: We validate the base version (with pre-release) using `packaging.version.Version`, but we manually validate the build metadata format. This is acceptable because build metadata has simple format requirements (alphanumeric characters, dots, hyphens).

- **Preserve existing validation for standard formats**: Continue using `packaging.version.Version` directly for versions without build metadata to maintain existing behavior.
  - **Rationale**: Existing tests and code paths rely on the current validation behavior. We only need special handling for versions with build metadata.
  - **Alternatives Considered**:
    - Always using split-based validation: Rejected because it adds unnecessary complexity for standard versions
  - **Trade-offs**: Slight code duplication, but clearer separation of concerns and easier to understand.

## Implementation Steps

### Phase 1: Update Version Validation Logic

**Objective**: Modify `read_cargo_version` to handle versions with both pre-release identifiers and build metadata.

- [x] **Task 1**: Update `read_cargo_version` function to handle build metadata
  - [x] Add helper function to split version into base version and build metadata
  - [x] Modify validation logic to handle versions with build metadata separately
  - [x] Validate base version (with optional pre-release) using `packaging.version.Version`
  - [x] Validate build metadata format (alphanumeric, dots, hyphens allowed)
  - [x] Preserve existing validation for versions without build metadata
  - [x] Update docstring to document support for build metadata
  - **Files**: `.github/scripts/version/src/version/cargo.py`
  - **Dependencies**: None
  - **Testing**: Run existing tests to ensure backward compatibility, then add new tests for PR version format
  - **Notes**: The helper function should split on the last `+` character (build metadata separator) and handle edge cases (no build metadata, multiple `+` characters in build metadata).

### Phase 2: Add Tests for PR Version Format

**Objective**: Add comprehensive tests to ensure PR versions with build metadata are properly validated.

- [x] **Task 1**: Add test cases for PR version format
  - [x] Add test fixture for PR version with build metadata (e.g., `0.2.1-pr26+87baede`)
  - [x] Add test for `read_cargo_version` with PR version format
  - [x] Add test for `update_cargo_version` with PR version format
  - [x] Add test for invalid build metadata format
  - [x] Verify existing tests still pass (backward compatibility)
  - **Files**:
    - `.github/scripts/version/tests/test_cargo.py`
    - `.github/scripts/version/tests/test_cargo/pr_version_build_metadata.toml` (new test fixture)
  - **Dependencies**: Phase 1 must be completed
  - **Testing**: Run pytest to verify all tests pass
  - **Notes**: Test fixture should contain a version like `0.2.1-pr26+87baede` to match the actual PR version format.

## Files to Modify/Create
- **New Files**:
  - `.github/scripts/version/tests/test_cargo/pr_version_build_metadata.toml` - Test fixture for PR version with build metadata
- **Modified Files**:
  - `.github/scripts/version/src/version/cargo.py` - Update `read_cargo_version` to handle versions with build metadata

## Testing Strategy
- **Unit Tests**:
  - Test `read_cargo_version` with PR version format (`X.Y.Z-prN+SHA`)
  - Test `read_cargo_version` with standard versions (backward compatibility)
  - Test `read_cargo_version` with pre-release only (backward compatibility)
  - Test `read_cargo_version` with build metadata only (backward compatibility)
  - Test `read_cargo_version` with invalid build metadata format
  - Test `update_cargo_version` with PR version format
  - Verify all existing tests still pass
- **Integration Tests**:
  - Test end-to-end PR version update workflow (if applicable)
- **Manual Testing**:
  - Run the version script in PR mode with a PR version that includes build metadata to verify it works in the actual workflow

## Breaking Changes
None - this fix maintains backward compatibility with all existing version formats.

## Migration Guide
N/A - no breaking changes.

## Documentation Updates
- [x] Update docstring for `read_cargo_version` to document support for build metadata
- [x] Add comment explaining the split-based validation approach

## Success Criteria
- `read_cargo_version` accepts valid PR versions with build metadata (format: `X.Y.Z-prN+SHA`)
- `update_cargo_version` successfully updates Cargo.toml with PR versions
- All existing tests continue to pass (backward compatibility maintained)
- New tests verify PR version format validation
- The pull request workflow no longer fails when updating Cargo.toml with PR versions

## Risks and Mitigations
- **Risk**: The split-based validation might incorrectly accept invalid versions
  - **Mitigation**: Add comprehensive tests for edge cases (invalid build metadata, malformed versions, etc.)
- **Risk**: Changes might break existing version validation for standard formats
  - **Mitigation**: Preserve existing validation path for versions without build metadata, run all existing tests
- **Risk**: Build metadata format validation might be too strict or too lenient
  - **Mitigation**: Follow SemVer 2.0.0 specification for build metadata format (alphanumeric, dots, hyphens)

## References
- Related BUG_ document: `plan/25W48/BUG_PR_VERSION_VALIDATION_FAILURE.md`
- Related PRs: #26 (the PR that triggered this bug)
- Related requirements: `plan/25W48/REQ_PR_BINARY_BUILDS.md`
- Related bugs: `plan/25W48/BUG_PR_VERSION_ERROR_ORDERING.md`
- SemVer 2.0.0 specification: https://semver.org/spec/v2.0.0.html
- PEP 440 specification: https://peps.python.org/pep-0440/
