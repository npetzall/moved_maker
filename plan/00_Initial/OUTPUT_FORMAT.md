# Output Format Specification

## Moved Block Format

### Standard Format (with source file comment)
```hcl
# From: <filename>
moved {
  from = <old_address>
  to   = <new_address>
}
```

### Example Output

#### Single Resource
```hcl
# From: main.tf
moved {
  from = aws_instance.web
  to   = module.compute.aws_instance.web
}
```

#### Single Data Source
```hcl
# From: data.tf
moved {
  from = data.aws_ami.example
  to   = module.compute.data.aws_ami.example
}
```

#### Multiple Blocks
```hcl
# From: main.tf
moved {
  from = aws_instance.web
  to   = module.compute.aws_instance.web
}

# From: storage.tf
moved {
  from = aws_s3_bucket.data
  to   = module.compute.aws_s3_bucket.data
}

# From: data.tf
moved {
  from = data.aws_ami.example
  to   = module.compute.data.aws_ami.example
}
```

## Formatting Rules

### Comments
- Include source filename comment before each moved block
- Format: `# From: <filename>` (filename only, not full path)
- Comment at column 0, no indentation

### Indentation
- Use 2 spaces for indentation
- `moved` keyword at column 0
- Opening brace on same line
- `from` and `to` indented with 2 spaces
- Closing brace on its own line at column 0

### Spacing
- Single blank line between moved blocks
- No trailing blank line at end of output

### Address Formatting
- Addresses are unquoted (Terraform identifiers)
- Use dot notation: `resource_type.resource_name`
- Module references: `module.<name>.<resource_type>.<resource_name>`

## Implementation

### Using BodyBuilder and BlockBuilder

**Building Moved Blocks Directly** (in block processor):
```rust
use hcl::edit::structure::{Attribute, Block};
use hcl::edit::expr::Expression;
use hcl::edit::Ident;
use std::path::Path;

// For resource blocks
fn build_resource_moved_block(
    resource_type: &str,
    resource_name: &str,
    module_name: &str,
    path: &Path,
) -> Block {
    let mut block = Block::builder(Ident::new("moved"))
        .attribute(Attribute::new("from", build_from_expression(resource_type, resource_name, false)))
        .attribute(Attribute::new("to", build_to_expression(module_name, resource_type, resource_name, false)))
        .build();
    
    // Add comment as prefix decor
    let filename = path.file_name().expect("path must have filename").to_string_lossy();
    let comment = format!("# From: {}\n", filename);
    block.decor_mut().set_prefix(&comment);
    
    block
}

// For data blocks
fn build_data_moved_block(
    data_type: &str,
    data_name: &str,
    module_name: &str,
    path: &Path,
) -> Block {
    let mut block = Block::builder(Ident::new("moved"))
        .attribute(Attribute::new("from", build_from_expression(data_type, data_name, true)))
        .attribute(Attribute::new("to", build_to_expression(module_name, data_type, data_name, true)))
        .build();
    
    // Add comment as prefix decor
    let filename = path.file_name().expect("path must have filename").to_string_lossy();
    let comment = format!("# From: {}\n", filename);
    block.decor_mut().set_prefix(&comment);
    
    block
}

// Utility functions (see BLOCK_PROCESSING.md for full implementation)
fn build_from_expression(resource_type: &str, resource_name: &str, is_data: bool) -> Expression {
    // Implementation in processor.rs
}

fn build_to_expression(
    module_name: &str,
    resource_type: &str,
    resource_name: &str,
    is_data: bool,
) -> Expression {
    // Implementation in processor.rs
}
```

**Building Final Body** (in output generator):
```rust
use hcl::edit::structure::{Body, Block};

fn build_output_body(blocks: &[Block]) -> Body {
    Body::builder()
        .blocks(blocks.iter().cloned())
        .build()
}
```

**Output Generation**:
```rust
// Collect decorated blocks during processing
let mut moved_blocks = Vec::new();
// ... process files and build blocks ...

// Build the body from collected blocks
let body = build_output_body(&moved_blocks);

// Convert to string using Display trait
println!("{}", body);
```

**Note**: 
- Blocks are built directly with comments attached via decor
- No intermediate data structures needed
- The `Body` type implements `Display`, so it can be directly converted to a string
- Formatting (indentation, spacing) is handled by the hcl-edit library

## Validation

### Address Validation
- Ensure addresses are valid Terraform identifiers
- No special characters (except dots for separation)
- Module name should be valid identifier

### Output Validation
- Each moved block should be valid HCL
- Can be directly pasted into Terraform configuration
- Should work with `terraform plan` and `terraform apply`

