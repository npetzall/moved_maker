# Implementation Plan: BUG_REMOVE_DATA_BLOCKS

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug where data blocks are incorrectly processed and moved blocks are generated for them. Data blocks should be ignored as they don't require moved blocks in Terraform.

## Context

Related bug report: `plan/25W45/BUG_REMOVE_DATA_BLOCKS.md`

## Implementation Plan

### Phase 1: Remove Core Functionality

- [x] Remove `"data"` from filter in `extract_blocks()` in `src/processor.rs` (line 14)
- [x] Update comment in `extract_blocks()` to remove "and data blocks" reference (line 9)
- [x] Remove `is_data` parameter from `build_from_expression()` and simplify logic (lines 20-35)
- [x] Remove `is_data` parameter from `build_to_expression()` and simplify logic (lines 38-58)
- [x] Remove `build_data_moved_block()` function entirely (lines 93-124)
- [x] Remove `build_data_moved_block` from imports in `src/main.rs` (line 11)
- [x] Remove data block handling from `src/main.rs` (remove `is_data` check on line 37 and conditional on lines 39-43)
- [x] Remove `build_data_moved_block` from imports in `src/output.rs` (line 15)

### Phase 2: Clean Up Tests

#### Unit Tests in `src/processor.rs`
- [x] Remove or update `test_extract_data_blocks()` (lines 150-162)
- [x] Remove `test_build_from_expression_data()` (lines 207-210)
- [x] Remove `test_build_to_expression_data()` (lines 219-222)
- [x] Remove `test_build_data_moved_block()` (lines 235-242)
- [x] Remove `test_extract_labels_from_data_block()` (lines 279-293)
- [x] Remove `test_data_moved_block_has_indented_attributes()` (lines 391-411)
- [x] Update `test_extract_from_mixed_blocks()` to only expect resource blocks (lines 181-196)

#### Unit Tests in `src/output.rs`
- [x] Remove `test_output_format_single_data()` (lines 61-69)
- [x] Update `test_output_format_multiple_blocks()` to only use resources (lines 72-83)
- [x] Update `test_output_body_has_indented_attributes()` to only use resources (lines 86-108)

#### Integration Tests in `tests/integration_test.rs`
- [x] Remove `test_single_data_file()` (lines 49-74)
- [x] Update `test_mixed_resources_and_data()` to only expect resource blocks (lines 108-135)
- [x] Update `test_multiple_files()` to remove data block assertions (lines 138-165)

### Phase 3: Update Documentation

- [x] Update `README.md` to remove data block references and examples
- [x] Update or remove data block sections in `plan/25W45/REQ_BLOCK_PROCESSING.md`
- [x] Update or remove data block sections in `work/25W45/DONE.md`

### Phase 4: Verification

- [x] Run `cargo test` to ensure all tests pass
- [x] Verify tool only processes resource blocks (test with files containing data blocks)
- [x] Verify no `moved` blocks are generated for data sources
- [x] Run integration tests to verify end-to-end behavior

## References

- Related bug report: `plan/25W45/BUG_REMOVE_DATA_BLOCKS.md`
