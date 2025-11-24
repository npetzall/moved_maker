# BUG: Workflows Using Unnecessary `fetch-depth: 0`

**Status**: ✅ Complete

## Description

Several workflows use `fetch-depth: 0` (full git history) when they don't need it. The `fetch-depth: 0` setting fetches the complete git history, which is slower, uses more network bandwidth, and consumes more storage. Only workflows that need to access git history (e.g., `git log`, `git describe`, `git tag`) require `fetch-depth: 0`. Workflows that only build, test, or run tools can use the default `fetch-depth: 1` (shallow clone).

## Current State

**Affected Files:**
- `.github/workflows/release-build.yaml` (4 occurrences)
- `.github/workflows/pr-label.yml` (1 occurrence)

### Detailed Analysis

#### `release-build.yaml`

1. **Line 16 - `security` job**:
   ```yaml
   - name: Checkout code
     uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
     with:
       ref: ${{ github.ref }}
       fetch-depth: 0
   ```
   - **Git commands used**: None
   - **Operations**: Runs `cargo deny`, `cargo audit`, `cargo geiger`
   - **Verdict**: ❌ **Unnecessary** - Can use default `fetch-depth: 1`

2. **Line 56 - `coverage` job**:
   ```yaml
   - name: Checkout code
     uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
     with:
       ref: ${{ github.ref }}
       fetch-depth: 0
   ```
   - **Git commands used**: None
   - **Operations**: Runs `cargo llvm-cov nextest`, generates coverage reports
   - **Verdict**: ❌ **Unnecessary** - Can use default `fetch-depth: 1`

3. **Line 110 - `build-and-release` job**:
   ```yaml
   - name: Checkout code
     uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
     with:
       ref: ${{ github.ref }}
       fetch-depth: 0
   ```
   - **Git commands used**: None
   - **Operations**: Builds release binaries, runs tests, creates checksums
   - **Verdict**: ❌ **Unnecessary** - Can use default `fetch-depth: 1`

4. **Line 180 - `release` job**:
   ```yaml
   - name: Checkout code
     uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
     with:
       ref: ${{ github.ref }}
       fetch-depth: 0
   ```
   - **Git commands used**: `git describe --tags --abbrev=0`, `git log`
   - **Operations**: Generates release notes by finding previous tag and listing commits
   - **Verdict**: ✅ **Required** - Must keep `fetch-depth: 0`

#### `pr-label.yml`

5. **Line 18 - `label` job**:
   ```yaml
   - name: Checkout code
     uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
     with:
       fetch-depth: 0
   ```
   - **Git commands used**: None
   - **Operations**: Uses `gh pr view` (GitHub API), no git operations
   - **Verdict**: ❌ **Unnecessary** - Can use default `fetch-depth: 1`

#### `release-version.yaml`

6. **Line 34 - `version` job**:
   ```yaml
   - name: Checkout code
     uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
     with:
       fetch-depth: 0
       token: ${{ steps.app-token.outputs.token }}
   ```
   - **Git commands used**: `git fetch --tags --force`, `git diff`, `git commit`, `git push`, `git tag`
   - **Operations**: Calculates version, commits changes, creates tags
   - **Verdict**: ✅ **Required** - Must keep `fetch-depth: 0`

## Expected State

Only workflows that need git history should use `fetch-depth: 0`. All other workflows should use the default `fetch-depth: 1` (or omit the parameter entirely).

### Summary

- **Required `fetch-depth: 0`**: 2 checkouts
  - `release-build.yaml` - `release` job (line 180)
  - `release-version.yaml` - `version` job (line 34)

- **Can use default**: 4 checkouts
  - `release-build.yaml` - `security` job (line 16)
  - `release-build.yaml` - `coverage` job (line 56)
  - `release-build.yaml` - `build-and-release` job (line 110)
  - `pr-label.yml` - `label` job (line 18)

## Impact

### Performance Impact
- **Severity**: Medium
- **Priority**: Low-Medium

- **Slower checkouts**: Full history fetch takes longer than shallow clone
- **Increased network usage**: More data transferred for each workflow run
- **Increased storage**: More disk space used on runners
- **Slower workflow execution**: Checkout step takes longer, delaying job start

### Cost Impact
- **Severity**: Low
- **Priority**: Low

- Slightly increased GitHub Actions minutes usage
- More network bandwidth consumption

### Developer Experience Impact
- **Severity**: Low
- **Priority**: Low

- Workflows may appear slower to start
- No functional impact (workflows still work correctly)

## When `fetch-depth: 0` is Required

`fetch-depth: 0` is required when workflows need to:

1. **Access git history**:
   - `git log` (with ranges like `tag1..tag2`)
   - `git describe --tags`
   - `git rev-list`
   - `git tag` operations that need to see all tags

2. **Perform git operations that need full context**:
   - `git diff` across commits
   - `git fetch --tags` (though this can work with shallow clones if tags are fetched separately)
   - Operations that need to traverse commit history

3. **Calculate versions from git history**:
   - Counting commits since last tag
   - Analyzing commit messages across history
   - Finding previous tags/versions


## Related Implementation Plan

See `work/25W46/BUG_WORKFLOWS_UNNECESSARY_FETCH_DEPTH.md` for the detailed implementation plan.
