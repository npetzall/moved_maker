# BUG: GitHub Actions workflows missing required Rust components

**Status**: ✅ Complete

## Description

Test and pre-commit jobs need `clippy` and `rustfmt` components but they're not installed. This can cause pre-commit hooks and linting checks to fail.

## Current State

✅ **FIXED** - All test and pre-commit jobs now include required components (`clippy`, `rustfmt`).

Previously, test and pre-commit jobs were missing required components:

**pull_request.yaml - test job (line 44-48):**
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    components: clippy rustfmt
```

**pull_request.yaml - pre-commit job (line 140-144):**
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    components: clippy rustfmt
```

## Expected State

Test and pre-commit jobs should include `clippy` and `rustfmt`:

```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@1.90.0
  with:
    components: clippy rustfmt
```

## Impact

### Functionality Impact
- **Severity**: High
- **Priority**: High

Missing components (`clippy`, `rustfmt`) means:
- Pre-commit hooks may fail if they require these tools
- Linting and formatting checks may not run correctly
- Inconsistent tooling across jobs


## Related Implementation Plan

See `work/25W46/BUG_GITHUB_WORKFLOWS_RUST_COMPONENTS.md` for the detailed implementation plan.
