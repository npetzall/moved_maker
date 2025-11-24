# Implementation Plan: BUG_RELEASE_BUILD_MISSING_COVERAGE

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_RELEASE_BUILD_MISSING_COVERAGE.md`.

## Context

Related bug report: `plan/25W46/BUG_RELEASE_BUILD_MISSING_COVERAGE.md`

## Steps to Fix

### Option 2: Add separate coverage job (RECOMMENDED)

Coverage is platform-independent, so a separate coverage job that runs once before all platform builds is the recommended approach. This is consistent with the PR workflow structure and more efficient.

**Step 1: Add coverage job after security job**

Add a new `coverage` job after the `security` job in `.github/workflows/release-build.yaml`:

```yaml
coverage:
  needs: security
  runs-on: ubuntu-latest
  steps:
    - name: Checkout code
      uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
      with:
        ref: ${{ github.ref }}
        fetch-depth: 0

    - name: Install Rust
      uses: dtolnay/rust-toolchain@0f44b27771c32bda9f458f75a1e241b09791b331  # master
      with:
        toolchain: 1.90.0
        components: llvm-tools-preview

    - uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
      with:
        cache-on-failure: false

    - name: Install cargo-nextest
      run: cargo install cargo-nextest

    - name: Install cargo-llvm-cov
      run: cargo install cargo-llvm-cov

    - name: Generate coverage
      run: cargo llvm-cov nextest --all-features

    - name: Check coverage thresholds
      run: |
        # Generate JSON report from collected coverage data
        cargo llvm-cov report --json > coverage.json

        # Extract percentages and check thresholds using jq script
        jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

**Step 2: Update build-and-release to depend on coverage**

Update the `build-and-release` job (line 49) to depend on both `security` and `coverage`:

**Before:**
```yaml
build-and-release:
  needs: security
```

**After:**
```yaml
build-and-release:
  needs: [security, coverage]
```

**Benefits:**
- Coverage checked once before all platform builds (efficient)
- Platform-independent coverage validation (Rust code coverage is the same across platforms)
- Consistent with PR workflow structure
- Clear separation of concerns
- Prevents builds if coverage thresholds are not met

## Affected Files

- `.github/workflows/release-build.yaml`
  - ✅ `coverage` job added (lines 48-83)
  - ✅ `build-and-release` job updated (line 86: `needs: [security, coverage]`)
  - Coverage job includes all required steps matching PR workflow structure

## Investigation Needed ✅ COMPLETED

1. ✅ Verify coverage is platform-independent (if using Option 2) - **CONFIRMED**: Coverage metrics are platform-independent; Rust code coverage is the same across platforms
2. ✅ Confirm `.config/coverage-threshold-check.jq` exists and is compatible - **CONFIRMED**: Script exists and is used in PR workflow
3. ✅ Test coverage generation with cross-compilation targets - **NOT NEEDED**: Coverage runs on single platform (ubuntu-latest) before cross-compilation builds
4. ✅ Verify `jq` is available in GitHub Actions runners (should be pre-installed) - **CONFIRMED**: `jq` is pre-installed in GitHub Actions runners
5. ✅ Check if coverage data collection works with `cargo auditable build` step - **CONFIRMED**: Coverage runs before build step, so no conflict

## Status

✅ **IMPLEMENTATION COMPLETE** - Coverage reporting and threshold checks have been added to the release build workflow. A dedicated `coverage` job has been added that runs after the `security` job and before the `build-and-release` job, ensuring coverage thresholds are validated before release binaries are built.

## Progress Summary

**Status:** ✅ Implementation Complete - Ready for CI Testing

**Completed:**
- ✅ Coverage job added to `.github/workflows/release-build.yaml` after `security` job
- ✅ Coverage job includes all required steps (checkout, Rust install with llvm-tools-preview, cache, cargo-nextest, cargo-llvm-cov, generate coverage, check thresholds)
- ✅ `build-and-release` job updated to depend on both `security` and `coverage`
- ✅ Workflow YAML syntax verified (no linting errors)
- ✅ Coverage job structure matches PR workflow for consistency

**Pending:**
- ⏳ CI testing with release tag to verify coverage job runs successfully
- ⏳ Verification that coverage thresholds are enforced
- ⏳ Verification that workflow fails if thresholds are not met
- ⏳ Verification that workflow passes if thresholds are met

