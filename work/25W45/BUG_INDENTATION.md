# Implementation Plan: BUG_INDENTATION

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug where attributes in moved blocks aren't indented. The solution uses attribute prefix decorations in the HCL library to add indentation while preserving comments.

## Context

Related bug report: `plan/25W45/BUG_INDENTATION.md`

## Implementation Plan (TDD Approach)

### Solution: Use Attribute Prefix Decorations

Based on the investigation, the solution is to set prefix decorations on attributes when building moved blocks. This leverages `hcl::edit`'s native encoding system to add indentation while preserving comments.

### Phase 1: Write Tests (Red)

- [x] **Add test for resource block indentation in `src/processor.rs`**:
  - [x] Create test `test_resource_moved_block_has_indented_attributes()`
  - [x] Build a resource moved block using `build_resource_moved_block()`
  - [x] Convert block to string via `Body::builder().block(block).build().to_string()`
  - [x] Assert output contains `"  from"` (indented attribute)
  - [x] Assert output contains `"  to"` (indented attribute)
  - [x] Assert output contains comment `"# From: <filename>"`
  - [x] Run test - should FAIL (red) since implementation doesn't exist yet ✓ Test fails as expected

- [x] **Add test for data block indentation in `src/processor.rs`**:
  - [x] Create test `test_data_moved_block_has_indented_attributes()`
  - [x] Build a data moved block using `build_data_moved_block()`
  - [x] Convert block to string via `Body::builder().block(block).build().to_string()`
  - [x] Assert output contains `"  from"` (indented attribute)
  - [x] Assert output contains `"  to"` (indented attribute)
  - [x] Assert output contains comment `"# From: <filename>"`
  - [x] Run test - should FAIL (red) since implementation doesn't exist yet ✓ Test fails as expected

- [x] **Add integration test in `src/output.rs`**:
  - [x] Create test `test_output_body_has_indented_attributes()`
  - [x] Build output body with multiple moved blocks (resource and data)
  - [x] Convert to string and verify all attributes are indented
  - [x] Verify all comments are preserved
  - [x] Run test - should FAIL (red) since implementation doesn't exist yet ✓ Test fails as expected

### Phase 2: Implement Solution (Green)

- [x] **Ensure `Decorate` trait is imported**:
  - [x] Verify `use hcl::edit::Decorate;` is present in `src/processor.rs` ✓ Already imported
  - [x] If not present, add the import
  - [x] This trait provides the `decor_mut()` method needed

- [x] **Modify `build_resource_moved_block()` in `src/processor.rs`**:
  - [x] Create the `from` attribute as a mutable variable
  - [x] Set its prefix decoration to `"  "` (2 spaces) using `attr.decor_mut().set_prefix("  ")`
  - [x] Create the `to` attribute as a mutable variable
  - [x] Set its prefix decoration to `"  "` (2 spaces)
  - [x] Add both attributes to the block builder
  - [x] Keep the existing comment logic unchanged
  - [x] Run tests - should PASS (green) ✓ All tests pass

- [x] **Modify `build_data_moved_block()` in `src/processor.rs`**:
  - [x] Apply the same changes as above for data blocks
  - [x] Create attributes as mutable, set prefix decorations, then add to block
  - [x] Run tests - should PASS (green) ✓ All tests pass

### Phase 3: Refactor (if needed)

- [x] **Review code for duplication**:
  - [x] Check if attribute indentation logic can be extracted to a helper function
  - [x] Consider if both functions can share common code
  - [x] Refactor if beneficial, ensuring all tests still pass
  - **Decision**: Code duplication is minimal and acceptable. Both functions are clear and maintainable as-is. Extracting a helper would add complexity without significant benefit.

### Phase 4: Verification

- [x] **Run all tests**:
  - [x] Run `cargo test` to ensure all tests pass ✓ 46 unit tests + 11 integration tests pass
  - [x] Verify no existing tests were broken ✓ All existing tests still pass

- [x] **Manual verification**:
  - [x] Run: `cargo run -- --src examples/02_networking --module-name compute` ✓
  - [x] Verify output shows indented attributes (2 spaces) ✓ Attributes are properly indented
  - [x] Verify comments are preserved ✓ All comments preserved
  - [x] Verify output matches expected format exactly ✓ Output matches expected format

### Code Changes

**Before** (current implementation):
```rust
let mut block = Block::builder(Ident::new("moved"))
    .attribute(Attribute::new(
        Ident::new("from"),
        build_from_expression(resource_type, resource_name, false),
    ))
    .attribute(Attribute::new(
        Ident::new("to"),
        build_to_expression(module_name, resource_type, resource_name, false),
    ))
    .build();
```

**After** (with indentation):
```rust
let mut from_attr = Attribute::new(
    Ident::new("from"),
    build_from_expression(resource_type, resource_name, false),
);
from_attr.decor_mut().set_prefix("  ");

let mut to_attr = Attribute::new(
    Ident::new("to"),
    build_to_expression(module_name, resource_type, resource_name, false),
);
to_attr.decor_mut().set_prefix("  ");

let mut block = Block::builder(Ident::new("moved"))
    .attribute(from_attr)
    .attribute(to_attr)
    .build();
```

### Expected Outcome

After implementation, the output should match the expected format:
```
# From: data.tf
moved {
  from = data.aws_availability_zones.available
  to = module.compute.data.aws_availability_zones.available
}
```

### Files to Modify

- `src/processor.rs`:
  - `build_resource_moved_block()` function (lines ~61-84)
  - `build_data_moved_block()` function (lines ~87-109)
  - Add `use hcl::edit::Decorate;` if not already present

### Verification

- [x] Attributes are indented with 2 spaces ✓
- [x] Comments are preserved ✓
- [x] All existing tests pass ✓ (46 unit tests + 11 integration tests)
- [x] Output matches expected format ✓
- [x] Works for both resource and data blocks ✓

## Status: ✅ COMPLETE

The fix has been successfully implemented using TDD approach:
- ✅ Phase 1: Tests written and failing (RED)
- ✅ Phase 2: Implementation complete, all tests passing (GREEN)
- ✅ Phase 3: Code review complete, no refactoring needed
- ✅ Phase 4: All verification steps passed

The output now correctly shows indented attributes while preserving comments.

## References

- Related bug report: `plan/25W45/BUG_INDENTATION.md`
