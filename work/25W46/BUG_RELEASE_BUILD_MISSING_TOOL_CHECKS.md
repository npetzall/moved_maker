# Implementation Plan: BUG_RELEASE_BUILD_MISSING_TOOL_CHECKS

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_RELEASE_BUILD_MISSING_TOOL_CHECKS.md`.

## Context

Related bug report: `plan/25W46/BUG_RELEASE_BUILD_MISSING_TOOL_CHECKS.md`

## Solution

Add explicit tool checks using workflow annotation commands to make failures highly visible:

### For `jq` Checks

**In `.github/workflows/release-build.yaml` (before line 77):**
```yaml
- name: Check jq availability
  run: |
    if ! command -v jq &> /dev/null; then
      echo "::error::jq is not installed. Required for coverage threshold checking."
      exit 1
    fi
    echo "✅ jq is available: $(jq --version)"
```

**In `.github/workflows/pull_request.yaml` (before line 103):**
```yaml
- name: Check jq availability
  run: |
    if ! command -v jq &> /dev/null; then
      echo "::error::jq is not installed. Required for coverage threshold checking."
      exit 1
    fi
    echo "✅ jq is available: $(jq --version)"
```

### For `gh` CLI Checks

**In `.github/workflows/release-build.yaml` (before line 221):**
```yaml
- name: Check gh CLI availability
  run: |
    if ! command -v gh &> /dev/null; then
      echo "::error::GitHub CLI (gh) is not installed. Required for creating releases."
      exit 1
    fi
    echo "✅ GitHub CLI is available: $(gh --version | head -n 1)"
```

**In `.github/workflows/pr-label.yml` (before line 18):**
```yaml
- name: Check gh CLI availability
  run: |
    if ! command -v gh &> /dev/null; then
      echo "::error::GitHub CLI (gh) is not installed. Required for PR label management."
      exit 1
    fi
    echo "✅ GitHub CLI is available: $(gh --version | head -n 1)"
```

## Workflow Annotation Commands

GitHub Actions supports workflow annotation commands that create visible messages in the UI:

- `::error::` - Creates an error annotation (red, visible in UI)
- `::warning::` - Creates a warning annotation (yellow, visible in UI)
- `::notice::` - Creates a notice annotation (blue, visible in UI)

These annotations appear:
- In the workflow run summary
- Inline with the step that produced them
- In the annotations tab
- As part of the check run status

## Implementation Details

### Step Placement

1. **jq Checks**:
   - `.github/workflows/release-build.yaml`: Should be placed in the `coverage` job, before the "Check coverage thresholds" step (before line 77)
   - `.github/workflows/pull_request.yaml`: Should be placed in the `coverage` job, before the "Check coverage thresholds" step (before line 103)

2. **gh CLI Checks**:
   - `.github/workflows/release-build.yaml`: Should be placed in the `release` job, before the "Create GitHub Release" step (before line 221)
   - `.github/workflows/pr-label.yml`: Should be placed in the `label` job, before the "Analyze commits and apply labels" step (before line 18)

### Error Handling

- Use `command -v` to check for tool availability (POSIX-compliant)
- Exit with code 1 to fail the step immediately
- Provide clear error message with `::error::` annotation
- Show success message with tool version for verification

### Example Implementation

```yaml
- name: Check jq availability
  run: |
    if ! command -v jq &> /dev/null; then
      echo "::error::jq is not installed. Required for coverage threshold checking."
      exit 1
    fi
    echo "✅ jq is available: $(jq --version)"

- name: Check coverage thresholds
  run: |
    # Generate JSON report from collected coverage data
    cargo llvm-cov report --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

```yaml
- name: Check gh CLI availability
  run: |
    if ! command -v gh &> /dev/null; then
      echo "::error::GitHub CLI (gh) is not installed. Required for creating releases."
      exit 1
    fi
    echo "✅ GitHub CLI is available: $(gh --version | head -n 1)"

- name: Create GitHub Release
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh release create "${{ github.ref_name }}" \
      --title "Release ${{ github.ref_name }}" \
      --notes-file release_notes.md \
      --verify-tag \
      ...
```

## Benefits