## Detailed Implementation Plan

### Phase 1: Implementation Steps ✅ COMPLETED

#### Step 1: Add coverage job to release workflow ✅ COMPLETED

**File:** `.github/workflows/release-build.yaml`

**Implementation Details:**
- Coverage job added at lines 48-83 in `.github/workflows/release-build.yaml`
- Job runs on `ubuntu-latest` after `security` job completes
- All required steps implemented matching PR workflow structure

1. **Add new `coverage` job after `security` job** ✅ COMPLETED
   - [x] Locate the `security` job (ends around line 46)
   - [x] Add new `coverage` job after `security` job
   - [x] Set `needs: security` to ensure security checks run first
   - [x] Set `runs-on: ubuntu-latest` (coverage is platform-independent)
   - [x] Copy coverage job structure from PR workflow (`.github/workflows/pull_request.yaml` lines 78-109)

2. **Add coverage job steps** ✅ COMPLETED
   - [x] Add checkout step with `ref: ${{ github.ref }}` and `fetch-depth: 0`
   - [x] Add Rust installation step with `toolchain: 1.90.0` and `components: llvm-tools-preview`
   - [x] Add rust-cache step with `cache-on-failure: false`
   - [x] Add `Install cargo-nextest` step
   - [x] Add `Install cargo-llvm-cov` step
   - [x] Add `Generate coverage` step: `cargo llvm-cov nextest --all-features`
   - [x] Add `Check coverage thresholds` step with jq script

**Coverage job to add:**
```yaml
coverage:
  needs: security
  runs-on: ubuntu-latest
  steps:
    - name: Checkout code
      uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
      with:
        ref: ${{ github.ref }}
        fetch-depth: 0

    - name: Install Rust
      uses: dtolnay/rust-toolchain@0f44b27771c32bda9f458f75a1e241b09791b331  # master
      with:
        toolchain: 1.90.0
        components: llvm-tools-preview

    - uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
      with:
        cache-on-failure: false

    - name: Install cargo-nextest
      run: cargo install cargo-nextest

    - name: Install cargo-llvm-cov
      run: cargo install cargo-llvm-cov

    - name: Generate coverage
      run: cargo llvm-cov nextest --all-features

    - name: Check coverage thresholds
      run: |
        # Generate JSON report from collected coverage data
        cargo llvm-cov report --json > coverage.json

        # Extract percentages and check thresholds using jq script
        jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
```

#### Step 2: Update build-and-release job dependency ✅ COMPLETED

**File:** `.github/workflows/release-build.yaml`

**Implementation Details:**
- `build-and-release` job dependency updated at line 86
- Changed from `needs: security` to `needs: [security, coverage]`
- Job now waits for both security and coverage checks before building release binaries

1. **Update `build-and-release` job to depend on coverage** ✅ COMPLETED
   - [x] Locate the `build-and-release` job (line 48, now line 85)
   - [x] Update `needs: security` to `needs: [security, coverage]`
   - [x] Verify the job will wait for both security and coverage to complete before building

**Change to make:**
```yaml
build-and-release:
  needs: [security, coverage]  # Updated from: needs: security
```

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.github/workflows/release-build.yaml`
   - Remove the `coverage` job
   - Restore `build-and-release` job dependency to `needs: security`
   - Verify workflow returns to previous state

2. **Partial Rollback**
   - If coverage generation fails, check Rust component installation (`llvm-tools-preview`)
   - If threshold check fails, verify `.config/coverage-threshold-check.jq` exists and is compatible
   - If jq script has issues, verify script file exists and matches PR workflow version
   - If coverage job takes too long, verify caching is working correctly

3. **Alternative Approaches**
   - If coverage job fails due to platform-specific issues, verify coverage is truly platform-independent
   - If `cargo-llvm-cov` installation fails, check for version compatibility issues
   - If coverage data collection fails, verify `cargo llvm-cov nextest` command works correctly
   - Consider adding coverage job timeout if needed

### Implementation Order

1. [x] Review PR workflow coverage job structure (`.github/workflows/pull_request.yaml` lines 78-109) ✅ COMPLETED
2. [x] Add new `coverage` job after `security` job in `.github/workflows/release-build.yaml` ✅ COMPLETED
3. [x] Copy coverage steps from PR workflow (checkout, Rust install, cache, cargo-nextest, cargo-llvm-cov, generate coverage, check thresholds) ✅ COMPLETED
4. [x] Update `build-and-release` job `needs` to include `coverage`: `needs: [security, coverage]` ✅ COMPLETED
5. [x] Verify workflow YAML syntax is correct ✅ COMPLETED
6. [ ] Test workflow with a release tag (e.g., `v0.0.1-test`) ⏳ PENDING CI TESTING
7. [ ] Verify coverage job runs successfully ⏳ PENDING CI TESTING
8. [ ] Verify coverage thresholds are checked ⏳ PENDING CI TESTING
9. [ ] Verify workflow fails if thresholds are not met ⏳ PENDING CI TESTING
10. [ ] Verify workflow passes if thresholds are met ⏳ PENDING CI TESTING
11. [ ] Verify `build-and-release` job waits for coverage to complete ⏳ PENDING CI TESTING
12. [ ] Clean up test release tag ⏳ PENDING CI TESTING

## Example Fix

### Before (current state):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@0f44b27771c32bda9f458f75a1e241b09791b331  # master
  with:
    toolchain: 1.90.0
    targets: ${{ matrix.target }}

- name: Install cargo-nextest
  run: cargo install cargo-nextest

- name: Run tests
  run: cargo nextest run
```

