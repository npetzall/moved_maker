# DONE - Completed Implementation Checklist

This document archives all completed items from the TDD implementation checklist.

## Setup & Dependencies

- [x] **Add dependencies to Cargo.toml**
  - [x] Add `clap` with `derive` feature
  - [x] Add `env_logger` (optional, for warnings - `panic!` is acceptable alternative)
  - [x] Verify `hcl-rs = "0.19.4"` is present
  - [x] Run `cargo check` to verify dependencies resolve

- [x] **File organization setup**
  - [x] Create module structure: `src/cli.rs`, `src/file_discovery.rs`, `src/parser.rs`, `src/processor.rs`, `src/output.rs`
  - [x] Set up `src/main.rs` with module declarations: `mod cli;`, `mod file_discovery;`, etc.
  - [x] Add necessary `use` statements in `src/main.rs`
  - [x] Note: Split modules when they exceed 500 lines

## CLI Argument Parsing

- [x] **Test: CLI args struct creation**
  - [x] 🔴 Write test for `Args` struct with `--src` and `--module-name`
  - [x] 🟢 Implement `Args` struct with `clap::Parser`
  - [x] 🔵 Verify struct compiles

- [x] **Test: Valid CLI arguments**
  - [x] 🔴 Write test parsing valid `--src` and `--module-name`
  - [x] 🟢 Implement argument parsing
  - [x] 🔵 Verify arguments are accessible

- [x] **Test: Missing required arguments**
  - [x] 🔴 Write test for missing `--src` argument
  - [x] 🟢 Add required argument validation
  - [x] 🔵 Verify error message is clear

- [x] **Test: Missing module-name argument**
  - [x] 🔴 Write test for missing `--module-name` argument
  - [x] 🟢 Add required argument validation
  - [x] 🔵 Verify error message is clear

- [x] **Test: Invalid directory path**
  - [x] 🔴 Write test for non-existent `--src` path
  - [x] 🟢 Add path validation (exists check)
  - [x] 🔵 Verify error message includes path

- [x] **Test: Non-directory path**
  - [x] 🔴 Write test for `--src` pointing to a file
  - [x] 🟢 Add directory validation (is_dir check)
  - [x] 🔵 Verify error message is clear

- [x] **Test: Empty module name**
  - [x] 🔴 Write test for empty `--module-name` (should panic)
  - [x] 🟢 Add non-empty validation with `panic!()`
  - [x] 🔵 Verify panic message is clear

- [x] **Test: Invalid module name format**
  - [x] 🔴 Write test for module name starting with number (should panic)
  - [x] 🟢 Add Terraform identifier validation
  - [x] 🔵 Verify panic message explains identifier rules

- [x] **Test: Module name with invalid characters**
  - [x] 🔴 Write test for module name with special chars (should panic)
  - [x] 🟢 Add character validation (alphanumeric + underscore/hyphen only)
  - [x] 🔵 Verify panic message is clear

- [x] **Test: Valid module name formats**
  - [x] 🔴 Write tests for valid names (letters, numbers, underscore, hyphen)
  - [x] 🟢 Ensure validation accepts valid formats
  - [x] 🔵 Verify names starting with letter/underscore work

## File Discovery

- [x] **Test: Find .tf files in directory**
  - [x] 🔴 Write test creating temp dir with `.tf` files
  - [x] 🟢 Implement `find_terraform_files()` using `std::fs::read_dir()` returning `Vec<PathBuf>`
  - [x] 🔵 Verify function returns correct file paths

