# Implementation Plan: BUG_REPLACE_GH_RELEASE_ACTION

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_REPLACE_GH_RELEASE_ACTION.md`.

## Context

Related bug report: `plan/25W46/BUG_REPLACE_GH_RELEASE_ACTION.md`

## Steps to Fix

1. Remove the `softprops/action-gh-release@v2` step from `.github/workflows/release-build.yaml`
2. Replace it with a `run:` step that uses `gh release create` command
3. Ensure `GH_TOKEN` environment variable is set (using `secrets.GITHUB_TOKEN`)
4. Use the existing `release_notes.md` file generated in the previous step
5. Upload all artifacts as release assets using `gh release create` file arguments
6. Test the workflow to ensure releases are created correctly

### Implementation Details

The `gh release create` command supports:
- `--title`: Release title
- `--notes-file`: Release notes from file (already generated in `release_notes.md`)
- Multiple file arguments: All artifacts can be passed as arguments
- `--verify-tag`: Verify that the tag exists before creating the release (will fail if tag doesn't exist)
- Draft/prerelease flags: Can be added if needed (`--draft`, `--prerelease`)

### Example Implementation

```yaml
- name: Create GitHub Release
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh release create "${{ github.ref_name }}" \
      --title "Release ${{ github.ref_name }}" \
      --notes-file release_notes.md \
      --verify-tag \
      artifacts/move_maker-linux-x86_64 \
      artifacts/move_maker-linux-x86_64.sha256 \
      artifacts/move_maker-linux-aarch64 \
      artifacts/move_maker-linux-aarch64.sha256 \
      artifacts/move_maker-macos-x86_64 \
      artifacts/move_maker-macos-x86_64.sha256 \
      artifacts/move_maker-macos-aarch64 \
      artifacts/move_maker-macos-aarch64.sha256
```

## Affected Files

- `.github/workflows/release-build.yaml` (lines 176-191) ✅ **FIXED**

## Related Work

This aligns with the approach taken in:
- `.github/workflows/pr-label.yml` - Already uses `gh` CLI directly with `GH_TOKEN` environment variable
- `plan/25W46/BUG_GITHUB_CLI_TOKEN.md` - Documents the pattern of using `gh` CLI directly

## References

- [GitHub CLI: gh release create](https://cli.github.com/manual/gh_release_create)
- [GitHub Actions: Using GitHub CLI in workflows](https://docs.github.com/en/actions/using-workflows/using-github-cli-in-workflows)
- [GitHub Actions runners include GitHub CLI by default](https://github.com/actions/runner-images)

## Status

✅ **FIXED** - Replaced `softprops/action-gh-release@v2` with native GitHub CLI (`gh release create`)

## Notes

- ✅ The `release_notes.md` file is already generated in the previous step (lines 137-169), so it can be directly used with `--notes-file`
- ✅ All artifacts are already downloaded to the `artifacts/` directory (lines 171-174), so paths are correct
- ✅ The `GH_TOKEN` environment variable uses `secrets.GITHUB_TOKEN` (same as `pr-label.yml`)
- ✅ The job already has `contents: write` permission (line 129), which is required for creating releases
- ✅ The `--verify-tag` flag is included to ensure the command fails if the tag doesn't exist, which is the desired behavior for this workflow
- ✅ Implementation complete: `softprops/action-gh-release@v2` has been replaced with native `gh release create` command

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/release-build.yaml`

**File:** `.github/workflows/release-build.yaml`

