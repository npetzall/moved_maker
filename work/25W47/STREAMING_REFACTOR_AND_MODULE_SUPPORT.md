# Implementation Plan: Streaming Refactor with Module Block Support

## Overview

This plan combines two major features:
1. **Streaming Refactor**: Refactor to use lazy evaluation with better separation of concerns
2. **Module Block Support**: Add support for module blocks in addition to resource blocks

Both features will be implemented following **Object-Oriented Programming (OOP)** principles and **Test-Driven Development (TDD)** methodology.

## Design Principles

### OOP Principles
- **Encapsulation**: Each struct holds its own data and behavior
- **Polymorphism**: Trait-based interfaces for common behavior
- **Single Responsibility**: Each component has one clear purpose
- **Composition**: Build complex behavior from simple components

### TDD Methodology
- Write tests first (Red)
- Implement minimal code to pass (Green)
- Refactor while keeping tests green (Refactor)
- Each component tested independently before integration

### Architecture Goals
- **Lazy Evaluation**: No work until iterator is consumed
- **Separation of Concerns**: Address building separate from block construction
- **Extensibility**: Easy to add new block types
- **Memory Efficiency**: Process files one at a time
- **Flexible Label Handling**: Use `Vec<String>` for labels to support varying numbers of labels per block type
- **Single Responsibility**: `AddressBuilder` is a pure utility with no state; file paths stored where they're used

---

## Design Decisions

### Label Storage
- **Use `Vec<String>` for labels**: Blocks can have varying numbers of labels (resource blocks have 2, module blocks have 1, future blocks may have different counts). Storing labels as a vector provides flexibility while maintaining type safety.
- **Convenience accessors**: Helper methods like `resource_type()` and `resource_name()` provide convenient access to specific label indices while keeping the underlying structure flexible.

### AddressBuilder Design
- **Pure utility, no state**: `AddressBuilder` is a stateless utility for building address expressions. It does not store file paths or any other metadata.
- **Single Responsibility**: `AddressBuilder` only builds expressions from segments - nothing else.
- **File paths stored where used**: `file_path` is stored directly in `MovedResource` and `MovedModule` where it's needed for comments, not in `AddressBuilder`.

### ToMovedBlock Trait Design
- **Default implementation for common logic**: The `to_block()` method has a default implementation that handles the common structure (attribute creation, indentation, block building, comment). This follows the Template Method pattern.
- **Required methods for block-specific logic**: Implementors only need to provide `from_expression()`, `to_expression()`, and `file_path()` methods, which contain the block-specific logic.
- **DRY principle**: Eliminates code duplication between `MovedResource` and `MovedModule` implementations.
- **Extensibility**: New block types can easily implement the trait by providing the three required methods, automatically getting the common block-building logic.

### Iterator Adapter Pipeline Design
- **Ownership chain**: Each adapter owns the next in the pipeline: `MovedBlockBuilder` → `TerraformFiles` → `ParsedFiles` → `MovedBlocks`. This creates a clear ownership hierarchy and makes the pipeline self-contained.
- **Single responsibility per adapter**:
  - `TerraformFiles`: File discovery only
  - `ParsedFiles`: File parsing only (owns `TerraformFiles`)
  - `MovedBlocks`: Block extraction and conversion (owns `ParsedFiles`)
- **File-level laziness**: Files are processed one at a time. `MovedBlocks` only loads the next file when the current file's blocks are exhausted. This is the meaningful level of laziness.
- **Block collection**: Blocks from the current body are collected into a `Vec<Block>`. This is appropriate because hcl-edit requires the entire file to be parsed before blocks can be accessed, so the file is already fully in memory. Block-level laziness within an already-parsed file provides no practical benefit.
- **Clean state management**: When all blocks from the current body are processed, the state is cleared and the next body is loaded. This eliminates deep nesting and makes the control flow clear.

---

## Phase 1: Foundation - AddressBuilder (TDD)

### 1.1 Write Tests for AddressBuilder

**File**: `src/output.rs`

**Task**: Create unit tests for `AddressBuilder` before implementation

- [x] Add test module `mod tests` in `output.rs`
- [x] Write test `test_address_builder_new()` - verify constructor
- [x] Write test `test_address_builder_build_single_segment()` - build expression with one segment
- [x] Write test `test_address_builder_build_multiple_segments()` - build expression with multiple segments
- [x] Write test `test_address_builder_build_resource_expression()` - build `resource_type.resource_name`
- [x] Write test `test_address_builder_build_module_expression()` - build `module.module_name`
- [x] Write test `test_address_builder_build_nested_expression()` - build `module.name.resource_type.resource_name`
- [x] Verify all tests fail (Red phase)

**Expected test structure**:
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_address_builder_new() {
        let builder = AddressBuilder::new();
        // Builder is just a utility, no state to verify
    }

    #[test]
    fn test_address_builder_build_single_segment() {
        let builder = AddressBuilder::new();
        let expr = builder.build(&["aws_instance"]);
        assert!(matches!(expr, Expression::Traversal(_)));
    }

    // ... more tests
}
```

### 1.2 Implement AddressBuilder

**File**: `src/output.rs`

**Task**: Implement `AddressBuilder` to make tests pass

- [x] Add `AddressBuilder` struct (no fields needed - pure utility)
- [x] Implement `new() -> Self` constructor
- [x] Implement `build(&self, segments: &[&str]) -> Expression` method
- [x] Use string parsing approach (Traversal::builder() API not directly compatible with edit::expr::Expression)
- [x] Verify all tests pass (Green phase)

**Expected implementation**:
```rust
pub struct AddressBuilder;

