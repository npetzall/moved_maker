# BUG: Coverage threshold check output doesn't show detailed information

## Description

The coverage threshold check in the CI workflow outputs only "Coverage thresholds met. ✅" multiple times, without showing what metrics are being checked, their actual values, or the thresholds. The output should be more informative, displaying each metric (lines, branches, functions), the actual coverage percentage, and the threshold for each.

## Current State

**Current output:**
```
Coverage thresholds met. ✅

Coverage thresholds met. ✅

Coverage thresholds met. ✅

Coverage thresholds met. ✅
```

**Current script (`.config/coverage-threshold-check.jq`):**
The script does generate individual check messages (lines 22-24), but the output format may not be displaying them properly, or they're being suppressed. The script outputs:
- Individual check results via `check()` function calls
- Final summary message "Coverage thresholds met. ✅"

**Workflow step (`.github/workflows/pull_request.yaml` lines 92-98):**
```yaml
- name: Check coverage thresholds
  run: |
    # Generate coverage in JSON format
    cargo llvm-cov nextest --all-features --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

## Expected State

The output should clearly show:
1. **What is being checked**: Line coverage, Branch coverage, Function coverage
2. **Actual values**: The current coverage percentage for each metric
3. **Thresholds**: The required threshold for each metric
4. **Status**: Whether each metric meets the threshold
5. **Final summary**: Overall pass/fail status

**Expected output format:**
```
✅ Line coverage: 95.39% (threshold: 80%)
⚠️  Branch coverage: N/A (no branches to cover)
✅ Function coverage: 94.74% (threshold: 85%)
Coverage thresholds met. ✅
```

Or if a threshold is not met:
```
✅ Line coverage: 95.39% (threshold: 80%)
⚠️  Branch coverage: N/A (no branches to cover)
❌ Function coverage: 75.00% is below threshold of 85%
Coverage thresholds not met. Failing CI.
```

## Impact

### Usability Impact
- **Severity**: Medium
- **Priority**: Medium

Current issues:
- **Lack of visibility**: Cannot see what metrics are being checked
- **No actual values**: Cannot see current coverage percentages
- **No threshold visibility**: Cannot see what thresholds are being enforced
- **Poor debugging**: Difficult to understand why checks pass or fail
- **Redundant output**: Same message repeated multiple times

### Benefits of Improved Output
- **Transparency**: Clear visibility into what's being checked
- **Debugging**: Easy to identify which metrics need improvement
- **Documentation**: Output serves as inline documentation of thresholds
- **CI logs**: More informative CI logs for reviewers


## Related Implementation Plan

See `work/25W46/BUG_WORKFLOWS_COVERAGE_OUTPUT_FORMAT.md` for the detailed implementation plan.
