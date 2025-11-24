# BUG: Coverage workflow executes tests twice instead of using report subcommand

**Status**: ✅ Complete

## Description

The coverage workflow in `.github/workflows/pull_request.yaml` executes tests twice - once to generate LCOV format and once to generate JSON format. This is inefficient and wastes CI time. Instead, tests should be executed once with coverage collection, and then the `cargo llvm-cov report` subcommand should be used to generate different output formats from the same coverage data.

## Current State

✅ **FIXED** - The coverage workflow has been updated to execute tests once and use the `report` subcommand to generate JSON format from the collected coverage data.

**Current (fixed) configuration:**

**Step 1 (line 100-101):** Run tests once with coverage collection
```yaml
- name: Generate coverage
  run: cargo llvm-cov nextest --all-features
```

**Step 2 (lines 103-109):** Generate JSON format from collected coverage data
```yaml
- name: Check coverage thresholds
  run: |
    # Generate JSON report from collected coverage data
    cargo llvm-cov report --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

The workflow now:
- Executes tests only once, reducing CI execution time
- Uses the `report` subcommand to generate JSON from collected coverage data
- Eliminates duplicate test execution and coverage data collection
- Improves CI efficiency and reduces resource usage

**Affected files:**
- `.github/workflows/pull_request.yaml` (lines 100-109 - coverage job steps)

## Expected State

Tests should be executed once with coverage collection, then the `report` subcommand should be used to generate different output formats from the same coverage data:

**Step 1:** Run tests once with coverage collection
```yaml
- name: Generate coverage
  run: cargo llvm-cov nextest --all-features
```

**Step 2:** Generate JSON format and check thresholds
```yaml
- name: Check coverage thresholds
  run: |
    # Generate JSON report from collected coverage data
    cargo llvm-cov report --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

## Impact

### Performance Impact
- **Severity**: Medium
- **Priority**: Medium

Current issues:
- **Doubled test execution time**: Tests run twice, wasting CI minutes
- **Increased CI costs**: More compute time used unnecessarily
- **Slower feedback**: PR checks take longer to complete
- **Resource waste**: Coverage data collected twice when it could be reused

### Benefits of Using Report Subcommand
- **Faster CI**: Tests execute only once
- **Efficient**: Coverage data collected once, multiple formats generated from it
- **Consistent**: All reports use the same coverage data snapshot
- **Best practice**: Aligns with cargo-llvm-cov recommended usage


## Related Implementation Plan

See `work/25W46/BUG_WORKFLOWS_COVERAGE_DUPLICATE_TEST_EXECUTION.md` for the detailed implementation plan.
