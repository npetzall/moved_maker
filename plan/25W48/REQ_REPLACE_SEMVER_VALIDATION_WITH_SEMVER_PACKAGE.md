# REQ: Replace SemVer Validation with semver Python Package

**Status**: ✅ Complete

## Overview
Replace the current regex-based SemVer 2.0.0 validation implementation with the `semver` Python package to simplify code, improve maintainability, and ensure proper SemVer 2.0.0 compliance.

## Motivation
The current implementation in `cargo.py` uses custom regex patterns and helper functions to validate SemVer 2.0.0 formats, particularly for versions with pre-release identifiers and build metadata (e.g., `0.2.1-pr26+87baede`). This approach:

- Requires maintaining custom regex patterns that may not cover all edge cases
- Duplicates validation logic that already exists in well-tested libraries
- Uses a mix of `packaging.version.Version` (PEP 440) and custom regex, which is inconsistent
- Is more error-prone and harder to maintain than using a dedicated SemVer library

The `semver` Python package provides robust, well-tested SemVer 2.0.0 validation and parsing, eliminating the need for custom validation code.

## Current Behavior
The `read_cargo_version()` function in `.github/scripts/version/src/version/cargo.py` currently:

1. Uses `_split_version_with_build_metadata()` to separate base version from build metadata
2. Uses `_validate_semver_format()` with regex to validate base versions with pre-release identifiers
3. Uses `_validate_build_metadata()` with regex to validate build metadata format
4. Falls back to `packaging.version.Version` for versions without build metadata

This results in:
- ~90 lines of custom validation code
- Complex logic to handle different version formats
- Potential edge cases not covered by regex patterns
- Inconsistent validation approach (PEP 440 vs SemVer 2.0.0)

## Proposed Behavior
Replace the custom validation logic with the `semver` Python package:

1. Add `semver>=3.0.0` to dependencies in `pyproject.toml`
2. Remove helper functions: `_split_version_with_build_metadata()`, `_validate_semver_format()`, and `_validate_build_metadata()`
3. Replace validation logic in `read_cargo_version()` with `semver.Version.parse(version)`
4. Remove `re` import (no longer needed)
5. Simplify the validation to a single call that handles all SemVer 2.0.0 formats

This will:
- Reduce code complexity (~90 lines to ~5 lines for validation)
- Use a well-tested, maintained library
- Ensure proper SemVer 2.0.0 compliance
- Provide consistent validation for all version formats
- Make the code easier to understand and maintain

## Use Cases
- **Version Validation**: Validate all SemVer 2.0.0 formats (standard, pre-release, build metadata, combinations)
- **PR Version Support**: Properly validate PR versions like `0.2.1-pr26+87baede`
- **Code Maintenance**: Reduce maintenance burden by using a standard library instead of custom regex
- **Future Extensibility**: Easily add version comparison, bumping, or other SemVer operations if needed

## Implementation Considerations
- **Dependency Addition**: Add `semver>=3.0.0` to `pyproject.toml` dependencies
- **Backward Compatibility**: Ensure all existing version formats continue to work (standard versions, pre-release only, build metadata only, PR versions)
- **Error Messages**: Maintain similar error message format for consistency
- **Testing**: Update tests to verify the new validation works correctly
- **Code Cleanup**: Remove unused imports (`re`) and helper functions
- **Documentation**: Update docstrings to reflect the use of `semver` package

## Alternatives Considered
- **Keep current regex-based approach**: Rejected because it's error-prone, harder to maintain, and doesn't leverage well-tested libraries
- **Use `semantic_version` package**: Considered but `semver` is more widely used and has a simpler API
- **Continue using `packaging.version.Version`**: Rejected because it follows PEP 440, not SemVer 2.0.0, and doesn't support SemVer pre-release formats like `pr26`

## Impact
- **Breaking Changes**: No - all existing version formats will continue to work
- **Documentation**: Update docstrings in `cargo.py` to mention `semver` package usage
- **Testing**: All existing tests should continue to pass; may add additional tests for edge cases
- **Dependencies**: Add `semver>=3.0.0` to `pyproject.toml` (new dependency)
- **Code Reduction**: Remove ~90 lines of custom validation code, replace with ~5 lines using `semver`

## References
- Related bugs: `plan/25W48/BUG_PR_VERSION_VALIDATION_FAILURE.md` (this fix addresses the root cause)
- Related requirements: `plan/25W48/REQ_PR_BINARY_BUILDS.md` (introduced PR version support)
- SemVer 2.0.0 specification: https://semver.org/spec/v2.0.0.html
- semver Python package: https://pypi.org/project/semver/
- semver documentation: https://python-semver.readthedocs.io/
