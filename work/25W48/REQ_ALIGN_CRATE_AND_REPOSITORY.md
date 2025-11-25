# Implementation Plan: Align Crate and Repository Names

**Status**: ✅ Complete

## Overview
Rename the crate from `move_maker` to `moved_maker` to match the repository name, and add missing metadata fields to `Cargo.toml` for better discoverability and consistency. This change will align the crate name with the repository name, reducing user confusion and improving the overall user experience.

## Checklist Summary

### Phase 1: Core Configuration Updates
- [x] 2/2 tasks completed

### Phase 2: Source Code and Test Updates
- [x] 2/2 tasks completed

### Phase 3: Documentation Updates
- [x] 2/2 tasks completed

### Phase 4: GitHub Workflows and Scripts
- [x] 3/3 tasks completed

## Context
Reference: `plan/25W48/REQ_ALIGN_CRATE_AND_REPOSITORY.md`

The crate name in `Cargo.toml` is currently `move_maker` while the repository name is `moved_maker`. This inconsistency can confuse users and tooling. Additionally, several key metadata fields are missing from `Cargo.toml`:
- Missing: `repository`, `description`, `keywords`, `categories`
- Present: `license` (Apache-2.0) - needs verification
- Optional: `homepage`, `documentation` (if using docs.rs)

**Decision**: Option A has been selected - rename the crate to `moved_maker` to match the repository. The current version is 0.2.0 (< 1.0.0), so breaking changes are acceptable.

## Goals
- Rename crate from `move_maker` to `moved_maker` across all files
- Add missing metadata fields to `Cargo.toml` (`repository`, `description`, `keywords`, `categories`)
- Update all references to the crate/binary name in source code, tests, documentation, and workflows
- Ensure CLI command name is consistent with the new crate name
- Verify all tests pass after the rename
- Update artifact names in release workflows and scripts

## Non-Goals
- Updating historical/planning documents in `plan/` and `work/` directories (these are for reference only)
- Changing functionality or behavior (this is purely a naming change)
- Updating external documentation or scripts that may reference the old name

## Design Decisions

**Decision 1: Rename crate to match repository name**
- **Rationale**: The repository name is `moved_maker`, and the current version (0.2.0) is < 1.0.0, making breaking changes acceptable. Consistent naming reduces confusion for users installing via `cargo install` and when linking between GitHub and crates.io.
- **Alternatives Considered**: Option B (keeping `move_maker` and documenting the difference) was rejected because it would require ongoing documentation maintenance and cause persistent confusion.
- **Trade-offs**: This is a breaking change for any existing users, but since the version is < 1.0.0, this is acceptable. The binary name will change, affecting any scripts or automation that reference it.

**Decision 2: Update CLI command name to match crate name**
- **Rationale**: Consistency between crate name and CLI command name improves user experience. Users expect `cargo install moved_maker` to provide a `moved_maker` binary.
- **Alternatives Considered**: Keeping the CLI command as `move_maker` while the crate is `moved_maker` was considered but rejected for consistency.
- **Trade-offs**: This changes the CLI command name, which may affect existing user scripts, but this is acceptable given the version is < 1.0.0.

**Decision 3: Add comprehensive metadata to Cargo.toml**
- **Rationale**: Required fields (`repository`, `description`) are needed for crates.io publishing. Optional fields (`keywords`, `categories`) improve discoverability. The `documentation` field is omitted since docs.rs is not currently configured.
- **Alternatives Considered**: Adding `homepage` and `documentation` fields were considered but omitted since they would point to non-existent resources.
- **Trade-offs**: None - these are standard metadata fields that improve the crate's discoverability and usability.

## Implementation Steps

### Phase 1: Core Configuration Updates

**Objective**: Update core configuration files with the new crate name and add missing metadata.

- [x] **Task 1**: Update Cargo.toml with new crate name and metadata
  - [x] Change `name = "move_maker"` to `name = "moved_maker"` in `Cargo.toml` (line 2)
  - [x] Add `repository = "https://github.com/npetzall/moved_maker"` field
  - [x] Add `description = "A CLI utility that parses Terraform files and generates moved blocks for refactoring resources into a submodule"` field
  - [x] Add `keywords = ["terraform", "refactoring", "moved-blocks", "cli"]` field
  - [x] Add `categories = ["command-line-utilities", "development-tools"]` field
  - [x] Verify `license = "Apache-2.0"` is correct
  - **Files**: `Cargo.toml`
  - **Dependencies**: None
  - **Testing**: Run `cargo check` to verify the configuration is valid
  - **Notes**: The `Cargo.lock` file will be automatically updated when running `cargo build` or `cargo update`

