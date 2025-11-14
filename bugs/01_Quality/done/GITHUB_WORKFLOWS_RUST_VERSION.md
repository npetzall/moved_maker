# Bug: GitHub Actions workflows missing Rust toolchain version specification

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
