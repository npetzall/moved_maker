# BUG: GitHub Actions workflows missing Rust toolchain version specification

**Status**: ✅ Complete

## Description

GitHub Actions workflows use `dtolnay/rust-toolchain@stable` without specifying the `toolchain` parameter, which means they install the latest stable Rust version instead of the specific version (1.90.0) specified in `Cargo.toml`. This can cause version mismatches between local development and CI environments.

## Current State

✅ **FIXED** - All workflows now specify `toolchain: 1.90.0` to match the version in `Cargo.toml`.

Previously, all workflows used `dtolnay/rust-toolchain@stable` without the `toolchain` parameter, which installed the latest stable Rust version instead of the version specified in `Cargo.toml`:

**Cargo.toml:**
```toml
rust-version = "1.90.0"
```

**Workflows (all jobs):**
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
```

**Affected files:**
- `.github/workflows/pull_request.yaml` (lines 15, 43, 68, 135)
- `.github/workflows/release.yaml` (lines 16, 165)

## Expected State

All Rust installations should specify the toolchain version `1.90.0` using the `toolchain` parameter:

```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
```

## Impact

### Consistency Impact
- **Severity**: Medium
- **Priority**: High

Version mismatch between `Cargo.toml` and workflows can cause:
- Build failures if CI uses a different Rust version than local development
- Inconsistent behavior across environments
- Potential compatibility issues

## Steps to Fix

Add the `toolchain` parameter to all `dtolnay/rust-toolchain` action usages. For actions that already have a `with` section, add `toolchain: 1.90.0` to it. For actions without a `with` section, add one.

**For actions without existing `with` parameters:**
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
```

**For actions with existing `with` parameters (e.g., `components`, `targets`):**
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    components: llvm-tools-preview  # existing parameter
```

## Affected Files

- `.github/workflows/pull_request.yaml`
  - `security` job (line 15)
  - `test` job (line 43)
  - `coverage` job (line 68)
  - `pre-commit` job (line 135)

- `.github/workflows/release.yaml`
  - `security` job (line 16)
  - `build-and-release` job (line 165)

## Example Fix

### Before:
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
```

### After (simple case):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
```

### After (with existing parameters):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    components: llvm-tools-preview
```

## References

- [dtolnay/rust-toolchain action documentation](https://github.com/dtolnay/rust-toolchain)
- [Cargo.toml rust-version field](https://doc.rust-lang.org/cargo/reference/manifest.html#the-rust-version-field)

## Notes

- The `@stable` tag refers to the action version, not the Rust toolchain version
- The `toolchain` parameter in the `with` section specifies which Rust toolchain version to install
- This ensures CI uses the exact same Rust version as specified in `Cargo.toml`


## Related Implementation Plan

See `work/25W46/BUG_GITHUB_WORKFLOWS_RUST_VERSION.md` for the detailed implementation plan.
