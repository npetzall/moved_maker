# Move Maker

A CLI utility that parses Terraform files and generates `moved` blocks for refactoring resources and data sources into a submodule.

## Overview

When refactoring Terraform code to move resources and data sources into a module, you need to tell Terraform about the address changes using `moved` blocks. This tool automates the generation of these blocks by scanning your Terraform files and creating the appropriate `moved` block declarations.

## Installation

```bash
cargo build --release
```

The binary will be available at `target/release/move_maker`.

## Usage

```bash
move_maker --src <directory> --module-name <module_name>
```

### Arguments

- `--src <directory>`: Source directory containing Terraform files (`.tf` files in the directory, non-recursive)
- `--module-name <name>`: Name of the module to move resources/data into

### Example

Given a directory with `main.tf`:
```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345"
  instance_type = "t3.micro"
}

data "aws_ami" "example" {
  most_recent = true
}
```

Running:
```bash
move_maker --src . --module-name compute
```

Will output:
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

## Features

- **Resource Blocks**: Generates moved blocks for `resource` blocks
- **Data Blocks**: Generates moved blocks for `data` blocks
- **Multiple Files**: Processes all `.tf` files in the source directory
- **Error Handling**: Continues processing other files if one fails to parse
- **Comments**: Includes source filename in comments for traceability
- **Meta-arguments**: Handles resources with `count` and `for_each` (address format remains the same)

## Address Format

### Resource Blocks
- **From**: `resource_type.resource_name`
- **To**: `module.<module_name>.<resource_type>.<resource_name>`

### Data Blocks
- **From**: `data.<data_type>.<data_name>`
- **To**: `module.<module_name>.data.<data_type>.<data_name>`

## Module Name Validation

The module name must be a valid Terraform identifier:
- Must start with a letter or underscore
- Can contain letters, numbers, underscores, and hyphens
- Examples: `compute`, `my-module`, `my_module`, `_private`

## Limitations

- Only processes top-level `resource` and `data` blocks
- Non-recursive: only searches the specified directory (not subdirectories)
- Ignores blocks with fewer than 2 labels (logs warning and skips)
- Blocks with 3+ labels use only the first 2 (type and name)

## Testing

Run all tests:
```bash
cargo test
```

Run only unit tests:
```bash
cargo test --lib
```

Run only integration tests:
```bash
cargo test --test integration_test
```

## Project Structure

```
src/
  cli.rs           - CLI argument parsing and validation
  file_discovery.rs - Finding .tf files in directory
  parser.rs        - HCL file parsing
  processor.rs     - Block extraction and moved block generation
  output.rs        - Output body generation
  main.rs          - Main orchestration logic

tests/
  fixtures/        - Sample Terraform files for testing
  integration_test.rs - End-to-end integration tests
```

## License

This project is provided as-is for use in Terraform refactoring workflows.

