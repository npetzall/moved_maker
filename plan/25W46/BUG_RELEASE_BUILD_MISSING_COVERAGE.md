# BUG: Release build is missing coverage reporting/check

**Status**: ✅ Complete

## Description

The release build workflow (`.github/workflows/release-build.yaml`) runs tests but does not generate coverage reports or check coverage thresholds. This is inconsistent with the pull request workflow (`.github/workflows/pull_request.yaml`), which includes a dedicated `coverage` job that generates coverage reports and enforces coverage thresholds. Releases should also validate coverage to ensure code quality standards are maintained before creating release binaries.

## Current State

✅ **IMPLEMENTED** - The release build workflow now includes a dedicated `coverage` job that generates coverage reports and enforces coverage thresholds, consistent with the PR workflow.

**Current release workflow configuration:**

The `build-and-release` job in `.github/workflows/release-build.yaml` (lines 48-131) includes:
- Security checks (in separate `security` job)
- Test execution (line 89-90): `cargo nextest run`
- Binary building and auditing
- **Missing**: Coverage generation and threshold checking

**Current (missing) coverage steps:**
- No `llvm-tools-preview` component installation
- No `cargo-llvm-cov` installation
- No coverage generation step
- No coverage threshold check step

**Comparison with PR workflow:**

The PR workflow (`.github/workflows/pull_request.yaml`) includes a dedicated `coverage` job (lines 78-109) that:
- Installs `llvm-tools-preview` component
- Installs `cargo-llvm-cov`
- Generates coverage: `cargo llvm-cov nextest --all-features`
- Checks thresholds using `.config/coverage-threshold-check.jq`

The release workflow should have similar coverage validation to ensure releases meet quality standards.

## Expected State

The release build workflow should include coverage reporting and threshold checks similar to the PR workflow. Coverage validation should run before building release binaries to ensure code quality standards are maintained.

**Expected coverage steps in release workflow:**

1. **Install llvm-tools-preview component** (in Rust installation step)
2. **Install cargo-llvm-cov** (after cargo-nextest installation)
3. **Generate coverage** (after or alongside test execution)
4. **Check coverage thresholds** (using the same jq script as PR workflow)

**Recommended implementation (Option 2 - separate coverage job):**

Create a separate `coverage` job that runs before `build-and-release`, similar to the PR workflow structure. This approach is recommended because:
- Coverage is platform-independent (Rust code coverage metrics are the same across platforms)
- More efficient (runs once before all platform builds)
- Consistent with PR workflow structure
- Clear separation of concerns

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

**Benefits of coverage in release workflow:**
- Ensures releases meet quality standards
- Consistent quality checks between PR and release workflows
- Prevents releases with low coverage
- Provides coverage metrics for release artifacts
- Platform-independent coverage check runs once before all builds (efficient)

## Impact

### Quality Impact
- **Severity**: Medium
- **Priority**: Medium

**Current issues:**
- Releases can be created without validating coverage thresholds
- Inconsistent quality checks between PR and release workflows
- No coverage metrics available for release builds
- Potential for releases with low coverage to be distributed

**Benefits of adding coverage:**
- Consistent quality validation across all workflows
- Releases meet the same coverage standards as PRs
- Coverage metrics available for release artifacts
- Prevents low-coverage code from being released

### CI/CD Impact
- **Severity**: Low to Medium
- **Priority**: Medium

**Performance considerations:**
- Coverage generation adds minimal overhead (tests already run)
- Threshold check is fast (uses existing coverage data)
- Can reuse coverage data from test execution (using `cargo llvm-cov report`)

**Workflow structure:**
- Coverage can be added to existing `build-and-release` job (minimal changes)
- Or added as separate job before builds (more consistent with PR workflow)
- Either approach maintains workflow efficiency


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_BUILD_MISSING_COVERAGE.md` for the detailed implementation plan.
