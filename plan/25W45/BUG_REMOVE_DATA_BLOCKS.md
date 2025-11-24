# BUG: Remove Data Block Handling

**Status**: ✅ Complete

## Description

After research, it has been determined that data blocks cannot and should not be moved. Data blocks are lookup blocks that will be looked up again if needed, so they don't require `moved` blocks. The current implementation incorrectly processes data blocks and generates `moved` blocks for them, which is unnecessary and incorrect.

## Root Cause

Data blocks in Terraform are different from resource blocks:
- **Resource blocks**: Represent infrastructure that needs to be tracked in state. When moved to a module, they require `moved` blocks to tell Terraform about the address change.
- **Data blocks**: Are lookup blocks that query existing infrastructure. They don't maintain state and will be re-evaluated when needed. Moving them to a module doesn't require `moved` blocks because Terraform will simply look them up again in their new location.

## Current Behavior

The tool currently:
1. Extracts data blocks from Terraform files
2. Generates `moved` blocks for data sources
3. Outputs `moved` blocks like:
   ```
   # From: data.tf
   moved {
     from = data.aws_ami.example
     to   = module.compute.data.aws_ami.example
   }
   ```

## Expected Behavior

The tool should:
1. Ignore data blocks completely
2. Only process resource blocks
3. Not generate any `moved` blocks for data sources

## Impact

- **Severity**: Medium (incorrect behavior, generates unnecessary output)
- **Priority**: High (should be fixed to align with Terraform semantics)

## Affected Files

### Core Implementation
- `src/main.rs`:
  - Line 11: Imports `build_data_moved_block`
  - Line 37: Checks `is_data` flag
  - Lines 39-43: Conditionally calls `build_data_moved_block()`

- `src/processor.rs`:
  - Line 9: Comment mentions "resource and data blocks"
  - Line 14: Filters for `"data"` blocks in `extract_blocks()`
  - Lines 20-35: `build_from_expression()` has `is_data` parameter and handles data blocks
  - Lines 38-58: `build_to_expression()` has `is_data` parameter and handles data blocks
  - Lines 93-124: `build_data_moved_block()` function (entire function should be removed)
  - Multiple tests that test data block functionality

- `src/output.rs`:
  - Line 15: Imports `build_data_moved_block`
  - Lines 61-69: `test_output_format_single_data()` test
  - Lines 72-83: `test_output_format_multiple_blocks()` test uses data blocks
  - Lines 86-108: `test_output_body_has_indented_attributes()` test uses data blocks

### Tests
- `tests/integration_test.rs`:
  - Lines 49-74: `test_single_data_file()` test
  - Lines 108-135: `test_mixed_resources_and_data()` test
  - Lines 138-165: `test_multiple_files()` test includes data blocks

### Documentation
- `README.md`: Mentions data blocks in description and examples
- `plan/25W45/REQ_BLOCK_PROCESSING.md`: Documents data block processing
- `work/25W45/DONE.md`: Documents data block implementation work

## Notes

- This is a breaking change in behavior, but it's correcting incorrect functionality
- Data blocks will simply be ignored, which is the correct behavior
- Resource blocks will continue to work as expected

## Related Implementation Plan

See `work/25W45/BUG_REMOVE_DATA_BLOCKS.md` for the detailed implementation plan.
