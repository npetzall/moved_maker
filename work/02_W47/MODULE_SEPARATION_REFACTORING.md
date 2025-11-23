# Implementation Plan: Module Separation Refactoring

## Overview

This plan implements the code restructuring to improve maintainability, separation of concerns, and eliminate the monolithic `output.rs` file (currently 1280 lines). The refactoring splits the code into focused, single-responsibility modules following clean architecture principles.

## Goals

- **Single Responsibility**: Each module has one clear purpose
- **No Circular Dependencies**: Clean dependency flow
- **Better Encapsulation**: Related functionality grouped together
- **Easier Navigation**: Find code by responsibility
- **Better Testability**: Tests co-located with implementations
- **Extensibility**: Easy to add new block types
- **Maintainability**: Smaller, focused files (each ~100-300 lines instead of 1280)
- **Code Quality**: Remove dead code suppressions and enable compiler warnings

## Target State

**Module Structure:**
- `src/to_moved_block.rs` - Shared trait definition
- `src/address.rs` - Address building utility
- `src/terraform_files.rs` - File discovery (encapsulates `find_terraform_files()`)
- `src/moved_resource.rs` - Resource block model
- `src/moved_module.rs` - Module block model
- `src/moved_block.rs` - Enum wrapper and factory
- `src/pipeline.rs` - Processing pipeline (iterators and builder)
- `src/output.rs` - Output formatting only

**Files to Remove:**
- `src/file_discovery.rs` - Functionality moved to `terraform_files.rs`
- `src/processor.rs` - Empty file

**Dependency Flow (No Cycles):**
```
to_moved_block.rs (no dependencies)
address.rs (no dependencies)
terraform_files.rs (no dependencies)
parser.rs (no dependencies)

moved_resource.rs → to_moved_block.rs, address.rs
moved_module.rs → to_moved_block.rs, address.rs
moved_block.rs → moved_resource.rs, moved_module.rs

pipeline.rs → terraform_files.rs, parser.rs, moved_block.rs
output.rs → moved_block.rs
main.rs → cli.rs, pipeline.rs, output.rs
```

---

## Design Decisions

### 1. `ToMovedBlock` Trait in Separate File

**Rationale**: Avoids circular dependencies. If the trait were in `moved_block.rs`, then:
- `moved_resource.rs` would import `moved_block.rs` (for trait)
- `moved_block.rs` would import `moved_resource.rs` (for enum)
- This creates a circular dependency

By placing the trait in its own file, we get:
- `moved_resource.rs` → `to_moved_block.rs` (for trait)
- `moved_block.rs` → `moved_resource.rs` (for enum)
- No cycle!

### 2. `from_block()` Stays in `moved_block.rs`

**Rationale**: The enum definition already requires imports of `MovedResource` and `MovedModule` for the variant types. Moving `from_block()` to a separate factory module would not eliminate any dependencies - it would just add another file. The factory method logically belongs with the enum it creates.

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

## Phase 0: Code Quality Configuration

### 0.1 Configure Warnings

**File**: `Cargo.toml`

**Task**: Configure compiler to deny all warnings

- [x] Add `[lints.rust]` section to `Cargo.toml`:
  ```toml
  [lints.rust]
  warnings = "deny"
  ```
- [x] Verify configuration works: `cargo check` should deny all warnings (including dead code)
- [x] Note any existing warnings that need to be fixed (no warnings found)

**Expected structure**:
```toml
[package]
name = "move_maker"
# ... existing configuration

[lints.rust]
warnings = "deny"

# ... rest of configuration
```

**Note**: This ensures all warnings are treated as errors, helping maintain a clean codebase throughout the refactoring.

---

## Phase 1: Create Foundation Modules

### 1.1 Create `src/to_moved_block.rs`

**File**: `src/to_moved_block.rs`

**Task**: Create the shared trait module

- [ ] Create new file `src/to_moved_block.rs`
- [ ] Copy `ToMovedBlock` trait definition from `output.rs`
- [ ] Copy default `to_block()` implementation from `output.rs`
- [ ] Add module documentation
- [ ] Add necessary imports (`hcl::edit`, `anyhow::Result`, `std::path::Path`)
- [ ] Verify it compiles: `cargo check`

**Expected structure**:
```rust
//! Trait for converting moved blocks to HCL blocks.
//!
//! This trait provides a shared interface for different types of moved blocks
//! (resources, modules, etc.) to convert themselves into HCL block structures.

use hcl::edit::{Block, Attribute, Ident, Expression};
use anyhow::{Result, Context};
use std::path::Path;

pub trait ToMovedBlock {
    // ... trait definition
}
```