impl AddressBuilder {
    pub fn new() -> Self {
        Self
    }

    pub fn build(&self, segments: &[&str]) -> Expression {
        let mut builder = hcl::expr::Traversal::builder();
        for segment in segments {
            builder = builder.attr(segment);
        }
        Expression::Traversal(builder.build())
    }
}
```

**Note**: `AddressBuilder` is a pure utility for building address expressions. It has no state and follows the Single Responsibility Principle - it only builds expressions, nothing else.

---

## Phase 2: ToMovedBlock Trait (TDD)

### 2.1 Write Tests for ToMovedBlock Trait

**File**: `src/output.rs`

**Task**: Define trait and write tests for trait behavior

- [x] Define `ToMovedBlock` trait with required methods and default `to_block()` implementation
- [x] Write test `test_to_moved_block_trait_exists()` - verify trait can be used
- [x] Verify test compiles but trait implementations don't exist yet (Red phase)

**Expected trait definition**:
```rust
pub trait ToMovedBlock {
    /// Build the "from" expression (block-specific logic)
    fn from_expression(&self) -> Expression;

    /// Build the "to" expression (block-specific logic)
    fn to_expression(&self) -> Expression;

    /// Get the file path for the comment (block-specific)
    fn file_path(&self) -> &Path;

    /// Default implementation that builds the moved block
    /// This handles the common logic: attribute creation, indentation, block building, and comment
    fn to_block(&self) -> Result<Block> {
        let from_expr = self.from_expression();
        let to_expr = self.to_expression();

        // Create attributes with indentation
        let mut from_attr = Attribute::new(Ident::new("from"), from_expr);
        from_attr.decor_mut().set_prefix("  ");

        let mut to_attr = Attribute::new(Ident::new("to"), to_expr);
        to_attr.decor_mut().set_prefix("  ");

        let mut block = Block::builder(Ident::new("moved"))
            .attribute(from_attr)
            .attribute(to_attr)
            .build();

        // Add comment with filename
        let filename = self.file_path()
            .file_name()
            .context("Path must have filename")?
            .to_string_lossy();
        let comment = format!("# From: {}\n", filename);
        block.decor_mut().set_prefix(comment.as_str());

        Ok(block)
    }
}
```

**Note**: The default `to_block()` implementation follows the Template Method pattern - it defines the structure while allowing implementors to provide the specific expression-building logic. This eliminates code duplication between `MovedResource` and `MovedModule`.

---

## Phase 3: MovedResource (TDD)

### 3.1 Write Tests for MovedResource

**File**: `src/output.rs`

**Task**: Write comprehensive tests for `MovedResource`

- [x] Write test `test_moved_resource_new()` - verify constructor
- [x] Write test `test_moved_resource_build_from_expression()` - verify from expression
- [x] Write test `test_moved_resource_build_to_expression()` - verify to expression
- [x] Write test `test_moved_resource_to_block()` - verify block conversion
- [x] Write test `test_moved_resource_to_block_has_comment()` - verify file comment
- [x] Write test `test_moved_resource_to_block_has_indented_attributes()` - verify formatting
- [x] Write test `test_moved_resource_to_block_output_format()` - verify exact output format
- [x] Verify all tests fail (Red phase)

**Expected test structure**:
```rust
#[test]
fn test_moved_resource_new() -> Result<()> {
    let path = PathBuf::from("main.tf");
    let labels = vec!["aws_instance".to_string(), "web".to_string()];
    let resource = MovedResource::new(
        labels.clone(),
        path,
        "compute".to_string(),
    )?;
    assert_eq!(resource.labels(), &labels);
    assert_eq!(resource.resource_type(), "aws_instance");
    assert_eq!(resource.resource_name(), "web");
    Ok(())
}

#[test]
fn test_moved_resource_to_block() -> Result<()> {
    let path = PathBuf::from("main.tf");
    let labels = vec!["aws_instance".to_string(), "web".to_string()];
    let resource = MovedResource::new(
        labels,
        path,
        "compute".to_string(),
    )?;
    let block = resource.to_block()?;
    assert_eq!(block.ident.value().to_string(), "moved");
    Ok(())
}
```

### 3.2 Implement MovedResource

**File**: `src/output.rs`

**Task**: Implement `MovedResource` to make tests pass

- [x] Add `MovedResource` struct with fields:
  - `labels: Vec<String>` - All labels from the block (flexible for any number)
  - `file_path: PathBuf` - Source file path (for comment)
  - `target_module_name: String` - Target module name
- [x] Implement `new()` constructor that validates labels (must have at least 2)
- [x] Implement accessor methods:
  - `labels(&self) -> &[String]` - Access all labels
  - `resource_type(&self) -> &str` - Convenience accessor for labels[0]
  - `resource_name(&self) -> &str` - Convenience accessor for labels[1]
- [x] Implement `build_from_expression()` - creates `AddressBuilder::new()` and uses `build()` with first 2 labels (private method)
- [x] Implement `build_to_expression()` - creates `AddressBuilder::new()` and uses `build()` with `["module", target_module_name, labels[0], labels[1]]` (private method)
- [x] Implement `ToMovedBlock` trait for `MovedResource`:
  - `from_expression()` delegates to `build_from_expression()`
  - `to_expression()` delegates to `build_to_expression()`
  - `file_path()` returns `&self.file_path`
  - `to_block()` uses the default implementation from the trait
- [x] Verify all tests pass (Green phase)

**Expected implementation**:
```rust
pub struct MovedResource {
    labels: Vec<String>,
    file_path: PathBuf,
    target_module_name: String,
}

