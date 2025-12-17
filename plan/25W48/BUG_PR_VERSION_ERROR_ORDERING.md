# BUG: PR Version Error Message Appears Before Calculation Steps

**Status**: ✅ Complete

## Overview
When the version script fails during PR version calculation, the error message appears at the beginning of the output instead of after the calculation steps complete. This makes debugging difficult as the error is shown before the context of what was being calculated.

## Environment
- **OS**: GitHub Actions (ubuntu-latest)
- **Rust Version**: 1.90.0
- **Tool Version**: Version script in `.github/scripts/version`
- **Terraform Version**: N/A

## Steps to Reproduce
1. Open or update a pull request
2. The `pull_request.yaml` workflow runs the `version` job
3. The version script encounters an error (e.g., validation failure)
4. Observe the output order

## Expected Behavior
1. All calculation steps should complete and print their output
2. The calculation summary should be printed
3. Error messages should appear at the end of the output, after all calculation steps complete
4. This provides context for understanding what was being calculated when the error occurred

## Actual Behavior
1. The error message appears at the very beginning of the output
2. Calculation steps and summary are printed after the error
3. This makes it difficult to understand the context of the error
4. Example output order:
   ```
   Error updating Cargo.toml: Invalid version format...
   Version mode: pr
   GitHub client initialized...
   Calculating PR version...
   [calculation steps...]
   PR Version Calculation Summary...
   ```

## Error Messages / Output
```
Error updating Cargo.toml: Invalid version format in Cargo.toml: 0.2.1-pr26+87baede. Expected semantic version (e.g., 1.0.0)
Version mode: pr
GitHub client initialized for repository: npetzall/moved_maker
Calculating PR version...
Found latest tag: v0.2.0
Base version: 0.2.0
Fetching merged PRs since timestamp 1763934208...
Found 7 merged PR(s) to analyze
Analyzing 7 PR(s) for version labels...
Determined bump type: PATCH (no major/minor labels found)
Counting commits since tag v0.2.0 that modify application code...
Found 1 commit(s) modifying application code
==================================================
PR Version Calculation Summary:
  Base version: 0.2.0
  Bump type: PATCH
  Commit count: 1
  Calculated base version: 0.2.1
  PR number: 26
  Commit SHA: 87baede66f6784ed93eb4bcc58e9379904b84a17 (shortened to 87baede)
  PR version: 0.2.1-pr26+87baede
==================================================
Updating Cargo.toml with version 0.2.1-pr26+87baede...
```

## Minimal Reproduction Case
Run the version script in PR mode and trigger any error during the update step:
```bash
VERSION_MODE=pr PR_NUMBER=26 COMMIT_SHA=87baede66f6784ed93eb4bcc58e9379904b84a17 GITHUB_TOKEN=... GITHUB_REPOSITORY=npetzall/moved_maker python -m version
```

## Additional Context
- The error message ordering issue suggests that exception handling or output buffering is causing the error to be printed before the calculation steps complete
- Python's `print()` statements may be buffered, causing output to appear out of order
- Error messages printed to `stderr` may appear before `stdout` output depending on buffering
- The issue occurs in `__main__.py` where exception handling prints errors before the calculation summary
- This makes debugging more difficult as users see the error before understanding what was being calculated
- Frequency: Always (when any error occurs during PR version calculation)

## Related Issues
- Related PRs: #26 (the PR that triggered this bug)
- Related requirements: `plan/25W48/REQ_PR_BINARY_BUILDS.md`
- Related bugs: `BUG_PR_VERSION_VALIDATION_FAILURE.md` (the validation error that exposes this ordering issue)
