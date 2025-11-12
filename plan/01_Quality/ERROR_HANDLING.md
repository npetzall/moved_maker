# Error Handling: anyhow

## Purpose
Improve error handling throughout the codebase with better error messages and context propagation

## Features
- Simple error handling with `Result<T, anyhow::Error>`
- Contextual error messages with `.context()`
- Automatic error conversion from other error types
- Better error propagation with `?` operator
- Error chain display with `{:?}` or `{:#}` formatting

## Compatibility
- ✅ Apple Silicon (ARM): Fully supported
- ✅ Linux (GitHub Actions): Fully supported

## Status

✅ **Selected** - This tool has been selected for the project. It will be added to `Cargo.toml` when implementing Phase 1.5.

## Installation

Add to `Cargo.toml`:
```toml
[dependencies]
anyhow = "1.0"  # ✅ Selected - Will be added in Phase 1.5
```

## Usage

### Basic Error Handling
```rust
use anyhow::{Context, Result};

fn parse_file(path: &Path) -> Result<String> {
    std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read file: {}", path.display()))
}
```

### Error Context
```rust
use anyhow::{Context, Result};

fn process_config() -> Result<()> {
    let config = load_config()
        .context("Failed to load configuration")?;
    
    validate_config(&config)
        .context("Configuration validation failed")?;
    
    Ok(())
}
```

### Error Propagation
```rust
use anyhow::Result;

fn main() -> Result<()> {
    let result = some_operation()?;
    println!("Success: {:?}", result);
    Ok(())
}
```

### Error Display
```rust
match result {
    Ok(value) => println!("Success: {:?}", value),
    Err(e) => {
        eprintln!("Error: {:#}", e);  // Pretty-printed error chain
        eprintln!("Error: {:?}", e);  // Debug format
    }
}
```

## Benefits

### For Development
- ✅ **Simpler error handling**: No need to define custom error types for simple cases
- ✅ **Better error messages**: Add context at each level of the call stack
- ✅ **Error chains**: See the full error chain from root cause to surface
- ✅ **Automatic conversion**: Works seamlessly with other error types

### For Testing
- ✅ **Easier test assertions**: Can check error messages and context
- ✅ **Better test failures**: Error messages help identify what went wrong
- ✅ **Error matching**: Can match on error messages in tests

### For Production
- ✅ **User-friendly errors**: Context helps users understand what went wrong
- ✅ **Debugging**: Error chains make debugging easier
- ✅ **Logging**: Error chains provide full context for logs

## Integration with Tests

### Testing Error Cases
```rust
use anyhow::Result;
use pretty_assertions::assert_eq;

#[test]
fn test_error_handling() {
    let result = parse_invalid_file();
    assert!(result.is_err());
    
    let error_msg = result.unwrap_err().to_string();
    assert!(error_msg.contains("Failed to read file"));
}
```

### Using with pretty_assertions
```rust
use anyhow::Result;
use pretty_assertions::assert_eq;

#[test]
fn test_error_messages() {
    let result: Result<String> = Err(anyhow::anyhow!("Base error"))
        .context("First context")
        .context("Second context");
    
    let error_str = format!("{:#}", result.unwrap_err());
    assert_eq!(
        error_str,
        "Second context\nCaused by:\n  First context\nCaused by:\n  Base error"
    );
}
```

## Best Practices

1. **Add Context at Boundaries**
   - Add context when crossing module boundaries
   - Add context when converting from external error types
   - Add context for user-facing operations

2. **Use Descriptive Messages**
   ```rust
   // Good
   .context("Failed to parse HCL file")
   
   // Better
   .with_context(|| format!("Failed to parse HCL file: {}", path.display()))
   ```

3. **Preserve Error Chains**
   - Use `?` operator to propagate errors
   - Add context without losing original error information
   - Use `{:#}` formatting to display full error chain

4. **For Complex Error Types**
   - Use `anyhow` for simple cases
   - Consider `thiserror` for library code that needs structured errors
   - Use `anyhow` in applications, `thiserror` in libraries

## Migration Strategy

### Current Code (using panic!)
```rust
fn parse_file(path: &Path) -> String {
    std::fs::read_to_string(path)
        .expect("Failed to read file")
}
```

### With anyhow
```rust
use anyhow::{Context, Result};

fn parse_file(path: &Path) -> Result<String> {
    std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read file: {}", path.display()))
}
```

### In main()
```rust
use anyhow::Result;

fn main() -> Result<()> {
    // All operations can use ? operator
    let content = parse_file(&path)?;
    process_content(&content)?;
    Ok(())
}
```

## When to Use anyhow vs thiserror

### Use anyhow when:
- ✅ Building applications (CLI tools, servers, etc.)
- ✅ Error messages are more important than error types
- ✅ You want simple error handling
- ✅ You're propagating errors from many different sources

### Use thiserror when:
- ✅ Building libraries
- ✅ Callers need to match on specific error types
- ✅ You need structured error information
- ✅ You want to implement specific error traits

**For move_maker**: Since it's a CLI application, `anyhow` is the recommended choice.

## References

- [anyhow Documentation](https://docs.rs/anyhow/)
- [anyhow GitHub Repository](https://github.com/dtolnay/anyhow)
- [Error Handling in Rust Book](https://doc.rust-lang.org/book/ch09-00-error-handling.html)