impl MovedResource {
    pub fn new(
        labels: Vec<String>,
        file_path: PathBuf,
        target_module_name: String,
    ) -> Result<Self> {
        if labels.len() < 2 {
            return Err(anyhow::anyhow!("Resource blocks must have at least 2 labels"));
        }
        Ok(Self {
            labels,
            file_path,
            target_module_name,
        })
    }

    pub fn labels(&self) -> &[String] {
        &self.labels
    }

    pub fn resource_type(&self) -> &str {
        &self.labels[0]
    }

    pub fn resource_name(&self) -> &str {
        &self.labels[1]
    }

    fn build_from_expression(&self) -> Expression {
        AddressBuilder::new().build(&[&self.labels[0], &self.labels[1]])
    }

    fn build_to_expression(&self) -> Expression {
        AddressBuilder::new().build(&[
            "module",
            &self.target_module_name,
            &self.labels[0],
            &self.labels[1],
        ])
    }
}

impl ToMovedBlock for MovedResource {
    fn from_expression(&self) -> Expression {
        self.build_from_expression()  // Delegates to private method
    }

    fn to_expression(&self) -> Expression {
        self.build_to_expression()  // Delegates to private method
    }

    fn file_path(&self) -> &Path {
        &self.file_path
    }

    // to_block() uses the default implementation from the trait
}
```

---

## Phase 4: MovedModule (TDD)

### 4.1 Write Tests for MovedModule

**File**: `src/output.rs`

**Task**: Write comprehensive tests for `MovedModule`

- [x] Write test `test_moved_module_new()` - verify constructor
- [x] Write test `test_moved_module_build_from_expression()` - verify from expression (`module.module_name`)
- [x] Write test `test_moved_module_build_to_expression()` - verify to expression (`module.target_module.module.module_name`)
- [x] Write test `test_moved_module_to_block()` - verify block conversion
- [x] Write test `test_moved_module_to_block_has_comment()` - verify file comment
- [x] Write test `test_moved_module_to_block_has_indented_attributes()` - verify formatting
- [x] Write test `test_moved_module_to_block_output_format()` - verify exact output format
- [x] Verify all tests fail (Red phase)

**Expected test structure**:
```rust
#[test]
fn test_moved_module_new() {
    let path = PathBuf::from("main.tf");
    let labels = vec!["web_server".to_string()];
    let module = MovedModule::new(
        labels.clone(),
        path,
        "a".to_string(),
    )?;
    assert_eq!(module.labels(), &labels);
    assert_eq!(module.module_name_local(), "web_server");
    Ok(())
}

#[test]
fn test_moved_module_to_block() -> Result<()> {
    let path = PathBuf::from("main.tf");
    let labels = vec!["web_server".to_string()];
    let module = MovedModule::new(
        labels,
        path,
        "a".to_string(),
    )?;
    let block = module.to_block()?;
    assert_eq!(block.ident.value().to_string(), "moved");
    // Verify from = module.web_server
    // Verify to = module.a.module.web_server
    Ok(())
}
```

### 4.2 Implement MovedModule

**File**: `src/output.rs`

**Task**: Implement `MovedModule` to make tests pass

- [x] Add `MovedModule` struct with fields:
  - `labels: Vec<String>` - All labels from the block (typically 1 for module)
  - `file_path: PathBuf` - Source file path (for comment)
  - `target_module_name: String` - Target module name
- [x] Implement `new()` constructor that validates labels (must have at least 1)
- [x] Implement accessor methods:
  - `labels(&self) -> &[String]` - Access all labels
  - `module_name_local(&self) -> &str` - Convenience accessor for labels[0]
- [x] Implement `build_from_expression()` - creates `AddressBuilder::new()` and uses `build()` with `["module", labels[0]]` (private method)
- [x] Implement `build_to_expression()` - creates `AddressBuilder::new()` and uses `build()` with `["module", target_module_name, "module", labels[0]]` (private method)
- [x] Implement `ToMovedBlock` trait for `MovedModule`:
  - `from_expression()` delegates to `build_from_expression()`
  - `to_expression()` delegates to `build_to_expression()`
  - `file_path()` returns `&self.file_path`
  - `to_block()` uses the default implementation from the trait
- [x] Verify all tests pass (Green phase)

**Expected implementation**:
```rust
pub struct MovedModule {
    labels: Vec<String>,
    file_path: PathBuf,
    target_module_name: String,
}

impl MovedModule {
    pub fn new(
        labels: Vec<String>,
        file_path: PathBuf,
        target_module_name: String,
    ) -> Result<Self> {
        if labels.len() < 1 {
            return Err(anyhow::anyhow!("Module blocks must have at least 1 label"));
        }
        Ok(Self {
            labels,
            file_path,
            target_module_name,
        })
    }

