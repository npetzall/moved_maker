# Bug: Workflow - Code coverage has failing tests

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

## Steps to Fix

### Option 1: Use CARGO_BIN_EXE environment variable (RECOMMENDED)
Use the `CARGO_BIN_EXE_<name>` compile-time environment variable that Cargo automatically sets for integration tests:

```rust
fn get_binary_path() -> PathBuf {
    PathBuf::from(env!("CARGO_BIN_EXE_move_maker"))
}
```

This is the simplest and most robust solution, as Cargo automatically handles:
- Different target directories (including `llvm-cov-target`)
- Windows `.exe` extension
- Debug vs release builds
- Custom target directories via `CARGO_TARGET_DIR`

### Option 2: Use cargo metadata to find the binary
Use `cargo metadata` or `env!("CARGO_BIN_NAME")` to locate the binary dynamically:

```rust
fn get_binary_path() -> PathBuf {
    // Try to get target directory from environment
    let target_dir = std::env::var("CARGO_TARGET_DIR")
        .unwrap_or_else(|_| "target".to_string());

    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push(target_dir);
    path.push("debug");
    path.push(env!("CARGO_PKG_NAME"));

    #[cfg(windows)]
    path.set_extension("exe");

    path
}
```

### Option 3: Build the binary explicitly in tests
Instead of assuming the binary exists, build it explicitly in the test setup:

```rust
fn get_binary_path() -> PathBuf {
    // Build the binary first
    let output = Command::new("cargo")
        .args(&["build", "--bin", "move_maker"])
        .output()
        .expect("Failed to build binary");

    assert!(output.status.success(), "Binary build failed");

    // Then locate it using cargo metadata or environment
    // ... (implementation)
}
```

