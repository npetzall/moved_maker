# Code Restructuring Plan: Module Separation

## Overview

This plan restructures the codebase to improve maintainability, separation of concerns, and eliminate the monolithic `output.rs` file (currently 1280 lines). The refactoring splits the code into focused, single-responsibility modules following clean architecture principles.

## Current Problems

1. **Monolithic `output.rs`**: 1280 lines containing multiple responsibilities:
   - Domain models (`MovedResource`, `MovedModule`, `MovedBlock`)
   - Trait definitions (`ToMovedBlock`)
   - Iterator adapters (`TerraformFiles`, `ParsedFiles`, `MovedBlocks`)
   - Builder pattern (`MovedBlockBuilder`)
   - Utility functions (`AddressBuilder`, `build_output_body`)
   - ~800 lines of tests

2. **Empty `processor.rs`**: Contains only comments, should be removed

3. **Tight coupling**: Many concepts bundled together in one file

4. **File discovery separation**: `find_terraform_files()` is a standalone function that should be encapsulated within `TerraformFiles`

5. **Dead code suppression**: Multiple `#[allow(dead_code)]` attributes suppress warnings for unused code that should either be used or removed

## Goals

- **Single Responsibility**: Each module has one clear purpose
- **No Circular Dependencies**: Clean dependency flow
- **Better Encapsulation**: Related functionality grouped together
- **Easier Navigation**: Find code by responsibility
- **Better Testability**: Tests co-located with implementations
- **Extensibility**: Easy to add new block types
- **Code Quality**: Remove dead code suppressions and enable compiler warnings

## Proposed Module Structure

### 1. `src/to_moved_block.rs` - Shared Trait

**Purpose**: Defines the shared interface for converting moved blocks to HCL blocks

**Contents**:
- `ToMovedBlock` trait definition
- Default `to_block()` implementation (Template Method pattern)
- Trait documentation

**Dependencies**: None (pure trait definition)

**Why Separate**:
- Avoids circular dependency issues
- Both `MovedResource` and `MovedModule` need this trait
- Keeps trait definition independent of implementations

---

### 2. `src/moved_resource.rs` - Resource Block Model

**Purpose**: Encapsulates all logic related to resource blocks

**Contents**:
- `MovedResource` struct definition
- `MovedResource::new()` constructor with validation
- Accessor methods (`labels()`, `resource_type()`, `resource_name()`)
- Private expression building methods
- `ToMovedBlock` trait implementation for `MovedResource`
- All related unit tests

**Dependencies**:
- `to_moved_block.rs` (for `ToMovedBlock` trait)
- `address.rs` (for `AddressBuilder`)

**Tests to Move**:
- `test_moved_resource_new()`
- `test_moved_resource_new_invalid_labels()`
- `test_moved_resource_build_from_expression()`
- `test_moved_resource_build_to_expression()`
- `test_moved_resource_to_block()`
- `test_moved_resource_to_block_has_comment()`
- `test_moved_resource_to_block_has_indented_attributes()`
- `test_moved_resource_to_block_output_format()`

---

### 3. `src/moved_module.rs` - Module Block Model

**Purpose**: Encapsulates all logic related to module blocks

**Contents**:
- `MovedModule` struct definition
- `MovedModule::new()` constructor with validation
- Accessor methods (`labels()`, `module_name_local()`)
- Private expression building methods
- `ToMovedBlock` trait implementation for `MovedModule`
- All related unit tests

**Dependencies**:
- `to_moved_block.rs` (for `ToMovedBlock` trait)
- `address.rs` (for `AddressBuilder`)

**Tests to Move**:
- `test_moved_module_new()`
- `test_moved_module_new_invalid_labels()`
- `test_moved_module_build_from_expression()`
- `test_moved_module_build_to_expression()`
- `test_moved_module_to_block()`
- `test_moved_module_to_block_has_comment()`
- `test_moved_module_to_block_has_indented_attributes()`
- `test_moved_module_to_block_output_format()`

---

### 4. `src/moved_block.rs` - Enum Wrapper

**Purpose**: Provides unified interface and factory for creating moved blocks

**Contents**:
- `MovedBlock` enum definition (wraps `MovedResource` and `MovedModule`)
- `MovedBlock::from_block()` factory method
- `MovedBlock::to_block()` method (delegates to inner types)
- Enum-related tests

**Dependencies**:
- `moved_resource.rs` (for `MovedResource` type)
- `moved_module.rs` (for `MovedModule` type)

**Why `from_block()` Stays Here**:
- The enum definition already requires imports of `MovedResource` and `MovedModule`
- Factory method logically belongs with the enum it creates
- No additional circular dependency introduced

