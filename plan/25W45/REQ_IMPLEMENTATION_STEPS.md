# Implementation Steps

## Step 1: Add Dependencies
**File**: `Cargo.toml`
- Add `clap` with `derive` feature for CLI parsing
- Add `env_logger` (optional, for warnings - `panic!` is acceptable alternative)
- No `walkdir` needed - using `std::fs` for non-recursive file discovery

## Step 2: Implement CLI Module
**File**: `src/cli.rs`
- Define `Args` struct with `clap::Parser`
- Implement validation function
- Return validated arguments

## Step 3: Implement File Discovery
**File**: `src/file_discovery.rs`
- Function to find all `.tf` files (non-recursive, only direct children)
- Return `Vec<PathBuf>` (use `panic!()` for fatal errors)
- Use `std::fs::read_dir()` for non-recursive directory reading

## Step 4: Implement HCL Parser
**File**: `src/parser.rs`
- Function to parse Terraform file: `parse_terraform_file(path: &Path) -> Result<Body, Error>`
- Use `hcl::edit::parser::parse_body()` to parse file content
- Return `Result<Body, Error>` - caller handles errors (log warning and continue)

## Step 5: Implement Block Processing
**File**: `src/processor.rs`
- Extract blocks from `Body` using `body.blocks().iter().filter()`
- Process resource blocks - build decorated `Block` structures
- Process data blocks - build decorated `Block` structures
- Create utility functions: `build_from_expression()` and `build_to_expression()`
- Use `path: &Path` parameter, extract filename with `file_name().expect(...)`

## Step 6: Implement Output Formatting
**File**: `src/output.rs`
- Build `Body` from collected `Block` structures using `Body::builder()`
- Convert `Body` to string using `Display` trait
- Blocks already have comments attached via decor

## Step 7: Implement Main Function
**File**: `src/main.rs`
- Declare modules: `mod cli;`, `mod file_discovery;`, `mod parser;`, `mod processor;`, `mod output;`
- Add necessary `use` statements
- Parse CLI arguments (panic on validation failure)
- Discover Terraform files (panic on fatal errors)
- For each file:
  - Parse HCL - log warning and continue on parse error
  - Extract blocks using `body.blocks().iter().filter()` for "resource" or "data"
  - For each filtered block:
    - Extract type and name from labels (log warning and skip if < 2 labels)
    - Build decorated `Block` structure with comment using `path: &Path`
    - Collect blocks
- Build final `Body` from collected blocks using `build_output_body()`
- Print `Body` to stdout using `Display` trait

## Step 8: Testing
See [TESTING.md](TESTING.md) for comprehensive testing strategy.

**Quick Summary**:
- Add unit tests for each component (in same files with `#[cfg(test)]`)
- Create integration tests in `tests/` directory
- Create test fixtures in `tests/fixtures/` with sample Terraform files
- Test edge cases (invalid files, missing labels, etc.)
- Verify output format and correctness
- Run tests with `cargo test`

## File Organization

**Approach**: Start with multiple files for better organization with tests
- Create modules: `src/cli.rs`, `src/file_discovery.rs`, `src/parser.rs`, `src/processor.rs`, `src/output.rs`
- Declare modules in `src/main.rs` using `mod` statements
- Split modules when they exceed 500 lines
- Unit tests in nested `#[cfg(test)]` modules within each source file
