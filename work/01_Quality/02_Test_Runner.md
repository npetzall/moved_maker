# Phase 2: Test Runner Implementation Plan

## Overview
Implement cargo-nextest for faster test execution and add pretty_assertions for better test failure diagnostics.

## Goals
- Faster test execution (up to 3x faster than cargo test)
- Better test output readability
- Enhanced assertion output with colored diffs

## Prerequisites
- [ ] Rust toolchain installed
- [ ] Existing test suite (tests should already exist)
- [ ] Phase 1 (Security) completed or in progress

## Implementation Tasks

### 1. Add pretty_assertions Dependency

- [ ] Open `Cargo.toml`
- [ ] Add `pretty_assertions` to `[dev-dependencies]` section:
  ```toml
  [dev-dependencies]
  pretty_assertions = "1.4"  # Check https://crates.io/crates/pretty_assertions for latest version
  ```
- [ ] Run `cargo build` to verify dependency is added correctly
- [ ] Verify no compilation errors

### 2. Update Tests to Use pretty_assertions

- [ ] Find all test files in `tests/` directory
- [ ] Find all test modules in `src/` files (if any)
- [ ] For each test file:
  - [ ] Add import at the top of the test module: `use pretty_assertions::assert_eq;`
  - [ ] Add import for `assert_ne!` if needed: `use pretty_assertions::{assert_eq, assert_ne};`
  - [ ] Note: After importing, use `assert_eq!` and `assert_ne!` normally - the import shadows the standard macros
  - [ ] No need to replace existing `assert_eq!` calls - they will automatically use the pretty_assertions version
  - [ ] Keep other assertions as-is (assert!, assert!(...), etc.)
- [ ] Run tests to verify they still pass: `cargo test`
- [ ] Intentionally break a test to verify colored diff output works
- [ ] Fix the test and verify all tests pass

### 3. Install cargo-nextest Locally

#### Apple Silicon (macOS)
- [ ] Install via Homebrew: `brew install cargo-nextest`
- [ ] Verify installation: `cargo nextest --version`
- [ ] Verify it works: `cargo nextest list`

#### Linux
- [ ] Install via cargo: `cargo install cargo-nextest`
- [ ] Note: GitHub Action `taiki-e/install-action@cargo-nextest` is for CI/CD workflows only, not for local installation
- [ ] Verify installation: `cargo nextest --version`
- [ ] Verify it works: `cargo nextest list`

#### Windows
- [ ] Install via cargo: `cargo install cargo-nextest`
- [ ] Or download pre-built binaries from [cargo-nextest releases](https://github.com/nextest-rs/nextest/releases)
- [ ] Verify installation: `cargo nextest --version`
- [ ] Verify it works: `cargo nextest list`

### 4. Test cargo-nextest Locally

- [ ] Run all tests with cargo-nextest: `cargo nextest run`
- [ ] Compare execution time with `cargo test` (optional but recommended)
- [ ] Verify all tests pass
- [ ] Run with JUnit XML output: `cargo nextest run --junit-xml test-results.xml`
- [ ] Verify JUnit XML file is created
- [ ] Review JUnit XML output format
- [ ] Test listing tests: `cargo nextest list`
- [ ] Verify test output is readable and informative

### 5. Update Documentation

- [ ] Update project README with test runner information:
  - [ ] Document cargo-nextest usage
  - [ ] Document pretty_assertions usage
  - [ ] Add examples of running tests locally
- [ ] Update CONTRIBUTING.md (if exists) with test instructions
- [ ] Add note about test execution time improvements

### 6. Handle Doctests (if applicable)

- [ ] Verify if project has doctests: `cargo test --doc`
- [ ] If doctests exist:
  - [ ] Document that doctests should be run separately: `cargo test --doc`
  - [ ] Note: Doctests are not supported by cargo-nextest; use `cargo test --doc` separately
- [ ] Verify doctests pass

### 7. Verification

- [ ] All tests pass locally with cargo-nextest
- [ ] All tests pass locally with pretty_assertions
- [ ] Test execution is faster (compare with `cargo test`)
- [ ] Documentation is updated
- [ ] Intentionally break a test to verify pretty_assertions output works

## Success Criteria

- [ ] `pretty_assertions` added to `Cargo.toml` dev-dependencies
- [ ] All test files updated to import `pretty_assertions::assert_eq!` (and `assert_ne!` if needed)
- [ ] Tests use `assert_eq!` and `assert_ne!` normally (the import shadows the standard macros)
- [ ] cargo-nextest installed locally and working
- [ ] All tests pass with cargo-nextest
- [ ] Documentation updated
- [ ] Test execution time improved (verified locally)

## Notes

- cargo-nextest is a drop-in replacement for `cargo test` for unit/integration tests
- Doctests are not supported by cargo-nextest; use `cargo test --doc` separately if needed
- pretty_assertions provides colored diff output for better test failure diagnostics
- CI/CD integration with cargo-nextest is handled in Phase 7 (Continuous Delivery) - see [07_Continuous_Delivery.md](07_Continuous_Delivery.md)

## References

- [cargo-nextest Documentation](https://nexte.st/)
- [cargo-nextest Installation Guide](https://nexte.st/docs/installation/)
- [pretty_assertions Documentation](https://docs.rs/pretty_assertions/)
- [TEST_RUNNER.md](../plan/01_Quality/TEST_RUNNER.md) - Detailed test runner documentation

