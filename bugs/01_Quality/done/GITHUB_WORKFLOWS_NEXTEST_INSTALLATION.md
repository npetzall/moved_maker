# Bug: GitHub Actions workflows using incorrect nextest installation method

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
