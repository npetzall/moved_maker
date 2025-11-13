# Bug: Attributes in moved blocks aren't indented

## Description

When running the tool, the attributes (`from` and `to`) inside the `moved` blocks are not properly indented. They appear at the beginning of the line instead of being indented within the block.

## Current Output

```
# From: data.tf
moved {
from = data.aws_availability_zones.available
to = module.compute.data.aws_availability_zones.available
}
```

## Expected Output

```
# From: data.tf
moved {
  from = data.aws_availability_zones.available
  to = module.compute.data.aws_availability_zones.available
}
```

## Steps to Reproduce

1. Run the tool with any Terraform directory:
   ```bash
   cargo run -- --src examples/02_networking --module-name compute
   ```

2. Observe the output - attributes are not indented

## Root Cause

The issue appears to be in how the HCL library (`hcl::edit`) formats blocks when converting them to strings. The `Body::to_string()` method or the `Block::to_string()` method may not be applying proper indentation to attributes within blocks.

## Affected Files

- `src/output.rs` - `build_output_body()` function
- `src/processor.rs` - `build_resource_moved_block()` and `build_data_moved_block()` functions

## Impact

- **Severity**: Low (cosmetic, but affects code style and readability)
- **Priority**: Medium (should be fixed for proper Terraform formatting standards)

## Notes

The HCL library may need custom formatting logic to ensure proper indentation, or we may need to use a different method to format the output.

## Investigation: Formatting Options

### Current Implementation

Currently, the output is generated using the `Display` trait:
- In `src/main.rs` line 55: `println!("{}", output_body);`
- This uses `Body`'s `Display` implementation
- The `Display` trait implementation may not apply proper indentation

### Potential Solution: `hcl::format::to_string`

According to investigation, `hcl::format::to_string` is available and will format HCL with proper indentation. However, there are open questions:

1. **Comment Preservation**: It's unclear if `hcl::format::to_string` will preserve comments that are attached via `Block::decor_mut().set_prefix()`. This needs to be tested.

2. **Display vs ToString vs Formatter**:
   - The `Display` trait is what's currently being used via `println!("{}", body)`
   - `Display` implementations typically call `to_string()` internally, but may not use `hcl::format::to_string`
   - We need to check if `Body`'s `Display` implementation uses `hcl::format::to_string` or a simpler formatting method
   - If `Display` doesn't use the formatter, we may need to explicitly call `hcl::format::to_string()` instead

### Key Findings

- `hcl::edit::structure::Body` (what we use) does NOT implement `Format` trait
- `hcl::Body` (different type) implements `Format` trait
- Conversion from `hcl::edit::structure::Body` to `hcl::Body` is possible via `From` trait
- **However**: Conversion loses decorations (comments) attached via `decor().prefix()`

### The Problem

We need BOTH:
- ✓ Proper indentation (available via `hcl::format::to_string`)
- ✓ Comments preserved (available via `Display` on `hcl::edit::structure::Body`)

But we can't have both with the current approach:
- Using `Display` gives us comments but no indentation
- Using `hcl::format::to_string` gives us indentation but loses comments

### Potential Solutions

1. **Format blocks individually and manually add comments**:
   - Convert each block to `hcl::Block`, format it, then prepend the comment
   - More complex but preserves both

2. **Use a custom formatter**:
   - Format the body structure with `hcl::format::to_string`
   - Manually insert comments at the correct positions
   - Requires parsing the formatted output to find insertion points

3. **Post-process the formatted output**:
   - Format with `hcl::format::to_string` for indentation
   - Use regex or string manipulation to add comments back
   - Simpler but less robust

4. **Check if there's a way to format `hcl::edit::structure::Body` directly**: ✓ **SOLUTION FOUND**
   - `hcl::edit` uses an `Encode` trait system that preserves decorations
   - `Body::Display` implementation uses `encode_decorated()` which preserves all decorations
   - **Key discovery**: Attributes can have prefix decorations set via `attr.decor_mut().set_prefix("  ")`
   - When attributes are encoded within a block body, their prefix decorations are written before the attribute
   - This means we can manually set indentation on attributes while preserving block-level comments

   **Implementation Approach**:
   - Modify `build_resource_moved_block()` and `build_data_moved_block()` in `src/processor.rs`
   - After creating attributes, set their prefix decorations: `attr.decor_mut().set_prefix("  ")`
   - This will cause `hcl::edit`'s encoder to write the indentation when formatting
   - No conversion needed - works directly with `hcl::edit::structure::Body` and `Display` trait

### Code Location to Investigate

- `src/main.rs:55` - Current output: `println!("{}", output_body);`
- `src/output.rs` - Could add a formatting function here that uses `hcl::format::to_string`

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
