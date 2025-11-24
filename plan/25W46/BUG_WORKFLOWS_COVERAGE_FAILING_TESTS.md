# BUG: Workflow - Code coverage has failing tests

**Status**: ✅ Complete

## Description

The PR workflow `coverage` job fails because integration tests cannot find the binary executable. The tests expect the binary at `target/debug/move_maker`, but when running with code coverage, the target directory is changed to `target/llvm-cov-target`, causing the binary to be in a different location.

## Current State

✅ **FIXED** - The integration tests now correctly locate the binary using `CARGO_BIN_EXE_move_maker` environment variable, which Cargo automatically sets for integration tests.

**Fixed implementation:**
```rust
fn get_binary_path() -> PathBuf {
    PathBuf::from(env!("CARGO_BIN_EXE_move_maker"))
}
```

**Note:** `CARGO_BIN_EXE_move_maker` is a compile-time environment variable set by Cargo that automatically points to the correct binary path, regardless of target directory configuration. This works with both standard builds and `cargo llvm-cov` builds.

**Fixed files:**
- `tests/integration_test.rs` (lines 7-9) - Updated `get_binary_path()` to use `CARGO_BIN_EXE_move_maker` environment variable

**Current workflow configuration:**
```yaml
- name: Generate coverage
  run: cargo llvm-cov nextest --all-features --lcov --output-path lcov.info

- name: Check coverage thresholds
  run: |
    # Generate coverage and extract percentages
    cargo llvm-cov nextest --all-features --summary-only > coverage-summary.txt
```

**Error output:**
```
FAIL [   0.005s] ( 1/49) move_maker::integration_test test_empty_directory
thread 'test_empty_directory' panicked at tests/integration_test.rs:205:10:
Failed to execute command: Os { code: 2, kind: NotFound, message: "No such file or directory" }
```

**Affected tests:**
- `test_empty_directory`
- `test_invalid_hcl_file`
- `test_module_name_with_hyphens`
- `test_mixed_resources_and_data`

**Root cause in test code:**
```rust
fn get_binary_path() -> PathBuf {
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("target");
    path.push("debug");
    path.push("move_maker");
    path
}
```

The test hardcodes the path to `target/debug/move_maker`, but `cargo llvm-cov` uses `--target-dir target/llvm-cov-target`, so the binary is at `target/llvm-cov-target/debug/move_maker` instead.

## Expected State

The coverage job should:
1. Successfully run all tests including integration tests
2. Generate coverage reports
3. Check coverage thresholds
4. Pass if thresholds are met

## Impact

### CI/CD Impact
- **Severity**: High
- **Priority**: High

The coverage job fails completely, preventing:
- Code coverage generation
- Coverage threshold validation
- Coverage reports from being generated

### Functionality Impact
- **Severity**: High
- **Priority**: High

Code coverage cannot be measured, which is a critical quality metric for the project.

## Root Cause

The integration tests use a hardcoded path to find the binary:
```rust
target/debug/move_maker
```

However, `cargo llvm-cov` changes the target directory to `target/llvm-cov-target` (as seen in the workflow), so the binary is not found at the expected location.

**Workflow evidence:**
The error shows the command is run with `--target-dir /home/runner/work/moved_maker/moved_maker/target/llvm-cov-target`, confirming the target directory is changed.


## Related Implementation Plan

See `work/25W46/BUG_WORKFLOWS_COVERAGE_FAILING_TESTS.md` for the detailed implementation plan.
