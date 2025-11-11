# Block Processing Logic

## Block Types to Process

### Resource Blocks
- **Pattern**: `resource "<TYPE>" "<NAME>" { ... }`
- **Example**: `resource "aws_instance" "web" { ... }`

### Data Blocks
- **Pattern**: `data "<TYPE>" "<NAME>" { ... }`
- **Example**: `data "aws_ami" "example" { ... }`

## Block Extraction

### From Parsed Body
```rust
use hcl::edit::structure::{Body, Block};

fn extract_blocks(body: &Body) -> Vec<&Block> {
    body.blocks()
        .iter()
        .filter(|block| {
            let ident = block.ident.value().to_string();
            ident == "resource" || ident == "data"
        })
        .collect()
}
```

**Note**: Use `body.blocks().iter()` to get an iterator, then filter for blocks with identifier "resource" or "data".

### Block Information Extraction

#### Resource Block
```rust
fn extract_resource_info(block: &Block) -> Option<(String, String)> {
    let ident = block.ident.value().to_string();
    if ident != "resource" {
        return None;
    }
    
    let labels: Vec<String> = block.labels
        .iter()
        .map(|l| l.value().to_string())
        .collect();
    
    if labels.len() >= 2 {
        Some((labels[0].clone(), labels[1].clone()))
    } else {
        None // Invalid resource block (missing type or name)
    }
}
```

#### Data Block
```rust
fn extract_data_info(block: &Block) -> Option<(String, String)> {
    let ident = block.ident.value().to_string();
    if ident != "data" {
        return None;
    }
    
    let labels: Vec<String> = block.labels
        .iter()
        .map(|l| l.value().to_string())
        .collect();
    
    if labels.len() >= 2 {
        Some((labels[0].clone(), labels[1].clone()))
    } else {
        None // Invalid data block (missing type or name)
    }
}
```

## Address Generation

### Resource Address
- **From**: `{resource_type}.{resource_name}`
- **To**: `module.{module_name}.{resource_type}.{resource_name}`

**Example**:
- Resource: `resource "aws_instance" "web"`
- From: `aws_instance.web`
- To: `module.compute.aws_instance.web`

### Data Address
- **From**: `data.{data_type}.{data_name}`
- **To**: `module.{module_name}.data.{data_type}.{data_name}`

**Example**:
- Data: `data "aws_ami" "example"`
- From: `data.aws_ami.example`
- To: `module.compute.data.aws_ami.example`

## Moved Block Generation

**Note**: Blocks are built directly as decorated `Block` structures using `BlockBuilder`. No intermediate data structures are needed.

### Generation Functions

**Note**: These functions build decorated `Block` structures directly with comments attached via decor.

#### For Resource
```rust
use hcl::edit::structure::{Attribute, Block};
use hcl::edit::expr::Expression;
use hcl::edit::Ident;
use std::path::Path;

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
```

#### For Data
```rust
use std::path::Path;

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
```

### Utility Functions for Expression Building

**Note**: These utility functions build Expression structures for identifier traversal paths using `hcl::expr::TraversalBuilder`. The approach:
1. Use `hcl::expr::Traversal::builder(Variable::unchecked(...))` to start a traversal
2. Chain `.attr(...)` calls to build the path (e.g., `module.module_name.resource_type.resource_name`)
3. Call `.build()` to create a `hcl::expr::Traversal`
4. Convert to `hcl::edit::expr::Expression` using `From`/`Into` traits (automatic conversion)

**Reference**: [TraversalBuilder documentation](https://docs.rs/hcl-rs/latest/hcl/expr/struct.TraversalBuilder.html)

```rust
use hcl::expr::{Traversal, Variable};
use hcl::edit::expr::Expression;

// Utility function for building "from" expression (identifier traversal)
// For resources: resource_type.resource_name
// For data: data.data_type.data_name
fn build_from_expression(
    resource_type: &str,
    resource_name: &str,
    is_data: bool,
) -> Expression {
    if is_data {
        // Build: data.data_type.data_name
        // Create traversal: data -> data_type -> data_name
        let traversal = Traversal::builder(Variable::unchecked("data"))
            .attr(resource_type)
            .attr(resource_name)
            .build();
        // Convert hcl-rs Traversal to hcl-edit Expression via From/Into
        traversal.into()
    } else {
        // Build: resource_type.resource_name
        // Create traversal: resource_type -> resource_name
        let traversal = Traversal::builder(Variable::unchecked(resource_type))
            .attr(resource_name)
            .build();
        // Convert hcl-rs Traversal to hcl-edit Expression via From/Into
        traversal.into()
    }
}

// Utility function for building "to" expression (module path)
// For resources: module.module_name.resource_type.resource_name
// For data: module.module_name.data.data_type.data_name
fn build_to_expression(
    module_name: &str,
    resource_type: &str,
    resource_name: &str,
    is_data: bool,
) -> Expression {
    if is_data {
        // Build: module.module_name.data.data_type.data_name
        // Create traversal: module -> module_name -> data -> data_type -> data_name
        let traversal = Traversal::builder(Variable::unchecked("module"))
            .attr(module_name)
            .attr("data")
            .attr(resource_type)
            .attr(resource_name)
            .build();
        // Convert hcl-rs Traversal to hcl-edit Expression via From/Into
        traversal.into()
    } else {
        // Build: module.module_name.resource_type.resource_name
        // Create traversal: module -> module_name -> resource_type -> resource_name
        let traversal = Traversal::builder(Variable::unchecked("module"))
            .attr(module_name)
            .attr(resource_type)
            .attr(resource_name)
            .build();
        // Convert hcl-rs Traversal to hcl-edit Expression via From/Into
        traversal.into()
    }
}
```

### Processing Flow
After extracting blocks with `body.blocks().iter().filter()`, iterate over the results (for_each-like):
```rust
let mut moved_blocks = Vec::new();

for block in filtered_blocks {
    // Extract type and name from labels
    // Build decorated Block structure directly
    let moved_block = match block.ident.value().to_string().as_str() {
        "resource" => build_resource_moved_block(...),
        "data" => build_data_moved_block(...),
        _ => continue,
    };
    moved_blocks.push(moved_block);
}
```

## Edge Cases

### Invalid Blocks
- Blocks with less than 2 labels: Log warning to stderr and skip
- Blocks with 2+ labels: Use first 2 labels (type and name), ignore additional labels
- Log warnings using `eprintln!()` or `env_logger`

### Nested Blocks
- Only process top-level blocks
- Ignore blocks nested inside other blocks (they're already in the module)

### Count/For Each
- Resources with `count` or `for_each` are handled the same way
- The address format remains the same (Terraform handles indexing)

