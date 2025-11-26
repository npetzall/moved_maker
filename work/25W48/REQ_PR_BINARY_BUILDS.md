# Implementation Plan: PR Binary Builds with Version Calculation

**Status**: ✅ Completed

## Overview
Enable binary builds and uploads in pull request workflows with version calculation that includes PR number as pre-release identifier and commit SHA as build metadata. This allows reviewers to download and test PR binaries without building locally.

## Checklist Summary

### Phase 1: Refactor Version Script
- [x] 3/3 tasks completed

### Phase 2: Update Workflow References
- [x] 2/2 tasks completed

### Phase 3: Add PR Binary Build Job
- [x] 2/2 tasks completed

### Phase 4: Testing and Documentation
- [x] 2/2 tasks completed

## Context
Reference: `plan/25W48/REQ_PR_BINARY_BUILDS.md`

Currently, pull request builds only run tests, security checks, and coverage analysis. They do not build or upload binaries, making it difficult for reviewers to test PR changes without building locally. The `release-version` script only handles release scenarios (main branch pushes) and updates `Cargo.toml`, creates git tags, and commits changes. PR mode will update `Cargo.toml` for binary builds but will not commit or tag changes.

## Goals
- Enable binary builds in PR workflows with unique version identifiers
- Refactor version calculation script to support both release and PR modes
- Calculate PR versions using semantic versioning with pre-release identifiers (`pr[PR-NUMBER]`) and build metadata (commit SHA)
- Upload PR binaries as artifacts for easy download and testing
- Maintain backward compatibility with existing release workflows

## Non-Goals
- Creating git tags or commits in PR workflows (version is only for binary identification and local testing)
- Releasing PR binaries to GitHub Releases (only artifact uploads)
- Building binaries for all platforms in PR workflows (can be limited to common platforms)

## Design Decisions

- **Rename `release-version` to `version`**: The script will handle both release and PR scenarios, so a more generic name is appropriate. This also aligns with the script's expanded functionality.
  - **Rationale**: The script will support multiple modes (release and PR), so "release-version" is too specific. A generic "version" name better reflects its purpose.
  - **Alternatives Considered**: Keeping the name "release-version" and creating a separate PR version script - rejected due to code duplication and maintenance burden.
  - **Trade-offs**: Requires updating all workflow references, but provides better long-term maintainability.

- **Mode Detection via Environment Variables**: Use environment variables (e.g., `VERSION_MODE=pr` or `VERSION_MODE=release`) to determine script behavior rather than inferring from context.
  - **Rationale**: Explicit mode control is clearer and more testable than inferring from GitHub context. Makes it easier to test locally and understand script behavior.
  - **Alternatives Considered**: Auto-detecting from GitHub event type - rejected as less explicit and harder to test.
  - **Trade-offs**: Requires workflows to set environment variables, but improves clarity and testability.

- **PR Version Format**: Use semantic versioning with pre-release identifier `pr[PR-NUMBER]` and build metadata `[SHORT-SHA]` (e.g., `1.2.3-pr123+abc1234`).
  - **Rationale**: Follows Semantic Versioning 2.0.0 specification, making versions parseable and sortable. Pre-release identifier clearly indicates PR context, build metadata provides commit traceability.
  - **Alternatives Considered**: Simple PR number in filename only - rejected as it loses version context and makes tracking harder.
  - **Trade-offs**: Version strings are longer but more informative and standards-compliant.

- **Update Cargo.toml in PR Mode**: In PR mode, update `Cargo.toml` and `Cargo.lock` with the PR version, same as release mode.
  - **Rationale**: Updating Cargo.toml ensures the version is embedded in the binary during build, making it available via `--version` flag. This provides consistency between PR and release builds and ensures version information is accessible in the binary itself.
  - **Alternatives Considered**: Skipping Cargo.toml updates in PR mode - rejected as it requires passing version via build flags and doesn't embed version in binary metadata.
  - **Trade-offs**: Cargo.toml is modified in PR workflow runs, but changes are not committed (only used for building binaries).

- **Binary Naming with Version**: Include full version in binary artifact names (e.g., `moved_maker-1.2.3-pr123+abc1234-linux-x86_64`).
  - **Rationale**: Full version in filename provides complete identification without needing to check checksum files. Makes it easy to identify which PR and commit a binary corresponds to.
  - **Alternatives Considered**: Simpler naming with version only in checksum - rejected as less convenient for users.
  - **Trade-offs**: Longer filenames but more informative.

## Implementation Steps

### Phase 1: Refactor Version Script

**Objective**: Rename `release-version` to `version` and add PR mode support with version calculation that includes PR number and commit SHA.