1. **Replace `softprops/action-gh-release@v2` step with `gh release create` command (lines 176-191)**
   - [x] Locate the "Create GitHub Release" step at lines 176-194
   - [x] Replace the entire step with:
     ```yaml
     - name: Create GitHub Release
       env:
         GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
       run: |
         gh release create "${{ github.ref_name }}" \
           --title "Release ${{ github.ref_name }}" \
           --notes-file release_notes.md \
           --verify-tag \
           artifacts/move_maker-linux-x86_64 \
           artifacts/move_maker-linux-x86_64.sha256 \
           artifacts/move_maker-linux-aarch64 \
           artifacts/move_maker-linux-aarch64.sha256 \
           artifacts/move_maker-macos-x86_64 \
           artifacts/move_maker-macos-x86_64.sha256 \
           artifacts/move_maker-macos-aarch64 \
           artifacts/move_maker-macos-aarch64.sha256
     ```
   - [x] Verify step placement (should be in `release` job, after artifact download step)
   - [x] Verify YAML indentation matches other steps
   - [x] Verify `GH_TOKEN` environment variable uses `secrets.GITHUB_TOKEN`
   - [x] Verify `--notes-file release_notes.md` references the file generated in previous step
   - [x] Verify `--verify-tag` flag is included to ensure tag exists before creating release
   - [x] Verify all artifact paths are correct (should match downloaded artifact names)

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.github/workflows/release-build.yaml`
   - Restore `softprops/action-gh-release@v2` step
   - Verify workflow returns to working state
   - Investigate GitHub CLI command issues before retrying

2. **Partial Rollback**
   - If release creation fails, investigate specific error:
     - Check if `GH_TOKEN` is properly set
     - Verify `release_notes.md` file exists and is readable
     - Verify all artifact files exist at specified paths
     - Check if tag exists (if `--verify-tag` is causing issues)
   - Consider removing `--verify-tag` flag if tag verification is not critical
   - Verify job permissions include `contents: write`

3. **Alternative Approach**
   - If `gh release create` command fails, consider:
     - Using `gh release create` without `--verify-tag` if tag verification is not needed
     - Verifying that `secrets.GITHUB_TOKEN` has sufficient permissions
     - Checking if job-level permissions need adjustment
     - Using explicit authentication: `echo "${{ secrets.GITHUB_TOKEN }}" | gh auth login --with-token`
     - Splitting release creation and asset upload into separate steps if needed

### Implementation Order

1. **Update `.github/workflows/release-build.yaml`** ✅
   - [x] Replace `softprops/action-gh-release@v2` step with `gh release create` command
   - [x] Ensure `GH_TOKEN` environment variable is set correctly
   - [x] Verify all artifact paths match downloaded artifact names

2. **Test via tag push** ⏳
   - Create a test tag (e.g., `v0.0.0-test`) to verify release workflow
   - Monitor workflow logs to ensure release creation succeeds
   - Verify release is created with correct title, notes, and assets
   - Check that all artifacts are uploaded correctly

3. **Final verification** ⏳
   - Test release workflow end-to-end with a real release tag
   - Verify release notes are correctly formatted
   - Verify all artifacts are attached to the release
   - Monitor workflow logs to ensure all GitHub CLI operations succeed

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:**
  - Release creation might fail if `GH_TOKEN` is not properly set or accessible
  - GitHub CLI command might fail with authentication errors
  - Release might not be created if tag doesn't exist (with `--verify-tag`)
  - Artifacts might not be uploaded if paths are incorrect
- **Mitigation:**
  - Easy rollback (just restore the action step)
  - GitHub CLI is pre-installed, so no installation issues
  - `secrets.GITHUB_TOKEN` is automatically available in all workflows
  - Can test incrementally via test tags
  - Well-documented GitHub CLI command
  - Job already has `contents: write` permission
- **Testing:**
  - Can be tested via test tag before affecting real releases
  - Release workflow can be verified through workflow logs
  - Release creation behavior can be verified through GitHub UI
- **Dependencies:**
  - `secrets.GITHUB_TOKEN` must be available (standard in all workflows)
  - GitHub CLI must be available (pre-installed in runners)
  - Job-level permissions must allow `contents: write` (already configured at line 129)
  - `release_notes.md` file must exist (generated in previous step at lines 137-169)
  - All artifacts must be downloaded to `artifacts/` directory (done at lines 171-174)
- **Permissions:**
  - Verify that `secrets.GITHUB_TOKEN` has sufficient permissions for:
    - Creating releases (`contents: write` - already configured at line 129)
    - Uploading release assets (`contents: write` - already configured)

### Expected Outcomes

After successful implementation:

- **Reduced Dependencies:** Eliminated external action dependency (`softprops/action-gh-release@v2`)
- **Consistency:** Aligned with `pr-label.yml` which already uses `gh` CLI directly
- **Better Control:** Direct control over release creation process using native GitHub CLI
- **Security:** One less third-party action reduces supply chain attack surface
- **Maintainability:** Native tooling is more stable and well-documented
- **Performance:** Slight reduction in workflow overhead (no action setup step)
- **Functionality:** Same release creation behavior with native tooling