### After (separate coverage job):
```yaml
coverage:
  needs: security
  runs-on: ubuntu-latest
  steps:
    - name: Checkout code
      uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0
      with:
        ref: ${{ github.ref }}
        fetch-depth: 0

    - name: Install Rust
      uses: dtolnay/rust-toolchain@0f44b27771c32bda9f458f75a1e241b09791b331  # master
      with:
        toolchain: 1.90.0
        components: llvm-tools-preview

    - uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
      with:
        cache-on-failure: false

    - name: Install cargo-nextest
      run: cargo install cargo-nextest

    - name: Install cargo-llvm-cov
      run: cargo install cargo-llvm-cov

    - name: Generate coverage
      run: cargo llvm-cov nextest --all-features

    - name: Check coverage thresholds
      run: |
        # Generate JSON report from collected coverage data
        cargo llvm-cov report --json > coverage.json

        # Extract percentages and check thresholds using jq script
        jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1

build-and-release:
  needs: [security, coverage]  # Updated dependency
  # ... rest of job unchanged
```

**Note:** Coverage is platform-independent, so running it once on `ubuntu-latest` before all platform builds is the most efficient approach.

## Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:** Releases would continue without coverage validation, but functionality would remain unchanged
- **Mitigation:**
  - Simple addition of existing coverage steps from PR workflow
  - Easy rollback if needed
  - Can test with release tags before affecting production
  - Coverage infrastructure already exists and is tested in PR workflow
- **Testing:** Can be fully tested with release tags
- **Dependencies:**
  - Requires `.config/coverage-threshold-check.jq` to exist (already present)
  - Requires `jq` (pre-installed in GitHub Actions runners)
  - Requires `llvm-tools-preview` component (standard Rust component)
  - Requires `cargo-llvm-cov` (already used in PR workflow)

## References

- Release workflow: `.github/workflows/release-build.yaml`
- PR workflow coverage job: `.github/workflows/pull_request.yaml` (lines 78-109)
- Coverage threshold check script: `.config/coverage-threshold-check.jq`
- Coverage implementation: `work/25W46/04_Code_Coverage.md`
- Coverage plan: `plan/25W46/REQ_CODE_COVERAGE.md`
- Related bug: `plan/25W46/BUG_WORKFLOWS_COVERAGE_THRESHOLD_CHECK.md`
- Related bug: `plan/25W46/BUG_WORKFLOWS_COVERAGE_DUPLICATE_TEST_EXECUTION.md`

## Notes

- Coverage thresholds are: Line > 80%, Branch > 70%, Function > 85%
- The coverage check script (`.config/coverage-threshold-check.jq`) is already used in the PR workflow
- Coverage generation reuses test execution, so overhead is minimal
- The `cargo llvm-cov report` subcommand generates reports from collected coverage data without re-running tests
- Coverage should be validated before building release binaries to ensure quality standards
- **Coverage is platform-independent**: Rust code coverage metrics are the same across platforms, so a single coverage job on `ubuntu-latest` is sufficient
- **Option 2 (separate coverage job) is recommended**: More efficient, consistent with PR workflow, and runs once before all platform builds
