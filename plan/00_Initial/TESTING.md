# Testing Strategy

## Overview
Testing strategy for the move_maker utility to ensure correct generation of moved blocks for Terraform resources and data sources.

## Test Types

### 1. Unit Tests
Test individual functions and components in isolation.

#### CLI Argument Parsing
- Test valid arguments
- Test missing required arguments
- Test invalid directory path
- Test non-directory path
- Test empty module name

#### File Discovery
- Test finding `.tf` files in directory
- Test ignoring non-`.tf` files
- Test ignoring subdirectories (non-recursive)
- Test empty directory
- Test directory with no `.tf` files

#### HCL Parsing
- Test parsing valid Terraform files
- Test handling invalid HCL syntax
- Test handling empty files
- Test handling files with only comments

#### Block Extraction
- Test extracting resource blocks
- Test extracting data blocks
- Test ignoring other block types (locals, variables, etc.)
- Test handling blocks with missing labels
- Test handling blocks with only one label

#### Block Processing
- Test resource block address generation
- Test data block address generation
- Test comment generation with filename
- Test module name in addresses

#### Output Generation
- Test Body building from blocks
- Test correct HCL formatting
- Test comment placement
- Test multiple blocks output

### 2. Integration Tests
Test the full workflow from file input to output.

#### End-to-End Tests
- Test complete workflow with sample Terraform files
- Test multiple files in directory
- Test resource and data blocks together
- Verify output format matches expected HCL

#### Sample Test Cases

**Test Case 1: Single Resource**
```hcl
# Input: main.tf
resource "aws_instance" "web" {
  instance_type = "t2.micro"
}
```
Expected output:
```hcl
# From: main.tf
moved {
  from = aws_instance.web
  to   = module.compute.aws_instance.web
}
```

**Test Case 2: Single Data Source**
```hcl
# Input: data.tf
data "aws_ami" "example" {
  most_recent = true
}
```
Expected output:
```hcl
# From: data.tf
moved {
  from = data.aws_ami.example
  to   = module.compute.data.aws_ami.example
}
```

**Test Case 3: Multiple Resources**
```hcl
# Input: main.tf
resource "aws_instance" "web" {}
resource "aws_s3_bucket" "data" {}
```
Expected output:
```hcl
# From: main.tf
moved {
  from = aws_instance.web
  to   = module.compute.aws_instance.web
}

# From: main.tf
moved {
  from = aws_s3_bucket.data
  to   = module.compute.aws_s3_bucket.data
}
```

**Test Case 4: Mixed Resources and Data**
```hcl
# Input: main.tf
resource "aws_instance" "web" {}
data "aws_ami" "example" {}
```
Expected output:
```hcl
# From: main.tf
moved {
  from = aws_instance.web
  to   = module.compute.aws_instance.web
}

# From: main.tf
moved {
  from = data.aws_ami.example
  to   = module.compute.data.aws_ami.example
}
```

### 3. Edge Case Tests

#### Invalid Input
- Invalid HCL syntax
- Missing block labels
- Blocks with only one label
- Empty files
- Files with only whitespace/comments

#### Special Cases
- Resource names with special characters (if valid in Terraform)
- Very long resource names
- Module names with hyphens/underscores
- Multiple files with same resource names (different files)

### 4. Error Handling Tests
- Test graceful handling of parse errors
- Test warning messages for invalid files
- Test continuation after errors
- Test proper exit codes

## Test Implementation

### Unit Tests Location
- Unit tests in same file as code (Rust convention)
- Use `#[cfg(test)]` module
- Example: `src/main.rs` or `src/processor.rs`

### Integration Tests Location
- Integration tests in `tests/` directory
- Create `tests/integration_test.rs`
- Use sample Terraform files in `tests/fixtures/`

### Integration Test Setup
- Build binary: `cargo build` (binary will be in `target/debug/move_maker`)
- Or use `cargo run --bin move_maker` for testing
- Use `std::process::Command` to execute binary and capture output
- Example structure:
```rust
use std::process::Command;

#[test]
fn test_single_resource() {
    let output = Command::new("target/debug/move_maker")
        .args(&["--src", "tests/fixtures", "--module-name", "compute"])
        .output()
        .expect("Failed to execute command");
    
    let stdout = String::from_utf8(output.stdout).unwrap();
    // Verify output matches expected format
}
```

### Test Fixtures
Create test fixtures directory:
```
tests/
  fixtures/
    single_resource.tf
    single_data.tf
    multiple_resources.tf
    mixed.tf
    invalid_syntax.tf
    empty.tf
```

### Example Test Structure

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use std::path::Path;

    #[test]
    fn test_build_resource_moved_block() {
        let path = Path::new("main.tf");
        let block = build_resource_moved_block(
            "aws_instance",
            "web",
            "compute",
            path
        );
        
        // Verify block structure
        assert_eq!(block.ident.value().to_string(), "moved");
        // Verify attributes
        // Verify comment
    }

    #[test]
    fn test_file_discovery() {
        // Create temp directory with .tf files
        // Test file discovery
    }
}
```

## Test Execution

### Run All Tests
```bash
cargo test
```

### Run Specific Test
```bash
cargo test test_build_resource_moved_block
```

### Run Integration Tests
```bash
cargo test --test integration_test
```

## Test Coverage Goals
- Unit test coverage for all public functions
- Integration tests for main workflows
- Edge case coverage for error handling
- Verify output format correctness

## Manual Testing
- Test with real Terraform configurations
- Verify output can be pasted into Terraform files
- Test with `terraform plan` to ensure moved blocks are valid
- Test with different module names