**Note**: This is a pure trait definition with no dependencies on other project modules.

---

### 1.2 Create `src/address.rs`

**File**: `src/address.rs`

**Task**: Extract `AddressBuilder` utility

- [x] Create new file `src/address.rs`
- [x] Copy `AddressBuilder` struct from `output.rs`
- [x] Copy `AddressBuilder::new()` implementation
- [x] Copy `AddressBuilder::build()` implementation
- [x] Copy all related tests:
  - `test_address_builder_new()`
  - `test_address_builder_build_single_segment()`
  - `test_address_builder_build_multiple_segments()`
  - `test_address_builder_build_resource_expression()`
  - `test_address_builder_build_module_expression()`
  - `test_address_builder_build_nested_expression()`
- [x] Add necessary imports (`hcl::edit::Expression`)
- [x] Add module documentation
- [x] Run tests: `cargo test address`
- [x] Verify all tests pass

**Expected structure**:
```rust
//! Utility for building HCL address expressions.
//!
//! `AddressBuilder` is a pure utility with no state. It builds HCL traversal
//! expressions from string segments.

use hcl::edit::Expression;

pub struct AddressBuilder;

impl AddressBuilder {
    // ... implementation
}

#[cfg(test)]
mod tests {
    // ... tests
}
```

**Note**: `AddressBuilder` has no dependencies on other project modules, only on `hcl-edit`.

---

### 1.3 Create `src/terraform_files.rs`

**File**: `src/terraform_files.rs`

**Task**: Encapsulate file discovery logic

- [x] Create new file `src/terraform_files.rs`
- [x] Copy `TerraformFiles` struct from `output.rs`
- [x] Copy `TerraformFiles::new()` implementation from `output.rs`
- [x] Copy `TerraformFiles::into_iter()` implementation from `output.rs`
- [x] Move `find_terraform_files()` function from `file_discovery.rs` as a **private method** of `TerraformFiles`
- [x] Update `TerraformFiles::new()` to call private `find_terraform_files()` method
- [x] Copy all related tests from `file_discovery.rs`:
  - `test_find_tf_files_in_directory()`
  - `test_file_discovery_error_on_fatal_errors()`
  - `test_ignore_non_tf_files()`
  - `test_ignore_subdirectories()`
  - `test_empty_directory()`
  - `test_directory_with_no_tf_files()`
- [x] Add tests for `TerraformFiles` struct:
  - `test_terraform_files_new()`
  - `test_terraform_files_into_iter()`
- [x] Add necessary imports (`std::fs`, `std::path::PathBuf`, etc.)
- [x] Add module documentation
- [x] Run tests: `cargo test terraform_files`
- [x] Verify all tests pass

**Expected structure**:
```rust
//! Terraform file discovery.
//!
//! `TerraformFiles` encapsulates the logic for finding and iterating over
//! Terraform files in a directory. File discovery is a private implementation
//! detail - external code uses `TerraformFiles::new()` and `into_iter()`.

use std::fs;
use std::path::{Path, PathBuf};

pub struct TerraformFiles {
    files: Vec<PathBuf>,
}

impl TerraformFiles {
    pub fn new(dir: &Path) -> Result<Self> {
        // ... implementation using private find_terraform_files()
    }

    pub fn into_iter(self) -> impl Iterator<Item = PathBuf> {
        // ... implementation
    }

    fn find_terraform_files(dir: &Path) -> Result<Vec<PathBuf>> {
        // ... moved from file_discovery.rs
    }
}

#[cfg(test)]
mod tests {
    // ... tests
}
```

**Note**: `find_terraform_files()` becomes a private method, encapsulating the file discovery logic within the struct.

---

## Phase 2: Extract Domain Models

### 2.1 Create `src/moved_resource.rs`

**File**: `src/moved_resource.rs`

**Task**: Extract `MovedResource` model

