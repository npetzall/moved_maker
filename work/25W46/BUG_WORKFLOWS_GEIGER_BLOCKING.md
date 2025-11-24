# Implementation Plan: BUG_WORKFLOWS_GEIGER_BLOCKING

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_WORKFLOWS_GEIGER_BLOCKING.md`.

## Context

Related bug report: `plan/25W46/BUG_WORKFLOWS_GEIGER_BLOCKING.md`

## Steps to Fix

### Step 1: Make geiger non-blocking

Change the step to treat exit code 1 as OK and upload the report:

**Before:**
```yaml
- name: Run cargo-geiger scan (blocking)
  run: cargo geiger --output-format json > geiger-report.json
```

**After:**
```yaml
- name: Run cargo-geiger scan
  run: cargo geiger --output-format json > geiger-report.json || [ $? -eq 1 ]

- name: Upload geiger report
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: geiger-report
    path: geiger-report.json
    if-no-files-found: warn
```

### Step 2: Update both workflow files

Apply the fix to:
- `.github/workflows/pull_request.yaml` (security job, around line 30)
- `.github/workflows/release-build.yaml` (security job, around line 34)

## Affected Files

- `.github/workflows/pull_request.yaml`
  - `security` job (lines 30-31)

- `.github/workflows/release-build.yaml`
  - `security` job (lines 34-35)

## Example Fix

### Before:
```yaml
- name: Run cargo-geiger scan (blocking)
  run: cargo geiger --output-format json > geiger-report.json
```

### After:
```yaml
- name: Run cargo-geiger scan
  run: cargo geiger --output-format json > geiger-report.json || [ $? -eq 1 ]

- name: Upload geiger report
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: geiger-report
    path: geiger-report.json
    if-no-files-found: warn
```

## Status

✅ **COMPLETED** - Geiger is now configured as informational (treats exit code 1 as OK) and uploads reports as artifacts. The workflow will fail on actual tool errors (exit codes 2+) but continue when unsafe code is found (exit code 1).

## References

- [cargo-geiger Documentation](https://github.com/rust-secure-code/cargo-geiger)
- [GitHub Actions upload-artifact](https://github.com/actions/upload-artifact)

## Notes

- `cargo-geiger` is an informational tool that reports unsafe code usage
- Unsafe code isn't necessarily bad - it's good to be aware of it
- The tool doesn't have pass/fail semantics like `cargo-deny` or `cargo-audit`
- The report should be available for review but shouldn't block the workflow
- Exit code 0: Success, no unsafe code found - step succeeds
- Exit code 1: Unsafe code found (informational) - `|| [ $? -eq 1 ]` treats this as OK, step succeeds
- Exit codes 2+: Actual tool errors (installation failures, missing dependencies, etc.) - step fails as it should
- Using `|| [ $? -eq 1 ]` treats only exit code 1 as OK, allowing other error codes to fail the step and workflow
- The artifact upload uses `if: always()` to upload even if the step fails (e.g., if a partial report was generated)

## Detailed Implementation Plan

### Phase 1: Implementation Steps ✅ COMPLETED

#### Step 1: Update `.github/workflows/pull_request.yaml` ✅ COMPLETED

**File:** `.github/workflows/pull_request.yaml`

1. **Update `security` job geiger step (lines 30-31)** ✅ COMPLETED
   - [x] Locate the "Run cargo-geiger scan (blocking)" step at lines 30-31 in the `security` job
   - [x] Replace:
     ```yaml
     - name: Run cargo-geiger scan (blocking)
       run: cargo geiger --output-format json > geiger-report.json
     ```
   - [x] With:
     ```yaml
     - name: Run cargo-geiger scan
       run: cargo geiger --output-format json > geiger-report.json || [ $? -eq 1 ]

     - name: Upload geiger report
       uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
       if: always()
       with:
         name: geiger-report
         path: geiger-report.json
         if-no-files-found: warn
     ```
   - [x] Verify step placement (should be after cargo-audit, before job ends)
   - [x] Verify the `|| [ $? -eq 1 ]` pattern correctly treats exit code 1 as OK

#### Step 2: Update `.github/workflows/release-build.yaml` ✅ COMPLETED

**File:** `.github/workflows/release-build.yaml`

1. **Update `security` job geiger step (lines 34-35)** ✅ COMPLETED
   - [x] Locate the "Run cargo-geiger scan (blocking)" step at lines 34-35 in the `security` job
   - [x] Replace:
     ```yaml
     - name: Run cargo-geiger scan (blocking)
       run: cargo geiger --output-format json > geiger-report.json
     ```
   - [x] With:
     ```yaml
     - name: Run cargo-geiger scan
       run: cargo geiger --output-format json > geiger-report.json || [ $? -eq 1 ]

     - name: Upload geiger report
       uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
       if: always()
       with:
         name: geiger-report
         path: geiger-report.json
         if-no-files-found: warn
     ```
   - [x] Verify step placement (should be after cargo-audit, before job ends)
   - [x] Verify the `|| [ $? -eq 1 ]` pattern correctly treats exit code 1 as OK

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.github/workflows/pull_request.yaml`
   - Revert changes to `.github/workflows/release-build.yaml`
   - Restore the original "(blocking)" step name and command
   - Verify workflows return to previous state

2. **Partial Rollback**
   - If exit code handling doesn't work as expected, verify cargo-geiger exit codes
   - Check if the `|| [ $? -eq 1 ]` pattern works correctly in the CI environment
   - Verify artifact upload works even when geiger fails
   - Test with `if-no-files-found: warn` to ensure it doesn't fail the workflow

3. **Alternative Approaches**
   - If `|| [ $? -eq 1 ]` doesn't work, consider using a shell script wrapper
   - Verify cargo-geiger documentation for exit code behavior
   - Consider using `continue-on-error: true` only if exit code detection is unreliable
   - Test artifact upload behavior with different failure scenarios

### Implementation Order

1. Start with `.github/workflows/pull_request.yaml` (PR workflow, easier to test)
2. Test via pull request to verify:
   - Workflow continues when geiger exits with 0 or 1 (success or unsafe code found)
   - Workflow fails when geiger exits with 2+ (actual tool errors)
   - Artifact is uploaded when geiger succeeds (exit 0 or 1)
   - Artifact upload attempts even if geiger fails (exit 2+), with graceful handling if file is missing
   - Downstream jobs (test, coverage) are not blocked by informational exit code 1
3. Verify artifact availability:
   - Check that `geiger-report.json` is available in workflow artifacts
   - Verify the artifact can be downloaded and contains valid JSON
4. Apply the same fix to `.github/workflows/release-build.yaml`
5. Test via release workflow to verify:
   - Same behavior as PR workflow
   - `build-and-release` job is not blocked by informational exit code 1
