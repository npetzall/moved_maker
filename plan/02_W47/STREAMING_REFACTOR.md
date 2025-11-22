# Streaming Refactoring Plan

## Purpose
Refactor the codebase to use a streaming, lazy evaluation approach with better separation of concerns. This refactoring will:
- Enable lazy processing of files and blocks
- Separate address building from moved block construction
- Prepare for module block support
- Follow OOP and decorator patterns

## Current State

### Current Architecture
- `run()` function in `main.rs` collects all blocks into a `Vec` before processing
- `build_resource_moved_block()` in `processor.rs` handles both expression building and block construction
- Expression building uses string parsing (inefficient)
- No separation between address building and moved block logic
- All processing happens eagerly

### Current Flow
```
run()
  -> find_terraform_files() (eager, returns Vec)
  -> for each file: parse_terraform_file() (eager)
  -> extract_blocks() (eager, returns Vec)
  -> build_resource_moved_block() (eager, does everything)
  -> collect all blocks in Vec
  -> build_output_body()
  -> print
```

## Proposed Architecture

### New Components

#### 1. `AddressBuilder`
- **Purpose**: Generic builder for creating traversal expressions from address segments
- **Responsibilities**:
  - Build traversal expressions from a list of string segments
  - Track the source file path
  - Know nothing about "from" or "to" - purely generic
- **Location**: `src/output.rs`
- **API**:
  ```rust
  pub struct AddressBuilder {
      file_path: PathBuf,
  }

  impl AddressBuilder {
      pub fn new(file_path: PathBuf) -> Self;
      pub fn file_path(&self) -> &PathBuf;
      pub fn build(&self, segments: &[&str]) -> Expression;
  }
  ```

#### 2. `MovedResource`
- **Purpose**: Represents a moved resource block
- **Responsibilities**:
  - Hold resource-specific data (type, name, file path, target module)
  - Use `AddressBuilder` to construct "from" and "to" expressions
  - Convert itself to an HCL Block
- **Location**: `src/output.rs`
- **API**:
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
      ) -> Self;
      fn build_from_expression(&self) -> Expression;
      fn build_to_expression(&self) -> Expression;
  }
  ```

#### 3. `MovedModule`
- **Purpose**: Represents a moved module block
- **Responsibilities**:
  - Hold module-specific data (module name, file path, target module)
  - Use `AddressBuilder` to construct "from" and "to" expressions
  - Convert itself to an HCL Block
- **Location**: `src/output.rs`
- **API**:
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
      ) -> Self;
      fn build_from_expression(&self) -> Expression;
      fn build_to_expression(&self) -> Expression;
  }
  ```

#### 4. `ToMovedBlock` Trait
- **Purpose**: Common interface for converting moved blocks to HCL Blocks
- **Location**: `src/output.rs`
- **API**:
  ```rust
  pub trait ToMovedBlock {
      fn to_block(&self) -> Result<Block>;
  }

  impl ToMovedBlock for MovedResource { ... }
  impl ToMovedBlock for MovedModule { ... }
  ```

#### 5. `MovedBlock` Enum
- **Purpose**: Type-safe container for either a `MovedResource` or `MovedModule`
- **Location**: `src/output.rs`
- **API**:
  ```rust
  pub enum MovedBlock {
      Resource(MovedResource),
      Module(MovedModule),
  }

  impl ToMovedBlock for MovedBlock { ... }
  ```

#### 6. `MovedBlockBuilder`
- **Purpose**: Main struct for generating moved blocks lazily
- **Responsibilities**:
  - Hold source path and module name
  - Provide lazy iterator over `MovedBlock` instances
  - No work during construction - everything lazy
- **Location**: `src/output.rs`
- **API**:
  ```rust
  pub struct MovedBlockBuilder {
      src: PathBuf,
      module_name: String,
  }

  impl MovedBlockBuilder {
      pub fn new(src: PathBuf, module_name: String) -> Self;
      pub fn moved_blocks(&self) -> impl Iterator<Item = Result<MovedBlock>> + '_;
  }
  ```

### New Flow
```
run()
  -> MovedBlockBuilder::new() (lazy, no work)
  -> moved_blocks() (returns iterator, still lazy)
  -> Iterator consumption triggers:
      -> find_terraform_files() (lazy, per file)
      -> parse_terraform_file() (lazy, per file)
      -> extract_blocks() (lazy, per file)
      -> MovedResource::new() or MovedModule::new() (lazy, per block)
  -> to_block() (lazy, per block)
  -> build_output_body()
  -> print
```

## Implementation Steps

### Step 1: Create AddressBuilder
- [ ] Add `AddressBuilder` struct to `src/output.rs`
- [ ] Implement `new()`, `file_path()`, and `build()` methods
- [ ] Use `hcl::expr::Traversal::builder()` with `.attr()` chaining
- [ ] Add unit tests for `AddressBuilder::build()`

### Step 2: Create ToMovedBlock Trait
- [ ] Define `ToMovedBlock` trait in `src/output.rs`
- [ ] Define `to_block()` method signature