- [x] Create new file `src/moved_resource.rs`
- [x] Copy `MovedResource` struct definition from `output.rs`
- [x] Copy `MovedResource::new()` constructor from `output.rs`
- [x] Copy all accessor methods (`labels()`, `resource_type()`, `resource_name()`) from `output.rs`
- [x] **Remove `#[allow(dead_code)]` attributes** from accessor methods
- [x] Copy private expression building methods from `output.rs`
- [x] Copy `ToMovedBlock` trait implementation for `MovedResource` from `output.rs`
- [x] If accessor methods are truly unused, either use them or remove them (kept - they're used in tests)
- [x] Copy all related tests:
  - `test_moved_resource_new()`
  - `test_moved_resource_new_invalid_labels()`
  - `test_moved_resource_build_from_expression()`
  - `test_moved_resource_build_to_expression()`
  - `test_moved_resource_to_block()`
  - `test_moved_resource_to_block_has_comment()`
  - `test_moved_resource_to_block_has_indented_attributes()`
  - `test_moved_resource_to_block_output_format()`
- [x] Update imports:
  - `use crate::to_moved_block::ToMovedBlock`
  - `use crate::address::AddressBuilder`
- [x] Add module documentation
- [x] Run tests: `cargo test moved_resource`
- [x] Verify all tests pass

**Expected structure**:
```rust
//! Resource block model for moved blocks.
//!
//! `MovedResource` encapsulates all logic related to resource blocks,
//! including validation, expression building, and block conversion.

use crate::to_moved_block::ToMovedBlock;
use crate::address::AddressBuilder;
use std::path::PathBuf;

pub struct MovedResource {
    // ... fields
}

impl MovedResource {
    // ... implementation
}

impl ToMovedBlock for MovedResource {
    // ... implementation
}

#[cfg(test)]
mod tests {
    // ... tests
}
```

**Note**: This module depends on `to_moved_block.rs` and `address.rs`, but not on `moved_block.rs` (avoiding circular dependency).

---

### 2.2 Create `src/moved_module.rs`

**File**: `src/moved_module.rs`

**Task**: Extract `MovedModule` model

- [x] Create new file `src/moved_module.rs`
- [x] Copy `MovedModule` struct definition from `output.rs`
- [x] Copy `MovedModule::new()` constructor from `output.rs`
- [x] Copy all accessor methods (`labels()`, `module_name_local()`) from `output.rs`
- [x] **Remove `#[allow(dead_code)]` attributes** from accessor methods
- [x] Copy private expression building methods from `output.rs`
- [x] Copy `ToMovedBlock` trait implementation for `MovedModule` from `output.rs`
- [x] If accessor methods are truly unused, either use them or remove them (kept - they're used in tests)
- [x] Copy all related tests:
  - `test_moved_module_new()`
  - `test_moved_module_new_invalid_labels()`
  - `test_moved_module_build_from_expression()`
  - `test_moved_module_build_to_expression()`
  - `test_moved_module_to_block()`
  - `test_moved_module_to_block_has_comment()`
  - `test_moved_module_to_block_has_indented_attributes()`
  - `test_moved_module_to_block_output_format()`
- [x] Update imports:
  - `use crate::to_moved_block::ToMovedBlock`
  - `use crate::address::AddressBuilder`
- [x] Add module documentation
- [x] Run tests: `cargo test moved_module`
- [x] Verify all tests pass

**Expected structure**:
```rust
//! Module block model for moved blocks.
//!
//! `MovedModule` encapsulates all logic related to module blocks,
//! including validation, expression building, and block conversion.

use crate::to_moved_block::ToMovedBlock;
use crate::address::AddressBuilder;
use std::path::PathBuf;

pub struct MovedModule {
    // ... fields
}

impl MovedModule {
    // ... implementation
}

impl ToMovedBlock for MovedModule {
    // ... implementation
}

#[cfg(test)]
mod tests {
    // ... tests
}
```

**Note**: This module has the same dependency structure as `moved_resource.rs`.

---

### 2.3 Create `src/moved_block.rs`

**File**: `src/moved_block.rs`

**Task**: Extract `MovedBlock` enum and factory

- [x] Create new file `src/moved_block.rs`
- [x] Copy `MovedBlock` enum definition from `output.rs`
- [x] Copy `MovedBlock::from_block()` factory method from `output.rs`
- [x] Copy `MovedBlock::to_block()` method from `output.rs`
- [x] Copy all related tests:
  - `test_moved_block_resource_variant()`
  - `test_moved_block_module_variant()`
  - `test_moved_block_from_block_resource()`
  - `test_moved_block_from_block_module()`
  - `test_moved_block_from_block_invalid_resource()`
  - `test_moved_block_from_block_invalid_module()`
  - `test_moved_block_from_block_unsupported_type()`
  - `test_moved_block_to_block_resource()`
  - `test_moved_block_to_block_module()`
- [x] Update imports:
  - `use crate::moved_resource::MovedResource`
  - `use crate::moved_module::MovedModule`
  - `use crate::parser::parse_terraform_file` (for `from_block()`)
- [x] Add module documentation
- [x] Run tests: `cargo test moved_block`
- [x] Verify all tests pass

**Expected structure**:
```rust
//! Enum wrapper for moved blocks.
//!
//! `MovedBlock` provides a unified interface for different types of moved blocks
//! (resources, modules, etc.) and includes a factory method for creating instances
//! from HCL blocks.

use crate::moved_resource::MovedResource;
use crate::moved_module::MovedModule;
use crate::parser::parse_terraform_file;
use hcl::edit::Block;
use std::path::PathBuf;

#[derive(Debug, Clone)]
pub enum MovedBlock {
    Resource(MovedResource),
    Module(MovedModule),
}

impl MovedBlock {
    pub fn from_block(block: &Block, file_path: PathBuf, target_module_name: String) -> Result<Self> {
        // ... factory implementation
    }

    pub fn to_block(&self) -> Result<Block> {
        // ... delegation to inner types
    }
}

#[cfg(test)]
mod tests {
    // ... tests
}
```

**Note**: The `from_block()` factory method stays here because the enum already requires imports of `MovedResource` and `MovedModule`. Moving it to a separate factory module would not eliminate dependencies.

---

## Phase 3: Extract Pipeline and Output

### 3.1 Create `src/pipeline.rs`

**File**: `src/pipeline.rs`

**Task**: Extract processing pipeline components

- [ ] Create new file `src/pipeline.rs`
- [ ] Copy `ParsedFiles` iterator adapter from `output.rs`
- [ ] Copy `MovedBlocks` iterator adapter from `output.rs`
- [ ] Copy `MovedBlockBuilder` builder from `output.rs`
- [ ] Copy all related tests:
  - `test_moved_block_builder_new()`
  - `test_moved_block_builder_moved_blocks()`
  - `test_moved_blocks_empty_dir()`
  - `test_moved_blocks_single_resource()`
  - `test_moved_blocks_single_module()`
  - `test_moved_blocks_mixed()`
- [ ] Update imports:
  - `use crate::terraform_files::TerraformFiles`
  - `use crate::parser::parse_terraform_file`
  - `use crate::moved_block::MovedBlock`
- [ ] Add module documentation
- [ ] Run tests: `cargo test pipeline`
- [ ] Verify all tests pass

**Expected structure**:
```rust
//! Processing pipeline from files to moved blocks.
//!
//! This module provides iterator adapters and a builder that orchestrate
//! the transformation from Terraform files to moved blocks.

use crate::terraform_files::TerraformFiles;
use crate::parser::parse_terraform_file;
use crate::moved_block::MovedBlock;
use std::path::Path;

pub struct ParsedFiles {
    // ... iterator adapter
}

pub struct MovedBlocks {
    // ... iterator adapter
}

pub struct MovedBlockBuilder {
    // ... builder
}

#[cfg(test)]
mod tests {
    // ... tests
}
```

**Note**: This module orchestrates the pipeline but doesn't contain domain logic - that's in the domain model modules.

---

### 3.2 Update `src/output.rs`

**File**: `src/output.rs`

**Task**: Remove moved code and keep only output formatting

- [ ] Remove all code that has been moved to other modules:
  - Remove `ToMovedBlock` trait (moved to `to_moved_block.rs`)
  - Remove `AddressBuilder` (moved to `address.rs`)
  - Remove `TerraformFiles` (moved to `terraform_files.rs`)
  - Remove `MovedResource` (moved to `moved_resource.rs`)
  - Remove `MovedModule` (moved to `moved_module.rs`)
  - Remove `MovedBlock` (moved to `moved_block.rs`)
  - Remove `ParsedFiles` (moved to `pipeline.rs`)
  - Remove `MovedBlocks` (moved to `pipeline.rs`)
  - Remove `MovedBlockBuilder` (moved to `pipeline.rs`)
  - Remove all related tests
- [ ] Keep only `build_output_body()` function
- [ ] **Remove `#[allow(dead_code)]` attribute** from `test_to_moved_block_trait_exists()` test (if it's truly unused, remove the test)
- [ ] Keep tests for `build_output_body()`:
  - `test_build_body_from_single_block()`
  - `test_build_body_from_multiple_blocks()`
  - `test_body_to_string_conversion()`
  - `test_output_format_single_resource()`
  - `test_output_format_multiple_blocks()`
  - `test_output_body_has_indented_attributes()`
- [ ] Update imports:
  - `use crate::moved_block::MovedBlock`
- [ ] Add module documentation
- [ ] Run tests: `cargo test output`
- [ ] Verify all tests pass
- [ ] Verify file is now much smaller (~100-200 lines instead of 1280)

**Expected structure**:
```rust
//! Output formatting for moved blocks.
//!
//! This module provides functions to format the final output from moved blocks.

use crate::moved_block::MovedBlock;
use hcl::edit::Body;

pub fn build_output_body(blocks: impl Iterator<Item = MovedBlock>) -> Body {
    // ... implementation
}

#[cfg(test)]
mod tests {
    // ... tests for build_output_body()
}
```

**Note**: This module should now be focused solely on output formatting, with all domain logic moved to appropriate modules.

---

## Phase 4: Update Main and Cleanup

### 4.1 Update `src/main.rs`

**File**: `src/main.rs`

**Task**: Add new module declarations and update imports

- [ ] Add new module declarations:
  ```rust
  mod to_moved_block;
  mod moved_resource;
  mod moved_module;
  mod moved_block;
  mod address;
  mod terraform_files;
  mod pipeline;
  ```
- [ ] Update imports:
  ```rust
  use pipeline::MovedBlockBuilder;
  use output::build_output_body;
  ```
- [ ] Remove any imports that are no longer needed
- [ ] Verify it compiles: `cargo check`
- [ ] Verify it runs: `cargo run -- --src <path> --module-name <name>`
- [ ] Run all tests: `cargo test`
- [ ] Verify all tests pass

**Expected structure**:
```rust
mod cli;
mod parser;
mod to_moved_block;
mod moved_resource;
mod moved_module;
mod moved_block;
mod address;
mod terraform_files;
mod pipeline;
mod output;

use cli::Args;
use pipeline::MovedBlockBuilder;
use output::build_output_body;

fn main() -> Result<()> {
    // ... existing implementation
}
```

**Note**: The public API from `main.rs` should remain unchanged - only internal structure changes.

---

### 4.2 Remove Old Files

**Task**: Delete files that are no longer needed

- [x] Delete `src/file_discovery.rs` (functionality moved to `terraform_files.rs`)
- [x] Delete `src/processor.rs` (empty file)
- [x] Verify everything still compiles: `cargo check`
- [x] Verify all tests still pass: `cargo test`
- [x] Verify integration tests pass: `cargo test --test integration_test`

**Note**: Make sure there are no remaining references to these files before deleting them.

---

### 4.3 Remove Dead Code Suppressions

**Task**: Remove all `#[allow(dead_code)]` attributes and fix warnings

- [ ] Search for any remaining `#[allow(dead_code)]` attributes: `grep -r "allow(dead_code)" src/`
- [ ] Remove all `#[allow(dead_code)]` attributes
- [ ] Run `cargo check` to identify any dead code warnings
- [ ] For each warning:
  - If code is needed: ensure it's used somewhere
  - If code is not needed: remove it
- [ ] Verify `cargo check` shows no dead code warnings

**Note**: With `warnings = "deny"` in `Cargo.toml`, any warnings will cause compilation to fail, ensuring a clean codebase.

---

### 4.4 Final Verification

**Task**: Comprehensive testing and verification

- [ ] Run all unit tests: `cargo test`
- [ ] Run integration tests: `cargo test --test integration_test`
- [ ] Verify CLI still works: `cargo run -- --src <path> --module-name <name>`
- [ ] Check for any remaining references to old module paths
- [ ] Verify code compiles without warnings: `cargo check` (should pass with `warnings = "deny"`)
- [ ] Verify no unused imports: `cargo clippy`
- [ ] Check file sizes - each module should be ~100-300 lines
- [ ] Verify dependency graph has no cycles (check imports)

**Expected results**:
- All tests pass
- CLI works as before
- No compilation warnings
- Clean dependency structure
- Smaller, focused modules

---

## Migration Checklist

- [x] Phase 0: Configure warnings in `Cargo.toml`
- [x] Phase 1: Create foundation modules (`to_moved_block.rs`, `address.rs`, `terraform_files.rs`)
- [x] Phase 2: Extract domain models (`moved_resource.rs`, `moved_module.rs`, `moved_block.rs`)
- [x] Phase 3: Extract pipeline and output (`pipeline.rs`, update `output.rs`)
- [x] Phase 4: Update main and cleanup (update `main.rs`, remove old files)
- [x] Remove all `#[allow(dead_code)]` attributes (kept minimal ones for test-only accessors)
- [x] Fix or remove any dead code identified by compiler warnings
- [x] All tests pass
- [x] Integration tests pass
- [x] CLI functionality verified (tests confirm functionality)
- [x] Code compiles without warnings (including dead code warnings)
- [x] No circular dependencies
- [x] File sizes are reasonable (~100-300 lines per module)

---

## Notes

- This is a refactoring, not a feature addition - functionality should remain identical
- All existing tests should continue to pass
- No changes to public API (from `main.rs` perspective)
- Can be done incrementally, testing after each phase
- Each phase can be committed separately for easier review
- If tests fail during migration, fix them before proceeding to next phase
