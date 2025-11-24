# Implementation Plan: BUG_GITHUB_WORKFLOWS_RUST_VERSION

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_GITHUB_WORKFLOWS_RUST_VERSION.md`.

## Context

Related bug report: `plan/25W46/BUG_GITHUB_WORKFLOWS_RUST_VERSION.md`

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/pull_request.yaml`

**File:** `.github/workflows/pull_request.yaml`

1. **Update `security` job (line 15)**
   - [x] Locate the step at line 15
   - [x] Replace:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
     ```
   - [x] With:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
       with:
         toolchain: 1.90.0
     ```
   - [x] Verify step placement (should be after checkout, before security tool installation)

2. **Update `test` job (line 43)**
   - [x] Locate the step at line 43
   - [x] Replace:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
     ```
   - [x] With:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
       with:
         toolchain: 1.90.0
     ```
   - [x] Verify step placement (should be after checkout, before cargo-nextest installation)

3. **Update `coverage` job (line 68)**
   - [x] Locate the step at line 68
   - [x] Replace:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
       with:
         components: llvm-tools-preview
     ```
   - [x] With:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
       with:
         toolchain: 1.90.0
         components: llvm-tools-preview
     ```
   - [x] Verify step placement (should be after checkout, before cargo-nextest installation)
   - [x] Ensure `components: llvm-tools-preview` is preserved

4. **Update `pre-commit` job (line 135)**
   - [x] Locate the step at line 135
   - [x] Replace:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
     ```
   - [x] With:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
       with:
         toolchain: 1.90.0
     ```
   - [x] Verify step placement (should be after Python setup, before pre-commit installation)

#### Step 2: Update `.github/workflows/release.yaml`

**File:** `.github/workflows/release.yaml`

1. **Update `security` job (line 16)**
   - [x] Locate the step at line 16
   - [x] Replace:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
     ```
   - [x] With:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
       with:
         toolchain: 1.90.0
     ```
   - [x] Verify step placement (should be after checkout, before security tool installation)

2. **Update `build-and-release` job (line 165)**
   - [x] Locate the step at line 165
   - [x] Replace:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
       with:
         targets: ${{ matrix.target }}
     ```
   - [x] With:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
       with:
         toolchain: 1.90.0
         targets: ${{ matrix.target }}
     ```
   - [x] Verify step placement (should be after Cargo.toml version update, before cargo-nextest installation)
   - [x] Ensure `targets: ${{ matrix.target }}` is preserved

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to affected workflow files
   - Remove `toolchain: 1.90.0` parameter from all `dtolnay/rust-toolchain` usages
   - Verify workflows return to working state

2. **Partial Rollback**
   - If only specific jobs fail, revert only those changes
   - Investigate why specific jobs fail with Rust 1.90.0
   - Consider job-specific solutions or version adjustments

3. **Alternative Approach**
   - If Rust 1.90.0 is not available or causes issues, consider:
     - Using the latest available stable version that matches or exceeds 1.90.0
     - Verifying Rust 1.90.0 availability in the action
     - Checking if `rust-version` in `Cargo.toml` needs adjustment

### Implementation Order

1. Start with `.github/workflows/pull_request.yaml` (lower risk, easier to test)
2. Test via pull request to verify all jobs work with Rust 1.90.0
3. Once verified, update `.github/workflows/release.yaml`
4. Test release workflow (can be done via test branch or after merge)

### Risk Assessment

- **Risk Level:** Medium
- **Impact if Failed:** Workflows would fail if Rust 1.90.0 is not available or incompatible with dependencies
- **Mitigation:** Easy rollback, can test via pull request before affecting main branch
- **Testing:** Can be fully tested via pull request before affecting main branch
- **Dependencies:** Ensure Rust 1.90.0 is available in `dtolnay/rust-toolchain` action

## Status

✅ **FIXED** - All workflows now specify `toolchain: 1.90.0` to match `Cargo.toml` rust-version
