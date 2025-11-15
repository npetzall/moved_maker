# Bug: Coverage threshold check output doesn't show detailed information

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

## Steps to Fix

### Step 1: Restructure script output format

The issue is with how jq processes comma-separated expressions when combined with pipe operators. The fix restructures the script to collect check outputs into an array first, then output them separately from the final summary.

**File:** `.config/coverage-threshold-check.jq`

**Change:** Restructure the output section to use array collection:

**Before:**
```jq
check($line; $line_count; 80; "Line"),
check($branch; $branch_count; 70; "Branch"),
check($func; $func_count; 85; "Function"),

(threshold_check) | if . then "Coverage thresholds met. ✅" else ... end
```

**After:**
```jq
(
  [check($line; $line_count; 80; "Line"),
   check($branch; $branch_count; 70; "Branch"),
   check($func; $func_count; 85; "Function")] | .[],
  "",
  (threshold_check | if . then "✅ All coverage thresholds met." else ... end)
)
```

This ensures:
- All individual check messages are displayed with detailed metrics
- Final summary appears only once (not repeated 4 times)
- Variables remain in scope for threshold validation
- Output format is clear and informative

### Step 2: Test the fix

Verify the output shows:
- ✅ Line coverage: X.XX% (threshold: 80%)
- ⚠️  Branch coverage: N/A (no branch to cover) OR ✅ Branch coverage: X.XX% (threshold: 70%)
- ✅ Function coverage: X.XX% (threshold: 85%)
- Empty line separator
- ✅ All coverage thresholds met. (single summary, not repeated)

## Affected Files

- `.config/coverage-threshold-check.jq` (lines 22-38 - restructured output format)

## Example Fix

### Before (problematic structure):
```jq
check($line; $line_count; 80; "Line"),
check($branch; $branch_count; 70; "Branch"),
check($func; $func_count; 85; "Function"),

# Only check thresholds for metrics that have items to cover
(if $line_count > 0 and $line < 80 then false else true end) and
(if $branch_count > 0 and $branch < 70 then false else true end) and
(if $func_count > 0 and $func < 85 then false else true end) |
if . then
  "Coverage thresholds met. ✅"
else
  "Coverage thresholds not met. Failing CI.",
  false
end
```

**Problem:** When jq processes comma-separated expressions followed by a piped expression, it evaluates the piped expression once for each comma-separated value. This causes the summary to be printed 4 times (once for each check output + 1), while the individual check messages are not displayed.

### After (fixed structure):
```jq
# Collect and output individual check results, then output final summary
(
  [check($line; $line_count; 80; "Line"),
   check($branch; $branch_count; 70; "Branch"),
   check($func; $func_count; 85; "Function")] | .[],
  "",
  # Check thresholds and output final summary
  ((if $line_count > 0 and $line < 80 then false else true end) and
   (if $branch_count > 0 and $branch < 70 then false else true end) and
   (if $func_count > 0 and $func < 85 then false else true end) |
   if . then
     "✅ All coverage thresholds met."
   else
     "❌ Coverage thresholds not met. Failing CI.",
     false
   end)
)
```

**Solution:** By collecting the check() outputs into an array first, then using `.[]` to output each element, we ensure:
- All individual check messages are displayed with detailed metrics
- Final summary appears only once (not repeated)
- Variables remain in scope for threshold validation
- Output format is clear and informative

**Output example (passing thresholds):**
```
✅ Line coverage: 95.38714991762768% (threshold: 80%)
⚠️  Branch coverage: N/A (no branch to cover)
✅ Function coverage: 94.73684210526316% (threshold: 85%)

✅ All coverage thresholds met.
```

**Output example (failing thresholds):**
```
❌ Line coverage 75.00% is below threshold of 80%
⚠️  Branch coverage: N/A (no branch to cover)
✅ Function coverage: 94.73684210526316% (threshold: 85%)

❌ Coverage thresholds not met. Failing CI.
```

## Status

✅ **FIXED** - Investigation complete, root cause identified and fixed

### Investigation Phase Complete
- ✅ Root cause identified: jq comma-separated expression evaluation issue
- ✅ Script restructured to properly display all check outputs
- ✅ Tested with both passing and failing threshold scenarios
- ✅ Output format now matches expected format with detailed metrics