1. **Early Failure Detection**: Fail fast with clear error messages
2. **Better Visibility**: Error annotations appear prominently in GitHub UI
3. **Easier Debugging**: Clear indication of what's missing
4. **Better UX**: Success messages confirm tools are available
5. **Documentation**: Makes tool dependencies explicit in workflow

## Testing

### Local Testing

```bash
# Test jq check
if ! command -v jq &> /dev/null; then
  echo "::error::jq is not installed. Required for coverage threshold checking."
  exit 1
fi
echo "✅ jq is available: $(jq --version)"

# Test gh CLI check
if ! command -v gh &> /dev/null; then
  echo "::error::GitHub CLI (gh) is not installed. Required for creating releases."
  exit 1
fi
echo "✅ GitHub CLI is available: $(gh --version | head -n 1)"
```

### CI Testing

1. Run workflow normally (should pass with tools available)
2. Simulate missing tool (temporarily rename tool or use different runner)
3. Verify error annotation appears in GitHub Actions UI
4. Verify workflow fails with clear error message

## Affected Files

- `.github/workflows/release-build.yaml`
  - Add `jq` check before line 77 (coverage job)
  - Add `gh` CLI check before line 221 (release job)
- `.github/workflows/pull_request.yaml`
  - Add `jq` check before line 103 (coverage job)
- `.github/workflows/pr-label.yml`
  - Add `gh` CLI check before line 18 (label job)

## References