- [x] **Task 1**: Rename release-version directory and package
  - [ ] Rename `.github/scripts/release-version/` to `.github/scripts/version/`
  - [ ] Update package name in `pyproject.toml` from `release-version` to `version`
  - [ ] Rename Python package directory from `release_version` to `version` (update `src/` structure)
  - [ ] Update all import statements in Python files to use new package name
  - [ ] Update `__main__.py` module name references
  - [ ] Update test files to use new package name
  - [ ] Update README.md if it exists
  - **Files**: `.github/scripts/version/pyproject.toml`, `.github/scripts/version/src/version/__init__.py`, `.github/scripts/version/src/version/__main__.py`, `.github/scripts/version/src/version/*.py`, `.github/scripts/version/tests/*.py`
  - **Dependencies**: None
  - **Testing**: Run tests to ensure package structure is correct
  - **Notes**: Use git mv to preserve history where possible

- [x] **Task 2**: Add PR mode support to version calculation
  - [ ] Add `VERSION_MODE` environment variable detection in `__main__.py` (default to "release" for backward compatibility)
  - [ ] Add `PR_NUMBER` and `COMMIT_SHA` environment variable reading in `__main__.py`
  - [ ] Create new function `calculate_pr_version()` in `version.py` that:
    - Takes base version (from latest tag or Cargo.toml), PR number, and commit SHA
    - Calculates version using same logic as release (bump type from PR labels, commit count)
    - Formats as semantic version with pre-release `pr[PR-NUMBER]` and build metadata `[SHORT-SHA]` (7 characters)
    - Validates version format
  - [ ] Modify `calculate_new_version()` to accept optional `mode`, `pr_number`, and `commit_sha` parameters
  - [ ] Update `__main__.py` to call appropriate version calculation based on mode
  - [ ] In PR mode: Update `Cargo.toml` and `Cargo.lock` with PR version (same as release mode)
  - [ ] In PR mode: Always output version to GITHUB_OUTPUT (even if unchanged)
  - [ ] In release mode: Maintain existing behavior (update Cargo.toml, create tags)
  - [ ] Note: PR mode updates Cargo.toml but does NOT commit or tag (changes are local to workflow run)
  - **Files**: `.github/scripts/version/src/version/__main__.py`, `.github/scripts/version/src/version/version.py`
  - **Dependencies**: Task 1
  - **Testing**: Test PR mode with various PR numbers and commit SHAs, test release mode still works
  - **Notes**: Ensure version strings are valid for use in filenames (no invalid characters)

- [x] **Task 3**: Add helper function for commit SHA shortening
  - [ ] Create function `shorten_commit_sha(sha: str, length: int = 7) -> str` in `version.py`
  - [ ] Validate SHA format and length
  - [ ] Use in `calculate_pr_version()` for build metadata
  - **Files**: `.github/scripts/version/src/version/version.py`
  - **Dependencies**: Task 2
  - **Testing**: Test with various SHA lengths and formats
  - **Notes**: Default to 7 characters for build metadata (common convention)

### Phase 2: Update Workflow References

**Objective**: Update all workflow files to use the renamed `version` script and ensure release workflows continue to work.

- [x] **Task 1**: Update release-version workflow
  - [ ] Update `.github/workflows/release-version.yaml` to use new script path: `.github/scripts/version`
  - [ ] Update command from `uv run python -m release_version` to `uv run python -m version`
  - [ ] Ensure `VERSION_MODE` is not set (defaults to "release")
  - **Files**: `.github/workflows/release-version.yaml`
  - **Dependencies**: Phase 1
  - **Testing**: Verify release workflow still works correctly
  - **Notes**: No functional changes, only path updates

- [x] **Task 2**: Update any other references to release-version
  - [ ] Search codebase for references to `release-version` or `release_version`
  - [ ] Update documentation files (README.md, DEVELOPMENT.md, etc.) if they mention the script
  - [ ] Update any comments in workflow files
  - **Files**: Various (search results will determine)
  - **Dependencies**: Phase 1
  - **Testing**: Verify no broken references
  - **Notes**: Use grep to find all references

### Phase 3: Add PR Binary Build Job

**Objective**: Add a new job to `pull_request.yaml` that builds binaries for PRs with calculated version and uploads them as artifacts.

- [x] **Task 1**: Add version calculation step to PR workflow
  - [ ] Add new step in `pull_request.yaml` (or create new job) that:
    - Installs uv and Python 3.13
    - Runs version script in PR mode with:
      - `VERSION_MODE=pr`
      - `PR_NUMBER=${{ github.event.pull_request.number }}`
      - `COMMIT_SHA=${{ github.sha }}`
      - `GITHUB_TOKEN` and `GITHUB_REPOSITORY` (already available)
    - Captures version output from GITHUB_OUTPUT
  - [ ] Make this step available to subsequent jobs via job outputs
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: Phase 2
  - **Testing**: Test version calculation in PR context
  - **Notes**: PR number and commit SHA are available in `github.event.pull_request.number` and `github.sha`

