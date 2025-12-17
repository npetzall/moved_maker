# BUG: PR Version Error Message Appears Before Update Message

**Status**: ✅ Complete

## Overview
When the version script fails during PR version update, the error message is printed to stderr before the "Updating Cargo.toml..." message appears on stdout, causing incorrect output ordering due to stderr being unbuffered while stdout is buffered.

## Environment
- **OS**: GitHub Actions (ubuntu-latest)
- **Rust Version**: 1.90.0
- **Tool Version**: Version script in `.github/scripts/version`
- **Terraform Version**: N/A

## Steps to Reproduce
1. Open or update a pull request
2. The `pull_request.yaml` workflow runs the `version` job
3. The version script calculates a PR version (e.g., `0.2.2-pr26+c5c00e2`)
4. The script attempts to update Cargo.toml with the PR version
5. The validation fails and the error message appears before the "Updating Cargo.toml..." message

## Expected Behavior
1. The "Updating Cargo.toml with version {version}..." message should appear first
2. Then the error message should appear if validation fails
3. Output should be in chronological order matching the code execution flow

## Actual Behavior
1. The error message appears first (printed to stderr)
2. The "Updating Cargo.toml with version {version}..." message appears after (printed to stdout)
3. Example output order:
   ```
   Error updating Cargo.toml: Invalid version format in Cargo.toml: 0.2.2-pr26+c5c00e2. Expected semantic version (e.g., 1.0.0)
   Updating Cargo.toml with version 0.2.2-pr26+c5c00e2...
   ```

## Error Messages / Output
```
Error updating Cargo.toml: Invalid version format in Cargo.toml: 0.2.2-pr26+c5c00e2. Expected semantic version (e.g., 1.0.0)
Updating Cargo.toml with version 0.2.2-pr26+c5c00e2...
```

## Minimal Reproduction Case
Run the version script in PR mode and trigger a validation error during the update step:
```bash
VERSION_MODE=pr PR_NUMBER=26 COMMIT_SHA=c5c00e2... GITHUB_TOKEN=... GITHUB_REPOSITORY=npetzall/moved_maker python -m version
```

## Additional Context
- The issue occurs because stderr is unbuffered while stdout is buffered, causing stderr output to appear before stdout output even when stdout print statements execute first
- Error messages are printed to stderr in `__main__.py` (line 126) and `cargo.py` (lines 52-55, 59, 120)
- The "Updating Cargo.toml..." message is printed to stdout in `__main__.py` (line 90) before calling `update_cargo_version()`, but the error from validation appears first
- Solution: Print all messages to stdout instead of stderr to ensure consistent ordering. This will also allow reverting the `sys.stdout.flush()` calls that were added in `BUG_PR_VERSION_ERROR_ORDERING` (now marked as Complete)
- Frequency: Always (when validation error occurs during PR version update)

## Related Issues
- Related PRs: #26 (the PR that triggered this bug)
- Related requirements: `plan/25W48/REQ_PR_BINARY_BUILDS.md`
- Related bugs: `BUG_PR_VERSION_VALIDATION_FAILURE.md` (the validation error that exposes this ordering issue), `BUG_PR_VERSION_ERROR_ORDERING.md` (previous fix that added flush calls)
