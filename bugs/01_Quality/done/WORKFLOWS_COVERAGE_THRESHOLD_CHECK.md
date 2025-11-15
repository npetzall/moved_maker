# Bug: Workflow - Code coverage threshold check doesn't work

## Description

The PR workflow `coverage` job fails to extract coverage percentages from the `cargo llvm-cov` summary output. The grep patterns in the workflow expect a format like "Lines: 94.67%", but `cargo llvm-cov --summary-only` outputs a table format instead. This causes the threshold check to read 0% for all metrics, even though the actual coverage is above thresholds (94.67% line coverage, 95.39% lines coverage, 94.74% function coverage).

## Progress Summary

**Status:** ✅ Solution Ready for Implementation

**Completed:**
- ✅ JSON output structure verified (`.data[0].totals.{lines,branches,functions}.percent` and `.count`)
- ✅ Working jq script created and tested locally
- ✅ Edge case handling verified (count = 0 skips threshold check)
- ✅ Script file approach selected (`.config/coverage-threshold-check.jq`)
- ✅ Script tested with actual coverage data (95.39% line, 0% branch, 94.74% function)

**Implementation Completed:**
- ✅ Created `.config/coverage-threshold-check.jq` script file
- ✅ Updated `.github/workflows/pull_request.yaml` to use script file
- ✅ Removed `bc` installation step
- ✅ Script tested locally and working correctly
- ⏳ Pending CI testing

## Current State

❌ **BROKEN** - The coverage threshold check always fails because it cannot parse the coverage percentages from the summary output.

✅ **IMPLEMENTED** - Solution implemented and tested locally. Working jq script created in `.config/coverage-threshold-check.jq`. Workflow updated to use JSON output format with script file. `bc` dependency removed. Ready for CI testing.

**Previous (broken) workflow configuration:**
```yaml
- name: Check coverage thresholds
  run: |
    # Generate coverage and extract percentages
    cargo llvm-cov nextest --all-features --summary-only > coverage-summary.txt
    cat coverage-summary.txt

    # Extract coverage percentages from summary
    LINE_COV=$(grep -oP '^\s*Lines:\s+\K[\d.]+' coverage-summary.txt || echo "0")
    BRANCH_COV=$(grep -oP '^\s*Branches:\s+\K[\d.]+' coverage-summary.txt || echo "0")
    FUNC_COV=$(grep -oP '^\s*Functions:\s+\K[\d.]+' coverage-summary.txt || echo "0")
```

**Current (fixed) workflow configuration:**
```yaml
- name: Check coverage thresholds
  run: |
    # Generate coverage in JSON format
    cargo llvm-cov nextest --all-features --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

**Error output:**
```
Filename                      Regions    Missed Regions     Cover   Functions  Missed Functions  Executed       Lines      Missed Lines     Cover    Branches   Missed Branches     Cover
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
cli.rs                            187                 4    97.86%           9                 0   100.00%         114                 1    99.12%           0                 0         -
file_discovery.rs                 170                 9    94.71%           8                 0   100.00%          78                 3    96.15%           0                 0         -
main.rs                            65                14    78.46%           2                 0   100.00%          50                15    70.00%           0                 0         -
output.rs                         190                12    93.68%           7                 0   100.00%          75                 3    96.00%           0                 0         -
parser.rs                         167                 4    97.60%           9                 1    88.89%          69                 1    98.55%           0                 0         -
processor.rs                      440                22    95.00%          22                 2    90.91%         221                 5    97.74%           0                 0         -
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
TOTAL                            1219                65    94.67%          57                 3    94.74%         607                28    95.39%           0                 0         -