    pub fn labels(&self) -> &[String] {
        &self.labels
    }

    pub fn module_name_local(&self) -> &str {
        &self.labels[0]
    }

    fn build_from_expression(&self) -> Expression {
        AddressBuilder::new().build(&["module", &self.labels[0]])
    }

    fn build_to_expression(&self) -> Expression {
        AddressBuilder::new().build(&[
            "module",
            &self.target_module_name,
            "module",
            &self.labels[0],
        ])
    }
}

impl ToMovedBlock for MovedModule {
    fn from_expression(&self) -> Expression {
        self.build_from_expression()  // Delegates to private method
    }

    fn to_expression(&self) -> Expression {
        self.build_to_expression()  // Delegates to private method
    }

    fn file_path(&self) -> &Path {
        &self.file_path
    }

    // to_block() uses the default implementation from the trait
}
```

---

## Phase 5: MovedBlock Enum (TDD)

### 5.1 Write Tests for MovedBlock Enum

**File**: `src/output.rs`

**Task**: Write tests for the enum wrapper

- [x] Write test `test_moved_block_resource_variant()` - create from `MovedResource`
- [x] Write test `test_moved_block_module_variant()` - create from `MovedModule`
- [x] Write test `test_moved_block_from_block_resource()` - create from resource HCL block
- [x] Write test `test_moved_block_from_block_module()` - create from module HCL block
- [x] Write test `test_moved_block_from_block_invalid_resource()` - resource with < 2 labels returns `Some(Err)`
- [x] Write test `test_moved_block_from_block_invalid_module()` - module with no labels returns `Some(Err)`
- [x] Write test `test_moved_block_from_block_unsupported_type()` - unsupported block type returns `None`
- [x] Write test `test_moved_block_to_block_resource()` - convert resource variant to block
- [x] Write test `test_moved_block_to_block_module()` - convert module variant to block
- [x] Verify all tests fail (Red phase)

### 5.2 Implement MovedBlock Enum

**File**: `src/output.rs`

**Task**: Implement enum with creation and delegation methods

- [x] Add `MovedBlock` enum with variants:
  - `Resource(MovedResource)`
  - `Module(MovedModule)`
- [x] Implement `from_block(block: &Block, file_path: &Path, module_name: &str) -> Option<Result<Self>>` method:
  - Determines block type from block identifier ("resource" or "module")
  - Extracts labels from block
  - Validates labels (resource needs 2+, module needs 1+)
  - Creates appropriate variant (`MovedResource` or `MovedModule`)
  - Returns `None` for unsupported block types (should be skipped silently)
  - Returns `Some(Ok(MovedBlock))` for successfully converted blocks
  - Returns `Some(Err(e))` for supported types with invalid labels (should warn and skip)
- [x] Implement `to_block(&self) -> Result<Block>` method that delegates to inner type
- [x] Note: `MovedBlock` does not implement `ToMovedBlock` trait - it just has methods that delegate
- [x] Verify all tests pass (Green phase)

**Expected implementation**:
```rust
pub enum MovedBlock {
    Resource(MovedResource),
    Module(MovedModule),
}

impl MovedBlock {
    /// Create a `MovedBlock` from an HCL Block
    ///
    /// Determines the block type from the block's identifier and creates
    /// the appropriate variant (Resource or Module)
    ///
    /// Returns:
    /// - `None` if the block type is not supported (resource/module) - should be skipped silently
    /// - `Some(Ok(MovedBlock))` if successfully converted
    /// - `Some(Err(e))` if supported type but conversion failed (e.g., invalid labels)
    pub fn from_block(
        block: &Block,
        file_path: &Path,
        module_name: &str,
    ) -> Option<Result<Self>> {
        let ident = block.ident.value().to_string();
        let labels: Vec<String> = block.labels
            .iter()
            .map(|l| l.as_str().to_string())
            .collect();

        match ident.as_str() {
            "resource" => {
                if labels.len() < 2 {
                    return Some(Err(anyhow::anyhow!(
                        "Resource block in {} has fewer than 2 labels",
                        file_path.display()
                    )));
                }
                Some(MovedResource::new(labels, file_path.to_path_buf(), module_name.to_string())
                    .map(Self::Resource))
            }
            "module" => {
                if labels.is_empty() {
                    return Some(Err(anyhow::anyhow!(
                        "Module block in {} has no labels",
                        file_path.display()
                    )));
                }
                Some(MovedModule::new(labels, file_path.to_path_buf(), module_name.to_string())
                    .map(Self::Module))
            }
            _ => None, // Unsupported block type, skip silently
        }
    }