- [x] **Task 2**: Update Cargo.lock (automatic)
  - [x] Run `cargo update --package moved_maker` or `cargo build` to update `Cargo.lock`
  - [x] Verify the package name in `Cargo.lock` has been updated
  - **Files**: `Cargo.lock`
  - **Dependencies**: Task 1 must be completed first
  - **Testing**: Verify `Cargo.lock` contains references to `moved_maker` instead of `move_maker`
  - **Notes**: This is automatically handled by Cargo, but should be verified

### Phase 2: Source Code and Test Updates

**Objective**: Update source code and test files to use the new crate/binary name.

- [x] **Task 1**: Update CLI command name in source code
  - [x] Change `#[command(name = "move_maker")]` to `#[command(name = "moved_maker")]` in `src/cli.rs` (line 20)
  - **Files**: `src/cli.rs`
  - **Dependencies**: Phase 1 must be completed
  - **Testing**: Run `cargo build --release` and verify the binary is named `moved_maker`
  - **Notes**: This changes the CLI command name that users will invoke

- [x] **Task 2**: Update integration test binary reference
  - [x] Change `env!("CARGO_BIN_EXE_move_maker")` to `env!("CARGO_BIN_EXE_moved_maker")` in `tests/integration_test.rs` (line 8)
  - **Files**: `tests/integration_test.rs`
  - **Dependencies**: Phase 1 must be completed
  - **Testing**: Run `cargo test --test integration_test` to verify tests pass
  - **Notes**: This macro is automatically generated by Cargo based on the crate name, but the code reference needs updating

### Phase 3: Documentation Updates

**Objective**: Update all documentation to reflect the new crate/binary name.

- [x] **Task 1**: Update README.md
  - [x] Change `target/release/move_maker` to `target/release/moved_maker` (line 15)
  - [x] Change `move_maker --src ...` to `moved_maker --src ...` in usage examples (line 20)
  - [x] Change `move_maker --src . --module-name compute` to `moved_maker --src . --module-name compute` (line 40)
  - **Files**: `README.md`
  - **Dependencies**: Phase 1 and Phase 2 must be completed
  - **Testing**: Verify all examples in README use the correct binary name
  - **Notes**: Ensure all command examples are updated consistently

- [x] **Task 2**: Update DEVELOPMENT.md
  - [x] Change `target/release/move_maker` to `target/release/moved_maker` (line 11)
  - [x] Change `move_maker --src ...` to `moved_maker --src ...` in usage examples (line 16)
  - [x] Change `move_maker --src . --module-name compute` to `moved_maker --src . --module-name compute` (line 36)
  - **Files**: `DEVELOPMENT.md`
  - **Dependencies**: Phase 1 and Phase 2 must be completed
  - **Testing**: Verify all examples in DEVELOPMENT.md use the correct binary name
  - **Notes**: Ensure all command examples are updated consistently

### Phase 4: GitHub Workflows and Scripts

**Objective**: Update GitHub workflows and Python scripts to use the new artifact and binary names.

- [x] **Task 1**: Update release-build.yaml workflow
  - [x] Change artifact names from `move_maker-linux-x86_64` to `moved_maker-linux-x86_64` (line 105)
  - [x] Change artifact names from `move_maker-macos-aarch64` to `moved_maker-macos-aarch64` (line 108)
  - [x] Change binary path from `target/${{ matrix.target }}/release/move_maker` to `target/${{ matrix.target }}/release/moved_maker` (line 159)
  - **Files**: `.github/workflows/release-build.yaml`
  - **Dependencies**: Phase 1 and Phase 2 must be completed
  - **Testing**: Verify the workflow file syntax is valid (YAML validation)
  - **Notes**: The test results filename uses `${{ matrix.artifact_name }}`, so it will update automatically

- [x] **Task 2**: Update release-version script
  - [x] Change default fallback from `"move_maker"` to `"moved_maker"` (line 61)
  - [x] Change error message from `"Using default package name: move_maker"` to `"Using default package name: moved_maker"` (line 64)
  - [x] Change fallback assignment from `package_name = "move_maker"` to `package_name = "moved_maker"` (line 65)
  - **Files**: `.github/scripts/release-version/src/release_version/__main__.py`
  - **Dependencies**: Phase 1 must be completed
  - **Testing**: Verify the script can still read the package name from `Cargo.toml` correctly
  - **Notes**: This is a fallback value, but should match the actual package name

- [x] **Task 3**: Update release-notes script and tests
  - [x] Change artifact download links from `move_maker-linux-x86_64` to `moved_maker-linux-x86_64` (line 194)
  - [x] Change artifact download links from `move_maker-linux-aarch64` to `moved_maker-linux-aarch64` (line 195)
  - [x] Change artifact download links from `move_maker-macos-x86_64` to `moved_maker-macos-x86_64` (line 196)
  - [x] Change artifact download links from `move_maker-macos-aarch64` to `moved_maker-macos-aarch64` (line 197)
  - [x] Update test assertions in `test_formatter.py` from `move_maker-*` to `moved_maker-*` (lines 125-126)
  - **Files**:
    - `.github/scripts/release-notes/src/release_notes/formatter.py`
    - `.github/scripts/release-notes/tests/test_formatter.py`
  - **Dependencies**: Phase 4, Task 1 must be completed (artifact names must match)
  - **Testing**: Run tests for the release-notes script to verify assertions pass
  - **Notes**: Ensure artifact names match those in the release-build.yaml workflow

