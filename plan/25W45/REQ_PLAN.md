# Move Maker - Implementation Plan

## Overview
A CLI utility that parses Terraform files and generates `moved` blocks for refactoring resources and data sources into a submodule.

## Requirements
1. Accept `--src` argument: folder containing Terraform files
2. Accept `--module-name` argument: name of the module resources/data should be moved into
3. Parse all `.tf` files in the source directory (non-recursive, only direct children)
4. Find all top-level `resource` blocks
5. Find all top-level `data` blocks
6. Generate `moved` blocks for each found resource/data block
7. Print all `moved` blocks to stdout in HCL format

## Architecture

### Components
1. **CLI Argument Parsing** - Parse `--src` and `--module-name` arguments
2. **File Discovery** - Find all `.tf` files in source directory (non-recursive, only direct children)
3. **HCL Parsing** - Parse each Terraform file using `hcl-rs` (via `hcl::edit`)
4. **Block Extraction** - Extract top-level `resource` and `data` blocks
5. **Moved Block Generation** - Generate `moved` blocks with correct addresses
6. **Output** - Print generated blocks to stdout

### Dependencies
- `hcl-rs = "0.19.4"` - Already in Cargo.toml (provides `hcl::edit`)
- `clap` - For CLI argument parsing (with `derive` feature)
- `env_logger` - For logging warnings (optional, `panic!` is acceptable for simple utility)
- No additional dependencies needed - using `std::fs` for non-recursive file discovery

### Address Format

#### Resource Blocks
- **From**: `resource_type.resource_name`
- **To**: `module.<module_name>.<resource_type>.<resource_name>`

#### Data Blocks
- **From**: `data.<data_type>.<data_name>`
- **To**: `module.<module_name>.data.<data_type>.<data_name>`

### Moved Block Format
```hcl
moved {
  from = <old_address>
  to   = <new_address>
}
```

## Implementation Order
1. Set up CLI argument parsing
2. Implement file discovery
3. Implement HCL parsing
4. Implement block extraction and processing
5. Generate moved blocks with utility functions for Expression building
6. Output formatting

## File Organization
- Start with multiple files (not single file) for better organization with tests
- Split modules when they exceed 500 lines
- Unit tests in nested `#[cfg(test)]` modules within source files
- Integration tests in `tests/` directory

## Error Handling Strategy
- **Fatal errors**: Use `panic!()` (appropriate for simple CLI utility)
- **Warnings**: Log using `env_logger` or `eprintln!()` to stderr
- **File discovery**: Return `Vec<PathBuf>`, panic on fatal errors
- **Block extraction**: Return `Vec<&Block>` (lifetime-safe, verified with hcl-edit API)
- **Invalid blocks**: Log warning and skip (support multiple labels)
- **Filename extraction**: Use `file_name()`, panic if not present

## Testing Strategy
See [TESTING.md](TESTING.md) for detailed testing strategy.

**Summary**:
- Unit tests for individual components
- Integration tests for end-to-end workflow
- Edge case testing (invalid files, missing labels, etc.)
- Test fixtures with sample Terraform files
- Verify output format and correctness
