# BUG: Attributes in moved blocks aren't indented

**Status**: ✅ Complete

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

## Related Implementation Plan

See `work/25W45/BUG_INDENTATION.md` for the detailed implementation plan.
