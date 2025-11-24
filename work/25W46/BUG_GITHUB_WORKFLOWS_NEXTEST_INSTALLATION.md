# Implementation Plan: BUG_GITHUB_WORKFLOWS_NEXTEST_INSTALLATION

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_GITHUB_WORKFLOWS_NEXTEST_INSTALLATION.md`.

## Context

Related bug report: `plan/25W46/BUG_GITHUB_WORKFLOWS_NEXTEST_INSTALLATION.md`

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/pull_request.yaml`

**File:** `.github/workflows/pull_request.yaml`

1. **Update `test` job (lines 45-46)**
   - [x] Locate the step at lines 45-46
   - [x] Replace:
     ```yaml
     - name: Install cargo-nextest
       uses: taiki-e/install-action@cargo-nextest
     ```
   - [x] With:
     ```yaml
     - name: Install cargo-nextest
       run: cargo install cargo-nextest
     ```
   - [x] Verify step placement (should be after Rust installation, before test execution)

2. **Update `coverage` job (lines 72-73)**
   - [x] Locate the step at lines 72-73
   - [x] Replace:
     ```yaml
     - name: Install cargo-nextest
       uses: taiki-e/install-action@cargo-nextest
     ```
   - [x] With:
     ```yaml
     - name: Install cargo-nextest
       run: cargo install cargo-nextest
     ```
   - [x] Verify step placement (should be after Rust installation with llvm-tools-preview, before cargo-llvm-cov installation)

3. **Update `pre-commit` job (lines 140-141)**
   - [x] Locate the step at lines 140-141
   - [x] Replace:
     ```yaml
     - name: Install cargo-nextest
       uses: taiki-e/install-action@cargo-nextest
     ```
   - [x] With:
     ```yaml
     - name: Install cargo-nextest
       run: cargo install cargo-nextest
     ```
   - [x] Verify step placement (should be after Rust installation, before pre-commit execution)

#### Step 2: Update `.github/workflows/release.yaml`

**File:** `.github/workflows/release.yaml`

1. **Update `build-and-release` job (lines 169-170)**
   - [x] Locate the step at lines 169-170
   - [x] Replace:
     ```yaml
     - name: Install cargo-nextest
       uses: taiki-e/install-action@cargo-nextest
     ```
   - [x] With:
     ```yaml
     - name: Install cargo-nextest
       run: cargo install cargo-nextest
     ```
   - [x] Verify step placement (should be after Rust installation with targets, before test execution)

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to affected workflow files
   - Restore `taiki-e/install-action@cargo-nextest` usage
   - Verify workflows return to working state

2. **Partial Rollback**
   - If only specific jobs fail, revert only those changes
   - Investigate why specific jobs fail
   - Consider job-specific solutions

3. **Alternative Approach**
   - If `cargo install` fails, consider:
     - Using `cargo install --locked cargo-nextest` for version stability
     - Adding `--version` flag to pin specific nextest version
     - Using `cargo binstall` if available

### Implementation Order

1. Start with `.github/workflows/pull_request.yaml` (lower risk, easier to test)
2. Test via pull request
3. Once verified, update `.github/workflows/release.yaml`
4. Test release workflow (can be done via test branch or after merge)

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:** Workflows would fail to install nextest, causing test failures
- **Mitigation:** Easy rollback, well-tested installation method
- **Testing:** Can be fully tested via pull request before affecting main branch
