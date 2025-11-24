# BUG: Workflow - pre-commit fails, local hooks expect software to be installed

**Status**: ✅ Complete

## Description

The PR workflow `pre-commit` job fails because the pre-commit hooks require additional software to be installed (`cargo-nextest`, `cargo-deny`, `cargo-audit`), but the workflow does not install these dependencies before running `pre-commit run --all-files`.

## Current State

✅ **FIXED** - The pre-commit workflow job now installs all required tools before running pre-commit hooks.

**Previous (incorrect) configuration:**
```yaml
- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

**Current (correct) configuration:**
```yaml
- name: Install pre-commit dependencies
  run: cargo install cargo-nextest cargo-deny cargo-audit
```

**Fixed files:**
- `.github/workflows/pull_request.yaml` (line 162) - Replaced single tool installation with combined installation step

**Pre-commit hooks that require additional tools (from `.pre-commit-config.yaml`):**
- `cargo-nextest` - ✅ Installed (line 162)
- `cargo-deny` - ✅ Installed (line 162)
- `cargo-audit` - ✅ Installed (line 162)
- `cargo-fmt` - ✅ Available via rustfmt component
- `cargo-check` - ✅ Available via cargo
- `cargo-clippy` - ✅ Available via clippy component
- `git-sumi` - ✅ Handled automatically by pre-commit (from external repo)
- `ripsecrets` - ✅ Handled automatically by pre-commit (from external repo)

## Expected State

The pre-commit job should:
1. Install all required tools before running pre-commit
2. Successfully run all pre-commit hooks
3. Pass if all checks pass, fail if any check fails

## Impact

### CI/CD Impact
- **Severity**: High
- **Priority**: High

The pre-commit job fails completely, preventing:
- Pre-commit checks from running in CI
- Code quality validation
- Security scanning
- Commit message validation

### Functionality Impact
- **Severity**: Medium
- **Priority**: Medium

Pre-commit hooks cannot run, so code quality and security checks are not enforced in CI.

## Root Cause

The workflow installs `cargo-nextest` but does not install other required tools:
- `cargo-deny` - Required by `cargo-deny` hook
- `cargo-audit` - Required by `cargo-audit` hook
- `git-sumi` - Handled automatically by pre-commit (from external repo)
- `ripsecrets` - Handled automatically by pre-commit (from external repo)


## Related Implementation Plan

See `work/25W46/BUG_WORKFLOWS_PRE_COMMIT_MISSING_DEPS.md` for the detailed implementation plan.