## Files to Modify/Create
- **Modified Files**:
  - `Cargo.toml` - Update crate name and add metadata fields
  - `Cargo.lock` - Auto-updated by Cargo (verify after changes)
  - `src/cli.rs` - Update CLI command name
  - `tests/integration_test.rs` - Update binary reference
  - `README.md` - Update all binary name references
  - `DEVELOPMENT.md` - Update all binary name references
  - `.github/workflows/release-build.yaml` - Update artifact names and binary paths
  - `.github/scripts/release-version/src/release_version/__main__.py` - Update default package name fallback
  - `.github/scripts/release-notes/src/release_notes/formatter.py` - Update artifact download links
  - `.github/scripts/release-notes/tests/test_formatter.py` - Update test assertions

## Testing Strategy
- **Unit Tests**: Run `cargo test` to verify all unit tests pass with the new crate name
- **Integration Tests**: Run `cargo test --test integration_test` to verify integration tests can find and execute the renamed binary
- **Build Verification**: Run `cargo build --release` and verify the binary is named `moved_maker`
- **Workflow Validation**: Verify YAML syntax is valid for updated workflow files
- **Script Tests**: Run tests for Python scripts to verify they handle the new package name correctly
- **Manual Testing**: Verify the binary can be executed with the new name and produces expected output

## Breaking Changes
- **Binary Name**: The compiled binary name changes from `move_maker` to `moved_maker`
- **CLI Command**: The CLI command name changes from `move_maker` to `moved_maker`
- **Artifact Names**: Release artifact names change from `move_maker-*` to `moved_maker-*`
- **Crate Name**: The crate name changes from `move_maker` to `moved_maker` (affects `cargo install`)

## Migration Guide
Since this is a breaking change, users will need to:

1. **Update installation**: If installed via `cargo install`, reinstall with the new name:
   ```bash
   cargo install moved_maker
   ```

2. **Update scripts**: Any scripts or automation that reference the `move_maker` binary should be updated to use `moved_maker`

3. **Update download scripts**: Any scripts that download specific artifact names should be updated to use the new artifact names (`moved_maker-*` instead of `move_maker-*`)

4. **Update documentation**: Any external documentation or references should be updated to reflect the new name

**Note**: Since the version is 0.2.0 (< 1.0.0), breaking changes are acceptable and expected.

## Documentation Updates
- [x] Update README.md (included in Phase 3, Task 1)
- [x] Update DEVELOPMENT.md (included in Phase 3, Task 2)
- [ ] Add/update doc comments (not required - no functional changes)
- [x] Update examples (included in README.md and DEVELOPMENT.md updates)

## Success Criteria
- All references to `move_maker` have been updated to `moved_maker` in code, tests, documentation, and workflows
- `Cargo.toml` contains all required metadata fields (`repository`, `description`, `keywords`, `categories`)
- All tests pass after the rename
- The binary builds successfully and is named `moved_maker`
- Integration tests can find and execute the renamed binary
- Release workflow artifact names match the new naming convention
- Python scripts correctly handle the new package name
- No references to the old name remain in functional code (historical documents excluded)

## Risks and Mitigations
- **Risk**: Breaking change for existing users
  - **Mitigation**: Version is 0.2.0 (< 1.0.0), so breaking changes are acceptable. Document the change in release notes.

- **Risk**: Missing a file that references the old name
  - **Mitigation**: Use `grep` to find all occurrences of `move_maker` and verify each one is either updated or intentionally left unchanged (historical documents)

- **Risk**: Tests fail after rename due to binary path issues
  - **Mitigation**: Verify integration tests use the correct `CARGO_BIN_EXE_*` macro and that Cargo generates it correctly

- **Risk**: Workflow failures due to incorrect artifact names
  - **Mitigation**: Ensure artifact names in `release-build.yaml` match those in `release-notes/formatter.py` and test the workflow in a branch before merging

- **Risk**: Cargo.lock not updating correctly
  - **Mitigation**: Run `cargo update --package moved_maker` explicitly and verify the changes

## References
- Related REQ_ document: `plan/25W48/REQ_ALIGN_CRATE_AND_REPOSITORY.md`
- Related issues: #8 (https://github.com/npetzall/moved_maker/issues/8)
- **Important**: When committing, include "fixes #8" in the commit message
