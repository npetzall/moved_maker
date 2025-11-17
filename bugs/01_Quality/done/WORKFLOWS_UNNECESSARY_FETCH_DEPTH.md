# Bug: Workflows Using Unnecessary `fetch-depth: 0`

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

## Solution

Remove `fetch-depth: 0` from checkouts that don't need it:

### Fix 1: `release-build.yaml` - `security` job (line 16)

**Before:**
```yaml
- name: Checkout code
  uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
  with:
    ref: ${{ github.ref }}
    fetch-depth: 0
```

**After:**
```yaml
- name: Checkout code
  uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
  with:
    ref: ${{ github.ref }}
```

### Fix 2: `release-build.yaml` - `coverage` job (line 56)

**Before:**
```yaml
- name: Checkout code
  uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
  with:
    ref: ${{ github.ref }}
    fetch-depth: 0
```

**After:**
```yaml
- name: Checkout code
  uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
  with:
    ref: ${{ github.ref }}
```

### Fix 3: `release-build.yaml` - `build-and-release` job (line 110)

**Before:**
```yaml
- name: Checkout code
  uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
  with:
    ref: ${{ github.ref }}
    fetch-depth: 0
```

**After:**
```yaml
- name: Checkout code
  uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
  with:
    ref: ${{ github.ref }}
```

### Fix 4: `pr-label.yml` - `label` job (line 18)

**Before:**
```yaml
- name: Checkout code
  uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
  with:
    fetch-depth: 0
```

**After:**
```yaml
- name: Checkout code
  uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
```

## Keep `fetch-depth: 0` (Do Not Change)

### `release-build.yaml` - `release` job (line 180)

**Keep as-is:**
```yaml
- name: Checkout code
  uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
  with:
    ref: ${{ github.ref }}
    fetch-depth: 0  # Required for git describe and git log
```

**Reason**: Uses `git describe --tags --abbrev=0` and `git log` to generate release notes.

### `release-version.yaml` - `version` job (line 34)

**Keep as-is:**
```yaml
- name: Checkout code
  uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
  with:
    fetch-depth: 0  # Required for git operations and version calculation
    token: ${{ steps.app-token.outputs.token }}
```

**Reason**: Uses `git fetch --tags`, `git diff`, `git commit`, `git push`, `git tag` for version calculation and git operations.

## Testing

### Verification Steps

1. **Test workflows still work correctly**:
   - Run `release-build.yaml` workflow (all jobs should pass)
   - Run `pr-label.yml` workflow (should still apply labels correctly)
   - Verify no git-related errors appear

2. **Verify performance improvement**:
   - Compare checkout times before and after (should be faster)
   - Check workflow execution times (should be slightly faster overall)

3. **Verify functionality**:
   - Security job: Should still run `cargo deny`, `cargo audit`, `cargo geiger` successfully
   - Coverage job: Should still generate coverage reports correctly
   - Build-and-release job: Should still build binaries successfully
   - Label job: Should still apply PR labels correctly

### Expected Behavior After Fix

- All workflows should continue to work exactly as before
- Checkout steps should complete faster
- No functional changes to workflow behavior
- Workflows that need git history (`release` and `version` jobs) continue to work correctly

## Affected Files

- `.github/workflows/release-build.yaml`
  - Line 16: Remove `fetch-depth: 0` from `security` job
  - Line 56: Remove `fetch-depth: 0` from `coverage` job
  - Line 110: Remove `fetch-depth: 0` from `build-and-release` job
  - Line 180: **Keep** `fetch-depth: 0` in `release` job (required)

- `.github/workflows/pr-label.yml`
  - Line 18: Remove `fetch-depth: 0` from `label` job

- `.github/workflows/release-version.yaml`
  - Line 34: **Keep** `fetch-depth: 0` in `version` job (required)

## Benefits of Fix

1. **Faster checkouts**: Shallow clone (`fetch-depth: 1`) is significantly faster than full history
2. **Reduced network usage**: Less data transferred per workflow run
3. **Reduced storage**: Less disk space used on runners
4. **Faster workflow execution**: Jobs start sooner after checkout completes
5. **Better resource utilization**: More efficient use of GitHub Actions resources

## References