    /// Convert to HCL Block by delegating to the inner type
    pub fn to_block(&self) -> Result<Block> {
        match self {
            MovedBlock::Resource(r) => r.to_block(),
            MovedBlock::Module(m) => m.to_block(),
        }
    }
}
```

**Design Note**: `MovedBlock` does not implement the `ToMovedBlock` trait because no code requires it as a trait bound. The `from_block()` method encapsulates the logic for creating a `MovedBlock` from an HCL `Block`, making it reusable and keeping the creation logic in one place. It returns `Option<Result<Self>>` to allow the iterator to skip unsupported block types (`None`) or handle conversion errors (`Some(Err)`), while successfully converted blocks return `Some(Ok(MovedBlock))`. It simply delegates to the inner `MovedResource` or `MovedModule`, both of which implement `ToMovedBlock`.

---

---

## Phase 6: Iterator Adapter Pipeline (TDD)

### 6.1 Write Tests for Iterator Adapters

**File**: `src/output.rs`

**Task**: Write tests for the iterator adapter pipeline

- [x] Write test `test_terraform_files_new()` - verify constructor
- [x] Write test `test_terraform_files_iter()` - verify file discovery (tested via integration)
- [x] Write test `test_parsed_files_new()` - verify constructor takes TerraformFiles by value (tested via integration)
- [x] Write test `test_parsed_files_iter()` - verify file parsing (tested via integration)
- [x] Write test `test_parsed_files_handles_parse_errors()` - continues on parse errors (tested via integration)
- [x] Write test `test_moved_blocks_new()` - verify constructor takes ParsedFiles by value (tested via integration)
- [x] Write test `test_moved_blocks_empty_dir()` - empty directory returns empty iterator
- [x] Write test `test_moved_blocks_single_resource()` - single resource file
- [x] Write test `test_moved_blocks_single_module()` - single module file
- [x] Write test `test_moved_blocks_mixed()` - resource and module in same file
- [x] Write test `test_moved_blocks_multiple_files()` - multiple files (tested via integration)
- [x] Write test `test_moved_blocks_handles_invalid_blocks()` - skips invalid blocks (tested via integration)
- [x] Write test `test_moved_block_builder_new()` - verify constructor
- [x] Write test `test_moved_block_builder_moved_blocks()` - verify full pipeline
- [x] Verify all tests fail (Red phase)

### 6.2 Implement Iterator Adapter Pipeline

**File**: `src/output.rs`

**Task**: Implement iterator adapters with ownership chain

- [x] Add `TerraformFiles` struct:
  - Field: `src: PathBuf`
  - Method: `new(src: PathBuf) -> Self`
  - Method: `into_iter(self) -> impl Iterator<Item = Result<PathBuf>>`
- [x] Add `ParsedFiles` struct:
  - Field: `files: Box<dyn Iterator<Item = Result<PathBuf>>>`
  - Method: `new(files: TerraformFiles) -> Self` (takes ownership)
  - Implement `Iterator<Item = Result<(PathBuf, Body)>>`
  - Handle file discovery and parsing errors (warnings, continue)
- [x] Add `MovedBlocks` struct:
  - Fields:
    - `parsed: ParsedFiles` (owns ParsedFiles)
    - `module_name: String`
    - `current_file: Option<PathBuf>`
    - `current_body: Option<Body>` (keeps body alive for block references)
    - `current_blocks: Vec<Block>` (stores blocks as owned values to avoid lifetime issues)
    - `current_block_index: usize` (tracks position in current_blocks)
  - Method: `new(parsed: ParsedFiles, module_name: String) -> Self` (takes ownership)
  - Method: `load_next_body(&mut self) -> bool` - loads next body from parsed, collects blocks into vector
  - Implement `Iterator<Item = Result<MovedBlock>>`:
    - Iterate over `current_blocks` using index
    - For each block, call `MovedBlock::from_block()` which returns `Option<Result<MovedBlock>>`:
      - `None` = unsupported block type, skip silently and continue to next block
      - `Some(Ok(m))` = successfully converted, return it
      - `Some(Err(e))` = supported type but invalid, warn and skip to next block
    - When `current_blocks` is exhausted, call `next()` on `parsed` to get next body
    - Filtering happens lazily in `Iterator::next()` via `MovedBlock::from_block()`
- [x] Add `MovedBlockBuilder` struct:
  - Fields: `src: PathBuf`, `module_name: String`
  - Method: `new(src: PathBuf, module_name: String) -> Self`
  - Method: `moved_blocks(self) -> MovedBlocks` (takes ownership, returns MovedBlocks)
- [x] Verify all tests pass (Green phase)

**Note**: Implementation uses `Vec<Block>` instead of iterator references. This is the correct approach because:
- **hcl-edit constraint**: The `hcl-edit` library requires parsing the entire file into a `Body` before blocks can be accessed. The entire file is already in memory, so block-level laziness provides no benefit.
- **No additional overhead**: Since the `Body` already contains all blocks in memory, collecting them into a `Vec<Block>` doesn't add significant overhead - it just creates owned copies of references that already exist.
- **Lifetime simplicity**: Using `Vec<Block>` avoids complex self-referential struct lifetime issues that would arise from storing an iterator that borrows from `current_body`.
- **File-level laziness is sufficient**: The meaningful level of laziness is at the file level (processing one file at a time), which is already achieved. Block-level laziness within a file that's already fully parsed provides no practical benefit.

**Note on Implementation**: The plan originally showed using an iterator (`Option<Box<dyn Iterator<Item = &Block> + '_>>`), but the actual implementation uses `Vec<Block>` with an index. This is the correct approach because:
- hcl-edit requires parsing the entire file before blocks can be accessed, so the file is already fully in memory
- Collecting blocks into a `Vec<Block>` doesn't add significant overhead since the data is already there
- This avoids complex self-referential struct lifetime issues
- File-level laziness (processing one file at a time) is the meaningful optimization

