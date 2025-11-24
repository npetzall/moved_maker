# BUG: GitHub Actions workflows using incorrect nextest installation method

**Status**: ✅ Complete

## Description

Workflows use `taiki-e/install-action@cargo-nextest` action instead of installing via `cargo install`. This prevents nextest from being cached and is inconsistent with other cargo tool installations.

## Current State

✅ **FIXED** - All workflows now use `cargo install cargo-nextest` instead of the action-based installation.

Previously, workflows used `taiki-e/install-action@cargo-nextest` action instead of installing via cargo:

**Current (incorrect):**
```yaml
- name: Install cargo-nextest
  uses: taiki-e/install-action@cargo-nextest
```

**Affected files:**
- `.github/workflows/pull_request.yaml` (lines 45-46, 72-73, 140-141)
- `.github/workflows/release.yaml` (line 169-170)

## Expected State

Replace action-based installation with cargo install:

```yaml
- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

## Impact

### Performance Impact
- **Severity**: Low
- **Priority**: Low

Using the action prevents nextest from being cached, leading to:
- Slightly slower CI runs
- Inconsistent installation method compared to other cargo tools

### Consistency Impact
- **Severity**: Low
- **Priority**: Low

Inconsistent installation method compared to other cargo tools like `cargo-deny`, `cargo-audit`, etc.

## Steps to Fix

Replace all instances of:
```yaml
- name: Install cargo-nextest
  uses: taiki-e/install-action@cargo-nextest
```

With:
```yaml
- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

## Affected Files

- `.github/workflows/pull_request.yaml`
  - `test` job (lines 45-46)
  - `coverage` job (lines 72-73)
  - `pre-commit` job (lines 140-141)

- `.github/workflows/release.yaml`
  - `build-and-release` job (lines 169-170)

## Example Fix

### Before:
```yaml
- name: Install cargo-nextest
  uses: taiki-e/install-action@cargo-nextest
```

### After:
```yaml
- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

## Status

✅ **FIXED** - All instances replaced with `cargo install cargo-nextest`


## Related Implementation Plan

See `work/25W46/BUG_GITHUB_WORKFLOWS_NEXTEST_INSTALLATION.md` for the detailed implementation plan.
