# Phase 3: Error Handling Implementation Plan

## Overview
Migrate error handling from `panic!` to `Result<T, anyhow::Error>` throughout the codebase for better error messages and context propagation.

## Goals
- Replace all `panic!` calls with proper error handling
- Add context to error messages using `.context()` and `.with_context()`
- Improve user-facing error messages
- Enable error chain display for debugging

## Prerequisites
- [ ] Rust toolchain installed
- [ ] Phase 2 (Test Runner) completed or in progress
- [ ] Understanding of current error handling patterns in codebase

## Implementation Tasks

### 1. Add anyhow Dependency

- [ ] Open `Cargo.toml`
- [ ] Add `anyhow` to `[dependencies]` section:
  ```toml
  [dependencies]
  anyhow = "1.0"  # Check crates.io for latest version if needed
  ```
- [ ] Run `cargo build` to verify dependency is added correctly
- [ ] Verify no compilation errors

**Note**: When using `use anyhow::Result;`, `Result<T>` is a type alias for `Result<T, anyhow::Error>`. This simplifies function signatures compared to writing `Result<T, anyhow::Error>` explicitly.

### 2. Identify Current Error Handling Patterns

- [ ] Search for `panic!` calls: `grep -r "panic!" src/`
- [ ] Search for `expect()` calls: `grep -r "\.expect(" src/`
- [ ] Search for `unwrap()` calls: `grep -r "\.unwrap()" src/`
- [ ] List all functions that use `panic!`, `expect()`, or `unwrap()`
- [ ] Document current error handling patterns
- [ ] Prioritize functions to migrate (start with user-facing functions)

### 3. Update Function Signatures

- [ ] For each function to migrate:
  - [ ] Change return type from `T` to `Result<T>` (where `Result` is `anyhow::Result<T>`, i.e., `Result<T, anyhow::Error>`)
  - [ ] Add `use anyhow::{Context, Result};` if not already present
  - [ ] Update function body to return `Result`
  - [ ] Replace `panic!` with `anyhow::bail!()` (preferred) or return `Err(anyhow::anyhow!(...))`
  - [ ] Replace `expect()` with `.context()` or `.with_context()`
  - [ ] Replace `unwrap()` with `?` operator or proper error handling
- [ ] Note: `main()` function will be updated in detail in Section 5 below
- [ ] Update all public functions first
- [ ] Then update internal functions

### 4. Add Error Context

- [ ] For each function that calls external operations:
  - [ ] Add context when reading files: `.with_context(|| format!("Failed to read file: {}", path.display()))`
  - [ ] Add context when parsing: `.context("Failed to parse HCL file")`
  - [ ] Add context when processing: `.context("Failed to process resource blocks")`
  - [ ] **Note**: Use `.context()` for static error messages, `.with_context()` for dynamic messages that need formatting
  - [ ] Add context at module boundaries
  - [ ] Add context for user-facing operations
- [ ] Use descriptive error messages
- [ ] Include relevant information (file paths, line numbers, etc.)
- [ ] Preserve original error information

### 5. Update main() Function

- [ ] Keep `main()` as `fn main()` (no return type)
- [ ] Create a `run()` function that returns `Result<()>`
- [ ] Call `run()` from `main()` and handle errors with proper display:
  ```rust
  use anyhow::Result;
  
  fn main() {
      if let Err(e) = run() {
          eprintln!("Error: {:#}", e);
          std::process::exit(1);
      }
  }
  
  fn run() -> Result<()> {
      // ... operations using ? operator ...
      Ok(())
  }
  ```
- [ ] This approach gives you more control over error formatting and exit codes
- [ ] Test error display with `{:#}` (pretty) and `{:?}` (debug) formats
- [ ] **Note**: Use `{:#}` for user-facing output (pretty-printed error chains), `{:?}` for debug logging
- [ ] Verify error messages are user-friendly

### 6. Update Tests

- [ ] Update test functions to handle `Result` types:
  - [ ] **Preferred**: Change test return type: `fn test_name() -> Result<()>` and use `?` operator
    ```rust
    #[test]
    fn test_parse_file() -> Result<()> {
        let content = parse_file(&path)?;
        assert_eq!(content, expected);
        Ok(())
    }
    ```
  - [ ] **Alternative**: For testing error cases, use `assert!(result.is_err())` and check error messages:
    ```rust
    #[test]
    fn test_parse_invalid_file() {
        let result = parse_file(&invalid_path);
        assert!(result.is_err());
        let error_msg = result.unwrap_err().to_string();
        assert!(error_msg.contains("Failed to read file"));
    }
    ```
