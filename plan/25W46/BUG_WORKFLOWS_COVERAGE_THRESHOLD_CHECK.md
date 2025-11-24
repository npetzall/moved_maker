# BUG: Workflow - Code coverage threshold check doesn't work

**Status**: ✅ Complete

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


## Related Implementation Plan

See `work/25W46/BUG_WORKFLOWS_COVERAGE_THRESHOLD_CHECK.md` for the detailed implementation plan.