❌ Line coverage 0% is below threshold of 80%
❌ Branch coverage 0% is below threshold of 70%
❌ Function coverage 0% is below threshold of 85%
Coverage thresholds not met. Failing CI.
```

**Root cause:**
The grep patterns expect lines like:
```
Lines: 94.67
Branches: 0.00
Functions: 94.74
```

But `cargo llvm-cov --summary-only` outputs a table format where the TOTAL row contains:
```
TOTAL  1219  65  94.67%  57  3  94.74%  607  28  95.39%  0  0  -
```

The columns in the TOTAL row are:
- Regions: 1219
- Missed Regions: 65
- Cover: 94.67%
- Functions: 57
- Missed Functions: 3
- Executed: 94.74%
- Lines: 607
- Missed Lines: 28
- Cover: 95.39%
- Branches: 0
- Missed Branches: 0
- Cover: - (N/A)

## Expected State

The coverage job should:
1. Successfully run all tests
2. Generate coverage reports
3. Extract coverage percentages from the summary output correctly
4. Check coverage thresholds against the extracted percentages
5. Pass if thresholds are met (Line > 80%, Branch > 70%, Function > 85%)

## Impact

### CI/CD Impact
- **Severity**: High
- **Priority**: High

The coverage job always fails, preventing:
- Coverage threshold validation
- PRs from being merged (if coverage is a required check)
- Accurate coverage reporting in CI

### Functionality Impact
- **Severity**: High
- **Priority**: High

Code coverage thresholds cannot be enforced, which is a critical quality metric for the project. The actual coverage is good (94.67% line, 95.39% lines, 94.74% function), but CI incorrectly reports it as 0%.

## Root Cause

The grep patterns in the workflow (lines 105-107 of `.github/workflows/pull_request.yaml`) are designed to match a simple text format like:
```
Lines: 94.67
Branches: 0.00
Functions: 94.74
```

However, `cargo llvm-cov --summary-only` outputs a table format with a TOTAL row that contains all metrics in a single line with space-separated columns. The grep patterns don't match this format, so they default to "0" (via the `|| echo "0"` fallback), causing the threshold check to fail.

**Workflow evidence:**
The error shows the coverage summary is generated correctly with good coverage numbers, but the extraction fails because the grep patterns don't match the table format.

## Steps to Fix

### Option 1: Parse the TOTAL row from table format (RECOMMENDED)
Extract percentages from the TOTAL row by parsing the table columns:

```yaml
- name: Check coverage thresholds
  run: |
    # Generate coverage and extract percentages
    cargo llvm-cov nextest --all-features --summary-only > coverage-summary.txt
    cat coverage-summary.txt

    # Extract coverage percentages from TOTAL row
    # Format: TOTAL  regions  missed  cover%  functions  missed  executed%  lines  missed  cover%  branches  missed  cover%
    TOTAL_LINE=$(grep "^TOTAL" coverage-summary.txt | awk '{print $9}' | sed 's/%//')
    TOTAL_BRANCH=$(grep "^TOTAL" coverage-summary.txt | awk '{print $12}' | sed 's/%//')
    TOTAL_FUNC=$(grep "^TOTAL" coverage-summary.txt | awk '{print $6}' | sed 's/%//')

    # Handle N/A for branch coverage (shown as "-")
    if [ "$TOTAL_BRANCH" = "-" ]; then
      TOTAL_BRANCH="0"
    fi

    LINE_COV=${TOTAL_LINE:-0}
    BRANCH_COV=${TOTAL_BRANCH:-0}
    FUNC_COV=${TOTAL_FUNC:-0}

    # Check thresholds (Line > 80%, Branch > 70%, Function > 85%)
    FAILED=0
    if (( $(echo "$LINE_COV < 80" | bc -l) )); then
      echo "❌ Line coverage $LINE_COV% is below threshold of 80%"
      FAILED=1
    else
      echo "✅ Line coverage: $LINE_COV% (threshold: 80%)"
    fi

    if (( $(echo "$BRANCH_COV < 70" | bc -l) )); then
      echo "❌ Branch coverage $BRANCH_COV% is below threshold of 70%"
      FAILED=1
    else
      echo "✅ Branch coverage: $BRANCH_COV% (threshold: 70%)"
    fi

    if (( $(echo "$FUNC_COV < 85" | bc -l) )); then
      echo "❌ Function coverage $FUNC_COV% is below threshold of 85%"
      FAILED=1
    else
      echo "✅ Function coverage: $FUNC_COV% (threshold: 85%)"
    fi

    if [ $FAILED -eq 1 ]; then
      echo "Coverage thresholds not met. Failing CI."
      exit 1
    fi