- [ ] Add tests for error cases:
  - [ ] Test error messages contain expected context
  - [ ] Test error chains are preserved
  - [ ] Test error display formats
- [ ] Update tests that use `pretty_assertions`:
  - [ ] Test error message assertions
  - [ ] Test error chain assertions
- [ ] Run all tests: `cargo nextest run`
- [ ] Verify all tests pass

### 7. Update Error Display

- [ ] Review error display in `main()` function (where `run()` is called):
  - [ ] Use `{:#}` for pretty-printed error chains
  - [ ] Use `{:?}` for debug output (if needed)
  - [ ] Ensure error messages are user-friendly
- [ ] Test error display with various error scenarios
- [ ] Verify error chains are displayed correctly
- [ ] Ensure sensitive information is not exposed in error messages

### 8. Handle Specific Error Types

- [ ] Review if any custom error types are needed
- [ ] For library code, consider `thiserror` (but `anyhow` is recommended for applications)
- [ ] Document decision to use `anyhow` (CLI application, not library)
- [ ] If needed, convert between `anyhow::Error` and other error types

### 9. Code Review and Refinement

- [ ] Review all migrated functions
- [ ] Ensure consistent error handling patterns
- [ ] Verify error messages are descriptive
- [ ] Check that error context is added at appropriate levels
- [ ] Ensure no `panic!`, `expect()`, or `unwrap()` calls remain in production code
- [ ] **Note**: `unwrap()` is acceptable in tests for:
  - Test setup code where you control the environment (e.g., `TempDir::new().unwrap()`)
  - Asserting expected errors (e.g., `result.unwrap_err()`)
  - Not acceptable when testing error handling paths
- [ ] Run clippy: `cargo clippy --all-features --all-targets -- -D warnings`
- [ ] Fix any clippy warnings related to error handling

### 10. Update Documentation

- [ ] Update project README with error handling information
- [ ] Document error handling patterns used in codebase
- [ ] Add examples of error handling
- [ ] Document how to add context to errors
- [ ] Update API documentation if applicable

### 11. Verification

- [ ] Run all tests: `cargo nextest run`
- [ ] Verify all tests pass
- [ ] Test error scenarios manually:
  - [ ] Invalid file paths
  - [ ] Invalid input files
  - [ ] Missing files
  - [ ] Permission errors
- [ ] Verify error messages are user-friendly
- [ ] Verify error chains are displayed correctly
- [ ] Run clippy and fix warnings
- [ ] Run security checks: `cargo deny check && cargo audit --deny warnings`

## Success Criteria

- [ ] `anyhow` added to `Cargo.toml` dependencies
- [ ] All `panic!` calls replaced with proper error handling
- [ ] All `expect()` calls replaced with `.context()` or `.with_context()`
- [ ] All `unwrap()` calls replaced with `?` operator or proper error handling (in production code)
- [ ] `main()` function updated to call a `run() -> Result<()>` function with proper error display
- [ ] Error context added at appropriate levels
- [ ] Error messages are user-friendly and descriptive
- [ ] All tests updated and passing
- [ ] Error display shows full error chains
- [ ] Documentation updated

## Notes

- Use `anyhow` for applications (CLI tools), not libraries
- Add context at module boundaries and user-facing operations
- Use descriptive error messages with relevant information
- Preserve error chains for debugging
- Use `{:#}` for pretty-printed error chains in user-facing output
- Avoid exposing sensitive information in error messages
- **Type alias**: `anyhow::Result<T>` is equivalent to `std::result::Result<T, anyhow::Error>`

## Migration Examples

### Before (using panic!)
```rust
fn parse_file(path: &Path) -> String {
    std::fs::read_to_string(path)
        .expect("Failed to read file")
}
```

### After (using anyhow)
```rust
use anyhow::{Context, Result};

fn parse_file(path: &Path) -> Result<String> {
    std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read file: {}", path.display()))
}
```

### Before (in main)
```rust
fn main() {
    let content = parse_file(&path);
    process_content(&content);
}
```

### After (in main)
```rust
use anyhow::Result;

fn main() {
    if let Err(e) = run() {
        eprintln!("Error: {:#}", e);
        std::process::exit(1);
    }
}

fn run() -> Result<()> {
    let content = parse_file(&path)?;
    process_content(&content)?;
    Ok(())
}
```

## References

- [anyhow Documentation](https://docs.rs/anyhow/)
- [anyhow GitHub Repository](https://github.com/dtolnay/anyhow)
- [Error Handling in Rust Book](https://doc.rust-lang.org/book/ch09-00-error-handling.html)
- [ERROR_HANDLING.md](../plan/01_Quality/ERROR_HANDLING.md) - Detailed error handling documentation