### Changes Made
- Updated `.config/coverage-threshold-check.jq` to use array-based output structure
- Script now displays individual check results before final summary
- Final summary appears only once (not repeated 4 times)

## References

- [jq documentation](https://stedolan.github.io/jq/manual/)
- [cargo-llvm-cov JSON output format](https://github.com/taiki-e/cargo-llvm-cov#json-output)
- [WORKFLOWS_COVERAGE_THRESHOLD_CHECK.md](done/WORKFLOWS_COVERAGE_THRESHOLD_CHECK.md) - Previous coverage threshold implementation

## Notes

- The current script already has the `check()` function that should output detailed information
- The issue might be with how `jq -e` handles multiple outputs
- The `-r` flag outputs raw strings (no JSON quotes)
- The `-e` flag exits with non-zero status if the last output is false
- Multiple outputs from jq are printed on separate lines
- The script outputs 4 values (3 checks + 1 summary), which might explain the 4 "Coverage thresholds met. ✅" messages
- Need to verify if individual check outputs are being suppressed or if they're just not visible in CI logs

## Detailed Implementation Plan

### Phase 1: Investigation Steps ✅ COMPLETED

#### Step 1: Verify current script output locally ✅

1. **Run the script and capture output** ✅
   - [x] Run `cargo llvm-cov report --json > coverage.json` to generate coverage data
   - [x] Run `jq -r -f .config/coverage-threshold-check.jq coverage.json` to test script
   - [x] Observe that only "Coverage thresholds met. ✅" appears 4 times
   - [x] Confirm individual check messages are not displayed

2. **Test check() function directly** ✅
   - [x] Test individual check() function calls to verify they work correctly
   - [x] Confirm check() function generates proper output when called directly
   - [x] Verify the issue is with script structure, not function logic

3. **Investigate jq behavior** ✅
   - [x] Research how jq processes comma-separated expressions with pipes
   - [x] Understand that piped expressions are evaluated once per comma-separated value
   - [x] Identify root cause: comma-separated check() calls + piped summary causes summary to repeat

**Investigation Results:**
- Script output confirmed: Only summary message appears 4 times
- check() function works correctly when called individually
- Root cause: jq evaluates piped expressions once per comma-separated value
- Solution identified: Use array collection to output checks, then summary separately

#### Step 2: Test solution approach ✅

1. **Test array-based output structure** ✅
   - [x] Test collecting check() outputs into an array
   - [x] Verify using `.[]` to output array elements works correctly
   - [x] Confirm variables remain in scope for threshold check
   - [x] Test that final summary appears only once

2. **Verify output format** ✅
   - [x] Test with passing thresholds - verify detailed metrics shown
   - [x] Test with failing thresholds - verify failure messages shown
   - [x] Confirm empty line spacing between checks and summary
   - [x] Verify all status indicators (✅/⚠️/❌) display correctly

**Solution Verified:**
- Array-based structure correctly displays all check outputs
- Final summary appears only once
- Output format matches expected format with detailed metrics
- Both passing and failing scenarios work correctly

### Phase 2: Implementation Steps ✅ COMPLETED

#### Step 3: Update coverage threshold check script ✅ COMPLETED

**File:** `.config/coverage-threshold-check.jq`

1. **Restructure script output** ✅
   - [x] Collect check() outputs into an array: `[check(...), check(...), check(...)]`
   - [x] Output array elements using `.[]` to display each check result
   - [x] Add empty line separator: `""`
   - [x] Compute and output final summary once after threshold check
   - [x] Ensure variables remain in scope for threshold validation

**Script structure implemented:**
```jq
# Collect and output individual check results, then output final summary
(
  [check($line; $line_count; 80; "Line"),
   check($branch; $branch_count; 70; "Branch"),
   check($func; $func_count; 85; "Function")] | .[],
  "",
  # Check thresholds and output final summary
  ((if $line_count > 0 and $line < 80 then false else true end) and
   (if $branch_count > 0 and $branch < 70 then false else true end) and
   (if $func_count > 0 and $func < 85 then false else true end) |
   if . then
     "✅ All coverage thresholds met."
   else
     "❌ Coverage thresholds not met. Failing CI.",
     false
   end)
)
```

**Benefits of the fix:**
- All individual check messages are displayed with detailed metrics
- Final summary appears only once (not repeated 4 times)
- Variables remain in scope for threshold validation
- Output format is clear and informative
- Maintains backward compatibility with existing workflow

#### Step 4: Test the updated script ✅ COMPLETED

1. **Test locally** ✅
   - [x] Run `jq -r -f .config/coverage-threshold-check.jq coverage.json`
   - [x] Verify output shows detailed metrics for each coverage type
   - [x] Confirm final summary appears only once
   - [x] Test with `-e` flag to verify exit code behavior

2. **Test edge cases** ✅
   - [x] Test with passing thresholds - all metrics above thresholds
   - [x] Test with failing thresholds - one or more metrics below thresholds
   - [x] Verify N/A handling for zero-count metrics (branches)
   - [x] Confirm error handling works correctly (script exits with error on failure)

**Test Results:**
- ✅ Passing thresholds: Shows detailed metrics + single success summary
- ✅ Failing thresholds: Shows detailed metrics with failure indicators + single failure summary
- ✅ Exit codes: Correctly returns 0 for pass, non-zero for fail (with `-e` flag)
- ✅ Output format: Matches expected format exactly

### Phase 3: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.config/coverage-threshold-check.jq`
   - Restore the original script structure (though it had the bug)
   - Verify workflow returns to previous state

2. **Partial Rollback**
   - If array structure causes issues, verify jq version compatibility
   - If output format is incorrect, adjust array output syntax
   - If variables are out of scope, adjust variable binding structure

3. **Alternative Approaches**
   - If array approach doesn't work, use separate output statements
   - If jq version is incompatible, document minimum version requirement
   - Consider using `empty` to suppress unwanted outputs

### Implementation Order

1. [x] Run script locally to reproduce the issue ✅
2. [x] Test check() function directly to verify it works ✅
3. [x] Investigate jq comma-separated expression behavior ✅
4. [x] Identify root cause: piped expression evaluated multiple times ✅
5. [x] Test array-based solution approach locally ✅
6. [x] Update `.config/coverage-threshold-check.jq` with array structure ✅
7. [x] Test updated script with passing thresholds ✅
8. [x] Test updated script with failing thresholds ✅
9. [x] Verify output format matches expected format ✅
10. [x] Verify exit code behavior with `-e` flag ✅
11. [ ] Create pull request and verify CI coverage job output
12. [ ] Verify other CI jobs still pass
13. [ ] Confirm coverage threshold check output is clear and informative in CI

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:** Coverage threshold check output would remain unclear, but functionality would still work
- **Mitigation:**
  - Simple structural change to jq script
  - Easy rollback if needed
  - Can test locally before affecting CI
  - No workflow changes required
- **Testing:** Fully tested locally with both passing and failing scenarios
- **Dependencies:**
  - Uses standard jq features (arrays, pipes, conditionals)
  - No additional dependencies required
  - Compatible with jq versions available in GitHub Actions runners

## Root Cause

The issue is with how jq processes comma-separated expressions when combined with pipe operators. In the original script structure:

```jq
check($line; $line_count; 80; "Line"),
check($branch; $branch_count; 70; "Branch"),
check($func; $func_count; 85; "Function"),

(threshold_check) | if . then "Coverage thresholds met. ✅" else ... end
```

When jq processes comma-separated expressions followed by a piped expression, it evaluates the piped expression once for each comma-separated value. This behavior caused:
- The three `check()` function outputs to be generated but not displayed properly
- The final summary expression to be evaluated 4 times (once for each of the 3 check outputs + 1 empty/boolean value)
- Only the summary messages to be visible, repeated 4 times, while individual check messages were suppressed

**Script evidence:**
- The `check()` function works correctly when called individually (verified through direct testing)
- The script structure with comma-separated expressions + piped summary causes the issue
- Local testing confirmed: only "Coverage thresholds met. ✅" appeared 4 times, with no individual check messages visible

**Solution:**
The fix restructures the script to collect `check()` outputs into an array first, then output them separately from the final summary. This ensures all individual check messages are displayed and the final summary appears only once. See the "Example Fix" section for the complete solution.
