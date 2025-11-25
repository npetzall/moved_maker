# Move Maker

A CLI utility that parses Terraform files and generates `moved` blocks for refactoring resources into a submodule.

## Overview

When refactoring Terraform code to move resources into a module, you need to tell Terraform about the address changes using `moved` blocks. This tool automates the generation of these blocks by scanning your Terraform files and creating the appropriate `moved` block declarations.

## Installation

```bash
cargo build --release
```

The binary will be available at `target/release/moved_maker`.

## Usage

```bash
moved_maker --src <directory> --module-name <module_name>
```

### Arguments

- `--src <directory>`: Source directory containing Terraform files (`.tf` files in the directory, non-recursive)
- `--module-name <name>`: Name of the module to move resources into

### Example

Given a directory with `main.tf`:
```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345"
  instance_type = "t3.micro"
}
```

Running:
```bash
moved_maker --src . --module-name compute
```

Will output:
```hcl
# From: main.tf
moved {
  from = aws_instance.web
  to   = module.compute.aws_instance.web
}
```

## Features

- **Resource Blocks**: Generates moved blocks for `resource` blocks
- **Multiple Files**: Processes all `.tf` files in the source directory
- **Error Handling**: Continues processing other files if one fails to parse
- **Comments**: Includes source filename in comments for traceability
- **Meta-arguments**: Handles resources with `count` and `for_each` (address format remains the same)

## Address Format

### Resource Blocks
- **From**: `resource_type.resource_name`
- **To**: `module.<module_name>.<resource_type>.<resource_name>`

## Module Name Validation

The module name must be a valid Terraform identifier:
- Must start with a letter or underscore
- Can contain letters, numbers, underscores, and hyphens
- Examples: `compute`, `my-module`, `my_module`, `_private`

## Limitations

- Only processes top-level `resource` blocks (data blocks are ignored as they don't require moved blocks)
- Non-recursive: only searches the specified directory (not subdirectories)
- Ignores blocks with fewer than 2 labels (logs warning and skips)
- Blocks with 3+ labels use only the first 2 (type and name)

## Documentation

- **[DEVELOPMENT.md](DEVELOPMENT.md)**: Installation, usage, testing, and development workflows
- **[TOOLING.md](TOOLING.md)**: Development tools and security tooling configuration
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Guidelines for contributing to the project
- **[SECURITY.md](SECURITY.md)**: Security policy and vulnerability reporting

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
