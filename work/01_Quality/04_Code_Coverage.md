# Phase 4: Code Coverage Implementation Plan

## Overview
Implement code coverage using cargo-llvm-cov to track and enforce coverage thresholds. CI/CD integration is handled in Phase 7 (Continuous Delivery).

## Goals
- Generate code coverage reports locally
- Set up coverage thresholds (Line > 80%, Branch > 70%, Function > 85%)
- Prepare for CI/CD integration (handled in Phase 7)
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

**Prerequisites:**
- [ ] Verify tests exist and pass: `cargo test` (or `cargo nextest run` if Phase 2 is completed)
- [ ] Ensure test suite is in a passing state before measuring coverage

- [ ] Generate coverage report: `cargo llvm-cov --all-features`
- [ ] View coverage summary in terminal: `cargo llvm-cov --all-features --summary-only`
- [ ] Review coverage summary (line, branch, function percentages)
- [ ] Generate HTML report: `cargo llvm-cov --html`
- [ ] Open HTML report in browser: `open target/llvm-cov/html/index.html` (macOS) or `xdg-open target/llvm-cov/html/index.html` (Linux)
  - Note: The HTML report is typically generated at `target/llvm-cov/html/index.html` by default
- [ ] Review coverage by file and function
- [ ] Identify areas with low coverage
- [ ] Document current coverage baseline

### 3. Generate Coverage with cargo-nextest

- [ ] Generate coverage with nextest: `cargo llvm-cov nextest --all-features`
- [ ] View coverage summary: `cargo llvm-cov nextest --all-features --summary-only`
- [ ] Verify coverage is generated correctly
- [ ] Compare coverage with standard `cargo test` (if applicable)
- [ ] Generate HTML report with nextest: `cargo llvm-cov nextest --all-features --html`
- [ ] Review coverage report
- [ ] Verify all tests are included in coverage
- [ ] Note: Doctests (`cargo test --doc`) are not included in coverage by default

### 4. Set Coverage Thresholds

- [ ] Review current coverage percentages:
  - [ ] Line coverage: Current % → Target: > 80%
  - [ ] Branch coverage: Current % → Target: > 70%
  - [ ] Function coverage: Current % → Target: > 85%
- [ ] Document coverage thresholds in [CODE_COVERAGE.md](../plan/01_Quality/CODE_COVERAGE.md) or project documentation
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
  - [ ] Example: Use `--ignore-filename-regex` to exclude patterns:
    ```bash
    cargo llvm-cov nextest --all-features --ignore-filename-regex 'tests/.*|src/main.rs'
    ```
  - [ ] Note: CI exclusions are configured in CI workflow (see [07_Continuous_Delivery.md](07_Continuous_Delivery.md))
- [ ] Document exclusions and reasoning

### 6. Improve Coverage (if needed)

- [ ] Review coverage report to identify low-coverage areas
- [ ] Prioritize areas to improve (in order):
  - [ ] Core business logic (processor.rs, parser.rs)
  - [ ] Critical paths
  - [ ] Error handling paths
  - [ ] Edge cases and boundary conditions
  - [ ] Utility functions
- [ ] Add tests to improve coverage:
  - [ ] Add unit tests for uncovered functions
  - [ ] Add integration tests for uncovered paths
  - [ ] Add error case tests
- [ ] Re-run coverage: `cargo llvm-cov nextest --all-features`
- [ ] Verify coverage improvements
- [ ] Repeat until thresholds are met

### 7. Update Documentation

- [ ] Update project README with coverage information:
  - [ ] How to generate coverage reports locally
  - [ ] Coverage thresholds
  - [ ] How to view coverage reports
- [ ] Document coverage exclusions and reasoning
- [ ] Add coverage badge to README (if using Codecov or similar)
- [ ] Update CONTRIBUTING.md (if exists) with coverage requirements

### 8. Verification

- [ ] Generate coverage locally: `cargo llvm-cov nextest --all-features --html`
- [ ] View coverage summary: `cargo llvm-cov nextest --all-features --summary-only`
- [ ] Verify coverage report is generated correctly
- [ ] Open and review HTML report to verify coverage visually
- [ ] Verify coverage thresholds are met (or plan to improve)
- [ ] Verify local coverage tooling works correctly
- [ ] Note: CI verification is handled in [07_Continuous_Delivery.md](07_Continuous_Delivery.md) Section 15

## Success Criteria

- [ ] cargo-llvm-cov installed locally and working
- [ ] llvm-tools-preview component installed
- [ ] Coverage reports can be generated locally
- [ ] Coverage thresholds documented (Line > 80%, Branch > 70%, Function > 85%)
- [ ] Local coverage tooling working correctly
- [ ] Note: CI integration success criteria are in [07_Continuous_Delivery.md](07_Continuous_Delivery.md)
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

## Troubleshooting

### Coverage Report Not Generated
- Verify llvm-tools-preview is installed: `rustup component list | grep llvm-tools`
- Reinstall if needed: `rustup component add llvm-tools-preview`
- Check that tests pass: `cargo nextest run`
- Verify cargo-llvm-cov is installed: `cargo llvm-cov --version`

### Coverage Percentages Seem Incorrect
- Verify exclusions are working: Check that test files are excluded
- Review HTML report to see which lines are covered
- Ensure all tests are running: `cargo nextest list`
- Check that coverage is generated with the same test command you use normally

### HTML Report Not Opening
- Verify report path: Check cargo-llvm-cov output for exact location
- Try absolute path: `open $(pwd)/target/llvm-cov/html/index.html` (macOS) or `xdg-open $(pwd)/target/llvm-cov/html/index.html` (Linux)
- Check that HTML report was actually generated (look for output messages)

### Coverage Generation is Slow
- This is normal; coverage collection adds overhead to test execution
- Consider using `--summary-only` for quick checks
- HTML reports can be large; generation may take time

## Notes

- Coverage thresholds should be adjusted upward over time, not downward
- Use `cargo llvm-cov nextest` for integration with cargo-nextest
- LCOV format is standard for CI/CD integration
- HTML reports are useful for local development
- Use `--summary-only` for quick coverage checks without generating full reports
- Coverage thresholds are enforced in CI, not in local tooling
- Coverage generation may take longer than regular test runs
- CI/CD integration is handled in Phase 7 (Continuous Delivery) - see [07_Continuous_Delivery.md](07_Continuous_Delivery.md)

## References

- [cargo-llvm-cov Documentation](https://github.com/taiki-e/cargo-llvm-cov)
- [Codecov Documentation](https://docs.codecov.com/)
- [CODE_COVERAGE.md](../plan/01_Quality/CODE_COVERAGE.md) - Detailed coverage documentation
- [07_Continuous_Delivery.md](07_Continuous_Delivery.md) - CI/CD integration for coverage

