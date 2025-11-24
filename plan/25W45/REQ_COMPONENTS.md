# Component Breakdown

## 1. CLI Module (`src/cli.rs`)
**Purpose**: Parse command-line arguments

**Input**:
- `--src <path>` - Source directory
- `--module-name <name>` - Module name

**Output**: `Args` struct with validated arguments

**Error Handling**:
- Validate that `--src` exists and is a directory (panic if invalid)
- Validate that `--module-name` is provided, non-empty, AND valid Terraform identifier
- Terraform identifier: alphanumeric + underscore/hyphen, must start with letter/underscore
- Use `panic!()` for validation failures (appropriate for CLI utility)

## 2. File Discovery (`src/file_discovery.rs`)
**Purpose**: Find all Terraform files in source directory

**Function**: `find_terraform_files(src: &Path) -> Vec<PathBuf>`

**Behavior**:
- **Non-recursive**: Only search the supplied folder, do not recurse into subdirectories
- Filter for files with `.tf` extension
- Return list of file paths

**Implementation**:
- Use `std::fs::read_dir()` to read directory contents
- Filter entries to only include files (not directories)
- Check file extension is `.tf`
- Use `panic!()` for fatal errors (directory doesn't exist, permission denied, etc.)

**Error Handling**:
- Fatal errors: `panic!()` (directory doesn't exist, unreadable, etc.)
- Non-fatal: Skip files that can't be read (log warning to stderr)
- Continue processing other files

## 3. HCL Parser (`src/parser.rs`)
**Purpose**: Parse Terraform HCL files

**Function**: `parse_terraform_file(path: &Path) -> Result<Body, Error>`

**Implementation**:
- Use `hcl::edit::parser::parse_body()` to parse file content
- Return parsed `Body` structure

**Why `hcl::edit::parser::parse_body()` instead of `hcl::parse()`?**
- Both functions can parse HCL and return a `Body` structure with a `blocks()` method
- `hcl::parse()` returns `hcl::Body` - simpler, doesn't preserve formatting/comments/whitespace
- `hcl::edit::parser::parse_body()` returns `hcl::edit::Body` - preserves all original formatting, comments, and whitespace
- For Terraform configuration files, `hcl::edit::parse_body()` is the recommended approach as it:
  - Preserves the original file structure (useful if we ever need to edit)
  - Is specifically designed for Terraform configuration parsing
  - Is more commonly used in the Terraform ecosystem
- Both work for our use case (just reading blocks), but `hcl::edit::parse_body()` is more feature-complete

**Error Handling**:
- Return `Result<Body, Error>` for invalid HCL syntax
- Caller should handle errors (log warning to stderr and continue, or panic)
- Error messages should include file path for debugging

## 4. Block Processor (`src/processor.rs`)
**Purpose**: Extract and process resource/data blocks

**Function**: `extract_blocks(body: &Body) -> Vec<&Block>`

**Implementation**:
- Use `body.blocks().iter()` to iterate over all blocks
- Filter blocks where identifier is either `"resource"` or `"data"`
- Return filtered list of blocks
- **Note**: `Vec<&Block>` is lifetime-safe - `body.blocks()` returns `Blocks<'a>` which is `Box<dyn Iterator<Item = &'a Block> + 'a>`
- Blocks are owned by Body, references are valid as long as Body is in scope

**Processing Flow**:
- The extraction function returns a filtered list of blocks
- Process each block with a `for_each`-like iteration
- For each block, extract type and name from labels
- Generate moved block based on block type (resource vs data)

**Block Processing**:
- For each filtered block, check the identifier:
  - If `"resource"`: labels[0] = type, labels[1] = name
  - If `"data"`: labels[0] = type, labels[1] = name
- **Support multiple labels**: Handle blocks with more than 2 labels (use first 2 for type/name)
- **Invalid blocks**: If less than 2 labels, log warning and skip
- Build `Block` structures directly using `Block::builder()`
- Add "from" and "to" attributes using utility functions to build Expression from identifier traversal
- Add comment using `Block::decor_mut().set_prefix()` with filename
- Return decorated `Block` structures (not intermediate data structures)

**Functions**:
- `build_resource_moved_block(resource_type, resource_name, module_name, path: &Path) -> Block`
- `build_data_moved_block(data_type, data_name, module_name, path: &Path) -> Block`
- `build_from_expression(resource_type, resource_name, is_data: bool) -> Expression` - Utility for "from" field (resource/data)
- `build_to_expression(module_name, resource_type, resource_name, is_data: bool) -> Expression` - Utility for "to" field (module path)
- **Filename extraction**: Use `path.file_name().expect("path must have filename")` - panic if not present

## 5. Output Generator (`src/output.rs`)
**Purpose**: Build final Body from collected moved blocks and output to stdout

**Function**:
- `build_output_body(blocks: &[Block]) -> Body` - Build body with all decorated blocks

**Implementation**:
- Use `Body::builder()` to collect all `Block` structures
- Blocks already have comments attached via decor
- Convert final `Body` to string using `Display` trait (via `to_string()` or `println!()`)

**Format**:
```hcl
# From: <filename>
moved {
  from = <from>
  to   = <to>
}
```

**Note**: Uses `BodyBuilder` and `BlockBuilder` from `hcl::edit` instead of string formatting to ensure proper HCL structure.

## 6. Main (`src/main.rs`)
**Purpose**: Orchestrate all components

**Flow**:
1. Parse CLI arguments (panic on validation failure)
2. Discover Terraform files (non-recursive, only in supplied folder) - panic on fatal errors
3. For each file:
   - Parse HCL using `parse_body()` - log warning and continue on parse error
   - Extract blocks using `body.blocks().iter().filter()` for "resource" or "data"
   - For each filtered block (for_each-like iteration):
     - Extract type and name from labels (log warning and skip if < 2 labels)
     - Build decorated `Block` structure with comment using `path: &Path`
     - Collect blocks
4. Build final `Body` from collected blocks using `build_output_body()`
5. Print `Body` to stdout using `Display` trait
