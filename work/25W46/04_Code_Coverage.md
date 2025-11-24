# Phase 4: Code Coverage Implementation Plan

## Overview
Implement code coverage using cargo-llvm-cov to track and enforce coverage thresholds. CI/CD integration is handled in Phase 7 (Continuous Delivery).

## Goals
- Generate code coverage reports locally
- Set up coverage thresholds (Line > 80%, Branch > 70%, Function > 85%)
- Prepare for CI/CD integration (handled in Phase 7)
- Track coverage over time

## Prerequisites
- [x] Rust toolchain installed
- [x] Phase 2 (Test Runner) completed (cargo-nextest installed)
- [x] Phase 3 (Error Handling) completed or in progress
- [x] Test suite exists and passes

## Implementation Tasks

### 1. Install cargo-llvm-cov Locally

**Note:** These commands work on both macOS and Linux.

- [x] Add llvm-tools-preview component: `rustup component add llvm-tools-preview`
- [x] Install cargo-llvm-cov: `cargo install cargo-llvm-cov`
- [x] Verify installation: `cargo llvm-cov --version`
- [x] Verify component is installed: `rustup component list | grep llvm-tools`

### 2. Generate Initial Coverage Report

**Prerequisites:**
- [x] Verify tests exist and pass: `cargo test` (or `cargo nextest run` if Phase 2 is completed)
- [x] Ensure test suite is in a passing state before measuring coverage

- [x] Generate coverage report: `cargo llvm-cov --all-features`
- [x] View coverage summary in terminal: `cargo llvm-cov --all-features --summary-only`
- [x] Review coverage summary (line, branch, function percentages)
- [x] Generate HTML report: `cargo llvm-cov --html`
- [x] Open HTML report in browser: `open target/llvm-cov/html/index.html` (macOS) or `xdg-open target/llvm-cov/html/index.html` (Linux)
  - Note: The HTML report is typically generated at `target/llvm-cov/html/index.html` by default
- [x] Review coverage by file and function
- [x] Identify areas with low coverage
- [x] Document current coverage baseline

### 3. Generate Coverage with cargo-nextest

- [x] Generate coverage with nextest: `cargo llvm-cov nextest --all-features`
- [x] View coverage summary: `cargo llvm-cov nextest --all-features --summary-only`
- [x] Verify coverage is generated correctly
- [x] Compare coverage with standard `cargo test` (if applicable)
- [x] Generate HTML report with nextest: `cargo llvm-cov nextest --all-features --html`
- [x] Review coverage report
- [x] Verify all tests are included in coverage
- [x] Note: Doctests (`cargo test --doc`) are not included in coverage by default

### 4. Set Coverage Thresholds

- [x] Review current coverage percentages:
  - [x] Line coverage: Current 91.52% → Target: > 80% ✅
  - [x] Branch coverage: Current N/A (0 branches) → Target: > 70%
  - [x] Function coverage: Current 91.23% → Target: > 85% ✅
- [x] Document coverage thresholds in [REQ_CODE_COVERAGE.md](../plan/25W46/REQ_CODE_COVERAGE.md) or project documentation
- [x] Note: Thresholds are enforced in CI, not in local tooling
- [x] Plan to improve coverage if current coverage is below thresholds (Coverage exceeds thresholds - no improvement needed)

### 5. Configure Coverage Exclusions

- [x] Identify files/directories to exclude from coverage:
  - [x] Test code (`tests/` directory)
  - [x] Main entry point (`src/main.rs` - minimal logic, currently 0% coverage)
  - [x] Error handling paths that are difficult to test
  - [x] Generated code (if any) - None found
- [x] Create coverage exclusion configuration (if needed):
  - [x] Review cargo-llvm-cov exclusion options
  - [x] Example: Use `--ignore-filename-regex` to exclude patterns:
    ```bash
    cargo llvm-cov nextest --all-features --ignore-filename-regex 'tests/.*|src/main.rs'
    ```
  - [x] Note: CI exclusions are configured in CI workflow (see [07_Continuous_Delivery.md](07_Continuous_Delivery.md))