**Tests to Move**:
- `test_moved_block_resource_variant()`
- `test_moved_block_module_variant()`
- `test_moved_block_from_block_resource()`
- `test_moved_block_from_block_module()`
- `test_moved_block_from_block_invalid_resource()`
- `test_moved_block_from_block_invalid_module()`
- `test_moved_block_from_block_unsupported_type()`
- `test_moved_block_to_block_resource()`
- `test_moved_block_to_block_module()`

---

### 5. `src/address.rs` - Address Building Utility

**Purpose**: Pure utility for building HCL address expressions

**Contents**:
- `AddressBuilder` struct
- `AddressBuilder::new()` constructor
- `AddressBuilder::build()` method
- All related unit tests

**Dependencies**: None (pure utility, uses only hcl-edit)

**Tests to Move**:
- `test_address_builder_new()`
- `test_address_builder_build_single_segment()`
- `test_address_builder_build_multiple_segments()`
- `test_address_builder_build_resource_expression()`
- `test_address_builder_build_module_expression()`
- `test_address_builder_build_nested_expression()`

---

### 6. `src/terraform_files.rs` - File Discovery (NEW)

**Purpose**: Encapsulates Terraform file discovery logic

**Contents**:
- `TerraformFiles` struct
- `TerraformFiles::new()` constructor
- Private `find_terraform_files()` method (moved from `file_discovery.rs`)
- Public `into_iter()` method
- All related unit tests (moved from `file_discovery.rs`)

**Dependencies**: None (uses only std::fs)

**Key Design Decision**:
- `find_terraform_files()` becomes a **private method** of `TerraformFiles`
- Encapsulates file discovery logic within the struct
- External code uses `TerraformFiles::new()` instead of calling standalone function

**Tests to Move** (from `file_discovery.rs`):
- `test_find_tf_files_in_directory()`
- `test_file_discovery_error_on_fatal_errors()`
- `test_ignore_non_tf_files()`
- `test_ignore_subdirectories()`
- `test_empty_directory()`
- `test_directory_with_no_tf_files()`

**Additional Tests**:
- `test_terraform_files_new()`
- `test_terraform_files_into_iter()`

---

### 7. `src/pipeline.rs` - Processing Pipeline

**Purpose**: Orchestrates the processing pipeline from files to moved blocks

**Contents**:
- `ParsedFiles` adapter (converts files to parsed bodies)
- `MovedBlocks` iterator (converts blocks to `MovedBlock` instances)
- `MovedBlockBuilder` builder (composes the pipeline)
- All related unit tests

**Dependencies**:
- `terraform_files.rs` (for `TerraformFiles`)
- `parser.rs` (for `parse_terraform_file`)
- `moved_block.rs` (for `MovedBlock::from_block()`)

**Tests to Move**:
- `test_moved_block_builder_new()`
- `test_moved_block_builder_moved_blocks()`
- `test_moved_blocks_empty_dir()`
- `test_moved_blocks_single_resource()`
- `test_moved_blocks_single_module()`
- `test_moved_blocks_mixed()`

---

### 8. `src/output.rs` - Output Formatting

**Purpose**: Formats the final output

**Contents**:
- `build_output_body()` function
- Related unit tests

**Dependencies**:
- `moved_block.rs` (for `MovedBlock::to_block()`)

**Tests to Move**:
- `test_build_body_from_single_block()`
- `test_build_body_from_multiple_blocks()`
- `test_body_to_string_conversion()`
- `test_output_format_single_resource()`
- `test_output_format_multiple_blocks()`
- `test_output_body_has_indented_attributes()`

---

### 9. Files to Keep As-Is

- `src/main.rs` - Entry point (will update imports)
- `src/cli.rs` - CLI argument parsing
- `src/parser.rs` - HCL parsing

---

### 10. Files to Remove

- `src/file_discovery.rs` - Functionality moved to `terraform_files.rs`
- `src/processor.rs` - Empty file, can be removed

---

## Final File Structure

```
src/
├── main.rs              # Entry point (orchestration)
├── cli.rs               # CLI argument parsing
├── terraform_files.rs   # TerraformFiles with private find_terraform_files()
├── parser.rs            # HCL parsing
├── to_moved_block.rs    # ToMovedBlock trait (shared interface)
├── moved_resource.rs    # MovedResource struct + ToMovedBlock impl
├── moved_module.rs      # MovedModule struct + ToMovedBlock impl
├── moved_block.rs       # MovedBlock enum + from_block() factory
├── address.rs           # AddressBuilder utility
├── pipeline.rs          # Iterator adapters and builder
└── output.rs            # Output formatting
```

