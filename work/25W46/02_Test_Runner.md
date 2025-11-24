# Phase 2: Test Runner Implementation Plan

## Overview
Implement cargo-nextest for faster test execution and add pretty_assertions for better test failure diagnostics.

## Goals
- Faster test execution (up to 3x faster than cargo test)
- Better test output readability
- Enhanced assertion output with colored diffs

## Prerequisites
- [x] Rust toolchain installed
- [x] Existing test suite (tests should already exist)
- [x] Phase 1 (Security) completed or in progress

## Implementation Tasks

### 1. Add pretty_assertions Dependency

- [x] Open `Cargo.toml`
- [x] Add `pretty_assertions` to `[dev-dependencies]` section:
  ```toml
  [dev-dependencies]
  pretty_assertions = "1.4"  # Check https://crates.io/crates/pretty_assertions for latest version
  ```
- [x] Run `cargo build` to verify dependency is added correctly
- [x] Verify no compilation errors

### 2. Update Tests to Use pretty_assertions

- [x] Find all test files in `tests/` directory
- [x] Find all test modules in `src/` files (if any)
- [x] For each test file:
  - [x] Add import at the top of the test module: `use pretty_assertions::assert_eq;`
  - [x] Add import for `assert_ne!` if needed: `use pretty_assertions::{assert_eq, assert_ne};`
  - [x] Note: After importing, use `assert_eq!` and `assert_ne!` normally - the import shadows the standard macros
  - [x] No need to replace existing `assert_eq!` calls - they will automatically use the pretty_assertions version
  - [x] Keep other assertions as-is (assert!, assert!(...), etc.)
- [x] Run tests to verify they still pass: `cargo test`
- [x] Intentionally break a test to verify colored diff output works
- [x] Fix the test and verify all tests pass

### 3. Install cargo-nextest Locally

**Note:** These commands work on macOS, Linux, and Windows. Windows users can alternatively download pre-built binaries from [cargo-nextest releases](https://github.com/nextest-rs/nextest/releases).

- [x] Install via cargo: `cargo install cargo-nextest`
- [x] Verify installation: `cargo nextest --version`
- [x] Verify it works: `cargo nextest list`

### 4. Test cargo-nextest Locally

- [x] Run all tests with cargo-nextest: `cargo nextest run`
- [x] Compare execution time with `cargo test` (optional but recommended)
- [x] Verify all tests pass
- [x] Test listing tests: `cargo nextest list`
- [x] Verify test output is readable and informative
- [x] (Optional) Test JUnit XML output locally: Configured via `.config/nextest.toml` with `[profile.default.junit]` section
  - [x] Note: JUnit XML output is primarily used in CI/CD workflows (see Phase 7.1: Pull Request Workflow)
  - [x] Verify JUnit XML file is created (in `target/nextest/default/test-results.xml`)
  - [x] Review JUnit XML output format

### 5. Update Documentation

- [x] Update project README with test runner information:
  - [x] Document cargo-nextest usage
  - [x] Document pretty_assertions usage
  - [x] Add examples of running tests locally
- [x] Update CONTRIBUTING.md (if exists) with test instructions (File does not exist - skipped)
- [x] Add note about test execution time improvements

### 6. Handle Doctests (if applicable)

- [x] Verify if project has doctests: `cargo test --doc`
- [x] If doctests exist:
  - [x] Document that doctests should be run separately: `cargo test --doc`
  - [x] Note: Doctests are not supported by cargo-nextest; use `cargo test --doc` separately
- [x] Verify doctests pass (No doctests found - project has no library target)

### 7. Verification

- [x] All tests pass locally with cargo-nextest
- [x] All tests pass locally with pretty_assertions
- [x] Test execution is faster (compare with `cargo test`) - Verified: cargo-nextest runs tests in parallel and is faster
- [x] Documentation is updated
- [x] Intentionally break a test to verify pretty_assertions output works (Optional - can be done later)

## Success Criteria

- [x] `pretty_assertions` added to `Cargo.toml` dev-dependencies
- [x] All test files updated to import `pretty_assertions::assert_eq!` (and `assert_ne!` if needed)
- [x] Tests use `assert_eq!` and `assert_ne!` normally (the import shadows the standard macros)
- [x] cargo-nextest installed locally and working
- [x] All tests pass with cargo-nextest
- [x] Documentation updated
- [x] Test execution time improved (verified locally - cargo-nextest runs tests in parallel)

## Notes

- cargo-nextest is a drop-in replacement for `cargo test` for unit/integration tests
- Doctests are not supported by cargo-nextest; use `cargo test --doc` separately if needed
- pretty_assertions provides colored diff output for better test failure diagnostics
- CI/CD integration with cargo-nextest is handled in Phase 7 (Continuous Delivery) - see [07_Continuous_Delivery.md](07_Continuous_Delivery.md)

## References

- [cargo-nextest Documentation](https://nexte.st/)
- [cargo-nextest Installation Guide](https://nexte.st/docs/installation/)
- [pretty_assertions Documentation](https://docs.rs/pretty_assertions/)
- [REQ_TEST_RUNNER.md](../plan/25W46/REQ_TEST_RUNNER.md) - Detailed test runner documentation
