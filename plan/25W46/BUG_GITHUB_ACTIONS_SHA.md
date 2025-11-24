# BUG: GitHub Actions workflows use version tags instead of full commit SHAs

**Status**: ✅ Complete

## Description

All GitHub Actions workflows in `.github/workflows/` are using version tags (e.g., `@v4`, `@v2`, `@stable`) instead of full commit SHAs for action references. This is a security best practice violation, as tags can be moved or updated, potentially introducing compromised code. GitHub recommends using full commit SHAs to pin actions to specific, immutable versions.

## Current State

✅ **FIXED** - All workflows now use full commit SHAs instead of version tags.

Previously, all workflows were using version tags instead of full SHAs:

### `pull_request.yaml`
- `actions/checkout@v4` (lines 12, 44, 76, 143) - 4 occurrences
- `dtolnay/rust-toolchain@stable` (lines 15, 47, 79, 151) - 4 occurrences
- `Swatinem/rust-cache@v2` (lines 19, 52, 84, 156) - 4 occurrences
- `actions/upload-artifact@v4` (line 63) - 1 occurrence
- `actions/setup-python@v4` (line 146) - 1 occurrence

### `pr-label.yml`
- `actions/checkout@v4` (line 16) - 1 occurrence
- Note: This workflow uses `gh` CLI directly (not `cli/cli-action@v2`)

### `release-build.yaml`
- `actions/checkout@v4` (lines 13, 62, 132) - 3 occurrences
- `dtolnay/rust-toolchain@stable` (lines 19, 68) - 2 occurrences
- `Swatinem/rust-cache@v2` (lines 23, 73) - 2 occurrences
- `actions/upload-artifact@v4` (lines 101, 119) - 2 occurrences
- `actions/download-artifact@v4` (line 172) - 1 occurrence
- Note: This workflow uses `gh` CLI directly for release creation (not `softprops/action-gh-release@v2`)

### `release-version.yaml`
- `actions/create-github-app-token@v2` (line 20) - 1 occurrence
- `actions/checkout@v4` (line 26) - 1 occurrence

## Expected State

All action references should use full commit SHAs in the format:
```yaml
uses: owner/repo@abc123def4567890123456789012345678901234
```

Instead of:
```yaml
uses: owner/repo@v4
```

## Security Impact

- **Severity**: Medium-High
- **Priority**: High (security best practice)

### Why This Matters

1. **Tag Immutability**: Tags can be force-pushed or deleted, allowing malicious code to be injected
2. **Supply Chain Security**: Using SHAs ensures you're using the exact version you tested
3. **GitHub Recommendations**: GitHub's security documentation recommends pinning to SHAs
4. **Compliance**: Many security standards (e.g., OWASP) recommend SHA pinning


## Related Implementation Plan

See `work/25W46/BUG_GITHUB_ACTIONS_SHA.md` for the detailed implementation plan.
