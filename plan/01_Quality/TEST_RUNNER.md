# Test Runner: cargo-nextest

## Purpose
Fast, modern test runner for Rust projects

## Features
- Up to 3x faster than `cargo test` through parallel execution
- Clean, informative output
- CI/CD integration with JUnit XML output
- Test retries for flaky tests
- Test timeouts and slow test detection
- Test partitioning and sharding for CI

## Compatibility
- ✅ Apple Silicon (ARM): Pre-built binaries available via Homebrew
- ✅ Linux (GitHub Actions): Pre-built binaries available for x86_64 and aarch64

## Installation

### Apple Silicon (macOS)
```bash
brew install cargo-nextest
```

### Linux / GitHub Actions
```bash
cargo install cargo-nextest
# Or use: taiki-e/install-action GitHub Action
```

## Usage

```bash
# Run all tests
cargo nextest run

# Run with JUnit XML output (for CI)
cargo nextest run --junit-xml results.xml

# List tests
cargo nextest list
```

## Integration Notes
- Drop-in replacement for `cargo test`
- Works with existing `#[test]` attributes
- No code changes required
- Can be used alongside `cargo test` for doctests

## Pros
- Significantly faster test execution
- Better CI integration
- Improved test output readability
- Active development and wide adoption

## Cons
- Additional tool to install
- Minor learning curve for advanced features
- Doctests not supported (use `cargo test --doc` separately)

## Testing Utilities

### pretty_assertions ✅ Selected

**Status**: ✅ **Selected** - This tool has been selected for the project. It will be added to `Cargo.toml` when implementing Phase 1.

**Purpose**: Enhanced assertion output with colored diffs for better test failure diagnostics

**Features**:
- Colored diff output for `assert_eq!` and `assert_ne!`
- Side-by-side comparison view
- Better readability for complex data structures
- Drop-in replacement for standard assertions

**Installation**:
Add to `Cargo.toml`:
```toml
[dev-dependencies]
pretty_assertions = "1.4"  # ✅ Selected - Will be added in Phase 1
```

**Usage**:
```rust
use pretty_assertions::assert_eq;

#[test]
fn test_example() {
    let expected = "Hello, World!";
    let actual = "Hello, Rust!";
    assert_eq!(expected, actual);  // Provides colored diff output
}
```

**Benefits**:
- ✅ Much easier to see what differs in test failures
- ✅ Works with all assertion macros
- ✅ No code changes needed beyond import
- ✅ Especially useful for string and complex type comparisons

**Integration Notes**:
- Add `#[macro_use]` or import `use pretty_assertions::assert_eq;`
- Can be used alongside standard assertions
- Works with all test frameworks

## CI Integration

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for complete CI/CD workflow examples.

## References
- [cargo-nextest Documentation](https://nexte.st/)
- [Installation Guide](https://nexte.st/docs/installation/)
- [pretty_assertions Documentation](https://docs.rs/pretty_assertions/)

