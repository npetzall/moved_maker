# File Parsing Strategy

## File Discovery

### Approach: Use `std::fs::read_dir` (non-recursive)
- **Non-recursive**: Only search the supplied folder, do not recurse into subdirectories
- Filter for `.tf` files only
- Handle errors gracefully (skip unreadable files)
- No external dependency needed

### Implementation
```rust
use std::fs;
use std::path::{Path, PathBuf};

fn find_terraform_files(src: &Path) -> Result<Vec<PathBuf>, Box<dyn std::error::Error>> {
    let mut files = Vec::new();
    
    for entry in fs::read_dir(src)? {
        let entry = entry?;
        let path = entry.path();
        
        // Only process files (not directories)
        if path.is_file() {
            // Check if extension is .tf
            if path.extension().map(|e| e == "tf").unwrap_or(false) {
                files.push(path);
            }
        }
    }
    
    Ok(files)
}
```

## HCL Parsing

### Using `hcl-rs` via `hcl::edit`
The `hcl-rs` crate re-exports `hcl-edit` functionality.

### API Usage
```rust
use hcl::edit::parser::parse_body;

fn parse_terraform_file(path: &Path) -> Result<hcl::edit::structure::Body, Box<dyn std::error::Error>> {
    let content = fs::read_to_string(path)?;
    let body = parse_body(&content)?;
    Ok(body)
}
```

### Why `hcl::edit::parser::parse_body()` instead of `hcl::parse()`?
- Both functions can parse HCL and return a `Body` structure with a `blocks()` method
- `hcl::parse()` returns `hcl::Body` - simpler, doesn't preserve formatting/comments/whitespace
- `hcl::edit::parser::parse_body()` returns `hcl::edit::Body` - preserves all original formatting, comments, and whitespace
- For Terraform configuration files, `hcl::edit::parse_body()` is the recommended approach
- Both work for reading blocks, but `hcl::edit::parse_body()` is more feature-complete and commonly used

### Block Structure
From `hcl-rs` documentation:
- `Body` contains a collection of `Block` items
- `Block` has:
  - `ident: Decorated<Ident>` - The block identifier (e.g., "resource", "data")
  - `labels: Vec<BlockLabel>` - The block labels (e.g., ["aws_instance", "example"])
  - `body: Body` - The block's body

### Accessing Block Information
```rust
// Get identifier
let ident = block.ident.value().to_string(); // "resource" or "data"

// Get labels
let labels: Vec<String> = block.labels
    .iter()
    .map(|label| label.value().to_string())
    .collect();

// For resource: labels[0] = type, labels[1] = name
// For data: labels[0] = type, labels[1] = name
```

## Error Handling

### File Reading Errors
- Log warning but continue processing other files
- Use `eprintln!` for warnings

### HCL Parsing Errors
- Log warning with file path
- Continue processing other files
- Don't fail entire operation on single file error

### Example Error Handling
```rust
for file_path in terraform_files {
    match parse_terraform_file(&file_path) {
        Ok(body) => {
            // Process body
        }
        Err(e) => {
            eprintln!("Warning: Failed to parse {}: {}", file_path.display(), e);
        }
    }
}
```

