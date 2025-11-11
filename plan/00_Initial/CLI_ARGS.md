# CLI Arguments Design

## Command Structure
```bash
move_maker --src <directory> --module-name <name>
```

## Arguments

### `--src` / `-s`
- **Type**: String (path)
- **Required**: Yes
- **Description**: Source folder containing Terraform files
- **Validation**:
  - Must exist
  - Must be a directory (not a file)
  - Should be readable

### `--module-name` / `-m`
- **Type**: String
- **Required**: Yes
- **Description**: Name of the module that resources and data should be moved into
- **Validation**:
  - Must be non-empty
  - Must be a valid Terraform identifier:
    - Alphanumeric characters, underscores, and hyphens
    - Must start with letter or underscore
    - Cannot start with number
  - Use `panic!()` on validation failure (appropriate for CLI utility)

## Implementation

### Using `clap` with derive feature
```rust
use clap::Parser;

#[derive(Parser, Debug)]
#[command(name = "move_maker")]
#[command(about = "Generates moved blocks for Terraform resources and data sources when refactoring into a submodule")]
struct Args {
    /// Source folder containing Terraform files
    #[arg(short, long)]
    src: String,

    /// Module name that resources and data should be moved into
    #[arg(short, long)]
    module_name: String,
}
```

### Validation Logic
```rust
fn validate_args(args: &Args) -> Result<(), String> {
    let src_path = Path::new(&args.src);
    
    if !src_path.exists() {
        return Err(format!("Source directory '{}' does not exist", args.src));
    }
    
    if !src_path.is_dir() {
        return Err(format!("'{}' is not a directory", args.src));
    }
    
    if args.module_name.is_empty() {
        panic!("Module name cannot be empty");
    }
    
    // Validate Terraform identifier format
    if !is_valid_terraform_identifier(&args.module_name) {
        panic!("Module name '{}' is not a valid Terraform identifier. Must start with letter/underscore and contain only alphanumeric, underscore, or hyphen", args.module_name);
    }
    
    Ok(())
}

fn is_valid_terraform_identifier(name: &str) -> bool {
    if name.is_empty() {
        return false;
    }
    
    let first_char = name.chars().next().unwrap();
    if !first_char.is_alphabetic() && first_char != '_' {
        return false;
    }
    
    name.chars().all(|c| c.is_alphanumeric() || c == '_' || c == '-')
}
```

### Error Messages
- Clear, actionable error messages
- Exit code 1 on validation failure
- Print to stderr