- [x] **Task 2**: Add build-binaries job to PR workflow
  - [ ] Create new `build-binaries` job that depends on `coverage` (or `test-ubuntu`)
  - [ ] Use matrix strategy for platforms (start with ubuntu-latest and macos-latest, same targets as release)
  - [ ] Install Rust with target platform
  - [ ] Use rust-cache for build caching
  - [ ] Get version from version calculation job output
  - [ ] Build release binary with `cargo build --release --target ${{ matrix.target }}`
  - [ ] Pass version to binary (may need to use `--version` flag or environment variable, or embed in binary name only)
  - [ ] Rename binary to include version: `moved_maker-{version}-{platform}`
  - [ ] Create checksum using existing create-checksum script
  - [ ] Upload binary and checksum as artifacts with appropriate retention period (e.g., 7 days for PRs)
  - [ ] Add test summary generation (similar to release workflow)
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: Task 1
  - **Testing**: Test binary builds in PR workflow, verify artifacts are uploaded correctly
  - **Notes**: Version may need to be embedded via Cargo build-time environment variable if required in binary output

### Phase 4: Testing and Documentation

**Objective**: Verify implementation works correctly and update documentation.

- [x] **Task 1**: Create tests for PR version calculation
  - [ ] Add unit tests for `calculate_pr_version()` function
  - [ ] Test various PR numbers and commit SHAs
  - [ ] Test version format validation
  - [ ] Test edge cases (very large PR numbers, short commit SHAs)
  - [ ] Add integration tests if needed
  - **Files**: `.github/scripts/version/tests/test_version.py`
  - **Dependencies**: Phase 1
  - **Testing**: Run pytest to verify tests pass
  - **Notes**: Ensure test coverage meets project standards

- [x] **Task 2**: Update documentation
  - [ ] Update README.md or DEVELOPMENT.md to document PR binary builds
  - [ ] Document version format and naming conventions
  - [ ] Document how to use PR binaries
  - [ ] Update any workflow documentation
  - **Files**: `README.md`, `DEVELOPMENT.md`, or relevant documentation files
  - **Dependencies**: Phase 3
  - **Testing**: Verify documentation is accurate and complete
  - **Notes**: Focus on user-facing documentation for PR binary usage

## Files to Modify/Create
- **New Files**:
  - None (refactoring existing files)
- **Modified Files**:
  - `.github/scripts/version/` (renamed from `release-version/`) - Refactor to support PR and release modes
  - `.github/workflows/pull_request.yaml` - Add version calculation and binary build job
  - `.github/workflows/release-version.yaml` - Update script path references
  - Documentation files - Update references and add PR binary build documentation

## Testing Strategy
- **Unit Tests**: Test PR version calculation logic, version formatting, SHA shortening, mode detection
- **Integration Tests**: Test version script in PR mode with mock GitHub client, test binary build process
- **Manual Testing**: Create a test PR to verify binary builds work, download and test PR binaries, verify version strings are correct

## Breaking Changes
- **Script Rename**: The `release-version` script is renamed to `version`. All workflow references must be updated.
  - **Migration**: Update any custom workflows or scripts that call `release-version` to use `version` instead.
  - **Impact**: Low - only affects internal workflows and scripts.

## Migration Guide
1. Update any custom workflows that reference `.github/scripts/release-version` to use `.github/scripts/version`
2. Update any scripts that call `python -m release_version` to use `python -m version`
3. For PR mode usage, set `VERSION_MODE=pr` environment variable along with `PR_NUMBER` and `COMMIT_SHA`

## Documentation Updates
- [ ] Update README.md with PR binary build information
- [ ] Update DEVELOPMENT.md with version script usage (PR vs release modes)
- [ ] Add/update doc comments in version script for PR mode
- [ ] Update workflow documentation if it exists

## Success Criteria
- Version script successfully calculates PR versions with format `X.Y.Z-pr[NUMBER]+[SHA]`
- PR workflows build and upload binaries for all target platforms
- Binary artifacts are named with version and platform identifiers
- Release workflows continue to work unchanged
- Version script supports both PR and release modes without breaking changes
- Documentation clearly explains PR binary builds and version format

## Risks and Mitigations
- **Risk**: Version script rename breaks existing workflows
  - **Mitigation**: Thoroughly test release workflows after rename, update all references systematically using grep
- **Risk**: PR version format conflicts with Cargo version requirements
  - **Mitigation**: Validate version format against Semantic Versioning spec and Cargo version requirements. Ensure PR version format (with pre-release and build metadata) is valid for Cargo.toml
- **Risk**: PR binary builds slow down PR workflow
  - **Mitigation**: Build binaries in parallel using matrix strategy, use rust-cache for faster builds, consider limiting to essential platforms initially
- **Risk**: Version calculation fails in PR context (missing PR number or SHA)
  - **Mitigation**: Add validation and clear error messages, provide fallback behavior if needed

## References
- Related REQ_ document: `plan/25W48/REQ_PR_BINARY_BUILDS.md`
- Related workflows: `.github/workflows/pull_request.yaml`, `.github/workflows/release-build.yaml`
- Related scripts: `.github/scripts/release-version/` (to be renamed to `version/`)
- Semantic Versioning: https://semver.org/
- GitHub Actions context: https://docs.github.com/en/actions/learn-github-actions/contexts
