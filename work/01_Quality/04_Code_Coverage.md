# Phase 4: Code Coverage Implementation Plan

## Overview
Implement code coverage using cargo-llvm-cov to track and enforce coverage thresholds in CI/CD.

## Goals
- Generate code coverage reports
- Enforce coverage thresholds in CI (Line > 80%, Branch > 70%, Function > 85%)
- Integrate coverage reporting with CI/CD
- Track coverage over time

## Prerequisites
- [ ] Rust toolchain installed
- [ ] Phase 2 (Test Runner) completed (cargo-nextest installed)
- [ ] Phase 3 (Error Handling) completed or in progress
- [ ] Test suite exists and passes

## Implementation Tasks

### 1. Install cargo-llvm-cov Locally

#### Apple Silicon (macOS)
- [ ] Install via Homebrew: `brew install cargo-llvm-cov`
- [ ] Verify installation: `cargo llvm-cov --version`
- [ ] Add llvm-tools-preview component: `rustup component add llvm-tools-preview`
- [ ] Verify component is installed: `rustup component list | grep llvm-tools`

#### Linux
- [ ] Add llvm-tools-preview component: `rustup component add llvm-tools-preview`
- [ ] Install cargo-llvm-cov: `cargo install cargo-llvm-cov`
- [ ] Verify installation: `cargo llvm-cov --version`
- [ ] Verify component is installed: `rustup component list | grep llvm-tools`

### 2. Generate Initial Coverage Report

- [ ] Generate coverage report: `cargo llvm-cov --all-features`
- [ ] Review coverage summary (line, branch, function percentages)
- [ ] Generate HTML report: `cargo llvm-cov --html`
- [ ] Open HTML report in browser: `open target/llvm-cov/html/index.html` (macOS) or `xdg-open target/llvm-cov/html/index.html` (Linux)
- [ ] Review coverage by file and function
- [ ] Identify areas with low coverage
- [ ] Document current coverage baseline

### 3. Generate Coverage with cargo-nextest

- [ ] Generate coverage with nextest: `cargo llvm-cov nextest --all-features`
- [ ] Verify coverage is generated correctly
- [ ] Compare coverage with standard `cargo test` (if applicable)
- [ ] Generate HTML report with nextest: `cargo llvm-cov nextest --all-features --html`
- [ ] Review coverage report
- [ ] Verify all tests are included in coverage

### 4. Set Coverage Thresholds

- [ ] Review current coverage percentages:
  - [ ] Line coverage: Current % → Target: > 80%
  - [ ] Branch coverage: Current % → Target: > 70%
  - [ ] Function coverage: Current % → Target: > 85%
- [ ] Document coverage thresholds in `CODE_COVERAGE.md` (if exists) or project documentation
- [ ] Note: Thresholds are enforced in CI, not in local tooling
- [ ] Plan to improve coverage if current coverage is below thresholds

### 5. Configure Coverage Exclusions

- [ ] Identify files/directories to exclude from coverage:
  - [ ] Test code (`tests/` directory)
  - [ ] Main entry point (`src/main.rs` - minimal logic)
  - [ ] Error handling paths that are difficult to test
  - [ ] Generated code (if any)
- [ ] Create coverage exclusion configuration (if needed):
  - [ ] Review cargo-llvm-cov exclusion options
  - [ ] Configure exclusions in CI workflow (if needed)
- [ ] Document exclusions and reasoning

### 6. Generate LCOV Format for CI

- [ ] Generate LCOV format: `cargo llvm-cov nextest --all-features --lcov --output-path lcov.info`
- [ ] Verify `lcov.info` file is created
- [ ] Review LCOV file format
- [ ] Test LCOV file can be uploaded to coverage services (if applicable)

### 7. Integrate into CI Workflow

#### Pull Request Workflow (`.github/workflows/pull_request.yaml`)
- [ ] Open `.github/workflows/pull_request.yaml`
- [ ] Add coverage job:
  - [ ] Set runs-on: `ubuntu-latest`
  - [ ] Add checkout step
  - [ ] Add Rust installation with llvm-tools-preview:
    ```yaml
    - name: Install Rust
      uses: dtolnay/rust-toolchain@stable
      with:
        components: llvm-tools-preview
    ```
  - [ ] Add cargo-nextest installation step
  - [ ] Add cargo-llvm-cov installation step:
    ```yaml
    - name: Install cargo-llvm-cov
      run: cargo install cargo-llvm-cov
    ```
  - [ ] Add coverage generation step:
    ```yaml
    - name: Generate coverage
      run: cargo llvm-cov nextest --all-features --lcov --output-path lcov.info
    ```
  - [ ] Add coverage threshold check step:
    ```yaml
    - name: Check coverage thresholds
      run: |
        cargo llvm-cov nextest --all-features --summary-only
        # Extract coverage percentages and check against thresholds
        # Line > 80%, Branch > 70%, Function > 85%
        # CI will fail if thresholds not met
    ```
  - [ ] Add coverage upload step (optional, for Codecov or similar):
    ```yaml
    - name: Upload to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: lcov.info
        flags: unittests
        name: codecov-umbrella
    ```