**Expected implementation structure** (actual implementation uses `Vec<Block>` instead of iterator):
```rust
/// Wrapper for Terraform file discovery
pub struct TerraformFiles {
    src: PathBuf,
}

impl TerraformFiles {
    pub fn new(src: PathBuf) -> Self {
        Self { src }
    }

    pub fn into_iter(self) -> impl Iterator<Item = Result<PathBuf>> {
        find_terraform_files(&self.src).into_iter()
    }
}

/// Adapter that converts file results to parsed bodies
/// Owns TerraformFiles
pub struct ParsedFiles {
    files: Box<dyn Iterator<Item = Result<PathBuf>>>,
}

impl ParsedFiles {
    pub fn new(files: TerraformFiles) -> Self {
        Self {
            files: Box::new(files.into_iter()),
        }
    }
}

impl Iterator for ParsedFiles {
    type Item = Result<(PathBuf, Body)>;

    fn next(&mut self) -> Option<Self::Item> {
        self.files.next().and_then(|file_result| {
            let file = file_result.map_err(|e| {
                eprintln!("Warning: Failed to discover file: {}", e);
                e
            }).ok()?;

            parse_terraform_file(&file)
                .map(|body| (file, body))
                .map_err(|e| {
                    eprintln!("Warning: Failed to parse {}: {}", file.display(), e);
                    e
                })
                .ok()
                .map(Ok)
        })
    }
}

/// Adapter that converts blocks to MovedBlocks, managing body iteration internally
/// Owns ParsedFiles
pub struct MovedBlocks {
    parsed: ParsedFiles,
    module_name: String,
    current_file: Option<PathBuf>,
    current_body: Option<Body>, // Keeps body alive for block references
    current_blocks: Option<Box<dyn Iterator<Item = &Block> + '_>>, // Iterator over blocks from current_body
}

impl MovedBlocks {
    pub fn new(parsed: ParsedFiles, module_name: String) -> Self {
        Self {
            parsed,
            module_name,
            current_file: None,
            current_body: None,
            current_blocks: None,
        }
    }

    /// Load blocks from the next body into current_blocks iterator
    /// Sets up lazy iteration over all blocks (filtering happens in Iterator::next())
    fn load_next_body(&mut self) -> bool {
        loop {
            match self.parsed.next() {
                Some(Ok((file_path, body))) => {
                    self.current_file = Some(file_path);
                    self.current_body = Some(body); // Store body to keep block references alive
                    self.current_blocks = Some(Box::new(self.current_body.as_ref().unwrap().blocks()));
                    return true;
                }
                Some(Err(e)) => {
                    eprintln!("Warning: {}", e);
                    continue; // Try next file instead of recursing
                }
                None => {
                    return false;
                }
            }
        }
    }
}

impl Iterator for MovedBlocks {
    type Item = Result<MovedBlock>;

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            // If we have current blocks, try to get next one
            if let Some(ref mut blocks_iter) = self.current_blocks {
                while let Some(block) = blocks_iter.next() {
                    let file_path = self.current_file.as_ref().expect("file_path should be set when blocks exist");

                    match MovedBlock::from_block(block, file_path, &self.module_name) {
                        None => continue, // Unsupported block type, skip silently
                        Some(Ok(moved_block)) => return Some(Ok(moved_block)),
                        Some(Err(e)) => {
                            eprintln!("Warning: {}", e);
                            continue; // Invalid block, warn and skip
                        }
                    }
                }
            }

            // Current blocks exhausted, clear and load next body
            self.current_file = None;
            self.current_body = None;
            self.current_blocks = None;

            // Load next body
            if !self.load_next_body() {
                return None; // No more bodies
            }
        }
    }
}

/// Main builder that composes the pipeline
pub struct MovedBlockBuilder {
    src: PathBuf,
    module_name: String,
}

impl MovedBlockBuilder {
    pub fn new(src: PathBuf, module_name: String) -> Self {
        Self { src, module_name }
    }

    pub fn moved_blocks(self) -> MovedBlocks {
        let files = TerraformFiles::new(self.src);
        let parsed = ParsedFiles::new(files);
        MovedBlocks::new(parsed, self.module_name)
    }
}
```

**Design Notes**:
- **Ownership Chain**: `MovedBlockBuilder` → `TerraformFiles` → `ParsedFiles` → `MovedBlocks`
- **File-Level Laziness**: Files are processed one at a time - this is the meaningful level of laziness. The iterator only loads the next file when the current file's blocks are exhausted.
- **Block Collection**: `MovedBlocks` collects all blocks from the current body into a `Vec<Block>`. This is appropriate because:
  - hcl-edit requires the entire file to be parsed into a `Body` before blocks can be accessed
  - The entire file is already in memory, so collecting blocks adds no significant overhead
  - This avoids complex lifetime issues from self-referential structs
  - Block-level laziness within an already-parsed file provides no practical benefit
- **Lazy Filtering**: Filtering happens lazily in `Iterator::next()` via `MovedBlock::from_block()` which returns `Option<Result<MovedBlock>>`:
  - `None` = unsupported block type, skip silently
  - `Some(Ok(m))` = successfully converted, return it
  - `Some(Err(e))` = supported type but invalid, warn and skip
- **Block Conversion**: Uses `MovedBlock::from_block()` to convert HCL blocks, which handles filtering and validation
- **Clean State**: Only `current_file`, `current_body`, and `current_blocks` need to be tracked
- **Body Lifetime**: `current_body` is stored to keep it alive while processing its blocks

