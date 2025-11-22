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

---

## Phase 1: Foundation - AddressBuilder (TDD)

### 1.1 Write Tests for AddressBuilder

**File**: `src/output.rs`

**Task**: Create unit tests for `AddressBuilder` before implementation

- [ ] Add test module `mod tests` in `output.rs`
- [ ] Write test `test_address_builder_new()` - verify constructor
- [ ] Write test `test_address_builder_file_path()` - verify file path accessor
- [ ] Write test `test_address_builder_build_single_segment()` - build expression with one segment
- [ ] Write test `test_address_builder_build_multiple_segments()` - build expression with multiple segments
- [ ] Write test `test_address_builder_build_resource_expression()` - build `resource_type.resource_name`
- [ ] Write test `test_address_builder_build_module_expression()` - build `module.module_name`
- [ ] Write test `test_address_builder_build_nested_expression()` - build `module.name.resource_type.resource_name`
- [ ] Verify all tests fail (Red phase)

**Expected test structure**:
```rust
#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_address_builder_new() {
        let path = PathBuf::from("test.tf");
        let builder = AddressBuilder::new(path.clone());
        assert_eq!(builder.file_path(), &path);
    }

    // ... more tests
}
```

### 1.2 Implement AddressBuilder

**File**: `src/output.rs`

**Task**: Implement `AddressBuilder` to make tests pass

- [ ] Add `AddressBuilder` struct with `file_path: PathBuf` field
- [ ] Implement `new(file_path: PathBuf) -> Self` constructor
- [ ] Implement `file_path(&self) -> &PathBuf` accessor
- [ ] Implement `build(&self, segments: &[&str]) -> Expression` method
- [ ] Use `hcl::expr::Traversal::builder()` with `.attr()` chaining
- [ ] Verify all tests pass (Green phase)

**Expected implementation**:
```rust
pub struct AddressBuilder {
    file_path: PathBuf,
}

impl AddressBuilder {
    pub fn new(file_path: PathBuf) -> Self {
        Self { file_path }
    }

    pub fn file_path(&self) -> &PathBuf {
        &self.file_path
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

---

## Phase 2: ToMovedBlock Trait (TDD)

### 2.1 Write Tests for ToMovedBlock Trait

**File**: `src/output.rs`

**Task**: Define trait and write tests for trait behavior

- [ ] Define `ToMovedBlock` trait with `to_block(&self) -> Result<Block>` method
- [ ] Write test `test_to_moved_block_trait_exists()` - verify trait can be used
- [ ] Verify test compiles but trait implementations don't exist yet (Red phase)

**Expected trait definition**:
```rust
pub trait ToMovedBlock {
    fn to_block(&self) -> Result<Block>;
}
```

---

## Phase 3: MovedResource (TDD)

### 3.1 Write Tests for MovedResource

**File**: `src/output.rs`

**Task**: Write comprehensive tests for `MovedResource`

- [ ] Write test `test_moved_resource_new()` - verify constructor
- [ ] Write test `test_moved_resource_build_from_expression()` - verify from expression
- [ ] Write test `test_moved_resource_build_to_expression()` - verify to expression
- [ ] Write test `test_moved_resource_to_block()` - verify block conversion
- [ ] Write test `test_moved_resource_to_block_has_comment()` - verify file comment
- [ ] Write test `test_moved_resource_to_block_has_indented_attributes()` - verify formatting
- [ ] Write test `test_moved_resource_to_block_output_format()` - verify exact output format
- [ ] Verify all tests fail (Red phase)

**Expected test structure**:
```rust
#[test]
fn test_moved_resource_new() {
    let path = PathBuf::from("main.tf");
    let resource = MovedResource::new(
        "aws_instance".to_string(),
        "web".to_string(),
        path,
        "compute".to_string(),
    );
    assert_eq!(resource.resource_type(), "aws_instance");
    assert_eq!(resource.resource_name(), "web");
}

