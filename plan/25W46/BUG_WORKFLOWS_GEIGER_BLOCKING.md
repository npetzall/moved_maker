# BUG: cargo-geiger configured as blocking in CI workflows

**Status**: ✅ Complete

## Description

`cargo-geiger` is currently configured as a blocking step in CI workflows, but it is not a pass/fail tool. After investigation, `cargo-geiger` is an informational tool that reports unsafe code usage in dependencies. It doesn't have exit codes that indicate pass/fail conditions, making it unsuitable as a blocking step.

## Current State

✅ **FIXED** - `cargo-geiger` has been updated in both `.github/workflows/pull_request.yaml` and `.github/workflows/release-build.yaml` to treat exit code 1 as informational (non-blocking) while still failing on actual tool errors.

**Previous (blocking) configuration:**
```yaml
- name: Run cargo-geiger scan (blocking)
  run: cargo geiger --output-format json > geiger-report.json
```

**Current (fixed) configuration:**
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

The step now:
- Treats exit code 1 (unsafe code found) as informational and allows the workflow to continue
- Fails the workflow on actual tool errors (exit codes 2+)
- Uploads the geiger report as an artifact for review

## Expected State

`cargo-geiger` should:
1. **Not be blocking for informational results**: The step should not fail the workflow if geiger reports unsafe code (exit code 1), as this is informational
2. **Fail on actual errors**: The step should fail the workflow if geiger encounters actual tool errors (exit codes 2+), such as installation failures or missing dependencies
3. **Upload the report**: The generated `geiger-report.json` should be uploaded as an artifact so it can be reviewed, even if the step fails

The tool is still valuable for security awareness and monitoring, but it should be informational rather than blocking for the normal case of finding unsafe code.

## Impact

### Workflow Impact
- **Severity**: Medium
- **Priority**: High

Current issues:
- Workflow may fail unnecessarily if geiger encounters errors
- Unsafe code detection is informational, not a security vulnerability
- The report is generated but not uploaded for review
- Blocks downstream jobs (like `build-and-release`) even though geiger is informational


## Related Implementation Plan

See `work/25W46/BUG_WORKFLOWS_GEIGER_BLOCKING.md` for the detailed implementation plan.
