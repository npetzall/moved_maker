# Release Workflow Build/Version Mismatch

## Summary

The release workflow builds the release artifacts before committing and tagging the version update to `Cargo.toml`. This results in the build happening on a different commit than the one that contains the version update, which is incorrect and can cause version mismatches.

## Affected File

- `.github/workflows/release.yaml`

## Current Behavior

The workflow executes in the following order:

1. **`version` job** (lines 37-135):
   - Calculates the new version
   - Updates `Cargo.toml` locally in the job (line 132-135)
   - Outputs the version for other jobs

2. **`build-and-release` job** (lines 137-224):
   - **Depends on `version` job** (line 138)
   - Updates `Cargo.toml` locally again (line 163-166)
   - Builds the release artifacts using this version
   - **BUT**: The commit that triggered the workflow does NOT have the updated version

3. **`release` job** (lines 226-312):
   - Updates `Cargo.toml` again (line 276-279)
   - Commits and pushes the version update to `main` (line 281-287)
   - Creates and pushes the git tag (line 289-292)
   - Creates the GitHub release (line 294-312)

## Problem

The `build-and-release` job builds the release on the original commit (the one that triggered the workflow), but the version update is only committed to the repository AFTER the build completes. This means:

1. The build happens on commit `ABC` (original push to main)
2. The version update is committed as commit `XYZ` (after build completes)
3. The tag points to commit `XYZ` (with the version update)
4. But the artifacts were built from commit `ABC` (without the version update)

This creates a mismatch where:
- The tag and release point to commit `XYZ` with the updated `Cargo.toml`
- But the binaries were built from commit `ABC` which may have a different version in `Cargo.toml`

## Expected Behavior

The workflow should:

1. Calculate the version
2. Update `Cargo.toml` and commit it to the repository
3. Create and push the tag
4. **Then** build the release artifacts from the tagged commit
5. Create the GitHub release with the artifacts

This ensures that:
- The tag points to the commit with the correct version
- The binaries are built from the same commit that has the version update
- Everything is consistent and traceable

## Impact

- Version mismatch between built artifacts and repository state
- Potential confusion about which commit the release artifacts correspond to
- Risk of incorrect version information in binaries
- Poor traceability and reproducibility


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_WORKFLOW_ORDER.md` for the detailed implementation plan.