- [GitHub Actions Workflow Commands](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions)
- [GitHub Actions Annotations](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-error-message)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [jq Documentation](https://stedolan.github.io/jq/)

## Status

✅ **COMPLETED** - All tool availability checks have been implemented

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Add jq availability check to coverage job

**File:** `.github/workflows/release-build.yaml`

1. **Add jq check step (before line 77)**
   - [x] Locate the `coverage` job (starts at line 48)
   - [x] Find the "Generate coverage" step (line 74-75)
   - [x] Add new step after "Generate coverage" and before "Check coverage thresholds" (before line 77)
   - [x] Insert the following step:
     ```yaml
     - name: Check jq availability
       run: |
         if ! command -v jq &> /dev/null; then
           echo "::error::jq is not installed. Required for coverage threshold checking."
           exit 1
         fi
         echo "✅ jq is available: $(jq --version)"
     ```
   - [x] Verify step placement: Should be after "Generate coverage" (line 74-75) and before "Check coverage thresholds" (line 77)
   - [x] Verify YAML indentation matches other steps in the job
   - [x] Verify the step name is descriptive and clear

2. **Verify coverage threshold check step**
   - [x] Ensure "Check coverage thresholds" step (line 77-83) remains unchanged
   - [x] Verify that `jq` command on line 83 will now have explicit check before it
   - [x] Confirm the workflow flow: Generate coverage → Check jq → Check thresholds

**Expected result after fix:**
```yaml
- name: Generate coverage
  run: cargo llvm-cov nextest --all-features

- name: Check jq availability
  run: |
    if ! command -v jq &> /dev/null; then
      echo "::error::jq is not installed. Required for coverage threshold checking."
      exit 1
    fi
    echo "✅ jq is available: $(jq --version)"

- name: Check coverage thresholds
  run: |
    # Generate JSON report from collected coverage data
    cargo llvm-cov report --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

#### Step 2: Add jq availability check to pull_request.yaml

**File:** `.github/workflows/pull_request.yaml`

1. **Add jq check step (before line 103)**
   - [x] Locate the `coverage` job (starts at line 78)
   - [x] Find the "Generate coverage" step (line 100-101)
   - [x] Add new step after "Generate coverage" and before "Check coverage thresholds" (before line 103)
   - [x] Insert the following step:
     ```yaml
     - name: Check jq availability
       run: |
         if ! command -v jq &> /dev/null; then
           echo "::error::jq is not installed. Required for coverage threshold checking."
           exit 1
         fi
         echo "✅ jq is available: $(jq --version)"
     ```
   - [x] Verify step placement: Should be after "Generate coverage" (line 100-101) and before "Check coverage thresholds" (line 103)
   - [x] Verify YAML indentation matches other steps in the job
   - [x] Verify the step name is descriptive and clear

2. **Verify coverage threshold check step**
   - [x] Ensure "Check coverage thresholds" step (line 103-109) remains unchanged
   - [x] Verify that `jq` command on line 109 will now have explicit check before it
   - [x] Confirm the workflow flow: Generate coverage → Check jq → Check thresholds

**Expected result after fix:**
```yaml
- name: Generate coverage
  run: cargo llvm-cov nextest --all-features

- name: Check jq availability
  run: |
    if ! command -v jq &> /dev/null; then
      echo "::error::jq is not installed. Required for coverage threshold checking."
      exit 1
    fi
    echo "✅ jq is available: $(jq --version)"

- name: Check coverage thresholds
  run: |
    # Generate JSON report from collected coverage data
    cargo llvm-cov report --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

#### Step 3: Add gh CLI availability check to release job

**File:** `.github/workflows/release-build.yaml`

1. **Add gh CLI check step (before line 221)**
   - [x] Locate the `release` job (starts at line 170)
   - [x] Find the "Download all artifacts" step (line 216-219)
   - [x] Add new step after "Download all artifacts" and before "Create GitHub Release" (before line 221)
   - [x] Insert the following step:
     ```yaml
     - name: Check gh CLI availability
       run: |
         if ! command -v gh &> /dev/null; then
           echo "::error::GitHub CLI (gh) is not installed. Required for creating releases."
           exit 1
         fi
         echo "✅ GitHub CLI is available: $(gh --version | head -n 1)"
     ```
   - [x] Verify step placement: Should be after "Download all artifacts" (line 216-219) and before "Create GitHub Release" (line 221)
   - [x] Verify YAML indentation matches other steps in the job
   - [x] Verify the step name is descriptive and clear

2. **Verify GitHub release creation step**
   - [x] Ensure "Create GitHub Release" step (line 221-236) remains unchanged
   - [x] Verify that `gh` command on line 225 will now have explicit check before it
   - [x] Confirm the workflow flow: Download artifacts → Check gh CLI → Create release

**Expected result after fix:**
```yaml
- name: Download all artifacts
  uses: actions/download-artifact@018cc2cf5baa6db3ef3c5f8a56943fffe632ef53  # v6.0.0
  with:
    path: artifacts

- name: Check gh CLI availability
  run: |
    if ! command -v gh &> /dev/null; then
      echo "::error::GitHub CLI (gh) is not installed. Required for creating releases."
      exit 1
    fi
    echo "✅ GitHub CLI is available: $(gh --version | head -n 1)"

- name: Create GitHub Release
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh release create "${{ github.ref_name }}" \
      --title "Release ${{ github.ref_name }}" \
      --notes-file release_notes.md \
      --verify-tag \
      ...
```

#### Step 4: Add gh CLI availability check to pr-label.yml

**File:** `.github/workflows/pr-label.yml`

1. **Add gh CLI check step (before line 18)**
   - [x] Locate the `label` job (starts at line 12)
   - [x] Find the "Checkout code" step (line 15-16)
   - [x] Add new step after "Checkout code" and before "Analyze commits and apply labels" (before line 18)
   - [x] Insert the following step:
     ```yaml
     - name: Check gh CLI availability
       run: |
         if ! command -v gh &> /dev/null; then
           echo "::error::GitHub CLI (gh) is not installed. Required for PR label management."
           exit 1
         fi
         echo "✅ GitHub CLI is available: $(gh --version | head -n 1)"
     ```
   - [x] Verify step placement: Should be after "Checkout code" (line 15-16) and before "Analyze commits and apply labels" (line 18)
   - [x] Verify YAML indentation matches other steps in the job
   - [x] Verify the step name is descriptive and clear

2. **Verify PR label management step**
   - [x] Ensure "Analyze commits and apply labels" step (line 18-50) remains unchanged
   - [x] Verify that `gh` commands on lines 25, 39, 43, 45 will now have explicit check before them
   - [x] Confirm the workflow flow: Checkout code → Check gh CLI → Analyze commits and apply labels

**Expected result after fix:**
```yaml
- name: Checkout code
  uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0

- name: Check gh CLI availability
  run: |
    if ! command -v gh &> /dev/null; then
      echo "::error::GitHub CLI (gh) is not installed. Required for PR label management."
      exit 1
    fi
    echo "✅ GitHub CLI is available: $(gh --version | head -n 1)"

- name: Analyze commits and apply labels
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    PR_NUM=${{ github.event.pull_request.number }}
    # ... rest of the step ...
```

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.github/workflows/release-build.yaml`
   - Revert changes to `.github/workflows/pull_request.yaml`
   - Revert changes to `.github/workflows/pr-label.yml`
   - Remove all "Check jq availability" steps from coverage jobs
   - Remove all "Check gh CLI availability" steps from release and label jobs
   - Verify workflows return to previous state
   - Confirm workflows still function (tools should be available on runners)

2. **Partial Rollback**
   - If jq check causes issues in one workflow, remove only that check step
   - If gh CLI check causes issues in one workflow, remove only that check step
   - Verify the remaining checks still work correctly
   - Investigate why the check failed (should not fail if tools are available)

3. **Alternative Approaches**
   - If `command -v` doesn't work on specific runners, use `which` as fallback:
     ```bash
     if ! command -v jq &> /dev/null && ! which jq &> /dev/null; then
       echo "::error::jq is not installed. Required for coverage threshold checking."
       exit 1
     fi
     ```
   - If version commands fail, simplify success message:
     ```bash
     echo "✅ jq is available"
     ```
   - Consider using GitHub Actions setup actions if available (e.g., `actions/setup-jq` if it exists)

### Phase 3: Testing Steps

#### Step 3: Local verification

1. **Test jq check script locally**
   - [ ] Run the jq check script locally:
     ```bash
     if ! command -v jq &> /dev/null; then
       echo "::error::jq is not installed. Required for coverage threshold checking."
       exit 1
     fi
     echo "✅ jq is available: $(jq --version)"
     ```
   - [ ] Verify script exits successfully when jq is available
   - [ ] Verify script outputs version information
   - [ ] (Optional) Temporarily rename jq to test error path: `mv $(which jq) $(which jq).bak`
   - [ ] (Optional) Run script again to verify error annotation appears
   - [ ] (Optional) Restore jq: `mv $(which jq).bak $(which jq)`

2. **Test gh CLI check script locally**
   - [ ] Run the gh CLI check script locally:
     ```bash
     if ! command -v gh &> /dev/null; then
       echo "::error::GitHub CLI (gh) is not installed. Required for creating releases."
       exit 1
     fi
     echo "✅ GitHub CLI is available: $(gh --version | head -n 1)"
     ```
   - [ ] Verify script exits successfully when gh is available
   - [ ] Verify script outputs version information
   - [ ] (Optional) Temporarily rename gh to test error path: `mv $(which gh) $(which gh).bak`
   - [ ] (Optional) Run script again to verify error annotation appears
   - [ ] (Optional) Restore gh: `mv $(which gh).bak $(which gh)`

3. **Validate YAML syntax**
   - [ ] Use a YAML linter or validator to check all workflow file syntax
   - [ ] Verify indentation is correct for all new steps
   - [ ] Verify no syntax errors are introduced in any workflow file
   - [ ] Check that step names are unique within each job

#### Step 4: CI verification

1. **Test pull_request workflow**
   - [ ] Create a test branch with the changes
   - [ ] Create a test PR to trigger pull_request workflow
   - [ ] Verify `coverage` job passes with jq check
   - [ ] Verify jq check step shows success message with version
   - [ ] Verify workflow completes successfully

2. **Test pr-label workflow**
   - [ ] Use the same test PR (or create a new one) to trigger pr-label workflow
   - [ ] Verify `label` job passes with gh CLI check
   - [ ] Verify gh CLI check step shows success message with version
   - [ ] Verify PR labels are applied correctly
   - [ ] Verify workflow completes successfully

3. **Test release-build workflow**
   - [ ] Create a test tag (e.g., `v0.0.0-test`) to trigger release workflow
   - [ ] Push the tag to trigger the workflow
   - [ ] Verify `coverage` job passes with jq check
   - [ ] Verify jq check step shows success message with version
   - [ ] Verify `release` job passes with gh CLI check
   - [ ] Verify gh CLI check step shows success message with version
   - [ ] Verify workflow completes successfully
   - [ ] Delete test tag after verification

4. **Verify error annotations (if possible)**
   - [ ] (Optional) Temporarily modify check to force failure for testing
   - [ ] Verify error annotation appears in GitHub Actions UI
   - [ ] Verify error annotation is visible in workflow run summary
   - [ ] Verify error annotation appears inline with the step
   - [ ] Restore correct check after testing

### Implementation Order

1. [x] Add jq availability check to `.github/workflows/release-build.yaml` (coverage job, before line 77)
2. [x] Add jq availability check to `.github/workflows/pull_request.yaml` (coverage job, before line 103)
3. [x] Add gh CLI availability check to `.github/workflows/release-build.yaml` (release job, before line 221)
4. [x] Add gh CLI availability check to `.github/workflows/pr-label.yml` (label job, before line 18)
5. [x] Validate YAML syntax of all workflow files
6. [ ] Test jq check script locally
7. [ ] Test gh CLI check script locally
8. [ ] Create test branch with changes
9. [ ] Create test PR to trigger pull_request workflow and pr-label workflow
10. [ ] Verify pull_request coverage job passes with jq check
11. [ ] Verify pr-label job passes with gh CLI check
12. [ ] Create test tag to trigger release workflow
13. [ ] Verify release-build coverage job passes with jq check
14. [ ] Verify release-build release job passes with gh CLI check
15. [ ] Verify all workflows complete successfully
16. [ ] Verify error annotations appear correctly (if testing error path)
17. [ ] Clean up test PR and test tag
18. [ ] Merge changes to main branch
19. [ ] Verify production workflow runs with real PR and tag

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:** Workflow would fail early with clear error message if tools are missing (which is the intended behavior). If tools are available (expected case), workflow continues normally.
- **Mitigation:**
  - Simple addition of two check steps
  - Easy rollback if needed (just remove the check steps)
  - Tools (`jq` and `gh`) are typically pre-installed on GitHub Actions runners
  - Checks use standard POSIX `command -v` which is widely supported
  - Can test locally before affecting CI
  - Can test with a test tag before affecting production releases
- **Testing:** Can be fully tested via test tag before affecting production releases
- **Dependencies:**
  - `jq` should be available on Ubuntu runners (typically pre-installed)
  - `gh` CLI should be available on GitHub Actions runners (typically pre-installed)
  - No additional installation steps required
  - Checks are non-blocking if tools are available (expected case)
- **Performance Considerations:**
  - Minimal performance impact: Four additional `command -v` checks across all workflows
  - Checks execute quickly (< 1 second each)
  - No network calls or heavy operations
  - Early failure detection saves time if tools are missing
- **Benefits:**
  - Early failure detection with clear error messages
  - Better visibility in GitHub Actions UI via annotations
  - Easier debugging when issues occur
  - Explicit documentation of tool dependencies
  - Improved developer experience

## Implementation Summary

### Completed Changes

All tool availability checks have been successfully implemented:

1. **`.github/workflows/release-build.yaml`**
   - ✅ Added `jq` availability check in `coverage` job (after "Generate coverage" step, before "Check coverage thresholds")
   - ✅ Added `gh` CLI availability check in `release` job (after "Download all artifacts" step, before "Create GitHub Release")

2. **`.github/workflows/pull_request.yaml`**
   - ✅ Added `jq` availability check in `coverage` job (after "Generate coverage" step, before "Check coverage thresholds")

3. **`.github/workflows/pr-label.yml`**
   - ✅ Added `gh` CLI availability check in `label` job (after "Checkout code" step, before "Analyze commits and apply labels")

### Implementation Details

- All checks use `command -v` for POSIX-compliant tool detection
- Error messages use GitHub Actions workflow annotation commands (`::error::`) for high visibility
- Success messages display tool versions for verification
- YAML syntax validated with no errors
- All steps properly indented and placed in correct workflow order

### Next Steps (Testing)

The implementation is complete and ready for testing. The following steps are recommended before merging:

1. Test jq and gh CLI check scripts locally
2. Create a test PR to verify pull_request and pr-label workflows
3. Create a test tag to verify release-build workflow
4. Verify error annotations appear correctly in GitHub Actions UI
5. Merge to main branch after successful testing
