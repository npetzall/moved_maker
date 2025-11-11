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