```

**Note:** Column positions may vary. Verify the exact column positions by examining the actual output format.

### Option 2: Use JSON output format with jq for extraction and threshold checking (RECOMMENDED)
Use `cargo llvm-cov --json` to get structured output and perform both extraction and threshold checking entirely within `jq`. The jq script is stored in a separate file for better maintainability and easier local testing.

**Step 1: Create `.config/coverage-threshold-check.jq`**
```jq
# Coverage threshold check script
# Thresholds: Line > 80%, Branch > 70%, Function > 85%
# Note: Skip threshold check if count is 0 (no branches/lines/functions to cover)

.data[0].totals as $s |
($s.lines.percent // 0) as $line |
($s.lines.count // 0) as $line_count |
($s.branches.percent // 0) as $branch |
($s.branches.count // 0) as $branch_count |
($s.functions.percent // 0) as $func |
($s.functions.count // 0) as $func_count |

def check(actual; count; threshold; name):
  if count == 0 then
    "⚠️  \(name) coverage: N/A (no \(name | ascii_downcase) to cover)"
  elif actual >= threshold then
    "✅ \(name) coverage: \(actual)% (threshold: \(threshold)%)"
  else
    "❌ \(name) coverage \(actual)% is below threshold of \(threshold)%"
  end;

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

**Step 2: Update workflow to use the script file**
```yaml
- name: Check coverage thresholds
  run: |
    # Generate coverage in JSON format
    cargo llvm-cov nextest --all-features --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

**Benefits:**
- More reliable parsing (structured data)
- Less prone to format changes
- Easier to debug
- No additional dependencies (`jq` is pre-installed in GitHub Actions runners)
- No need for `bc` or bash floating-point arithmetic
- All logic in one place (extraction + threshold checking)
- Cleaner and more maintainable code
- **File-based approach:** Script stored in `.config/coverage-threshold-check.jq` for:
  - Easier local testing: `jq -r -e -f .config/coverage-threshold-check.jq coverage.json`
  - Better version control and code review
  - Reusability in other scripts or documentation

**Note:** `jq` is pre-installed in GitHub Actions runners, so no installation is needed. The `-e` flag causes `jq` to exit with a non-zero status if the last output value is `false`, which triggers the `|| exit 1` to fail the CI step.

**Edge case handling:** When a metric has a count of 0 (e.g., no branches in the codebase), the threshold check is skipped for that metric. This prevents false failures when there are no items to cover. The script displays "⚠️ N/A" for such metrics.

### Option 3: Use cargo-llvm-cov's built-in threshold checking
If `cargo-llvm-cov` supports threshold checking natively, use that instead of manual parsing:

```yaml
- name: Check coverage thresholds
  run: |
    cargo llvm-cov nextest --all-features --lcov --output-path lcov.info \
      --fail-under-line 80 \
      --fail-under-branch 70 \
      --fail-under-function 85
```

**Note:** Verify if `cargo-llvm-cov` supports these flags. If not, this option is not viable.

**Recommended approach:** Option 2 (JSON parsing with jq), as it provides the most reliable and maintainable solution. It eliminates the need for `bc`, handles all logic in one place, and is less prone to format changes. Option 1 is a viable alternative if JSON output is not available, but requires verifying exact column positions.

## Affected Files

- `.github/workflows/pull_request.yaml`
  - `coverage` job (lines 70-135)
  - `Check coverage thresholds` step (lines 98-135)
  - Grep patterns for extracting coverage percentages (lines 105-107)

## Investigation Needed ✅ COMPLETED

1. ✅ Verify the JSON output structure from `cargo llvm-cov --json` - **DONE**: Structure verified as `.data[0].totals.{lines,branches,functions}.{percent,count}`
2. ✅ Test the jq parsing script with the actual JSON output format - **DONE**: Script tested and working
3. ✅ Verify the JSON paths for coverage percentages - **DONE**: Paths confirmed (`.data[0].totals.lines.percent`, `.data[0].totals.branches.percent`, `.data[0].totals.functions.percent`)
4. ✅ Test threshold checking logic with jq - **DONE**: Logic verified with actual coverage data
5. ⏳ Check if `cargo-llvm-cov` has built-in threshold checking flags (Option 3) - **DEFERRED**: Using Option 2 (jq script) as recommended solution
6. ✅ Test the fix locally - **DONE**: Script tested locally with `cargo llvm-cov nextest --all-features --json`

## Test Failures Summary

The coverage job always fails with:
- Line coverage reported as 0% (actual: 94.67%)
- Branch coverage reported as 0% (actual: 0% or N/A)
- Function coverage reported as 0% (actual: 94.74%)

All failures are due to the same root cause: grep patterns don't match the table format output.

## Status

✅ **IMPLEMENTATION COMPLETE - READY FOR CI TESTING**

**Progress Summary:**
- ✅ Phase 1 (Investigation) - COMPLETED
  - JSON structure verified (`.data[0].totals.{lines,branches,functions}.percent`)
  - Working jq script created and tested locally
  - Edge case handling verified (count = 0)
  - Script file approach selected (`.config/coverage-threshold-check.jq`)
- ✅ Phase 2 (Implementation) - COMPLETED
  - ✅ Created `.config/coverage-threshold-check.jq` script file
  - ✅ Updated `.github/workflows/pull_request.yaml` to use script file
  - ✅ Removed `bc` installation step (lines 95-96)
  - ✅ Script tested locally and working correctly

**Implementation Details:**
- Script file: `.config/coverage-threshold-check.jq` ✅
- Workflow updated: `.github/workflows/pull_request.yaml` (lines 95-101) ✅
- Local testing: Script verified working with actual coverage data ✅

## Detailed Implementation Plan

### Phase 1: Investigation Steps ✅ COMPLETED

#### Step 1: Understand the JSON output format ✅

1. **Examine the JSON output structure** ✅
   - [x] Run `cargo llvm-cov nextest --all-features --json` locally
   - [x] Inspect the JSON structure to verify paths:
     - `.data[0].totals.lines.percent` for line coverage
     - `.data[0].totals.branches.percent` for branch coverage
     - `.data[0].totals.functions.percent` for function coverage
   - [x] Document the exact JSON structure and any edge cases
   - [x] Verify how missing/null values are represented
   - [x] Handle edge case where count is 0 (no branches/lines/functions to cover) - skip threshold check

2. **Test jq parsing script** ✅
   - [x] Create a test script with the jq expression
   - [x] Test extraction of coverage percentages
   - [x] Test threshold comparison logic
   - [x] Verify handling of edge cases (null values, missing fields, count = 0)
   - [x] Test that the script correctly exits with error when thresholds aren't met

**Verified JSON Structure:**
- Path: `.data[0].totals.{lines,branches,functions}.percent` for percentages
- Path: `.data[0].totals.{lines,branches,functions}.count` for counts
- Edge case: When count is 0, percentage may be 0% or 100% - threshold check is skipped

**Working jq Script:**
```jq
.data[0].totals as $s |
($s.lines.percent // 0) as $line |
($s.lines.count // 0) as $line_count |
($s.branches.percent // 0) as $branch |
($s.branches.count // 0) as $branch_count |
($s.functions.percent // 0) as $func |
($s.functions.count // 0) as $func_count |

def check(actual; count; threshold; name):
  if count == 0 then
    "⚠️  \(name) coverage: N/A (no \(name | ascii_downcase) to cover)"
  elif actual >= threshold then
    "✅ \(name) coverage: \(actual)% (threshold: \(threshold)%)"
  else
    "❌ \(name) coverage \(actual)% is below threshold of \(threshold)%"
  end;

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

#### Step 2: Verify jq availability and functionality ✅

1. **Confirm jq is available** ✅
   - [x] Verify `jq` is pre-installed in GitHub Actions runners (confirmed)
   - [x] Test the jq script syntax locally (verified working)
   - [x] Verify the `-e` flag behavior (exit on false) (tested and working)

### Phase 2: Implementation Steps ✅ COMPLETED

#### Step 3: Create jq script file ✅ COMPLETED

**File:** `.config/coverage-threshold-check.jq`

1. **Create the jq script file** ✅
   - [x] Create `.config/coverage-threshold-check.jq` with the verified script from Phase 1
   - [x] Ensure the script includes comments explaining thresholds and edge case handling

**Script file to create:**
```jq
# Coverage threshold check script
# Thresholds: Line > 80%, Branch > 70%, Function > 85%
# Note: Skip threshold check if count is 0 (no branches/lines/functions to cover)

.data[0].totals as $s |
($s.lines.percent // 0) as $line |
($s.lines.count // 0) as $line_count |
($s.branches.percent // 0) as $branch |
($s.branches.count // 0) as $branch_count |
($s.functions.percent // 0) as $func |
($s.functions.count // 0) as $func_count |

def check(actual; count; threshold; name):
  if count == 0 then
    "⚠️  \(name) coverage: N/A (no \(name | ascii_downcase) to cover)"
  elif actual >= threshold then
    "✅ \(name) coverage: \(actual)% (threshold: \(threshold)%)"
  else
    "❌ \(name) coverage \(actual)% is below threshold of \(threshold)%"
  end;

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

**Benefits of file-based approach:**
- Easier to test locally: `jq -r -e -f .config/coverage-threshold-check.jq coverage.json`
- Better maintainability: script is version controlled and reviewable separately
- Cleaner workflow file: shorter YAML, easier to read
- Reusable: can be used in other scripts or documentation

#### Step 4: Update workflow file ✅ COMPLETED

**File:** `.github/workflows/pull_request.yaml`

1. **Remove `bc` installation step (lines 95-96)** ✅
   - [x] Remove the `Install bc` step since it's no longer needed with jq

2. **Update `Check coverage thresholds` step (lines 95-101)** ✅
   - [x] Replace the entire step with Option 2 implementation:
     - Change `--summary-only` to `--json` in cargo llvm-cov command
     - Replace grep/awk/bc logic with jq script file reference
     - Update output file from `coverage-summary.txt` to `coverage.json`
   - [x] Use `jq -r -e -f` to read from the script file
   - [x] Ensure error handling is correct (jq `-e` flag + `|| exit 1`)

**Workflow step to implement:**
```yaml
- name: Check coverage thresholds
  run: |
    # Generate coverage in JSON format
    cargo llvm-cov nextest --all-features --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

3. **Test locally** ✅
   - [x] Test the script file: `jq -r -e -f .config/coverage-threshold-check.jq coverage.json`
   - [x] Verify the script file works the same as the inline version tested in Phase 1
   - [x] Confirm error handling works correctly (script exits with error when thresholds aren't met)

### Phase 3: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.github/workflows/pull_request.yaml`
   - Restore the original grep patterns
   - Restore the `bc` installation step if needed
   - Verify workflow returns to previous state

2. **Partial Rollback**
   - If JSON paths are incorrect, verify the actual JSON structure and adjust paths
   - If jq script has syntax errors, test locally and fix
   - If threshold logic is incorrect, adjust comparison operators in jq
   - Verify error handling catches parsing failures (jq `-e` flag behavior)

3. **Alternative Approaches**
   - If JSON output format is incompatible, fall back to Option 1 (table parsing with awk)
   - If jq is not available (unlikely), use Option 1 or install jq explicitly
   - Consider Option 3 (built-in threshold flags) if `cargo-llvm-cov` supports them
   - Verify `cargo-llvm-cov` version compatibility and JSON output format

### Implementation Order

1. [x] Run `cargo llvm-cov nextest --all-features --json` locally to examine JSON structure ✅
2. [x] Verify JSON paths for coverage percentages (`.data[0].totals.lines.percent`, etc.) ✅
3. [x] Test the jq script locally with the generated JSON file ✅
4. [x] Verify threshold checking logic works correctly (test both pass and fail scenarios) ✅
5. [x] Verify edge case handling (count = 0) works correctly ✅
6. [x] Create `.config/coverage-threshold-check.jq` with the verified jq script ✅
7. [x] Test the script file locally: `jq -r -e -f .config/coverage-threshold-check.jq coverage.json` ✅
8. [x] Remove `bc` installation step from workflow (lines 95-96) ✅
9. [x] Update `Check coverage thresholds` step to use JSON output and script file ✅
10. [ ] Create pull request and verify CI coverage job passes
11. [ ] Verify other CI jobs still pass
12. [ ] Confirm coverage thresholds are validated correctly in CI

### Risk Assessment

- **Risk Level:** Low to Medium
- **Impact if Failed:** Coverage threshold check would continue to fail, blocking PRs
- **Mitigation:**
  - Simple change to parsing logic
  - Easy rollback if needed
  - Can test locally before affecting CI
  - Multiple parsing options available
- **Testing:** Can be fully tested locally with `cargo llvm-cov` before affecting CI
- **Dependencies:**
  - Option 1 (table parsing) requires `bc` for floating-point comparisons (currently installed in workflow)
  - Option 2 (JSON) uses `jq` which is pre-installed in GitHub Actions runners, and eliminates the need for `bc`
  - Option 3 (built-in flags) depends on `cargo-llvm-cov` feature support

## Example Fix

### Before:
```yaml
# Extract coverage percentages from summary
LINE_COV=$(grep -oP '^\s*Lines:\s+\K[\d.]+' coverage-summary.txt || echo "0")
BRANCH_COV=$(grep -oP '^\s*Branches:\s+\K[\d.]+' coverage-summary.txt || echo "0")
FUNC_COV=$(grep -oP '^\s*Functions:\s+\K[\d.]+' coverage-summary.txt || echo "0")
```

### After (Option 1 - Table parsing):
```yaml
# Extract coverage percentages from TOTAL row
# Format: TOTAL  regions  missed  cover%  functions  missed  executed%  lines  missed  cover%  branches  missed  cover%
TOTAL_LINE=$(grep "^TOTAL" coverage-summary.txt | awk '{print $9}' | sed 's/%//')
TOTAL_BRANCH=$(grep "^TOTAL" coverage-summary.txt | awk '{print $12}' | sed 's/%//')
TOTAL_FUNC=$(grep "^TOTAL" coverage-summary.txt | awk '{print $6}' | sed 's/%//')

# Handle N/A for branch coverage
if [ "$TOTAL_BRANCH" = "-" ]; then
  TOTAL_BRANCH="0"
fi

LINE_COV=${TOTAL_LINE:-0}
BRANCH_COV=${TOTAL_BRANCH:-0}
FUNC_COV=${TOTAL_FUNC:-0}
```

**Note:** Column positions (9, 12, 6) need to be verified against actual output format.

### After (Option 2 - JSON parsing with jq script file):

**1. Create `.config/coverage-threshold-check.jq`:**
```jq
# Coverage threshold check script
# Thresholds: Line > 80%, Branch > 70%, Function > 85%
# Note: Skip threshold check if count is 0 (no branches/lines/functions to cover)

.data[0].totals as $s |
($s.lines.percent // 0) as $line |
($s.lines.count // 0) as $line_count |
($s.branches.percent // 0) as $branch |
($s.branches.count // 0) as $branch_count |
($s.functions.percent // 0) as $func |
($s.functions.count // 0) as $func_count |

def check(actual; count; threshold; name):
  if count == 0 then
    "⚠️  \(name) coverage: N/A (no \(name | ascii_downcase) to cover)"
  elif actual >= threshold then
    "✅ \(name) coverage: \(actual)% (threshold: \(threshold)%)"
  else
    "❌ \(name) coverage \(actual)% is below threshold of \(threshold)%"
  end;

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

**2. Update workflow step:**
```yaml
- name: Check coverage thresholds
  run: |
    # Generate coverage in JSON format
    cargo llvm-cov nextest --all-features --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

**Benefits of Option 2:**
- More reliable parsing (structured data)
- Less prone to format changes
- Easier to debug
- No additional dependencies (`jq` is pre-installed in GitHub Actions runners)
- No need for `bc` or bash floating-point arithmetic
- All logic in one place (extraction + threshold checking)
- Cleaner and more maintainable code

## References

- Coverage workflow: `.github/workflows/pull_request.yaml` (lines 70-135)
- Cargo llvm-cov documentation: https://github.com/taiki-e/cargo-llvm-cov
- Coverage plan: `plan/01_Quality/CODE_COVERAGE.md`
- Coverage implementation: `work/01_Quality/04_Code_Coverage.md`