---

## Dependency Graph (No Cycles)

```
to_moved_block.rs (no dependencies)

address.rs (no dependencies)

moved_resource.rs
  ├── to_moved_block.rs
  └── address.rs

moved_module.rs
  ├── to_moved_block.rs
  └── address.rs

moved_block.rs
  ├── moved_resource.rs
  └── moved_module.rs

terraform_files.rs (no dependencies)

parser.rs (no dependencies)

pipeline.rs
  ├── terraform_files.rs
  ├── parser.rs
  └── moved_block.rs

output.rs
  └── moved_block.rs

main.rs
  ├── cli.rs
  ├── pipeline.rs (via MovedBlockBuilder)
  └── output.rs
```

---

## Implementation Steps

### Phase 0: Code Quality Configuration

0. **Configure Warnings**
   - Add `[lints.rust]` section to `Cargo.toml`:
     ```toml
     [lints.rust]
     warnings = "deny"
     ```
   - Verify configuration works: `cargo check` should deny all warnings (including dead code)

### Phase 1: Create New Module Files

1. **Create `src/to_moved_block.rs`**
   - Copy `ToMovedBlock` trait from `output.rs`
   - Add module documentation
   - Verify it compiles

2. **Create `src/address.rs`**
   - Copy `AddressBuilder` struct and implementation from `output.rs`
   - Copy related tests
   - Update imports
   - Run tests to verify

3. **Create `src/terraform_files.rs`**
   - Create `TerraformFiles` struct
   - Move `find_terraform_files()` from `file_discovery.rs` as private method
   - Move `TerraformFiles` struct and `into_iter()` from `output.rs`
   - Copy related tests from `file_discovery.rs`
   - Update imports
   - Run tests to verify

### Phase 2: Extract Domain Models

4. **Create `src/moved_resource.rs`**
   - Copy `MovedResource` struct from `output.rs`
   - Copy `MovedResource` implementation
   - Copy `ToMovedBlock` implementation for `MovedResource`
   - Copy related tests
   - **Remove `#[allow(dead_code)]` attributes** from accessor methods (`labels()`, `resource_type()`, `resource_name()`)
   - Update imports (add `use crate::to_moved_block::ToMovedBlock` and `use crate::address::AddressBuilder`)
   - Run tests to verify
   - If accessor methods are truly unused, either use them or remove them

5. **Create `src/moved_module.rs`**
   - Copy `MovedModule` struct from `output.rs`
   - Copy `MovedModule` implementation
   - Copy `ToMovedBlock` implementation for `MovedModule`
   - Copy related tests
   - **Remove `#[allow(dead_code)]` attributes** from accessor methods (`labels()`, `module_name_local()`)
   - Update imports (add `use crate::to_moved_block::ToMovedBlock` and `use crate::address::AddressBuilder`)
   - Run tests to verify
   - If accessor methods are truly unused, either use them or remove them

6. **Create `src/moved_block.rs`**
   - Copy `MovedBlock` enum from `output.rs`
   - Copy `MovedBlock::from_block()` method
   - Copy `MovedBlock::to_block()` method
   - Copy related tests
   - Update imports (add `use crate::moved_resource::MovedResource` and `use crate::moved_module::MovedModule`)
   - Run tests to verify

### Phase 3: Extract Pipeline and Output

7. **Create `src/pipeline.rs`**
   - Copy `ParsedFiles` from `output.rs`
   - Copy `MovedBlocks` iterator from `output.rs`
   - Copy `MovedBlockBuilder` from `output.rs`
   - Copy related tests
   - Update imports:
     - `use crate::terraform_files::TerraformFiles`
     - `use crate::parser::parse_terraform_file`
     - `use crate::moved_block::MovedBlock`
   - Run tests to verify

