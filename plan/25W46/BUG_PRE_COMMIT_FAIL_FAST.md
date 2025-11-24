# BUG: Pre-commit fail_fast configuration - should be false locally, true in CI

**Status**: ✅ Complete

## Description

The `.pre-commit-config.yaml` currently has `fail_fast: true` set globally. This means that pre-commit stops on the first failure both locally and in CI. However, for better developer experience, `fail_fast` should be `false` locally (so developers can see all failures at once), but `true` in CI (to fail fast and save CI resources).

## Current State

✅ **FIXED** - The pre-commit fail_fast configuration has been updated to use different behavior for local vs CI.

**Previous (incorrect) configuration:**
- `.pre-commit-config.yaml` (line 7): `fail_fast: true` (applied to both local and CI)
- `.github/workflows/pull_request.yaml` (line 126): `pre-commit run --all-files` (no override)

**Current (correct) configuration:**
- `.pre-commit-config.yaml` (line 7): `fail_fast: false` (default for local development)
- `.github/workflows/pull_request.yaml` (line 126): `pre-commit run --all-files --fail-fast` (overrides for CI)

**Fixed files:**
- `.pre-commit-config.yaml` (line 7) - Changed `fail_fast: true` to `fail_fast: false`
- `.github/workflows/pull_request.yaml` (line 126) - Added `--fail-fast` flag to pre-commit command

## Expected State

1. **Local Development:**
   - `fail_fast: false` in `.pre-commit-config.yaml` (or default behavior)
   - All hooks run even if some fail, showing all failures at once
   - Better developer experience - can fix multiple issues in one iteration

2. **CI Environment:**
   - `fail_fast: true` when running in CI
   - Stops on first failure to save CI resources and time
   - Faster feedback in CI pipelines

## Impact

### Developer Experience Impact
- **Severity**: Medium
- **Priority**: Medium

When `fail_fast: true` is set locally:
- Developers must fix issues one at a time
- Multiple iterations needed to see all failures
- Slower development workflow
- Frustrating when multiple unrelated issues exist

### CI/CD Impact
- **Severity**: Low
- **Priority**: Low

Current CI behavior (fail_fast: true) is actually desired, but we need to differentiate between local and CI environments.

## Root Cause

Pre-commit's `fail_fast` setting is a global configuration in `.pre-commit-config.yaml` that applies to all environments. However, pre-commit provides a command-line flag `--fail-fast` that can override the config file setting, allowing different behavior in local vs CI environments.

## Investigation Results

### ✅ Solution: Command-Line Flag Override

**Investigation completed:** Pre-commit supports a `--fail-fast` command-line flag that overrides the config setting.

**Verification:**
- ✅ Verified: `--fail-fast` flag exists in pre-commit CLI (confirmed via `pre-commit run --help`)
- ✅ Flag overrides config file setting when used
- ✅ Works with current pre-commit version (minimum: 4.4.0)
- ✅ This is the standard, recommended approach per pre-commit documentation

**How it works:**
- The `fail_fast` setting in `.pre-commit-config.yaml` applies by default
- The `--fail-fast` command-line flag overrides the config file setting
- This allows setting `fail_fast: false` in config (for local) and using `--fail-fast` flag in CI

**Implementation:**
1. Update `.pre-commit-config.yaml`: Set `fail_fast: false` (default for local development)
2. Update `.github/workflows/pull_request.yaml`: Add `--fail-fast` flag to the pre-commit command

```bash
# Local (uses config: fail_fast: false)
pre-commit run --all-files

# CI (overrides with --fail-fast flag)
pre-commit run --all-files --fail-fast
```

**Why this approach:**
- ✅ Simple and clean - no environment variables needed
- ✅ No separate config files to maintain
- ✅ Standard pre-commit feature, well-documented
- ✅ Easy to understand and maintain


## Related Implementation Plan

See `work/25W46/BUG_PRE_COMMIT_FAIL_FAST.md` for the detailed implementation plan.
