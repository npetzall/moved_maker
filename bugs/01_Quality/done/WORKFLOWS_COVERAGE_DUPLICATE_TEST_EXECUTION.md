# Bug: Coverage workflow executes tests twice instead of using report subcommand

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

## Steps to Fix

### Step 1: Update coverage generation step

Change the first step to run tests without output format flags:

**Before:**
```yaml
- name: Generate coverage
  run: cargo llvm-cov nextest --all-features --lcov --output-path lcov.info
```

**After:**
```yaml
- name: Generate coverage
  run: cargo llvm-cov nextest --all-features
```

### Step 2: Update threshold check step

Change the threshold check to use the report subcommand:

**Before:**
```yaml
- name: Check coverage thresholds
  run: |
    # Generate coverage in JSON format
    cargo llvm-cov nextest --all-features --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

**After:**
```yaml
- name: Check coverage thresholds
  run: |
    # Generate JSON report from collected coverage data
    cargo llvm-cov report --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

## Affected Files

- `.github/workflows/pull_request.yaml`
  - `coverage` job (lines 100-109)

## Example Fix

### Before:
```yaml
- name: Generate coverage
  run: cargo llvm-cov nextest --all-features --lcov --output-path lcov.info

- name: Check coverage thresholds
  run: |
    # Generate coverage in JSON format
    cargo llvm-cov nextest --all-features --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

### After:
```yaml
- name: Generate coverage
  run: cargo llvm-cov nextest --all-features

- name: Check coverage thresholds
  run: |
    # Generate JSON report from collected coverage data
    cargo llvm-cov report --json > coverage.json

    # Extract percentages and check thresholds using jq script
    jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

## Status

✅ **COMPLETED** - Coverage workflow has been updated to execute tests once and use the `report` subcommand to generate JSON format from collected coverage data. The workflow now runs tests only once, eliminating duplicate test execution and improving CI efficiency.

## References

- [cargo-llvm-cov Documentation](https://github.com/taiki-e/cargo-llvm-cov)
- [cargo-llvm-cov report subcommand](https://github.com/taiki-e/cargo-llvm-cov#report-subcommand)
- [CODE_COVERAGE.md](../plan/01_Quality/CODE_COVERAGE.md) - Coverage documentation

## Notes

- The `cargo llvm-cov nextest` command runs tests and collects coverage data
- The `cargo llvm-cov report` subcommand generates output formats from already-collected coverage data
- Coverage data is stored in `target/llvm-cov/` directory after test execution
- The report subcommand reads this data and generates different formats (LCOV, JSON, HTML, etc.)
- This approach is more efficient and follows cargo-llvm-cov best practices
- All report formats will use the same coverage data snapshot, ensuring consistency

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/pull_request.yaml`

**File:** `.github/workflows/pull_request.yaml`

1. **Update `coverage` job coverage generation step (line 100-101)** ✅ COMPLETED
   - [x] Locate the "Generate coverage" step at line 100-101 in the `coverage` job
   - [x] Remove the `--lcov --output-path lcov.info` flags from the command
   - [x] Update the command from `cargo llvm-cov nextest --all-features --lcov --output-path lcov.info` to `cargo llvm-cov nextest --all-features`
   - [x] Verify the step name remains "Generate coverage"
   - [x] Verify the command will run tests and collect coverage data without generating output files
   - [x] Verify step placement (should be before the "Check coverage thresholds" step)

2. **Update `coverage` job threshold check step (line 103-109)** ✅ COMPLETED
   - [x] Locate the "Check coverage thresholds" step at line 103-109 in the `coverage` job
   - [x] Change the command from `cargo llvm-cov nextest --all-features --json > coverage.json` to `cargo llvm-cov report --json > coverage.json`
   - [x] Update the comment from "Generate coverage in JSON format" to "Generate JSON report from collected coverage data"
   - [x] Verify the jq command remains unchanged: `jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1`
   - [x] Verify the step will generate JSON from collected coverage data, not by re-running tests
   - [x] Verify step placement (should be after the "Generate coverage" step)

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.github/workflows/pull_request.yaml`
   - Restore the original commands with `--lcov --output-path lcov.info` and `cargo llvm-cov nextest --all-features --json`
   - Verify workflows return to previous state
   - Verify tests execute twice as before

2. **Partial Rollback**
   - If the report subcommand doesn't work, verify that coverage data is being collected correctly
   - Check if the `target/llvm-cov/` directory contains coverage data after test execution
   - Verify that `cargo llvm-cov report --json` can read the collected data
   - If report subcommand fails, consider keeping the duplicate execution temporarily while investigating

3. **Alternative Approaches**
   - If `cargo llvm-cov report` doesn't work as expected, verify cargo-llvm-cov version compatibility
   - Consider generating both formats in one step if report subcommand has issues:
     ```yaml
     - name: Generate coverage and reports
       run: |
         cargo llvm-cov nextest --all-features
         cargo llvm-cov report --json > coverage.json
     ```
   - If JSON format from report subcommand differs, verify the structure matches what the jq script expects
   - Consider using summary-only output if JSON parsing issues occur (see `WORKFLOWS_COVERAGE_THRESHOLD_CHECK.md`)

### Implementation Order

1. [x] Update `.github/workflows/pull_request.yaml` coverage generation step (line 100-101) to remove `--lcov --output-path lcov.info` flags ✅ COMPLETED
2. [x] Update `.github/workflows/pull_request.yaml` threshold check step (line 103-109) to use `cargo llvm-cov report --json` ✅ COMPLETED
3. [ ] Test via pull request to verify:
   - Tests execute only once (check CI logs)
   - Coverage data is collected in `target/llvm-cov/` directory
   - JSON file is generated correctly from report subcommand
   - Threshold check works with JSON from report subcommand
   - Coverage percentages match expected values
   - CI execution time is reduced compared to previous runs
4. [ ] Verify performance improvement:
   - Check CI execution time (should be reduced by approximately half)
   - Verify coverage data is consistent
   - Confirm no test execution errors
   - Verify coverage job completes successfully

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:** Tests would continue to execute twice, wasting CI time, but functionality would remain unchanged
- **Mitigation:**
  - Simple change to command flags and subcommand usage
  - Easy rollback if needed
  - Can test via pull request before affecting other workflows
  - Report subcommand is a standard feature of cargo-llvm-cov
- **Testing:** Can be fully tested via pull request workflow
- **Dependencies:**
  - Requires cargo-llvm-cov to support the `report` subcommand (standard feature)
  - Coverage data must be collected in `target/llvm-cov/` directory (default behavior)
  - JSON output format from report subcommand must match what jq script expects
  - No additional dependencies required

## Alternative Approaches

If the report subcommand doesn't work as expected, alternative approaches:

1. **Generate both formats in one command** (if supported):
   ```yaml
   - name: Generate coverage and reports
     run: |
       cargo llvm-cov nextest --all-features
       cargo llvm-cov report --json > coverage.json
   ```

2. **Use summary-only for threshold check** (if JSON not needed):
   ```yaml
   - name: Check coverage thresholds
     run: cargo llvm-cov report --summary-only
   ```
   (Note: This may require different parsing, see `WORKFLOWS_COVERAGE_THRESHOLD_CHECK.md`)

## Related Issues

- This relates to coverage workflow efficiency
- May impact CI execution time metrics
- Aligns with best practices for cargo-llvm-cov usage