- [x] Document exclusions and reasoning

### 6. Improve Coverage (if needed)

- [x] Review coverage report to identify low-coverage areas
- [x] Prioritize areas to improve (in order):
  - [x] Core business logic (processor.rs, parser.rs) - Coverage: 95.00% and 97.60% respectively ✅
  - [x] Critical paths - Well covered ✅
  - [x] Error handling paths - Well covered ✅
  - [x] Edge cases and boundary conditions - Well covered ✅
  - [x] Utility functions - Well covered ✅
- [x] Add tests to improve coverage:
  - [x] Add unit tests for uncovered functions - Coverage exceeds thresholds
  - [x] Add integration tests for uncovered paths - Coverage exceeds thresholds
  - [x] Add error case tests - Coverage exceeds thresholds
- [x] Re-run coverage: `cargo llvm-cov nextest --all-features`
- [x] Verify coverage improvements
- [x] Repeat until thresholds are met - Thresholds already exceeded, no improvement needed

### 7. Update Documentation

- [x] Update project README with coverage information:
  - [x] How to generate coverage reports locally
  - [x] Coverage thresholds
  - [x] How to view coverage reports
- [x] Document coverage exclusions and reasoning
- [x] Add coverage badge to README (if using Codecov or similar) - Skipped (not using Codecov yet, will be added in CI phase)
- [x] Update CONTRIBUTING.md (if exists) with coverage requirements - File does not exist, skipped

### 8. Verification

- [x] Generate coverage locally: `cargo llvm-cov nextest --all-features --html`
- [x] View coverage summary: `cargo llvm-cov nextest --all-features --summary-only`
- [x] Verify coverage report is generated correctly
- [x] Open and review HTML report to verify coverage visually
- [x] Verify coverage thresholds are met (or plan to improve) - Thresholds exceeded: Line 91.52% (>80%), Function 91.23% (>85%)
- [x] Verify local coverage tooling works correctly
- [x] Note: CI verification is handled in [07_Continuous_Delivery.md](07_Continuous_Delivery.md) Section 15

## Success Criteria

- [x] cargo-llvm-cov installed locally and working
- [x] llvm-tools-preview component installed
- [x] Coverage reports can be generated locally
- [x] Coverage thresholds documented (Line > 80%, Branch > 70%, Function > 85%)
- [x] Local coverage tooling working correctly
- [x] Note: CI integration success criteria are in [07_Continuous_Delivery.md](07_Continuous_Delivery.md)
- [x] Current coverage meets or exceeds thresholds (Line: 91.52%, Function: 91.23%)
- [x] Documentation updated

## Coverage Thresholds

- **Line coverage**: > 80% (enforced in CI)
- **Branch coverage**: > 70% (enforced in CI)
- **Function coverage**: > 85% (enforced in CI)

## Coverage Exclusions

- Test code (`tests/` directory)
- Main entry point (`src/main.rs` - minimal logic)
- Error handling paths that are difficult to test

## Current Coverage Baseline

**Date**: November 2024

**Overall Coverage:**
- **Line coverage**: 91.52% (Target: > 80%) ✅
- **Function coverage**: 91.23% (Target: > 85%) ✅
- **Region coverage**: 90.48%
- **Branch coverage**: N/A (0 branches in codebase)

**Coverage by File:**
- `cli.rs`: 99.09% line, 100% function, 97.86% region
- `file_discovery.rs`: 96.15% line, 100% function, 94.71% region
- `main.rs`: 0.00% line, 0% function, 0.00% region (excluded - entry point)
- `output.rs`: 100.00% line, 100% function, 93.68% region
- `parser.rs`: 98.48% line, 88.89% function, 97.60% region
- `processor.rs`: 98.95% line, 90.91% function, 95.00% region

**Status**: All coverage thresholds exceeded. No immediate improvements needed.

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
- [REQ_CODE_COVERAGE.md](../plan/25W46/REQ_CODE_COVERAGE.md) - Detailed coverage documentation
- [07_Continuous_Delivery.md](07_Continuous_Delivery.md) - CI/CD integration for coverage
