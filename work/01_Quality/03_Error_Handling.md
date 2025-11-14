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

- [x] Open `Cargo.toml`
- [x] Add `anyhow` to `[dependencies]` section:
  ```toml
  [dependencies]
  anyhow = "1.0"  # Check crates.io for latest version if needed
  ```
- [x] Run `cargo build` to verify dependency is added correctly
- [x] Verify no compilation errors

**Note**: When using `use anyhow::Result;`, `Result<T>` is a type alias for `Result<T, anyhow::Error>`. This simplifies function signatures compared to writing `Result<T, anyhow::Error>` explicitly.

### 2. Identify Current Error Handling Patterns

- [x] Search for `panic!` calls: `grep -r "panic!" src/`
- [x] Search for `expect()` calls: `grep -r "\.expect(" src/`
- [x] Search for `unwrap()` calls: `grep -r "\.unwrap()" src/`
- [x] List all functions that use `panic!`, `expect()`, or `unwrap()`
- [x] Document current error handling patterns
- [x] Prioritize functions to migrate (start with user-facing functions)

### 3. Update Function Signatures

- [x] For each function to migrate:
  - [x] Change return type from `T` to `Result<T>` (where `Result` is `anyhow::Result<T>`, i.e., `Result<T, anyhow::Error>`)
  - [x] Add `use anyhow::{Context, Result};` if not already present
  - [x] Update function body to return `Result`
  - [x] Replace `panic!` with `anyhow::bail!()` (preferred) or return `Err(anyhow::anyhow!(...))`
  - [x] Replace `expect()` with `.context()` or `.with_context()`
  - [x] Replace `unwrap()` with `?` operator or proper error handling
- [x] Note: `main()` function will be updated in detail in Section 5 below
- [x] Update all public functions first
- [x] Then update internal functions

### 4. Add Error Context

- [x] For each function that calls external operations:
  - [x] Add context when reading files: `.with_context(|| format!("Failed to read file: {}", path.display()))`
  - [x] Add context when parsing: `.context("Failed to parse HCL file")`
  - [x] Add context when processing: `.context("Failed to process resource blocks")`
  - [x] **Note**: Use `.context()` for static error messages, `.with_context()` for dynamic messages that need formatting
  - [x] Add context at module boundaries
  - [x] Add context for user-facing operations
- [x] Use descriptive error messages
- [x] Include relevant information (file paths, line numbers, etc.)
- [x] Preserve original error information

### 5. Update main() Function

- [x] Keep `main()` as `fn main()` (no return type)
- [x] Create a `run()` function that returns `Result<()>`
- [x] Call `run()` from `main()` and handle errors with proper display:
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
- [x] This approach gives you more control over error formatting and exit codes
- [x] Test error display with `{:#}` (pretty) and `{:?}` (debug) formats
- [x] **Note**: Use `{:#}` for user-facing output (pretty-printed error chains), `{:?}` for debug logging
- [x] Verify error messages are user-friendly

### 6. Update Tests

- [x] Update test functions to handle `Result` types:
  - [x] **Preferred**: Change test return type: `fn test_name() -> Result<()>` and use `?` operator
    ```rust
    #[test]
    fn test_parse_file() -> Result<()> {
        let content = parse_file(&path)?;
        assert_eq!(content, expected);
        Ok(())
    }
    ```
  - [x] **Alternative**: For testing error cases, use `assert!(result.is_err())` and check error messages:
    ```rust
    #[test]
    fn test_parse_invalid_file() {
        let result = parse_file(&invalid_path);
        assert!(result.is_err());
        let error_msg = result.unwrap_err().to_string();
        assert!(error_msg.contains("Failed to read file"));
    }
    ```
- [x] Add tests for error cases:
  - [x] Test error messages contain expected context
  - [x] Test error chains are preserved
  - [x] Test error display formats
- [x] Update tests that use `pretty_assertions`:
  - [x] Test error message assertions
  - [x] Test error chain assertions
- [x] Run all tests: `cargo nextest run`
- [x] Verify all tests pass

### 7. Update Error Display

- [x] Review error display in `main()` function (where `run()` is called):
  - [x] Use `{:#}` for pretty-printed error chains
  - [x] Use `{:?}` for debug output (if needed)
  - [x] Ensure error messages are user-friendly
- [x] Test error display with various error scenarios
- [x] Verify error chains are displayed correctly
- [x] Ensure sensitive information is not exposed in error messages

### 8. Handle Specific Error Types

- [x] Review if any custom error types are needed
- [x] For library code, consider `thiserror` (but `anyhow` is recommended for applications)
- [x] Document decision to use `anyhow` (CLI application, not library)
- [x] If needed, convert between `anyhow::Error` and other error types

### 9. Code Review and Refinement

- [x] Review all migrated functions
- [x] Ensure consistent error handling patterns
- [x] Verify error messages are descriptive
- [x] Check that error context is added at appropriate levels
- [x] Ensure no `panic!`, `expect()`, or `unwrap()` calls remain in production code
- [x] **Note**: `unwrap()` is acceptable in tests for:
  - Test setup code where you control the environment (e.g., `TempDir::new().unwrap()`)
  - Asserting expected errors (e.g., `result.unwrap_err()`)
  - Not acceptable when testing error handling paths
- [x] Run clippy: `cargo clippy --all-features --all-targets -- -D warnings`
- [x] Fix any clippy warnings related to error handling

### 10. Update Documentation

- [x] Update DEVELOPMENT.md with error handling information
- [x] Document error handling patterns used in codebase
- [x] Add examples of error handling
- [x] Document how to add context to errors
- [x] Update API documentation if applicable

### 11. Verification

- [x] Run all tests: `cargo nextest run`
- [x] Verify all tests pass
- [x] Test error scenarios manually:
  - [x] Invalid file paths
  - [x] Invalid input files
  - [x] Missing files
  - [x] Permission errors
- [x] Verify error messages are user-friendly
- [x] Verify error chains are displayed correctly
- [x] Run clippy and fix warnings
- [x] Run security checks: `cargo deny check --config .config/deny.toml && cargo audit --deny warnings`

## Success Criteria

- [x] `anyhow` added to `Cargo.toml` dependencies
- [x] All `panic!` calls replaced with proper error handling
- [x] All `expect()` calls replaced with `.context()` or `.with_context()`
- [x] All `unwrap()` calls replaced with `?` operator or proper error handling (in production code)
- [x] `main()` function updated to call a `run() -> Result<()>` function with proper error display
- [x] Error context added at appropriate levels
- [x] Error messages are user-friendly and descriptive
- [x] All tests updated and passing
- [x] Error display shows full error chains
- [x] Documentation updated

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
