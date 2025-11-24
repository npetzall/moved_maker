# BUG: Workflows - No test report found

**Status**: ✅ Complete

## Description

The PR workflow `test` job attempts to upload test results from `test-results.xml`, but the file is not found. When running locally, nextest places the JUnit XML output in `target/nextest/default/` folder, but the workflow expects it at the root level.

## Current State

✅ **FIXED** - The workflow upload step has been updated to use a wildcard pattern to find the test results file.

**Previous (broken) workflow configuration:**
```yaml
- name: Run tests
  run: cargo nextest run

- name: Upload test results
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: test-results-${{ matrix.os }}
    path: test-results.xml
```

**Current (fixed) workflow configuration:**
```yaml
- name: Run tests
  run: cargo nextest run

- name: Upload test results
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: test-results-${{ matrix.os }}
    path: target/nextest/**/test-results.xml
    if-no-files-found: warn
```

**Current nextest configuration (`.config/nextest.toml`):**
```toml
[profile.default.junit]
path = "test-results.xml"
```

**Local behavior:**
- When running `cargo nextest run` locally, the JUnit XML is generated in `target/nextest/default/test-results.xml`
- The configuration specifies `path = "test-results.xml"` (relative path)

## Expected State

The test job should successfully:
1. Run nextest tests
2. Generate JUnit XML output
3. Upload the test results artifact

The artifact upload should work whether the file is at the root level or in a subdirectory.

## Impact

### CI/CD Impact
- **Severity**: Medium
- **Priority**: Medium

The test results artifact upload fails, preventing:
- Test result visualization in GitHub Actions
- Test result artifact downloads
- Test result analysis tools from accessing the data

### Functionality Impact
- **Severity**: Low
- **Priority**: Low

Tests still run successfully, but test result artifacts are not available for download or analysis.

## Root Cause

The nextest configuration specifies a relative path `test-results.xml`, but nextest may place the file in a different location (e.g., `target/nextest/default/test-results.xml`) depending on the working directory or nextest version behavior. The workflow upload step expects the file at the root level.


## Related Implementation Plan

See `work/25W46/BUG_WORKFLOWS_TEST_REPORT_PATH.md` for the detailed implementation plan.
