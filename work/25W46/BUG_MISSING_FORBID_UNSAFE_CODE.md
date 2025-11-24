# Implementation Plan: BUG_MISSING_FORBID_UNSAFE_CODE

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_MISSING_FORBID_UNSAFE_CODE.md`.

## Context

Related bug report: `plan/25W46/BUG_MISSING_FORBID_UNSAFE_CODE.md`

## Steps to Fix

### Step 1: Add the attribute to main.rs

Add `#![forbid(unsafe_code)]` immediately after the license comment block and before the module declarations:

**File:** `src/main.rs`

**Location:** After line 13 (end of license comment), before line 14 (first `mod` declaration)

**Change:**
```rust
// ... license comment ...
#![forbid(unsafe_code)]
mod cli;
```

## Affected Files

- `src/main.rs` (add attribute after license comment, before module declarations)

## Example Fix

### Before:
```rust
// Copyright 2025 Nils Petzall
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
mod cli;
```

### After:
```rust
// Copyright 2025 Nils Petzall
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
#![forbid(unsafe_code)]
mod cli;
```

## Status

✅ **COMPLETED** - `#![forbid(unsafe_code)]` attribute has been added to `src/main.rs`. The project builds and all tests pass with the new attribute, confirming no unsafe code exists in the codebase.

## References

- [Rust Reference: The `forbid` attribute](https://doc.rust-lang.org/reference/attributes/diagnostics.html#the-forbid-attribute)
- [Rust Book: Unsafe Rust](https://doc.rust-lang.org/book/ch19-01-unsafe-rust.html)
- [Rust API Guidelines: Unsafe Code](https://rust-lang.github.io/api-guidelines/documentation.html#c-unsafe)

## Notes

- The `#![forbid(unsafe_code)]` attribute must be placed at the crate root (in `main.rs` for binary crates, or `lib.rs` for library crates)
- This attribute applies to the entire crate, including all modules
- The attribute uses `#![...]` (with `!`) because it's a crate-level attribute, not a module-level attribute
- If unsafe code is needed in the future, this attribute would need to be removed or changed to `#![deny(unsafe_code)]` (which allows overriding) or `#![warn(unsafe_code)]` (which only warns)
- This complements `cargo-geiger` by providing compile-time enforcement in addition to runtime scanning
- The attribute will cause compilation to fail if any unsafe code is introduced, providing immediate feedback during development

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `src/main.rs`

**File:** `src/main.rs`

1. **Add `#![forbid(unsafe_code)]` attribute (line 14)** ✅ COMPLETED
   - [x] Locate the end of the license comment block (line 13)
   - [x] Add `#![forbid(unsafe_code)]` on a new line after the license comment (line 14)
   - [x] Verify placement: The attribute should be:
     - After the license comment (after line 13)
     - Before any module declarations (`mod` statements, before line 15)
     - At the crate root level
   - [x] Verify the attribute uses `#![...]` syntax (with `!`) for crate-level attributes
   - [x] Verify the file structure:
     ```rust
     // ... license comment ...
     #![forbid(unsafe_code)]
     mod cli;
     // ... rest of the file ...
     ```

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `src/main.rs`
   - Remove the `#![forbid(unsafe_code)]` attribute
   - Verify the project builds and tests pass
   - Restore the file to its previous state

2. **Partial Rollback**
   - If the attribute causes compilation issues, verify that no unsafe code exists in the codebase
   - Check if any dependencies use unsafe code that might conflict
   - Consider changing to `#![deny(unsafe_code)]` (allows overriding) if needed
   - Consider changing to `#![warn(unsafe_code)]` (only warns) if needed

3. **Alternative Approaches**
   - If `#![forbid(unsafe_code)]` is too strict, use `#![deny(unsafe_code)]` instead:
     ```rust
     #![deny(unsafe_code)]
     ```
   - If only warnings are desired, use `#![warn(unsafe_code)]`:
     ```rust
     #![warn(unsafe_code)]
     ```
   - Verify that `cargo-geiger` still works correctly with the attribute
   - Check if any transitive dependencies require unsafe code

### Implementation Order

1. [x] Add `#![forbid(unsafe_code)]` to `src/main.rs` (line 14, after license comment) ✅ COMPLETED
2. [x] Run `cargo build` to verify the project compiles ✅ COMPLETED
3. [x] Run `cargo test` to ensure all tests pass ✅ COMPLETED
4. [x] Verify no unsafe code exists: The build should succeed if no unsafe code is present ✅ COMPLETED
5. [ ] Check CI workflows: Ensure all CI checks pass with the new attribute
6. [ ] (Optional) Test unsafe code rejection: Temporarily add unsafe code to verify it's rejected:
   ```rust
   // This should cause a compile error with #![forbid(unsafe_code)]
   unsafe {
       let x = 5;
   }
   ```
   Then remove the test code and verify the build succeeds again

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:** Project would fail to compile if unsafe code is present, but this is the intended behavior
- **Mitigation:**
  - Simple one-line addition
  - Easy rollback if needed
  - Can test locally before committing
  - If issues arise, can switch to `#![deny(unsafe_code)]` or `#![warn(unsafe_code)]`
- **Testing:** Can be fully tested locally with `cargo build` and `cargo test`
- **Dependencies:**
  - No additional dependencies required
  - Attribute is part of the Rust standard library
  - Should not affect existing code if no unsafe code is present
  - Complements existing `cargo-geiger` usage in CI workflows