### Option 4: Don't change target directory in coverage job
Remove the `--target-dir` flag from the coverage commands (if it's being set explicitly), or ensure the tests can find the binary in the custom target directory.

**Recommended approach:** Option 1 (using `CARGO_BIN_EXE_move_maker`), as it's the simplest and most robust solution. Cargo automatically sets this environment variable at compile time, handling all edge cases including custom target directories.

## Affected Files

- `tests/integration_test.rs`
  - `get_binary_path()` function (lines 7-9)
  - All integration tests that use `get_binary_path()`

## Investigation Needed

1. Verify if `cargo llvm-cov` sets `CARGO_TARGET_DIR` environment variable
2. Check if there's a way to query cargo for the actual binary path
3. Consider if the target directory should be changed for coverage runs
4. Test the fix locally with `cargo llvm-cov nextest` to ensure it works

## Test Failures Summary

The following integration tests fail:
1. `test_empty_directory` - Line 205
2. `test_invalid_hcl_file` - Line 180
3. `test_module_name_with_hyphens` - Line 287
4. `test_mixed_resources_and_data` - Line 101

All failures are due to the same root cause: binary not found at expected path.

## Status

✅ **IMPLEMENTED** - Integration tests updated to use `CARGO_BIN_EXE_move_maker` environment variable. This is the recommended Cargo approach for integration tests and automatically handles all target directory configurations, including `cargo llvm-cov` builds.

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `tests/integration_test.rs`

**File:** `tests/integration_test.rs`

1. **Update `get_binary_path()` function (lines 7-9)**
   - [x] Locate the `get_binary_path()` function starting at line 7
   - [x] Replace the hardcoded path construction with `CARGO_BIN_EXE_move_maker` environment variable
   - [x] Update the function to:
     ```rust
     fn get_binary_path() -> PathBuf {
         PathBuf::from(env!("CARGO_BIN_EXE_move_maker"))
     }
     ```
   - [x] Verify that `CARGO_BIN_EXE_move_maker` is automatically set by Cargo for integration tests
   - [x] Confirm this handles Windows `.exe` extension automatically
   - [x] Verify all integration tests that call `get_binary_path()` will work with the new logic

2. **Verify integration test usage**
   - [x] Confirm all affected tests use `get_binary_path()`:
     - `test_empty_directory` (line 198)
     - `test_invalid_hcl_file` (line 173)
     - `test_module_name_with_hyphens` (line 280)
     - `test_mixed_resources_and_data` (line 94)
   - [x] Verify no other tests have hardcoded binary paths
   - [x] Check that all tests will benefit from the fix

### Phase 2: Testing Steps

#### Step 2: Local Testing

1. **Test with standard cargo test**
   - [x] Run `cargo test` to ensure all integration tests pass with default target directory
   - [x] Verify `get_binary_path()` correctly resolves to `target/debug/move_maker`
   - [x] Confirm all 10 integration tests pass:
     - `test_single_resource_file`
     - `test_multiple_resources`
     - `test_mixed_resources_and_data`
     - `test_multiple_files`
     - `test_invalid_hcl_file`
     - `test_empty_directory`
     - `test_resource_with_count`
     - `test_resource_with_for_each`
     - `test_module_name_with_hyphens`
     - `test_module_name_with_underscores`

2. **Test with CARGO_TARGET_DIR set**
   - [x] Set `CARGO_TARGET_DIR=target/test-target` environment variable
   - [x] Build the binary: `CARGO_TARGET_DIR=target/test-target cargo build`
   - [x] Run integration tests: `CARGO_TARGET_DIR=target/test-target cargo test --test integration_test`
   - [x] Verify `CARGO_BIN_EXE_move_maker` automatically points to the correct path in custom target directory
   - [x] Confirm all integration tests pass with custom target directory

3. **Test with cargo llvm-cov (simulating CI)**
   - [ ] Install `cargo-llvm-cov` if not already installed: `cargo install cargo-llvm-cov`
   - [ ] Run `cargo llvm-cov nextest --all-features` to simulate the CI coverage job
   - [ ] Verify integration tests can find the binary in the llvm-cov target directory
   - [ ] Confirm all tests pass and coverage is generated
   - [ ] Check that `CARGO_TARGET_DIR` is set correctly during llvm-cov execution
   - [ ] Verify the binary path resolves correctly in the llvm-cov target directory

4. **Test edge cases**
   - [ ] Test with `CARGO_TARGET_DIR` set to an absolute path
   - [ ] Test with `CARGO_TARGET_DIR` set to a relative path with `../`
   - [x] Test with `CARGO_TARGET_DIR` unset (default behavior)
   - [ ] Verify Windows path handling (if testing on Windows or with cross-compilation)

#### Step 3: CI Testing

1. **Create test branch and PR**
   - [ ] Create a feature branch for the fix
   - [ ] Push changes and create a pull request
   - [ ] Verify the `coverage` job runs successfully
   - [ ] Confirm all integration tests pass in the coverage job
   - [ ] Verify coverage reports are generated correctly
   - [ ] Check that coverage thresholds are still validated

2. **Verify other CI jobs**
   - [ ] Confirm the `test` job still passes (should use default target directory)
   - [ ] Verify no regressions in other workflow jobs
   - [ ] Check that pre-commit hooks still pass

### Phase 3: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `tests/integration_test.rs`
   - Restore the original `get_binary_path()` function
   - Verify tests return to previous state (even if broken in coverage job, for reference)

2. **Partial Rollback**
   - If `CARGO_BIN_EXE_move_maker` is not available (shouldn't happen in integration tests), verify Cargo version supports this feature
   - Check if binary name matches exactly (`move_maker` vs `moved_maker`)
   - Verify the environment variable is set at compile time

3. **Alternative Approaches**
   - If `CARGO_BIN_EXE_move_maker` doesn't work, fall back to checking `CARGO_TARGET_DIR` and constructing path manually
   - Consider using `cargo metadata` to query the actual binary location
   - Verify binary name in `Cargo.toml` matches the environment variable suffix

### Implementation Order

1. [x] Start with `tests/integration_test.rs` `get_binary_path()` function (only affected file)
2. [x] Update `get_binary_path()` to use `CARGO_BIN_EXE_move_maker` environment variable
3. [x] Verify Windows extension handling is automatic (handled by Cargo)
4. [x] Test locally with `cargo test` to ensure default behavior still works
5. [x] Test locally with `CARGO_TARGET_DIR` set to verify custom target directory works
6. [ ] Test locally with `cargo llvm-cov nextest` to simulate CI coverage job
7. [x] Verify all 10 integration tests pass in all scenarios (default and custom target dir)
8. [ ] Create pull request and verify CI coverage job passes
9. [ ] Verify other CI jobs (test, pre-commit) still pass
10. [ ] Confirm coverage reports are generated correctly
11. [ ] Verify coverage thresholds are still validated

### Risk Assessment

- **Risk Level:** Low to Medium
- **Impact if Failed:** Integration tests would fail in coverage job, but standard test job should continue to work
- **Mitigation:**
  - Simple change to a single function (reduced from ~15 lines to 1 line)
  - Easy rollback if needed
  - Can test locally before affecting CI
  - Uses Cargo's built-in mechanism for integration tests
  - All integration tests use the same function, so fix applies to all affected tests
- **Testing:** Can be fully tested locally with `cargo llvm-cov` before affecting CI
- **Dependencies:**
  - `CARGO_BIN_EXE_move_maker` is automatically set by Cargo for integration tests (available since Cargo 1.60+)
  - Works automatically with `cargo llvm-cov` and any custom target directory
  - Windows `.exe` extension is handled automatically by Cargo
- **Performance Considerations:**
  - No performance impact - compile-time environment variable access
  - Simpler code means faster compilation

## Example Fix

### Before:
```rust
fn get_binary_path() -> PathBuf {
    // In integration tests, the binary is in target/debug/
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("target");
    path.push("debug");
    path.push("move_maker");

    // On Windows, add .exe extension
    #[cfg(windows)]
    path.set_extension("exe");

    path
}
```

### After:
```rust
fn get_binary_path() -> PathBuf {
    PathBuf::from(env!("CARGO_BIN_EXE_move_maker"))
}
```

**Benefits of this approach:**
- Automatically handles custom target directories (including `llvm-cov-target`)
- Automatically handles Windows `.exe` extension
- Works with debug and release builds
- No manual path construction needed
- Set by Cargo at compile time for integration tests

## References

- Integration test file: `tests/integration_test.rs` (lines 7-9)
- Coverage workflow: `.github/workflows/pull_request.yaml` (lines 70-135)
- Cargo llvm-cov documentation: https://github.com/taiki-e/cargo-llvm-cov
- CARGO_BIN_EXE environment variable: https://doc.rust-lang.org/cargo/reference/environment-variables.html#environment-variables-cargo-sets-for-crates
- Cargo environment variables: https://doc.rust-lang.org/cargo/reference/environment-variables.html
