# BUG: PR workflow test job fails with invalid --junit-xml flag

**Status**: ✅ Complete

## Description

The PR workflow `test` job fails because `cargo nextest run --junit-xml test-results.xml` uses an invalid flag. The `--junit-xml` argument is not recognized by `cargo nextest run`.

## Current State

✅ **FIXED** - The invalid `--junit-xml` flag has been removed from the workflow.

**Previous (incorrect) command:**
```yaml
- name: Run tests
  run: cargo nextest run --junit-xml test-results.xml
```

**Current (correct) command:**
```yaml
- name: Run tests
  run: cargo nextest run
```

**Fixed files:**
- `.github/workflows/pull_request.yaml` (line 60) - Flag removed, now uses configuration file approach

## Expected State

The test job should successfully run nextest and generate JUnit XML output for test result uploads.

The `.config/nextest.toml` file already contains JUnit XML configuration:
```toml
[profile.default.junit]
path = "test-results.xml"
```

## Impact

### CI/CD Impact
- **Severity**: High
- **Priority**: High

The test job fails completely, preventing:
- Test execution in PR workflows
- Test result artifact uploads
- CI/CD pipeline completion

### Functionality Impact
- **Severity**: High
- **Priority**: High

All pull requests will fail CI checks, blocking merges until this is fixed.

## Root Cause

The `--junit-xml` flag is not a valid argument for `cargo nextest run`. Nextest uses configuration files (`.config/nextest.toml`) to specify JUnit XML output paths, not command-line flags.


## Related Implementation Plan

See `work/25W46/BUG_NEXTEST_JUNIT_XML_FLAG.md` for the detailed implementation plan.
