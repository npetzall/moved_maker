# REQ: PR Binary Builds with Version Calculation

**Status**: ✅ Completed

## Overview
Enable binary builds and uploads in pull request workflows with version calculation that includes PR number as pre-release identifier and commit SHA as build metadata.

## Motivation
Currently, pull request builds only run tests, security checks, and coverage analysis. They do not build or upload binaries, making it difficult for reviewers to test PR changes without building locally. By building binaries in PR workflows with unique version identifiers, reviewers can easily download and test PR changes, improving the review process and catching platform-specific issues earlier.

## Current Behavior
- PR workflows (`pull_request.yaml`) only upload test results and security reports
- Binaries are only built in release workflows (`release-build.yaml`) when a version tag is detected
- Version calculation script (`release-version`) only handles release scenarios (main branch pushes)
- No way to identify which PR or commit a binary corresponds to

## Proposed Behavior
1. **Rename `release-version` to `version`**: Refactor the version calculation script to handle both release and PR scenarios
2. **PR version format**: Calculate version using the same logic as releases, but with:
   - Pre-release identifier: `pr[PR-NUMBER]` (e.g., `pr123`)
   - Build metadata: Short commit SHA (e.g., `abc1234`)
   - Example: `1.2.3-pr123+abc1234`
3. **Build binaries in PR workflows**: Add a new job to `pull_request.yaml` that:
   - Calculates the PR version using the refactored version script
   - Updates `Cargo.toml` and `Cargo.lock` with the PR version
   - Builds release binaries for all target platforms (same as release builds)
   - Uploads binaries as artifacts (with checksums)
   - Does NOT create git tags or commits (version is only for binary identification and local testing)

## Use Cases
- **PR Reviewers**: Download and test PR binaries without building locally
- **Cross-platform Testing**: Verify binaries work on different platforms before merging
- **CI/CD Validation**: Ensure binary builds succeed before release
- **Version Tracking**: Identify which PR and commit a binary corresponds to via version string

## Implementation Considerations
- **Version Script Refactoring**:
  - Rename `.github/scripts/release-version/` to `.github/scripts/version/`
  - Add mode detection (release vs PR) based on context (environment variables or workflow type)
  - For PR mode: Get PR number from `github.event.pull_request.number` or `GITHUB_REF`
  - For PR mode: Get commit SHA from `github.sha` or `GITHUB_SHA`
  - For PR mode: Update `Cargo.toml` and `Cargo.lock` with PR version (same as release mode)
  - For PR mode: Do NOT create git tags or commits (version update is local to workflow run)
  - For release mode: Maintain existing behavior (update Cargo.toml, create tags)

- **PR Workflow Changes**:
  - Add new `build-binaries` job that depends on `coverage` (or `test-ubuntu`)
  - Use matrix strategy for multiple platforms (same as release builds)
  - Calculate version using refactored script in PR mode
  - Build binaries with version embedded (may need to pass version to cargo build)
  - Upload binaries and checksums as artifacts
  - Set appropriate retention period for PR artifacts (shorter than release artifacts)

- **Version Format**:
  - Follow Semantic Versioning 2.0.0 specification
  - Pre-release: `pr[PR-NUMBER]` (e.g., `pr123`)
  - Build metadata: Short commit SHA (7 characters, e.g., `abc1234`)
  - Full example: `1.2.3-pr123+abc1234`
  - Ensure version string is valid for use in filenames and Cargo version fields

- **Binary Naming**:
  - Use version in binary artifact names: `moved_maker-{version}-{platform}`
  - Example: `moved_maker-1.2.3-pr123+abc1234-linux-x86_64`
  - Or simpler: `moved_maker-pr123-{platform}` (version in checksum file)

- **Dependencies**:
  - Ensure version script can access PR number and commit SHA in PR context
  - May need to pass additional environment variables from workflow to script
  - Consider using `github.event.pull_request.number` and `github.sha` in workflow

- **Backward Compatibility**:
  - Release workflows should continue to work with renamed script
  - Update all references to `release-version` in workflows and documentation
  - Ensure release mode behavior is unchanged

## Alternatives Considered
- **Separate PR version script**: Rejected - too much code duplication, maintenance burden
- **Simple PR number in filename only**: Rejected - loses version context, harder to track
- **Build binaries only on specific label**: Rejected - adds friction, should be automatic
- **Use existing release workflow for PRs**: Rejected - release workflow is tag-triggered, PRs don't have tags

## Impact
- **Breaking Changes**: No - this is additive functionality
- **Documentation**:
  - Update workflow documentation to describe PR binary builds
  - Update version calculation documentation to describe PR mode
  - Document version format and naming conventions
- **Testing**:
  - Test version calculation in PR mode with various PR numbers and commit SHAs
  - Test binary builds in PR workflow
  - Verify backward compatibility with release workflows
  - Test version string formatting and validation
- **Dependencies**:
  - No new external dependencies required
  - May need to update workflow environment variable usage

## References
- Related workflows: `.github/workflows/pull_request.yaml`, `.github/workflows/release-build.yaml`
- Related scripts: `.github/scripts/release-version/`
- Semantic Versioning: https://semver.org/
- GitHub Actions context: https://docs.github.com/en/actions/learn-github-actions/contexts