- [ ] Verify workflow syntax
- [ ] Commit and push changes

### 8. Implement Coverage Threshold Enforcement

- [ ] Create script or workflow step to check coverage thresholds:
  - [ ] Extract coverage percentages from `cargo llvm-cov` output
  - [ ] Compare against thresholds (Line > 80%, Branch > 70%, Function > 85%)
  - [ ] Fail CI if thresholds not met
- [ ] Options for threshold checking:
  - [ ] Use `cargo llvm-cov --summary-only` and parse output
  - [ ] Use `cargo llvm-cov --json` and parse JSON
  - [ ] Use external tool or script
- [ ] Test threshold enforcement locally (if possible)
- [ ] Add threshold check to CI workflow
- [ ] Verify CI fails if thresholds are not met

### 9. Configure Coverage Service (Optional)

#### Codecov (Recommended)
- [ ] Sign up for Codecov account (if not already)
- [ ] Add repository to Codecov
- [ ] Get Codecov token (if required)
- [ ] Add Codecov upload step to CI workflow (already in step 7)
- [ ] Configure Codecov settings:
  - [ ] Set coverage thresholds
  - [ ] Configure coverage reports
  - [ ] Set up coverage badges (if desired)
- [ ] Verify coverage reports appear in Codecov

#### Alternative: Coveralls, Code Climate, etc.
- [ ] Choose coverage service
- [ ] Configure service
- [ ] Add upload step to CI workflow
- [ ] Verify coverage reports

### 10. Improve Coverage (if needed)

- [ ] Review coverage report to identify low-coverage areas
- [ ] Prioritize areas to improve:
  - [ ] Critical paths
  - [ ] Error handling paths
  - [ ] Edge cases
- [ ] Add tests to improve coverage:
  - [ ] Add unit tests for uncovered functions
  - [ ] Add integration tests for uncovered paths
  - [ ] Add error case tests
- [ ] Re-run coverage: `cargo llvm-cov nextest --all-features`
- [ ] Verify coverage improvements
- [ ] Repeat until thresholds are met

### 11. Update Documentation

- [ ] Update project README with coverage information:
  - [ ] How to generate coverage reports locally
  - [ ] Coverage thresholds
  - [ ] How to view coverage reports
- [ ] Document coverage exclusions and reasoning
- [ ] Add coverage badge to README (if using Codecov or similar)
- [ ] Update CONTRIBUTING.md (if exists) with coverage requirements

### 12. Verification

- [ ] Generate coverage locally: `cargo llvm-cov nextest --all-features --html`
- [ ] Verify coverage report is generated correctly
- [ ] Verify coverage thresholds are met (or plan to improve)
- [ ] Create test PR to verify CI coverage job runs
- [ ] Verify coverage job passes in CI
- [ ] Verify coverage thresholds are enforced in CI
- [ ] Verify coverage reports are uploaded (if using service)
- [ ] Review coverage trends over time

## Success Criteria

- [ ] cargo-llvm-cov installed locally and working
- [ ] llvm-tools-preview component installed
- [ ] Coverage reports can be generated locally
- [ ] Coverage thresholds documented (Line > 80%, Branch > 70%, Function > 85%)
- [ ] Coverage job added to CI workflow
- [ ] Coverage thresholds enforced in CI
- [ ] Coverage reports generated in CI
- [ ] Coverage service configured (if applicable)
- [ ] Current coverage meets or exceeds thresholds
- [ ] Documentation updated

## Coverage Thresholds

- **Line coverage**: > 80% (enforced in CI)
- **Branch coverage**: > 70% (enforced in CI)
- **Function coverage**: > 85% (enforced in CI)

## Coverage Exclusions

- Test code (`tests/` directory)
- Main entry point (`src/main.rs` - minimal logic)
- Error handling paths that are difficult to test

## Notes

- Coverage thresholds should be adjusted upward over time, not downward
- Use `cargo llvm-cov nextest` for integration with cargo-nextest
- LCOV format is standard for CI/CD integration
- HTML reports are useful for local development
- Coverage thresholds are enforced in CI, not in local tooling

## References

- [cargo-llvm-cov Documentation](https://github.com/taiki-e/cargo-llvm-cov)
- [Codecov Documentation](https://docs.codecov.com/)
- [CODE_COVERAGE.md](../plan/01_Quality/CODE_COVERAGE.md) - Detailed coverage documentation

