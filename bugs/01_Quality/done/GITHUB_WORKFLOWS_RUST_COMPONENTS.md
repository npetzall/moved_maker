# Bug: GitHub Actions workflows missing required Rust components

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

## Steps to Fix

### For test job in `pull_request.yaml`:

Replace:
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
```

With:
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@1.90.0
  with:
    components: clippy rustfmt
```

### For pre-commit job in `pull_request.yaml`:

Replace:
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
```

With:
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@1.90.0
  with:
    components: clippy rustfmt
```

## Affected Files

- `.github/workflows/pull_request.yaml`
  - `test` job (lines 42-43)
  - `pre-commit` job (lines 134-135)

## Example Fix

### Before (test job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
```

### After (test job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@1.90.0
  with:
    components: clippy rustfmt
```

## References

- [dtolnay/rust-toolchain action documentation](https://github.com/dtolnay/rust-toolchain)

## Status

✅ **FIXED** - All test and pre-commit jobs now include `clippy` and `rustfmt` components

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/pull_request.yaml`

**File:** `.github/workflows/pull_request.yaml`

1. **Update `test` job (lines 44-48)**
   - [x] Locate the step at lines 44-48
   - [x] Replace:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
       with:
         toolchain: 1.90.0
     ```
   - [x] With:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
       with:
         toolchain: 1.90.0
         components: clippy rustfmt
     ```
   - [x] Verify step placement (should be after checkout, before cargo-nextest installation)
   - [x] Ensure `toolchain: 1.90.0` is preserved

2. **Update `pre-commit` job (lines 140-144)**
   - [x] Locate the step at lines 140-144
   - [x] Replace:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
       with:
         toolchain: 1.90.0
     ```
   - [x] With:
     ```yaml
     - name: Install Rust
       uses: dtolnay/rust-toolchain@stable
       with:
         toolchain: 1.90.0
         components: clippy rustfmt
     ```
   - [x] Verify step placement (should be after Python setup, before pre-commit installation)
   - [x] Ensure `toolchain: 1.90.0` is preserved

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to affected workflow files
   - Remove `components: clippy rustfmt` from Rust installation steps
   - Verify workflows return to working state

2. **Partial Rollback**
   - If only specific jobs fail, revert only those changes
   - Investigate why specific jobs fail with clippy/rustfmt components
   - Consider job-specific solutions or component adjustments

3. **Alternative Approach**
   - If components fail to install, consider:
     - Installing components separately using `rustup component add clippy rustfmt`
     - Verifying component availability for Rust 1.90.0
     - Using alternative installation methods if needed

### Implementation Order

1. Start with `.github/workflows/pull_request.yaml` `test` job (lower risk, easier to test)
2. Test via pull request to verify test job works with clippy and rustfmt components
3. Once verified, update `pre-commit` job
4. Test pre-commit job via pull request to verify pre-commit hooks work correctly
5. Verify all jobs pass before considering complete

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:** Workflows would fail if clippy/rustfmt components are not available for Rust 1.90.0, or if component installation causes issues
- **Mitigation:** Easy rollback, components are standard and well-supported, can test via pull request before affecting main branch
- **Testing:** Can be fully tested via pull request before affecting main branch
- **Dependencies:** Ensure clippy and rustfmt components are available for Rust 1.90.0 in the `dtolnay/rust-toolchain` action