---

## Phase 7: Update main.rs to Use New Architecture

### 7.1 Write Integration Tests

**File**: `tests/integration_test.rs`

**Task**: Write/update integration tests for new architecture

- [x] Update existing integration tests to verify output format unchanged
- [x] Add test `test_integration_resource_blocks()` - verify resource blocks work (existing tests cover this)
- [x] Add test `test_integration_module_blocks()` - verify module blocks work (`test_single_module_file`, `test_multiple_modules`)
- [x] Add test `test_integration_mixed_blocks()` - verify both types together (`test_mixed_resources_and_modules`)
- [x] Add test `test_integration_multiple_files()` - verify multiple files (existing `test_multiple_files` covers this)
- [x] Verify tests fail or need updates (Red phase)

### 7.2 Refactor main.rs

**File**: `src/main.rs`

**Task**: Update `run()` function to use new architecture

- [x] Update imports:
  - Remove `build_resource_moved_block` from processor
  - Add `MovedBlockBuilder` from output
  - Remove unused imports (`find_terraform_files`, `parse_terraform_file`, `extract_blocks`)
- [x] Refactor `run()` function:
  - Create `MovedBlockBuilder::new(args.src, args.module_name)` (takes ownership of args)
  - Call `moved_blocks()` which takes `self` by value and returns `MovedBlocks` iterator
  - Iterate over `MovedBlocks` iterator
  - Convert each `MovedBlock` to `Block` using `to_block()`
  - Collect blocks into vector
  - Build output body and print
- [x] Remove old eager collection logic
- [x] Fix `ParsedFiles` iterator to continue on parse errors (use loop instead of and_then)
- [x] Verify integration tests pass (Green phase)

**Expected refactored structure**:
```rust
fn run() -> Result<()> {
    let args = Args::parse();
    args.validate()?;

    let builder = MovedBlockBuilder::new(args.src, args.module_name);
    let mut moved_blocks = Vec::new();

    for moved_block_result in builder.moved_blocks() {
        match moved_block_result {
            Ok(moved_block) => {
                match moved_block.to_block() {
                    Ok(block) => moved_blocks.push(block),
                    Err(e) => {
                        eprintln!("Warning: Failed to convert moved block: {}", e);
                    }
                }
            }
            Err(e) => {
                eprintln!("Warning: {}", e);
            }
        }
    }

    let output_body = build_output_body(&moved_blocks);
    println!("{}", output_body);
    Ok(())
}
```

**Note**: `moved_blocks()` takes `self` by value, transferring ownership of the builder to the iterator. This is intentional - the iterator owns the entire pipeline.

---

## Phase 8: Cleanup and Remove Old Code

### 8.1 Remove Deprecated Functions

**File**: `src/processor.rs`

**Task**: Remove functions moved to new architecture

- [x] Remove `build_resource_moved_block()` function
- [x] Remove `build_from_expression()` function
- [x] Remove `build_to_expression()` function
- [x] Remove `extract_blocks()` function (not used in new architecture)
- [x] Add comment explaining where functionality moved to

### 8.2 Update Tests in processor.rs

**File**: `src/processor.rs`

**Task**: Update tests to reflect new architecture

- [x] Remove tests for `build_resource_moved_block()` (moved to `MovedResource` tests)
- [x] Remove tests for `build_from_expression()` (moved to `AddressBuilder` tests)
- [x] Remove tests for `build_to_expression()` (moved to `AddressBuilder` tests)
- [x] Remove tests for `extract_blocks()` (function removed)
- [x] Verify all tests pass

### 8.3 Update Tests in output.rs

**File**: `src/output.rs`

**Task**: Update existing tests to use new structure

- [x] Update `build_output_body()` tests to use `MovedResource::to_block()` instead of `build_resource_moved_block()`
- [x] Verify all tests pass
- [x] Ensure test coverage is maintained

---

## Phase 9: Add Module Block Test Fixtures

### 9.1 Create Test Fixtures

**File**: `tests/fixtures/`

**Task**: Create test fixtures for module blocks

- [x] Create `single_module.tf` - single module block
- [x] Create `multiple_modules.tf` - multiple module blocks
- [x] Create `mixed_resources_and_modules.tf` - resources and modules together
- [ ] Create `nested_module.tf` - module with nested structure (if applicable) - Not needed for basic functionality

**Example fixture** (`single_module.tf`):
```hcl
module "web_server" {
  source = "./modules/web"

  instance_count = 3
  instance_type  = "t3.medium"
}
```

### 9.2 Add Integration Tests for Module Blocks

**File**: `tests/integration_test.rs`

**Task**: Add comprehensive integration tests

- [x] Add test using `single_module.tf` fixture (`test_single_module_file`)
- [x] Add test using `multiple_modules.tf` fixture (`test_multiple_modules`)
- [x] Add test using `mixed_resources_and_modules.tf` fixture (`test_mixed_resources_and_modules`)
- [x] Add test for module name with hyphens (`test_module_name_with_hyphens_for_modules`)
- [x] Add test for module name with underscores (`test_module_name_with_underscores_for_modules`)
- [x] Verify output format matches expected format
- [x] Verify all tests pass (15 integration tests passing)

---

## Phase 10: Refactoring and Optimization

### 10.1 Code Review and Refactoring

**Task**: Review code for improvements