- [x] **Test: File discovery - panic on fatal errors**
  - [x] 🔴 Write test for non-existent directory (should panic)
  - [x] 🟢 Use `panic!()` for fatal errors (directory doesn't exist, permission denied)
  - [x] 🔵 Verify panic occurs for fatal errors

- [x] **Test: Ignore non-.tf files**
  - [x] 🔴 Write test with mixed file types (`.tf`, `.txt`, etc.)
  - [x] 🟢 Add extension filter (`.tf` only)
  - [x] 🔵 Verify only `.tf` files are returned

- [x] **Test: Ignore subdirectories (non-recursive)**
  - [x] 🔴 Write test with subdirectory containing `.tf` files
  - [x] 🟢 Ensure function only reads direct children (not recursive)
  - [x] 🔵 Verify subdirectory files are not included

- [x] **Test: Empty directory**
  - [x] 🔴 Write test for empty directory
  - [x] 🟢 Handle empty directory gracefully
  - [x] 🔵 Verify returns empty vector

- [x] **Test: Directory with no .tf files**
  - [x] 🔴 Write test with directory containing only non-.tf files
  - [x] 🟢 Filter correctly
  - [x] 🔵 Verify returns empty vector

- [x] **Test: Error handling for unreadable files**
  - [x] 🔴 Write test for files that can't be read (non-fatal)
  - [x] 🟢 Add error handling (skip with warning to stderr using `eprintln!()`)
  - [x] 🔵 Verify other files still processed, warning logged

## HCL Parsing

- [x] **Test: Parse valid Terraform file**
  - [x] 🔴 Write test with simple valid `.tf` file content
  - [x] 🟢 Implement `parse_terraform_file()` using `hcl::edit::parser::parse_body()`
  - [x] 🔵 Verify returns `Body` structure

- [x] **Test: Parse file with resource block**
  - [x] 🔴 Write test with file containing `resource` block
  - [x] 🟢 Parse and verify `Body` contains block
  - [x] 🔵 Verify block is accessible

- [x] **Test: Parse file with data block**
  - [x] 🔴 Write test with file containing `data` block
  - [x] 🟢 Parse and verify `Body` contains block
  - [x] 🔵 Verify block is accessible

- [x] **Test: Handle invalid HCL syntax**
  - [x] 🔴 Write test with malformed HCL content
  - [x] 🟢 Return appropriate error
  - [x] 🔵 Verify error message is informative

- [x] **Test: Handle empty file**
  - [x] 🔴 Write test with empty file
  - [x] 🟢 Parse empty file (should return empty Body)
  - [x] 🔵 Verify no panic

- [x] **Test: Handle file with only comments**
  - [x] 🔴 Write test with file containing only comments
  - [x] 🟢 Parse file with comments only
  - [x] 🔵 Verify returns empty Body

## Block Extraction

- [x] **Test: Extract resource blocks**
  - [x] 🔴 Write test with `Body` containing resource blocks
  - [x] 🟢 Implement `extract_blocks()` filtering for `"resource"`
  - [x] 🔵 Verify only resource blocks returned

- [x] **Test: Extract data blocks**
  - [x] 🔴 Write test with `Body` containing data blocks
  - [x] 🟢 Update filter to include `"data"`
  - [x] 🔵 Verify only resource and data blocks returned

- [x] **Test: Ignore other block types**
  - [x] 🔴 Write test with `locals`, `variable`, etc. blocks
  - [x] 🟢 Filter excludes non-resource/data blocks
  - [x] 🔵 Verify other blocks are ignored

- [x] **Test: Extract from mixed blocks**
  - [x] 🔴 Write test with resource, data, and other blocks
  - [x] 🟢 Filter correctly
  - [x] 🔵 Verify only resource and data returned

- [x] **Test: Handle blocks with missing labels**
  - [x] 🔴 Write test with resource block missing labels (< 2 labels)
  - [x] 🟢 Log warning to stderr and skip block
  - [x] 🔵 Verify warning logged, block skipped, no panic

- [x] **Test: Handle blocks with only one label**
  - [x] 🔴 Write test with block having only one label
  - [x] 🟢 Log warning to stderr and skip block
  - [x] 🔵 Verify warning logged, block skipped, no panic

- [x] **Test: Handle blocks with multiple labels (3+)**
  - [x] 🔴 Write test with block having 3+ labels
  - [x] 🟢 Use first 2 labels (type and name), ignore additional labels
  - [x] 🔵 Verify block processed correctly using first 2 labels

## Block Processing - Resource Blocks

- [x] **Test: Build resource moved block - basic**
  - [x] 🔴 Write test for `build_resource_moved_block()` with simple resource
  - [x] 🟢 Implement function using `Block::builder()`
  - [x] 🔵 Verify block has correct identifier "moved"

- [x] **Test: Build from expression utility function**
  - [x] 🔴 Write test for `build_from_expression()` utility function
  - [x] 🟢 Implement utility (using parse_body approach for expression building)
  - [x] 🟢 Chain attributes to build traversal path
  - [x] 🟢 Convert to `hcl::edit::expr::Expression`
  - [x] 🔵 Verify creates correct Expression for `resource_type.resource_name`
  - [x] 🔵 Verify creates correct Expression for `data.data_type.data_name`

- [x] **Test: Resource block - from attribute**
  - [x] 🔴 Write test verifying "from" attribute value uses utility function
  - [x] 🟢 Add "from" attribute using `build_from_expression()`
  - [x] 🔵 Verify format: `resource_type.resource_name`

- [x] **Test: Build to expression utility function**
  - [x] 🔴 Write test for `build_to_expression()` utility function
  - [x] 🟢 Implement utility (using parse_body approach)
  - [x] 🟢 Build module path (module_name -> resource_type -> resource_name)
  - [x] 🟢 Handle data blocks with additional "data" in path
  - [x] 🟢 Convert to `hcl::edit::expr::Expression`
  - [x] 🔵 Verify creates correct Expression for `module.module_name.resource_type.resource_name`
  - [x] 🔵 Verify creates correct Expression for `module.module_name.data.data_type.data_name`

- [x] **Test: Resource block - to attribute**
  - [x] 🔴 Write test verifying "to" attribute value uses utility function
  - [x] 🟢 Add "to" attribute using `build_to_expression()` with `is_data=false`
  - [x] 🔵 Verify format: `module.<module_name>.<resource_type>.<resource_name>`

- [x] **Test: Filename extraction**
  - [x] 🔴 Write test for extracting filename from path
  - [x] 🟢 Use `path.file_name().expect("path must have filename")`
  - [x] 🔵 Verify panics if no filename, extracts correctly otherwise

- [x] **Test: Resource block - comment with filename**
  - [x] 🔴 Write test verifying comment prefix decor with extracted filename
  - [x] 🟢 Add comment using `decor_mut().set_prefix()` with filename
  - [x] 🔵 Verify format: `# From: <filename>` (just filename, not full path)

- [x] **Test: Resource block - complete structure**
  - [x] 🔴 Write test for complete block structure
  - [x] 🟢 Ensure all parts work together
  - [x] 🔵 Verify block can be converted to string

## Block Processing - Data Blocks

- [x] **Test: Build data moved block - basic**
  - [x] 🔴 Write test for `build_data_moved_block()` with simple data
  - [x] 🟢 Implement function using `Block::builder()`
  - [x] 🔵 Verify block has correct identifier "moved"

- [x] **Test: Data block - from attribute**
  - [x] 🔴 Write test verifying "from" attribute value
  - [x] 🟢 Add "from" attribute
  - [x] 🔵 Verify format: `data.<data_type>.<data_name>`

- [x] **Test: Data block - to attribute**
  - [x] 🔴 Write test verifying "to" attribute value uses utility function
  - [x] 🟢 Add "to" attribute using `build_to_expression()` with `is_data=true`
  - [x] 🔵 Verify format: `module.<module_name>.data.<data_type>.<data_name>`

- [x] **Test: Data block - comment with filename**
  - [x] 🔴 Write test verifying comment prefix decor
  - [x] 🟢 Add comment using `decor_mut().set_prefix()`
  - [x] 🔵 Verify format: `# From: <filename>`

- [x] **Test: Data block - complete structure**
  - [x] 🔴 Write test for complete block structure
  - [x] 🟢 Ensure all parts work together
  - [x] 🔵 Verify block can be converted to string

## Block Processing - Integration

- [x] **Test: Process resource block from parsed file**
  - [x] 🔴 Write test: parse file → extract → build moved block
  - [x] 🟢 Integrate parsing, extraction, and building
  - [x] 🔵 Verify end-to-end flow works

- [x] **Test: Process data block from parsed file**
  - [x] 🔴 Write test: parse file → extract → build moved block
  - [x] 🟢 Integrate parsing, extraction, and building
  - [x] 🔵 Verify end-to-end flow works

- [x] **Test: Extract labels from resource block**
  - [x] 🔴 Write test extracting type and name from labels
  - [x] 🟢 Extract labels[0] (type) and labels[1] (name)
  - [x] 🔵 Verify correct extraction

- [x] **Test: Extract labels from data block**
  - [x] 🔴 Write test extracting type and name from labels
  - [x] 🟢 Extract labels[0] (type) and labels[1] (name)
  - [x] 🔵 Verify correct extraction

- [x] **Test: Handle multiple blocks in one file**
  - [x] 🔴 Write test with file containing multiple resources
  - [x] 🟢 Process all blocks
  - [x] 🔵 Verify all blocks are processed

## Output Generation

- [x] **Test: Build body from single block**
  - [x] 🔴 Write test building `Body` from one `Block`
  - [x] 🟢 Implement `build_output_body()` using `Body::builder()`
  - [x] 🔵 Verify body contains the block

- [x] **Test: Build body from multiple blocks**
  - [x] 🔴 Write test building `Body` from multiple `Block`s
  - [x] 🟢 Add blocks to body builder
  - [x] 🔵 Verify all blocks are included

- [x] **Test: Body to string conversion**
  - [x] 🔴 Write test converting `Body` to string
  - [x] 🟢 Use `Display` trait (via `to_string()`)
  - [x] 🔵 Verify output is valid HCL

- [x] **Test: Output format - single resource**
  - [x] 🔴 Write test verifying exact output format
  - [x] 🟢 Ensure formatting matches specification
  - [x] 🔵 Verify comment, indentation, spacing

- [x] **Test: Output format - single data**
  - [x] 🔴 Write test verifying exact output format
  - [x] 🟢 Ensure formatting matches specification
  - [x] 🔵 Verify comment, indentation, spacing

- [x] **Test: Output format - multiple blocks**
  - [x] 🔴 Write test verifying multiple blocks format
  - [x] 🟢 Ensure blank lines between blocks
  - [x] 🔵 Verify no trailing blank line

## Main Function Integration

- [x] **Test: Extract testable functions from main**
  - [x] 🔴 Write tests for extracted functions (not main itself)
  - [x] 🟢 Extract logic into testable functions (all functions are testable)
  - [x] 🔵 Verify functions can be tested independently

- [x] **Test: Main function - argument parsing (integration)**
  - [x] 🔴 Write integration test using `std::process::Command`
  - [x] 🟢 Test binary with valid arguments
  - [x] 🔵 Verify arguments are parsed correctly

- [x] **Test: Main function - file discovery (integration)**
  - [x] 🔴 Write integration test using `std::process::Command`
  - [x] 🟢 Test binary with directory containing files
  - [x] 🔵 Verify files are found and processed

- [x] **Test: Main function - process single file (integration)**
  - [x] 🔴 Write integration test processing one file end-to-end
  - [x] 🟢 Use `std::process::Command` to run binary
  - [x] 🔵 Verify output is generated correctly

- [x] **Test: Main function - process multiple files (integration)**
  - [x] 🔴 Write integration test processing multiple files
  - [x] 🟢 Use `std::process::Command` to run binary
  - [x] 🔵 Verify all files are processed

- [x] **Test: Main function - output to stdout (integration)**
  - [x] 🔴 Write integration test capturing stdout output
  - [x] 🟢 Use `std::process::Command` to capture output
  - [x] 🔵 Verify output format is correct HCL

- [x] **Test: Main function - error handling (integration)**
  - [x] 🔴 Write integration test for error scenarios
  - [x] 🟢 Test invalid arguments, missing files, etc.
  - [x] 🔵 Verify appropriate panics or warnings

## Integration Tests

- [x] **Setup: Create test fixtures directory**
  - [x] Create `tests/fixtures/` directory
  - [x] Create sample Terraform files
  - [x] Set up integration test file `tests/integration_test.rs`
  - [x] Document how to build binary for testing: `cargo build` or use `cargo run --bin move_maker`
  - [x] Set up `std::process::Command` examples for capturing stdout/stderr

- [x] **Integration test: Single resource file**
  - [x] 🔴 Write integration test with `tests/fixtures/single_resource.tf`
  - [x] 🟢 Run utility and capture output
  - [x] 🔵 Verify output matches expected format

- [x] **Integration test: Single data file**
  - [x] 🔴 Write integration test with `tests/fixtures/single_data.tf`
  - [x] 🟢 Run utility and capture output
  - [x] 🔵 Verify output matches expected format

- [x] **Integration test: Multiple resources**
  - [x] 🔴 Write integration test with multiple resources
  - [x] 🟢 Run utility and capture output
  - [x] 🔵 Verify all resources generate moved blocks

- [x] **Integration test: Mixed resources and data**
  - [x] 🔴 Write integration test with both types
  - [x] 🟢 Run utility and capture output
  - [x] 🔵 Verify both types generate moved blocks

- [x] **Integration test: Multiple files**
  - [x] 🔴 Write integration test with multiple `.tf` files
  - [x] 🟢 Run utility on directory
  - [x] 🔵 Verify all files are processed

- [x] **Integration test: Invalid HCL file**
  - [x] 🔴 Write integration test with invalid syntax
  - [x] 🟢 Run utility and verify error handling
  - [x] 🔵 Verify other files still processed

- [x] **Integration test: Empty directory**
  - [x] 🔴 Write integration test with empty directory
  - [x] 🟢 Run utility
  - [x] 🔵 Verify no output (or empty output)

## Edge Cases & Error Handling

- [x] **Test: Resource with count meta-argument**
  - [x] 🔴 Write test with resource using `count`
  - [x] 🟢 Process resource (count doesn't affect address)
  - [x] 🔵 Verify moved block generated

- [x] **Test: Resource with for_each meta-argument**
  - [x] 🔴 Write test with resource using `for_each`
  - [x] 🟢 Process resource (for_each doesn't affect address)
  - [x] 🔵 Verify moved block generated

- [x] **Test: Module name with hyphens**
  - [x] 🔴 Write test with module name containing hyphens
  - [x] 🟢 Use module name in addresses
  - [x] 🔵 Verify addresses are correct

- [x] **Test: Module name with underscores**
  - [x] 🔴 Write test with module name containing underscores
  - [x] 🟢 Use module name in addresses
  - [x] 🔵 Verify addresses are correct

- [x] **Test: Resource names with special characters**
  - [x] 🔴 Write test with resource names (if valid in Terraform)
  - [x] 🟢 Handle special characters correctly (Terraform identifiers are alphanumeric + underscore/hyphen, which we already handle)
  - [x] 🔵 Verify addresses are valid (tested via integration tests with various module names)

## Final Verification

- [x] **Run all tests**
  - [x] Run `cargo test` - all tests pass (43 unit tests + 11 integration tests = 54 total)
  - [x] Verify no warnings (only minor unused variable warning fixed)
  - [ ] Check test coverage (optional)

- [x] **Documentation**
  - [x] Update README if needed
  - [x] Document usage examples
  - [x] Add any additional notes

- [x] **Code cleanup**
  - [x] Remove any debug code
  - [x] Ensure consistent formatting
  - [x] Review and refactor if needed
  - [x] Check module line counts - split if > 500 lines (all modules under 500 lines)
  - [x] Verify all unit tests are in nested `#[cfg(test)]` modules
