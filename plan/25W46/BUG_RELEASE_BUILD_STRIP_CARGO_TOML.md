# BUG: Release Build Workflow - Manual Strip Command Interferes with cargo-auditable

**Status**: ✅ Complete

## Description

The `release-build.yaml` workflow uses a manual `strip` command to remove debug symbols from release binaries. However, this can interfere with `cargo auditable`, which embeds dependency information into a dedicated linker section. The manual `strip` command may remove this section, preventing users from auditing the released binaries. The solution is to use Cargo's built-in `strip` option in `Cargo.toml`, which preserves custom linker sections (including audit data) while still removing debug symbols.

## Current State

**File**: `.github/workflows/release-build.yaml` (lines 141-143)

The workflow currently uses a manual strip command:
```yaml
- name: Strip binary (Linux/macOS)
  if: matrix.os != 'windows'
  run: strip target/${{ matrix.target }}/release/move_maker
```

**File**: `Cargo.toml`

The `Cargo.toml` does not have a `strip` configuration in the release profile:
```toml
[package]
name = "move_maker"
version = "0.1.0"
rust-version = "1.90.0"
edition = "2024"
license = "Apache-2.0"

[dependencies]
hcl-rs = "0.19.4"
clap = { version = "4.5", features = ["derive"] }
env_logger = "0.11"
anyhow = "1.0"

[dev-dependencies]
tempfile = "3.10"
pretty_assertions = "1.4"
```

### Workflow Context

The workflow builds with `cargo auditable` to embed dependency information:
```yaml
- name: Build release binary with embedded dependency info
  run: cargo auditable build --release --target ${{ matrix.target }}

- name: Audit release binary
  run: cargo audit bin target/${{ matrix.target }}/release/move_maker

- name: Strip binary (Linux/macOS)
  if: matrix.os != 'windows'
  run: strip target/${{ matrix.target }}/release/move_maker
```

## Problem

### Issue 1: Manual Strip May Remove Audit Data

The `cargo auditable` tool embeds dependency information into a dedicated linker section of the compiled binary. The manual `strip` command can remove this section, which means:

- ✅ The audit step (line 139) works because it runs **before** stripping
- ❌ The final stripped binary may lose the embedded audit data
- ❌ Users who download the release binary cannot audit it
- ❌ The purpose of using `cargo auditable` is defeated

### Issue 2: OS-Specific Conditional Logic

The workflow uses conditional logic to handle different operating systems:
```yaml
if: matrix.os != 'windows'
```

This adds complexity and requires special handling for Windows (where `strip` isn't available by default).

### Issue 3: Inconsistent Configuration

Stripping is configured in the workflow file rather than in `Cargo.toml`, which is the standard location for build configuration. This makes it:
- Less discoverable
- Harder to test locally
- Inconsistent with Rust best practices

## Expected State

### Cargo.toml

Add `strip = "debuginfo"` to the release profile:
```toml
[package]
name = "move_maker"
version = "0.1.0"
rust-version = "1.90.0"
edition = "2024"
license = "Apache-2.0"

[dependencies]
hcl-rs = "0.19.4"
clap = { version = "4.5", features = ["derive"] }
env_logger = "0.11"
anyhow = "1.0"

[dev-dependencies]
tempfile = "3.10"
pretty_assertions = "1.4"

[profile.release]
strip = "debuginfo"  # Strip debug symbols, preserve custom linker sections (e.g., cargo-auditable data)
```

### Workflow

Remove the manual strip step:
```yaml
- name: Build release binary with embedded dependency info
  run: cargo auditable build --release --target ${{ matrix.target }}

- name: Audit release binary
  run: cargo audit bin target/${{ matrix.target }}/release/move_maker

# Strip step removed - handled by Cargo.toml profile.release.strip
```

## Impact

### Security Impact
- **Severity**: Medium
- **Priority**: Medium-High

- **Loss of audit capability**: Released binaries may not be auditable by end users
- **Supply chain security**: Users cannot verify dependencies in production binaries
- **Defeats purpose of cargo-auditable**: The embedded dependency information is lost

### Code Quality Impact
- **Severity**: Low-Medium
- **Priority**: Medium

- **Inconsistent configuration**: Build settings should be in `Cargo.toml`, not workflows
- **OS-specific logic**: Unnecessary conditional handling
- **Maintainability**: Harder to test and verify locally


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_BUILD_STRIP_CARGO_TOML.md` for the detailed implementation plan.