#[test]
fn test_moved_resource_to_block() -> Result<()> {
    let path = PathBuf::from("main.tf");
    let resource = MovedResource::new(
        "aws_instance".to_string(),
        "web".to_string(),
        path,
        "compute".to_string(),
    );
    let block = resource.to_block()?;
    assert_eq!(block.ident.value().to_string(), "moved");
    Ok(())
}
```

### 3.2 Implement MovedResource

**File**: `src/output.rs`

**Task**: Implement `MovedResource` to make tests pass

- [ ] Add `MovedResource` struct with fields:
  - `resource_type: String`
  - `resource_name: String`
  - `address_builder: AddressBuilder`
  - `target_module_name: String`
- [ ] Implement `new()` constructor
- [ ] Implement accessor methods (optional, for testing)
- [ ] Implement `build_from_expression()` - uses `AddressBuilder::build()` with `[resource_type, resource_name]`
- [ ] Implement `build_to_expression()` - uses `AddressBuilder::build()` with `["module", target_module_name, resource_type, resource_name]`
- [ ] Implement `ToMovedBlock` trait for `MovedResource`
- [ ] In `to_block()`, create `Block` with `from` and `to` attributes
- [ ] Add file comment using `AddressBuilder::file_path()`
- [ ] Verify all tests pass (Green phase)

**Expected implementation**:
```rust
pub struct MovedResource {
    resource_type: String,
    resource_name: String,
    address_builder: AddressBuilder,
    target_module_name: String,
}

impl MovedResource {
    pub fn new(
        resource_type: String,
        resource_name: String,
        file_path: PathBuf,
        target_module_name: String,
    ) -> Self {
        Self {
            resource_type,
            resource_name,
            address_builder: AddressBuilder::new(file_path),
            target_module_name,
        }
    }

    fn build_from_expression(&self) -> Expression {
        self.address_builder.build(&[&self.resource_type, &self.resource_name])
    }

    fn build_to_expression(&self) -> Expression {
        self.address_builder.build(&[
            "module",
            &self.target_module_name,
            &self.resource_type,
            &self.resource_name,
        ])
    }
}

impl ToMovedBlock for MovedResource {
    fn to_block(&self) -> Result<Block> {
        // Implementation details
    }
}
```

---

## Phase 4: MovedModule (TDD)

### 4.1 Write Tests for MovedModule

**File**: `src/output.rs`

**Task**: Write comprehensive tests for `MovedModule`

- [ ] Write test `test_moved_module_new()` - verify constructor
- [ ] Write test `test_moved_module_build_from_expression()` - verify from expression (`module.module_name`)
- [ ] Write test `test_moved_module_build_to_expression()` - verify to expression (`module.target_module.module.module_name`)
- [ ] Write test `test_moved_module_to_block()` - verify block conversion
- [ ] Write test `test_moved_module_to_block_has_comment()` - verify file comment
- [ ] Write test `test_moved_module_to_block_has_indented_attributes()` - verify formatting
- [ ] Write test `test_moved_module_to_block_output_format()` - verify exact output format
- [ ] Verify all tests fail (Red phase)

**Expected test structure**:
```rust
#[test]
fn test_moved_module_new() {
    let path = PathBuf::from("main.tf");
    let module = MovedModule::new(
        "web_server".to_string(),
        path,
        "a".to_string(),
    );
    assert_eq!(module.module_name_local(), "web_server");
}

