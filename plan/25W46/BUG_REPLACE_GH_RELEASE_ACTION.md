# BUG: Replace softprops/action-gh-release with GitHub CLI (gh)

**Status**: ✅ Complete

## Description

The release workflow (`.github/workflows/release-build.yaml`) uses `softprops/action-gh-release@v2` to create GitHub releases. This action is unnecessary since GitHub CLI (`gh`) is already pre-installed in GitHub Actions runners. Using the native `gh` CLI directly provides better control, reduces dependencies, and aligns with the approach already used in `pr-label.yml`.

## Current State

✅ **FIXED** - The release workflow now uses native GitHub CLI (`gh release create`) instead of `softprops/action-gh-release@v2`.

### `.github/workflows/release-build.yaml`

**Lines 176-191**: Now uses native `gh release create` command:

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

**Previously (lines 176-194)**: Used `softprops/action-gh-release@v2` to create releases.

## Expected State

Replace the action with native GitHub CLI commands:

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

## Benefits

1. **Reduced Dependencies**: Eliminates external action dependency
2. **Consistency**: Aligns with `pr-label.yml` which already uses `gh` CLI directly
3. **Better Control**: Direct control over release creation process
4. **Security**: One less third-party action to trust
5. **Maintainability**: Native tooling is more stable and well-documented
6. **Performance**: Slight reduction in workflow overhead (no action setup)

## Impact

- **Severity**: Low (functionality improvement)
- **Priority**: Medium (quality improvement, consistency)

### Why This Matters

1. **Consistency**: The project already uses `gh` CLI in `pr-label.yml`, so using it for releases maintains consistency
2. **Dependency Reduction**: Fewer external actions mean fewer potential points of failure
3. **Security**: One less third-party action reduces supply chain attack surface
4. **Maintainability**: Native GitHub CLI is maintained by GitHub and has better long-term support


## Related Implementation Plan

See `work/25W46/BUG_REPLACE_GH_RELEASE_ACTION.md` for the detailed implementation plan.
