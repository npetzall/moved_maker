# BUG: PR Version Validation Fails with Build Metadata

**Status**: ✅ Complete

## Overview
The pull request workflow fails when updating Cargo.toml with PR versions that include build metadata (format: `X.Y.Z-prN+SHA`). The version validation rejects valid semantic versions with build metadata because `packaging.version.Version` doesn't properly support the `+` build metadata suffix.

## Environment
- **OS**: GitHub Actions (ubuntu-latest)
- **Rust Version**: 1.90.0
- **Tool Version**: Version script in `.github/scripts/version`
- **Terraform Version**: N/A

## Steps to Reproduce
1. Open or update a pull request
2. The `pull_request.yaml` workflow runs the `version` job
3. The version script calculates a PR version (e.g., `0.2.1-pr26+87baede`)
4. The script attempts to update Cargo.toml with the PR version
5. The workflow fails with a validation error

## Expected Behavior
1. PR version should be calculated successfully (e.g., `0.2.1-pr26+87baede`)
2. Cargo.toml should be updated with the PR version (semantic version with pre-release identifier and build metadata is valid according to SemVer 2.0.0)

## Actual Behavior
1. PR version calculation completes successfully
2. When attempting to update Cargo.toml, the validation fails because `packaging.version.Version` doesn't properly support build metadata (`+` suffix)
3. The workflow fails with: `Error updating Cargo.toml: Invalid version format in Cargo.toml: 0.2.1-pr26+87baede. Expected semantic version (e.g., 1.0.0)`

## Error Messages / Output
```
Error updating Cargo.toml: Invalid version format in Cargo.toml: 0.2.1-pr26+87baede. Expected semantic version (e.g., 1.0.0)
```

## Minimal Reproduction Case
Run the version script in PR mode with a PR version that includes build metadata:
```bash
VERSION_MODE=pr PR_NUMBER=26 COMMIT_SHA=87baede66f6784ed93eb4bcc58e9379904b84a17 GITHUB_TOKEN=... GITHUB_REPOSITORY=npetzall/moved_maker python -m version
```

## Additional Context
- The PR version format `X.Y.Z-prN+SHA` is a valid semantic version according to SemVer 2.0.0 specification (pre-release identifier and build metadata)
- The `packaging.version.Version` class from Python's `packaging` library has limitations with build metadata validation
- The code in `version.py` (line 373-374) already acknowledges this limitation with a comment: "Note: packaging.version.Version doesn't support build metadata in pre-release, but we can validate the base version and format separately"
- The issue occurs in `cargo.py` in the `read_cargo_version` function (line 50) which validates the full version string, including build metadata
- The `update_cargo_version` function calls `read_cargo_version` to check the current version before updating, which triggers the validation error
- Related to: `REQ_PR_BINARY_BUILDS.md` which introduced PR version support
- Frequency: Always (when PR version includes build metadata)

## Related Issues
- Related PRs: #26 (the PR that triggered this bug)
- Related requirements: `plan/25W48/REQ_PR_BINARY_BUILDS.md`
- Related bugs: `BUG_PR_VERSION_ERROR_ORDERING.md` (error message appears at wrong position)