#[test]
fn test_moved_module_to_block() -> Result<()> {
    let path = PathBuf::from("main.tf");
    let module = MovedModule::new(
        "web_server".to_string(),
        path,
        "a".to_string(),
    );
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

- [ ] Add `MovedModule` struct with fields:
  - `module_name_local: String`
  - `address_builder: AddressBuilder`
  - `target_module_name: String`
- [ ] Implement `new()` constructor
- [ ] Implement accessor methods (optional, for testing)
- [ ] Implement `build_from_expression()` - uses `AddressBuilder::build()` with `["module", module_name_local]`
- [ ] Implement `build_to_expression()` - uses `AddressBuilder::build()` with `["module", target_module_name, "module", module_name_local]`
- [ ] Implement `ToMovedBlock` trait for `MovedModule`
- [ ] In `to_block()`, create `Block` with `from` and `to` attributes
- [ ] Add file comment using `AddressBuilder::file_path()`
- [ ] Verify all tests pass (Green phase)

**Expected implementation**:
```rust
pub struct MovedModule {
    module_name_local: String,
    address_builder: AddressBuilder,
    target_module_name: String,
}

impl MovedModule {
    pub fn new(
        module_name_local: String,
        file_path: PathBuf,
        target_module_name: String,
    ) -> Self {
        Self {
            module_name_local,
            address_builder: AddressBuilder::new(file_path),
            target_module_name,
        }
    }

    fn build_from_expression(&self) -> Expression {
        self.address_builder.build(&["module", &self.module_name_local])
    }

    fn build_to_expression(&self) -> Expression {
        self.address_builder.build(&[
            "module",
            &self.target_module_name,
            "module",
            &self.module_name_local,
        ])
    }
}

impl ToMovedBlock for MovedModule {
    fn to_block(&self) -> Result<Block> {
        // Implementation details
    }
}
```

---

## Phase 5: MovedBlock Enum (TDD)

### 5.1 Write Tests for MovedBlock Enum

**File**: `src/output.rs`

**Task**: Write tests for the enum wrapper

- [ ] Write test `test_moved_block_resource_variant()` - create from `MovedResource`
- [ ] Write test `test_moved_block_module_variant()` - create from `MovedModule`
- [ ] Write test `test_moved_block_to_block_resource()` - convert resource variant to block
- [ ] Write test `test_moved_block_to_block_module()` - convert module variant to block
- [ ] Verify all tests fail (Red phase)

### 5.2 Implement MovedBlock Enum

**File**: `src/output.rs`

**Task**: Implement enum and trait implementation

- [ ] Add `MovedBlock` enum with variants:
  - `Resource(MovedResource)`
  - `Module(MovedModule)`
- [ ] Implement `ToMovedBlock` trait for `MovedBlock` (delegates to inner type)
- [ ] Verify all tests pass (Green phase)

**Expected implementation**:
```rust
pub enum MovedBlock {
    Resource(MovedResource),
    Module(MovedModule),
}

impl ToMovedBlock for MovedBlock {
    fn to_block(&self) -> Result<Block> {
        match self {
            MovedBlock::Resource(r) => r.to_block(),
            MovedBlock::Module(m) => m.to_block(),
        }
    }
}
```

---

## Phase 6: Processor Updates - Module Block Extraction (TDD)

### 6.1 Write Tests for Module Block Extraction

**File**: `src/processor.rs`

**Task**: Write tests for extracting module blocks

- [ ] Write test `test_extract_module_blocks()` - extract module blocks from body
- [ ] Write test `test_extract_module_blocks_ignores_resources()` - only extracts modules
- [ ] Write test `test_extract_module_blocks_ignores_data()` - ignores data blocks
- [ ] Write test `test_extract_module_blocks_from_mixed_blocks()` - handles mixed content
- [ ] Write test `test_extract_module_blocks_empty_body()` - handles empty body
- [ ] Verify all tests fail (Red phase)

### 6.2 Implement Module Block Extraction

**File**: `src/processor.rs`

**Task**: Implement `extract_module_blocks()` function

- [ ] Add `extract_module_blocks(body: &Body) -> Vec<&Block>` function
- [ ] Filter blocks where `block.ident.value() == "module"`
- [ ] Return vector of module blocks
- [ ] Verify all tests pass (Green phase)

**Expected implementation**:
```rust
/// Extract module blocks from a parsed Body
pub fn extract_module_blocks(body: &Body) -> Vec<&Block> {
    body.blocks()
        .filter(|block| {
            let ident = block.ident.value().to_string();
            ident == "module"
        })
        .collect()
}
```

---

## Phase 7: MovedBlockBuilder (TDD)

### 7.1 Write Tests for MovedBlockBuilder

**File**: `src/output.rs`

**Task**: Write tests for the builder and iterator

- [ ] Write test `test_moved_block_builder_new()` - verify constructor (lazy, no work)
- [ ] Write test `test_moved_block_builder_moved_blocks_empty_dir()` - empty directory returns empty iterator
- [ ] Write test `test_moved_block_builder_moved_blocks_single_resource()` - single resource file
- [ ] Write test `test_moved_block_builder_moved_blocks_single_module()` - single module file
- [ ] Write test `test_moved_block_builder_moved_blocks_mixed()` - resource and module in same file
- [ ] Write test `test_moved_block_builder_moved_blocks_multiple_files()` - multiple files
- [ ] Write test `test_moved_block_builder_handles_parse_errors()` - continues on parse errors
- [ ] Write test `test_moved_block_builder_handles_invalid_blocks()` - skips invalid blocks
- [ ] Verify all tests fail (Red phase)

### 7.2 Implement MovedBlockBuilder

**File**: `src/output.rs`

**Task**: Implement builder with lazy iterator

- [ ] Add `MovedBlockBuilder` struct with fields:
  - `src: PathBuf`
  - `module_name: String`
- [ ] Implement `new(src: PathBuf, module_name: String) -> Self` constructor
- [ ] Implement `moved_blocks(&self) -> impl Iterator<Item = Result<MovedBlock>> + '_` method
- [ ] In iterator:
  - Use `find_terraform_files()` to get file iterator
  - For each file, parse and extract blocks
  - Convert resource blocks to `MovedResource` wrapped in `MovedBlock::Resource`
  - Convert module blocks to `MovedModule` wrapped in `MovedBlock::Module`
  - Handle errors gracefully (warnings, continue)
- [ ] Verify all tests pass (Green phase)

**Expected implementation structure**:
```rust
pub struct MovedBlockBuilder {
    src: PathBuf,
    module_name: String,
}

impl MovedBlockBuilder {
    pub fn new(src: PathBuf, module_name: String) -> Self {
        Self { src, module_name }
    }

    pub fn moved_blocks(&self) -> impl Iterator<Item = Result<MovedBlock>> + '_ {
        // Lazy iterator implementation
        find_terraform_files(&self.src)
            .into_iter()
            .flat_map(|file_result| {
                // Handle file discovery errors
                match file_result {
                    Ok(file) => {
                        // Parse and extract blocks
                        // Convert to MovedBlock instances
                    }
                    Err(e) => {
                        // Log warning, return empty iterator
                    }
                }
            })
    }
}
```

---

## Phase 8: Update main.rs to Use New Architecture

### 8.1 Write Integration Tests

**File**: `tests/integration_test.rs`

**Task**: Write/update integration tests for new architecture

- [ ] Update existing integration tests to verify output format unchanged
- [ ] Add test `test_integration_resource_blocks()` - verify resource blocks work
- [ ] Add test `test_integration_module_blocks()` - verify module blocks work
- [ ] Add test `test_integration_mixed_blocks()` - verify both types together
- [ ] Add test `test_integration_multiple_files()` - verify multiple files
- [ ] Verify tests fail or need updates (Red phase)

### 8.2 Refactor main.rs

**File**: `src/main.rs`

**Task**: Update `run()` function to use new architecture

- [ ] Update imports:
  - Remove `build_resource_moved_block` from processor
  - Add `MovedBlockBuilder` from output
  - Add `ToMovedBlock` trait
- [ ] Refactor `run()` function:
  - Create `MovedBlockBuilder::new(args.src, args.module_name)`
  - Use `moved_blocks()` iterator
  - Convert each `MovedBlock` to `Block` using `to_block()`
  - Collect blocks into vector
  - Build output body and print
- [ ] Remove old eager collection logic
- [ ] Verify integration tests pass (Green phase)

**Expected refactored structure**:
```rust
fn run() -> Result<()> {
    let args = Args::parse();
    args.validate()?;

    let builder = MovedBlockBuilder::new(args.src.clone(), args.module_name.clone());
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

---

## Phase 9: Cleanup and Remove Old Code

### 9.1 Remove Deprecated Functions

**File**: `src/processor.rs`

**Task**: Remove functions moved to new architecture

- [ ] Remove `build_resource_moved_block()` function
- [ ] Remove `build_from_expression()` function
- [ ] Remove `build_to_expression()` function
- [ ] Keep `extract_blocks()` function (still used)
- [ ] Keep `extract_module_blocks()` function (newly added)
- [ ] Update any remaining tests that reference removed functions

### 9.2 Update Tests in processor.rs

**File**: `src/processor.rs`

**Task**: Update tests to reflect new architecture

- [ ] Remove tests for `build_resource_moved_block()` (moved to `MovedResource` tests)
- [ ] Remove tests for `build_from_expression()` (moved to `AddressBuilder` tests)
- [ ] Remove tests for `build_to_expression()` (moved to `AddressBuilder` tests)
- [ ] Keep tests for `extract_blocks()`
- [ ] Keep tests for `extract_module_blocks()`
- [ ] Verify all tests pass

### 9.3 Update Tests in output.rs

**File**: `src/output.rs`

**Task**: Update existing tests to use new structure

- [ ] Update `build_output_body()` tests to use `MovedResource::to_block()` instead of `build_resource_moved_block()`
- [ ] Verify all tests pass
- [ ] Ensure test coverage is maintained

---

## Phase 10: Add Module Block Test Fixtures

### 10.1 Create Test Fixtures

**File**: `tests/fixtures/`

**Task**: Create test fixtures for module blocks

- [ ] Create `single_module.tf` - single module block
- [ ] Create `multiple_modules.tf` - multiple module blocks
- [ ] Create `mixed_blocks.tf` - resources and modules together
- [ ] Create `nested_module.tf` - module with nested structure (if applicable)

**Example fixture** (`single_module.tf`):
```hcl
module "web_server" {
  source = "./modules/web"

  instance_count = 3
  instance_type  = "t3.medium"
}
```

### 10.2 Add Integration Tests for Module Blocks

**File**: `tests/integration_test.rs`

**Task**: Add comprehensive integration tests

- [ ] Add test using `single_module.tf` fixture
- [ ] Add test using `multiple_modules.tf` fixture
- [ ] Add test using `mixed_blocks.tf` fixture
- [ ] Verify output format matches expected format
- [ ] Verify all tests pass

---

## Phase 11: Refactoring and Optimization

### 11.1 Code Review and Refactoring

**Task**: Review code for improvements

- [ ] Review `AddressBuilder` implementation for efficiency
- [ ] Review `MovedResource` and `MovedModule` for code duplication
- [ ] Extract common logic if needed (DRY principle)
- [ ] Ensure all error handling is consistent
- [ ] Verify all comments and documentation are clear

### 11.2 Performance Verification

**Task**: Verify lazy evaluation works correctly

- [ ] Verify files are processed one at a time (not all loaded into memory)
- [ ] Verify iterator is truly lazy (no work until consumed)
- [ ] Run performance tests if needed
- [ ] Compare memory usage with old implementation

---

## Phase 12: Documentation and Final Verification

### 12.1 Update Documentation

**Task**: Update code documentation

- [ ] Add doc comments to all public structs and methods
- [ ] Add examples in documentation where helpful
- [ ] Update module-level documentation
- [ ] Verify documentation is accurate

### 12.2 Final Test Suite Verification

**Task**: Run full test suite

- [ ] Run `cargo test` - all unit tests pass
- [ ] Run `cargo test --test integration_test` - all integration tests pass
- [ ] Run `cargo nextest run` - verify test runner works
- [ ] Verify code coverage is maintained or improved
- [ ] Fix any failing tests

### 12.3 Verify Output Format

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

### Phase 6: Processor Updates
- [ ] Write tests for module block extraction
- [ ] Implement module block extraction

### Phase 7: MovedBlockBuilder
- [ ] Write tests for MovedBlockBuilder
- [ ] Implement MovedBlockBuilder

### Phase 8: Update main.rs
- [ ] Write/update integration tests
- [ ] Refactor main.rs

### Phase 9: Cleanup
- [ ] Remove deprecated functions
- [ ] Update tests in processor.rs
- [ ] Update tests in output.rs

### Phase 10: Test Fixtures
- [ ] Create module block test fixtures
- [ ] Add integration tests for module blocks

### Phase 11: Refactoring
- [ ] Code review and refactoring
- [ ] Performance verification

### Phase 12: Documentation
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
3. **Extensibility**: Easy to add new block types (just implement `ToMovedBlock`)
4. **Testability**: Each component tested independently
5. **Maintainability**: Clear separation of concerns
6. **Performance**: Use `Traversal::builder()` instead of string parsing
7. **Module Support**: Complete support for both resource and module blocks
8. **OOP Compliance**: Proper encapsulation, polymorphism, and single responsibility
9. **TDD Compliance**: Tests drive design and ensure correctness

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
  - `plan/02_W47/STREAMING_REFACTOR.md`
  - `plan/02_W47/MODULE_BLOCK_SUPPORT.md`