- [ ] Review `AddressBuilder` implementation for efficiency (should be stateless utility, created when needed)
- [ ] Review `MovedResource` and `MovedModule` for code duplication
- [ ] Extract common logic if needed (DRY principle) - both use `file_path` similarly
- [ ] Ensure all error handling is consistent
- [ ] Verify all comments and documentation are clear
- [ ] Verify `file_path` is stored in the right place (not in `AddressBuilder`)

### 10.2 Performance Verification

**Task**: Verify lazy evaluation works correctly

- [ ] Verify files are processed one at a time (not all loaded into memory)
- [ ] Verify iterator is truly lazy (no work until consumed)
- [ ] Run performance tests if needed
- [ ] Compare memory usage with old implementation

---

## Phase 11: Documentation and Final Verification

### 11.1 Update Documentation

**Task**: Update code documentation

- [ ] Add doc comments to all public structs and methods
- [ ] Add examples in documentation where helpful
- [ ] Update module-level documentation
- [ ] Verify documentation is accurate

### 11.2 Final Test Suite Verification

**Task**: Run full test suite

- [ ] Run `cargo test` - all unit tests pass
- [ ] Run `cargo test --test integration_test` - all integration tests pass
- [ ] Run `cargo nextest run` - verify test runner works
- [ ] Verify code coverage is maintained or improved
- [ ] Fix any failing tests

### 11.3 Verify Output Format

**Task**: Ensure output format matches expectations

- [ ] Compare output from old and new implementations
- [ ] Verify resource blocks output format unchanged
- [ ] Verify module blocks output format is correct
- [ ] Test with real-world Terraform files if available
- [ ] Document any format differences (should be none)

---

## Checklist Summary

### Phase 1: Foundation - AddressBuilder
- [ ] Write tests for AddressBuilder
- [ ] Implement AddressBuilder

### Phase 2: ToMovedBlock Trait
- [ ] Define trait and write tests

### Phase 3: MovedResource
- [ ] Write tests for MovedResource
- [ ] Implement MovedResource

### Phase 4: MovedModule
- [ ] Write tests for MovedModule
- [ ] Implement MovedModule

### Phase 5: MovedBlock Enum
- [ ] Write tests for MovedBlock
- [ ] Implement MovedBlock

### Phase 6: MovedBlockBuilder
- [ ] Write tests for MovedBlockBuilder
- [ ] Implement MovedBlockBuilder

### Phase 7: Update main.rs
- [x] Write/update integration tests
- [x] Refactor main.rs

### Phase 8: Cleanup
- [x] Remove deprecated functions
- [x] Update tests in processor.rs
- [x] Update tests in output.rs

### Phase 9: Test Fixtures
- [x] Create module block test fixtures
- [x] Add integration tests for module blocks

### Phase 10: Refactoring
- [ ] Code review and refactoring
- [ ] Performance verification

### Phase 11: Documentation
- [ ] Update documentation
- [ ] Final test suite verification
- [ ] Verify output format

---

## Testing Strategy

### Unit Tests (TDD)
- Each component tested independently
- Tests written before implementation
- Tests verify both success and error cases
- Tests verify exact output format

### Integration Tests
- End-to-end tests with real file structures
- Tests verify both resource and module blocks
- Tests verify error handling
- Tests verify output format matches expectations

### Regression Tests
- Compare output from old and new implementations
- Ensure all existing test fixtures still work
- Verify backward compatibility

---

## Benefits

1. **Memory Efficiency**: Process files one at a time instead of loading all into memory
2. **Lazy Evaluation**: No work until iterator is consumed
3. **Extensibility**: Easy to add new block types (just implement `ToMovedBlock` with three methods)
4. **Flexible Label Handling**: `Vec<String>` for labels supports any number of labels per block type
5. **Testability**: Each component tested independently
6. **Maintainability**: Clear separation of concerns
7. **Performance**: Use `Traversal::builder()` instead of string parsing
8. **Module Support**: Complete support for both resource and module blocks
9. **OOP Compliance**: Proper encapsulation, polymorphism, and single responsibility
10. **TDD Compliance**: Tests drive design and ensure correctness
11. **Clean Architecture**: `AddressBuilder` is a pure utility with no state; file paths stored where they're used
12. **DRY Principle**: Default `to_block()` implementation eliminates code duplication between block types
13. **Template Method Pattern**: Trait default method defines structure, implementors provide specific logic
14. **Iterator Adapter Pipeline**: Clean ownership chain with composable adapters (Files → Parsed → MovedBlocks), eliminating deep nesting and making control flow clear

---

## Related Files

- `src/output.rs` - Main file for new architecture
- `src/processor.rs` - Block extraction functions
- `src/main.rs` - Entry point (needs refactoring)
- `tests/integration_test.rs` - Integration tests
- `tests/fixtures/` - Test fixtures

---

## References

- [HCL TraversalBuilder Documentation](https://docs.rs/hcl-rs/latest/hcl/expr/struct.TraversalBuilder.html)
- [Rust Iterator Pattern](https://doc.rust-lang.org/book/ch13-02-iterators.html)
- [Terraform Module Blocks Documentation](https://developer.hashicorp.com/terraform/language/modules/syntax)
- Original plans:
  - `plan/25W47/STREAMING_REFACTOR.md`
  - `plan/25W47/MODULE_BLOCK_SUPPORT.md`
