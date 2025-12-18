# BUG: Coverage summary shows ❌ overall status when branch coverage is N/A

**Status**: ✅ Fixed

## Overview
The coverage summary script incorrectly shows a red cross (❌) for the overall status when branch coverage is N/A (no branches to cover), even though line and function coverage meet their thresholds.

## Environment
- **OS**: GitHub Actions (ubuntu-latest)
- **Rust Version**: 1.90.0
- **Tool Version**: N/A (script issue)
- **Terraform Version**: N/A

## Steps to Reproduce
1. Run the pull request workflow with coverage job
2. The "Generate coverage summary" step executes
3. Coverage data shows:
   - Lines: 95.52% (✅ above 80.0% threshold)
   - Branches: N/A (⚠️ no branches to cover)
   - Functions: 97.27% (✅ above 85.0% threshold)
4. Overall status incorrectly shows ❌ instead of ✅

## Expected Behavior
The overall status should be ✅ when all metrics that have data (total > 0) meet their thresholds. Metrics with N/A (total == 0) should be skipped from the threshold check, as they indicate there are no items to cover.

## Actual Behavior
The overall status shows ❌ because the code checks `overall.branch_coverage.percent >= threshold_branch` even when `overall.branch_coverage.total == 0`. When total is 0, the percent is likely 0.0, which fails the check `0.0 >= 70.0`.

## Error Messages / Output
```
Code Coverage Summary
Overall Coverage
Status: ❌

Metric	Coverage	Status	Threshold
Lines	95.52% (1001/1048)	✅	80.0%
Branches	N/A	⚠️	70.0%
Functions	97.27% (107/110)	✅	85.0%
```

## Minimal Reproduction Case
The issue occurs in `.github/scripts/coverage-summary/src/coverage_summary/generator.py` at lines 71-78. The overall status calculation checks all three metrics without skipping N/A metrics:

```python
if (
    overall.line_coverage.percent >= threshold_line
    and overall.branch_coverage.percent >= threshold_branch
    and overall.function_coverage.percent >= threshold_function
):
    overall_status = "✅"
else:
    overall_status = "❌"
```

When `overall.branch_coverage.total == 0`, the percent is 0.0, causing `0.0 >= 70.0` to fail.

**Evidence**: The jq script at `.config/coverage-threshold-check.jq` correctly handles this by checking `if $branch_count > 0 and $branch < 70`, meaning it only fails if there are branches AND the coverage is below threshold.

## Additional Context
- **Affected file**: `.github/scripts/coverage-summary/src/coverage_summary/generator.py` (lines 71-78, overall status calculation)
- **Root cause**: The overall status check doesn't skip metrics with `total == 0` (N/A), causing false failures
- **Impact**: Coverage summaries incorrectly show failure status when branch coverage is N/A, even when all available metrics meet thresholds
- **Frequency**: Always occurs when branch coverage is N/A (common in Rust projects with minimal branching)
- **Workaround**: None currently - the status is misleading
- **Related code**: The jq script (`.config/coverage-threshold-check.jq`) correctly handles N/A metrics by only checking thresholds when `count > 0`

## Related Issues
- Related PRs: N/A