8. **Update `src/output.rs`**
   - Remove all moved code
   - Keep only `build_output_body()` function
   - Keep related tests
   - **Remove `#[allow(dead_code)]` attribute** from `test_to_moved_block_trait_exists()` test (if it's truly unused, remove the test)
   - Update imports (add `use crate::moved_block::MovedBlock`)
   - Run tests to verify

### Phase 4: Update Main and Cleanup

9. **Update `src/main.rs`**
   - Add new module declarations:
     ```rust
     mod to_moved_block;
     mod moved_resource;
     mod moved_module;
     mod moved_block;
     mod address;
     mod terraform_files;
     mod pipeline;
     ```
   - Update imports:
     ```rust
     use pipeline::MovedBlockBuilder;
     use output::build_output_body;
     ```
   - Verify it compiles and runs

10. **Remove Old Files**
    - Delete `src/file_discovery.rs`
    - Delete `src/processor.rs`
    - Verify everything still compiles

11. **Remove Dead Code Suppressions**
    - Search for any remaining `#[allow(dead_code)]` attributes: `grep -r "allow(dead_code)" src/`
    - Remove all `#[allow(dead_code)]` attributes
    - Run `cargo check` to identify any dead code warnings
    - For each warning:
      - If code is needed: ensure it's used somewhere
      - If code is not needed: remove it
    - Verify `cargo check` shows no dead code warnings

12. **Final Verification**
    - Run all tests: `cargo test`
    - Run integration tests: `cargo test --test integration_test`
    - Verify CLI still works: `cargo run -- --src <path> --module-name <name>`
    - Check for any remaining references to old module paths
    - Verify `cargo check` shows no warnings (especially no dead code warnings)

---

## Key Design Decisions

### 1. `from_block()` Stays in `moved_block.rs`

**Rationale**: The enum definition already requires imports of `MovedResource` and `MovedModule` for the variant types. Moving `from_block()` to a separate factory module would not eliminate any dependencies - it would just add another file. The factory method logically belongs with the enum it creates.

### 2. `ToMovedBlock` Trait in Separate File

**Rationale**: This avoids circular dependencies. If the trait were in `moved_block.rs`, then:
- `moved_resource.rs` would import `moved_block.rs` (for trait)
- `moved_block.rs` would import `moved_resource.rs` (for enum)
- This creates a circular dependency

By placing the trait in its own file, we get:
- `moved_resource.rs` → `to_moved_block.rs` (for trait)
- `moved_block.rs` → `moved_resource.rs` (for enum)
- No cycle!

### 3. `find_terraform_files()` as Private Method

**Rationale**: Encapsulates file discovery logic within `TerraformFiles`. External code uses `TerraformFiles::new()` and `into_iter()`, not a standalone function. This follows OOP encapsulation principles.

### 4. Each Concrete Type in Own File

**Rationale**:
- Single Responsibility Principle
- Easier to find and maintain code
- Clear separation of concerns
- Better test organization

### 5. Remove Dead Code Suppressions

**Rationale**:
- `#[allow(dead_code)]` attributes hide unused code that should either be used or removed
- Dead code indicates incomplete refactoring or unused public APIs
- Denying all warnings (not just dead code) helps maintain a clean, warning-free codebase
- Configuration in `Cargo.toml` ensures warnings are enforced project-wide

**Implementation**:
- Remove all `#[allow(dead_code)]` attributes from the codebase
- Add `[lints.rust]` section to `Cargo.toml` with `warnings = "deny"`
- Fix any legitimate warnings by either using the code or removing it

---

## Testing Strategy

1. **Move tests with code**: Each module's tests move with the module
2. **Run tests after each phase**: Verify nothing breaks during migration
3. **Integration tests**: Ensure end-to-end functionality still works
4. **No test changes needed**: Tests should work as-is after updating imports

---

## Migration Checklist

- [ ] Phase 0: Configure dead code warnings in `Cargo.toml`
- [ ] Phase 1: Create new module files (`to_moved_block.rs`, `address.rs`, `terraform_files.rs`)
- [ ] Phase 2: Extract domain models (`moved_resource.rs`, `moved_module.rs`, `moved_block.rs`)
- [ ] Phase 3: Extract pipeline and output (`pipeline.rs`, update `output.rs`)
- [ ] Phase 4: Update main and cleanup (update `main.rs`, remove old files)
- [ ] Remove all `#[allow(dead_code)]` attributes
- [ ] Fix or remove any dead code identified by compiler warnings
- [ ] All tests pass
- [ ] Integration tests pass
- [ ] CLI functionality verified
- [ ] Code compiles without warnings (including dead code warnings)
- [ ] Documentation updated if needed

---

## Benefits Summary

1. **Single Responsibility**: Each module has one clear purpose
2. **No Circular Dependencies**: Clean dependency flow
3. **Better Encapsulation**: Related functionality grouped together
4. **Easier Navigation**: Find code by responsibility
5. **Better Testability**: Tests co-located with implementations
6. **Extensibility**: Easy to add new block types
7. **Maintainability**: Smaller, focused files (each ~100-300 lines instead of 1280)

---

## Notes

- This is a refactoring, not a feature addition - functionality should remain identical
- All existing tests should continue to pass
- No changes to public API (from `main.rs` perspective)
- Can be done incrementally, testing after each phase