### Step 3: Create MovedResource
- [ ] Add `MovedResource` struct to `src/output.rs`
- [ ] Implement `new()` constructor
- [ ] Implement `build_from_expression()` and `build_to_expression()` methods
- [ ] Implement `ToMovedBlock` trait for `MovedResource`
- [ ] Add unit tests for `MovedResource`

### Step 4: Create MovedModule
- [ ] Add `MovedModule` struct to `src/output.rs`
- [ ] Implement `new()` constructor
- [ ] Implement `build_from_expression()` and `build_to_expression()` methods
- [ ] Implement `ToMovedBlock` trait for `MovedModule`
- [ ] Add unit tests for `MovedModule`

### Step 5: Create MovedBlock Enum
- [ ] Add `MovedBlock` enum to `src/output.rs`
- [ ] Implement `ToMovedBlock` trait for `MovedBlock`
- [ ] Add unit tests for `MovedBlock`

### Step 6: Create MovedBlockBuilder
- [ ] Add `MovedBlockBuilder` struct to `src/output.rs`
- [ ] Implement `new()` constructor
- [ ] Implement `moved_blocks()` method returning lazy iterator
- [ ] Handle file discovery errors gracefully
- [ ] Handle parsing errors gracefully (warnings, continue)
- [ ] Extract resource blocks and convert to `MovedResource`
- [ ] Add unit tests for `MovedBlockBuilder`

### Step 7: Update main.rs
- [ ] Update imports to use new types
- [ ] Refactor `run()` to use `MovedBlockBuilder`
- [ ] Update to use lazy iterator pattern
- [ ] Convert `MovedBlock` instances to `Block` using trait
- [ ] Verify output format remains the same

### Step 8: Update processor.rs
- [ ] Remove `build_resource_moved_block()` function (moved to `MovedResource`)
- [ ] Remove `build_from_expression()` and `build_to_expression()` functions (moved to `AddressBuilder`)
- [ ] Keep `extract_blocks()` function (still needed)
- [ ] Add `extract_module_blocks()` function for future module support
- [ ] Update any tests that reference removed functions

### Step 9: Update Tests
- [ ] Update existing tests in `output.rs` to use new structure
- [ ] Add tests for `AddressBuilder`
- [ ] Add tests for `MovedResource`
- [ ] Add tests for `MovedModule`
- [ ] Add tests for `MovedBlockBuilder`
- [ ] Update integration tests if needed
- [ ] Verify all existing tests pass

### Step 10: Add Module Block Support (Future)
- [ ] Update `MovedBlockBuilder::moved_blocks()` to extract module blocks
- [ ] Convert module blocks to `MovedModule` instances
- [ ] Add module block test fixtures
- [ ] Add tests for module block processing

## Design Principles

### 1. Lazy Evaluation
- No work performed during construction
- All processing happens when iterator is consumed
- Files processed one at a time (memory efficient)

### 2. Separation of Concerns
- `AddressBuilder`: Generic address construction
- `MovedResource`/`MovedModule`: Block-specific logic
- `MovedBlockBuilder`: Orchestration and iteration
- `ToMovedBlock`: Common interface

### 3. Decorator Pattern
- Iterator chain transforms data step by step
- Each step is independent and composable
- Errors handled gracefully at each step

### 4. OOP Principles
- Encapsulation: Each struct holds its own data
- Polymorphism: Trait-based interface
- Single Responsibility: Each component has one job

## Benefits

1. **Memory Efficiency**: Process files one at a time instead of loading all into memory
2. **Lazy Evaluation**: No work until needed
3. **Extensibility**: Easy to add new block types (just implement `ToMovedBlock`)
4. **Testability**: Each component can be tested independently
5. **Maintainability**: Clear separation of concerns
6. **Performance**: Use `Traversal::builder()` instead of string parsing

## Migration Strategy

1. Implement new structure alongside existing code
2. Add comprehensive tests for new components
3. Update `main.rs` to use new structure
4. Remove old code from `processor.rs`
5. Update all tests
6. Verify output format is identical

## Testing Strategy

### Unit Tests
- `AddressBuilder::build()` with various segment combinations
- `MovedResource::to_block()` produces correct output
- `MovedModule::to_block()` produces correct output
- `MovedBlockBuilder::moved_blocks()` returns correct iterator

### Integration Tests
- End-to-end test with multiple files
- Test error handling (invalid files, parse errors)
- Verify output format matches current implementation

### Regression Tests
- Compare output from old and new implementations
- Ensure all existing test fixtures still work

## Related Work

- **MODULE_BLOCK_SUPPORT.md**: This refactoring prepares for module block support
- The new structure makes it trivial to add `MovedModule` support

## Implementation

This plan has been combined with module block support into a single implementation plan following OOP and TDD principles:

- **Implementation Plan**: `work/02_W47/STREAMING_REFACTOR_AND_MODULE_SUPPORT.md`

The combined plan integrates both the streaming refactor and module block support, with a phased TDD approach.

## References

- [HCL TraversalBuilder Documentation](https://docs.rs/hcl-rs/latest/hcl/expr/struct.TraversalBuilder.html)
- [Rust Iterator Pattern](https://doc.rust-lang.org/book/ch13-02-iterators.html)
- [Decorator Pattern](https://en.wikipedia.org/wiki/Decorator_pattern)