- [actions/checkout documentation](https://github.com/actions/checkout)
- [Git shallow clone documentation](https://git-scm.com/docs/git-clone#Documentation/git-clone.txt---depthltdepthgt)
- [GitHub Actions: Checkout action inputs](https://github.com/actions/checkout#inputs)

## Additional Notes

### Default Behavior

When `fetch-depth` is not specified, `actions/checkout` uses `fetch-depth: 1` by default, which creates a shallow clone with only the latest commit. This is sufficient for most workflows that don't need git history.

### When to Use `fetch-depth: 0`

Use `fetch-depth: 0` only when:
- You need to run `git log` with commit ranges (e.g., `git log tag1..tag2`)
- You need to use `git describe` to find tags
- You need to count commits or analyze commit history
- You need to perform git operations that require full history context

### Performance Impact

The performance difference between `fetch-depth: 1` and `fetch-depth: 0` depends on repository size:
- **Small repositories**: Minimal difference (seconds)
- **Large repositories**: Significant difference (can be minutes for very large repos)
- **Typical repositories**: Noticeable improvement (10-30 seconds faster)

## Status

✅ **COMPLETED** - Implementation finished, all unnecessary `fetch-depth: 0` removed

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/release-build.yaml`

**File:** `.github/workflows/release-build.yaml`

1. **Update `security` job (line 16)**
   - [x] Locate the checkout step at line 16-24
   - [x] Remove `fetch-depth: 0` from the `with` block
   - [x] Keep `ref: ${{ github.ref }}` parameter
   - [x] Verify YAML syntax is correct (no trailing commas, proper indentation)
   - [x] Verify the checkout step still has the correct action version

2. **Update `coverage` job (line 56)**
   - [x] Locate the checkout step at line 56-64 (line numbers may shift after first edit)
   - [x] Remove `fetch-depth: 0` from the `with` block
   - [x] Keep `ref: ${{ github.ref }}` parameter
   - [x] Verify YAML syntax is correct (no trailing commas, proper indentation)
   - [x] Verify the checkout step still has the correct action version

3. **Update `build-and-release` job (line 110)**
   - [x] Locate the checkout step at line 110-118 (line numbers may shift after previous edits)
   - [x] Remove `fetch-depth: 0` from the `with` block
   - [x] Keep `ref: ${{ github.ref }}` parameter
   - [x] Verify YAML syntax is correct (no trailing commas, proper indentation)
   - [x] Verify the checkout step still has the correct action version

4. **Verify `release` job (line 180) - DO NOT CHANGE**
   - [x] Locate the checkout step at line 180-188 (line numbers may shift after previous edits)
   - [x] Verify `fetch-depth: 0` is still present (required for git describe and git log)
   - [x] Verify the comment explaining why it's required is present
   - [x] Do not modify this checkout step

#### Step 2: Update `.github/workflows/pr-label.yml`

**File:** `.github/workflows/pr-label.yml`

1. **Update `label` job (line 18)**
   - [x] Locate the checkout step at line 18-22
   - [x] Remove `fetch-depth: 0` from the `with` block
   - [x] Remove the entire `with` block if it only contained `fetch-depth: 0`
   - [x] Verify YAML syntax is correct (no trailing commas, proper indentation)
   - [x] Verify the checkout step still has the correct action version

#### Step 3: Verify `.github/workflows/release-version.yaml`

**File:** `.github/workflows/release-version.yaml`

1. **Verify `version` job (line 34) - DO NOT CHANGE**
   - [x] Locate the checkout step at line 34-38
   - [x] Verify `fetch-depth: 0` is still present (required for git operations)
   - [x] Verify the comment explaining why it's required is present
   - [x] Verify `token` parameter is still present
   - [x] Do not modify this checkout step

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to affected workflow files
   - Restore `fetch-depth: 0` to all modified checkout steps
   - Verify workflows return to working state
   - Investigate why shallow clone caused issues before retrying

2. **Partial Rollback**
   - If only specific jobs fail, restore `fetch-depth: 0` to those jobs only
   - Investigate why specific jobs require full history
   - Common issues:
     - Hidden git commands in scripts or actions
     - Actions that internally use git history
     - Build tools that check git history
   - Consider if specific jobs actually need full history after investigation

3. **Alternative Approach**
   - If shallow clone causes issues, investigate root cause:
     - Check if any actions or scripts use git commands that require history
     - Verify if any build tools access git history
     - Consider using `fetch-depth: 0` only for jobs that actually need it
   - Document why specific jobs require full history if they do

### Implementation Order

1. **Start with `.github/workflows/pr-label.yml`** (lowest risk, easiest to test)
   - Update `label` job checkout step
   - Test via pull request to verify label job still works
   - Verify no git-related errors appear
   - Monitor checkout time improvement

2. **Update `.github/workflows/release-build.yaml`** (one job at a time)
   - Start with `security` job (lowest risk, runs early in workflow)
     - Update checkout step
     - Test via pull request or release workflow
     - Verify security tools still work correctly
   - Then `coverage` job
     - Update checkout step
     - Test via pull request or release workflow
     - Verify coverage generation still works correctly
   - Then `build-and-release` job (most complex, runs last)
     - Update checkout step
     - Test via release workflow
     - Verify builds and releases still work correctly
   - Verify `release` job still has `fetch-depth: 0` (do not change)

3. **Final verification**
   - Run full release workflow to verify all jobs work correctly
   - Compare checkout times before and after (should be faster)
   - Verify no functional regressions
   - Monitor workflow execution times

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:**
  - Workflows might fail if they actually need git history (unlikely based on analysis)
  - Some actions or scripts might use git commands that require history (should be caught in testing)
  - Build tools might access git history (should be caught in testing)
- **Mitigation:**
  - Easy rollback (just restore `fetch-depth: 0`)
  - Can test incrementally via pull requests
  - Changes are simple (removing one parameter)
  - No functional changes expected (only performance improvement)
  - Can verify each job independently before moving to next
- **Testing:**
  - Can be fully tested via pull requests before affecting main branch
  - Each job can be tested independently
  - Checkout behavior can be verified through workflow logs
  - Performance improvement can be measured through workflow execution times
- **Dependencies:**
  - No new dependencies required
  - Uses standard `actions/checkout` behavior (default `fetch-depth: 1`)
  - Compatible with all GitHub Actions runners
  - No changes to workflow logic or job dependencies

### Expected Outcomes

After successful implementation:

- **Performance Improvement:** Checkout steps complete 10-30 seconds faster (depending on repository size)
- **Network Usage Reduction:** Less data transferred per workflow run (shallow clone vs full history)
- **Storage Reduction:** Less disk space used on runners
- **Faster Workflow Execution:** Jobs start sooner after checkout completes
- **Better Resource Utilization:** More efficient use of GitHub Actions resources
- **No Functional Changes:** All workflows continue to work exactly as before
- **Maintained Functionality:** Workflows that need git history (`release` and `version` jobs) continue to work correctly with `fetch-depth: 0`
