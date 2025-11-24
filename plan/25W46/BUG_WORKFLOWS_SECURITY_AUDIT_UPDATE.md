# BUG: Workflow - Security audit fails when running `cargo audit update`

**Status**: ✅ Complete

## Description

The security workflow jobs in both `pull_request.yaml` and `release-build.yaml` fail when attempting to update the vulnerability database using `cargo audit update`. The command fails because `cargo audit` does not have an `update` subcommand. The error prevents the security checks from completing, blocking PRs and releases.

## Progress Summary

**Status:** ✅ Implementation Complete - Ready for CI Testing

**Completed:**
- ✅ Root cause identified: `cargo audit` doesn't have an `update` subcommand
- ✅ Solution verified: `cargo audit` automatically fetches latest database on each run
- ✅ Removed `cargo audit update` step from `.github/workflows/pull_request.yaml`
- ✅ Removed `cargo audit update` step from `.github/workflows/release-build.yaml`
- ✅ Updated `TOOLING.md` documentation
- ✅ Updated `DEVELOPMENT.md` documentation
- ✅ Updated `plan/25W46/REQ_SECURITY.md` documentation
- ✅ Updated `work/25W46/01_Security.md` documentation

**Ready for Testing:**
- ⏳ Test in CI (PR workflow)
- ⏳ Test in CI (release workflow)

## Current State

✅ **FIXED** - The `cargo audit update` step has been removed from both workflow files. The security workflow should now complete successfully as `cargo audit` automatically updates the database when it runs.

**Fixed workflow configuration:**
```yaml
- name: Run cargo-deny checks (blocking)
  run: cargo deny check --config .config/deny.toml

- name: Run cargo-audit checks (blocking)
  run: cargo audit --deny warnings
```

**Previous error output (before fix):**
```
Run cargo audit update

error: unrecognized subcommand 'update'

rgo audit [OPTIONS] [COMMAND]

For more information, try '--help'.

Error: Process completed with exit code 2.
```

**Fixed workflows:**
1. `.github/workflows/pull_request.yaml` - `security` job (removed lines 27-28)
2. `.github/workflows/release-build.yaml` - `security` job (removed lines 31-32)

## Expected State

The security workflow should:
1. Successfully install security tools
2. Run cargo-deny checks
3. Run cargo-audit checks (which automatically fetches the latest vulnerability database)
4. Run cargo-geiger scan
5. Complete without errors

## Impact

### CI/CD Impact
- **Severity**: High
- **Priority**: High

The security workflow always fails, preventing:
- Security vulnerability scanning from completing
- PRs from being merged (if security is a required check)
- Releases from being built (security job blocks `build-and-release` job)
- Accurate security reporting in CI

### Functionality Impact
- **Severity**: High
- **Priority**: High

Security checks cannot be performed, which is a critical quality and safety metric for the project. The vulnerability database update step blocks all subsequent security checks.

## Root Cause

The workflow attempts to run `cargo audit update` to update the vulnerability database before running the audit. However, `cargo audit` does not have an `update` subcommand.

According to the RustSec Advisory Database documentation and cargo-audit behavior:
- `cargo audit` automatically fetches the latest advisory database from the RustSec Advisory Database each time it runs
- There is no separate `update` command needed
- The database is cached locally and refreshed automatically when `cargo audit` is executed

**Workflow evidence:**
The error occurs in both PR and release workflows at the "Update vulnerability database" step, which runs `cargo audit update`. This command is invalid and causes the workflow to fail with exit code 2.


## Related Implementation Plan

See `work/25W46/BUG_WORKFLOWS_SECURITY_AUDIT_UPDATE.md` for the detailed implementation plan.
