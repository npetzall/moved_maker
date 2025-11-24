# Implementation Plan: Work Document Structure Migration

**Status**: ✅ Complete

## Overview

This implementation plan covers the migration from the current sequential directory structure to the new year-week based structure with standardized `REQ_` and `BUG_` prefixes. The migration includes directory renaming, file renaming, splitting bug files (which contain both reports and implementation plans), and updating all references.

## Checklist Summary

### Phase 1: Directory Renaming
- [x] 2/2 tasks completed

### Phase 2: File Renaming and Prefixing
- [x] 1/1 tasks completed

### Phase 3: Bug File Splitting
- [x] 1/1 tasks completed (42/42 files processed)

### Phase 4: Reference Updates
- [x] 1/1 tasks completed

## Context

Related plan document: `plan/25W48/REQ_WORK_DOCUMENT_STRUCTURE.md`

The current structure uses sequential prefixes (`00_Initial`, `01_Quality`, `02_W47`, `03_W48`) and mixes document types. We need to migrate to a year-week format (`25W45`, `25W46`, `25W47`, `25W48`) with consistent `REQ_` and `BUG_` prefixes, and properly separate bug reports from implementation plans.

## Goals

- Rename all directories to year-week format
- Add `REQ_` or `BUG_` prefixes to all planning documents
- Split bug files: extract bug reports to `plan/`, extract implementation plans to `work/`
- Update all references to moved files and directories
- Ensure no broken links remain

## Non-Goals

- Updating content of documents (only structure and references)
- Creating new documents
- Updating status headers (can be done separately)

## Design Decisions

**Directory Mapping**: Use the specified mappings:
- `00_Initial` → `25W45`
- `01_Quality` → `25W46`
- `02_W47` → `25W47` (already correct format)
- `03_W48` → `25W48` (already correct format)

**Rationale**: These mappings preserve chronological organization while using the new year-week format.

**Bug File Splitting Strategy**: Bug files in `bugs/` contain both bug reports and implementation details. We'll:
1. Extract bug report sections (Description, Current State, Expected State, Impact, Root Cause, etc.) to `plan/` with `BUG_` prefix
2. Extract implementation/fix sections (Steps to Fix, Fixed implementation, etc.) to `work/` with matching filename

**Rationale**: This aligns with the new structure where `plan/` contains requests/bugs and `work/` contains implementation plans.

**Reference Checking**: After migration, search for all references to old paths and update them.

**Rationale**: Ensures documentation integrity and prevents broken links.

## Implementation Steps

### Phase 1: Directory Renaming

**Objective**: Rename all directories to year-week format

- [x] **Task 1**: Rename directories
  - [x] Rename `plan/00_Initial/` → `plan/25W45/`
  - [x] Rename `plan/01_Quality/` → `plan/25W46/`
  - [x] Rename `plan/02_W47/` → `plan/25W47/`
  - [x] Rename `plan/03_W48/` → `plan/25W48/`
  - [x] Rename `work/00_Initial/` → `work/25W45/`
  - [x] Rename `work/01_Quality/` → `work/25W46/`
  - [x] Rename `work/02_W47/` → `work/25W47/`
  - [x] Rename `work/03_W48/` → `work/25W48/`
  - **Files**: Directory structure
  - **Testing**: Verify directories exist with new names
  - **Notes**: Use `git mv` to preserve history

- [x] **Task 2**: Remove `bugs/` directory (after Phase 3)
  - [x] Verify all bug files migrated in Phase 3
  - [x] Remove `bugs/` directory
  - **Files**: `bugs/` directory
  - **Testing**: Verify `bugs/` directory no longer exists
  - **Notes**: Only remove after all files are migrated in Phase 3

### Phase 2: File Renaming and Prefixing

**Objective**: Add `REQ_` or `BUG_` prefixes to all planning documents and ensure `work/` filenames match

- [x] **Task 1**: Rename files in all `plan/` directories
  - [x] For each directory (`plan/25W45/`, `plan/25W46/`, `plan/25W47/`, `plan/25W48/`):
    - [x] Identify which files are requests vs bugs (check content/headers)
    - [x] Add `REQ_` prefix to request files
    - [x] Add `BUG_` prefix to bug files
  - [x] Rename files in `work/` directories to match `plan/` filenames
  - **Files**: All `.md` files in `plan/` and `work/` directories
  - **Testing**: Verify all `plan/` files have `REQ_` or `BUG_` prefix, and filenames match between `plan/` and `work/`
  - **Notes**: Use `git mv` to preserve history. Files like `RELEASE_NOTES_NOT_FOUND.md` are bugs.

### Phase 3: Bug File Splitting

**Objective**: Split bug files from `bugs/` directory into bug reports (`plan/`) and implementation plans (`work/`)

- [x] **Task 1**: Split bug files
  - [x] For each bug file in `bugs/00_Initial/done/` (2 files processed: INDENTATION, REMOVE_DATA_BLOCKS):
    - [x] Extract bug report sections (Description, Current State, Expected State, Impact, Root Cause, etc.) to `plan/25W45/BUG_[name].md`
    - [x] Extract implementation/fix sections (Steps to Fix, Fixed implementation, etc.) to `work/25W45/BUG_[name].md`
    - [x] Add status header (`**Status**: ✅ Complete`) to bug report in `plan/`
    - [x] Ensure both files reference each other
  - [x] For each bug file in `bugs/01_Quality/done/` (40 files processed):
    - [x] Extract bug report sections to `plan/25W46/BUG_[name].md`
    - [x] Extract implementation/fix sections to `work/25W46/BUG_[name].md`
    - [x] Add status header (`**Status**: ✅ Complete`) to bug report in `plan/`
    - [x] Ensure both files reference each other
  - [x] Remove `bugs/` directory (after all files migrated)
  - **Files**: All `.md` files in `bugs/00_Initial/done/` and `bugs/01_Quality/done/`
  - **Testing**: Verify both files created for each bug, content properly separated, `bugs/` directory removed
  - **Notes**: Bug report should end before implementation details (typically before "Steps to Fix" or "Fixed implementation" sections)

### Phase 4: Reference Updates

**Objective**: Update all references to moved files and directories

- [x] **Task 1**: Find and update all references
  - [x] Search for references to old paths: `grep -r "plan/(00_Initial|01_Quality|02_W47|03_W48)" .`
  - [x] Search for references to old paths: `grep -r "work/(00_Initial|01_Quality|02_W47|03_W48)" .`
  - [x] Search for bugs references: `grep -r "bugs/" .`
  - [x] Update all found references in `.md` files, `DEVELOPMENT.md`, and `.cursorrules` files to use new paths (active files updated, bugs/ directory references remain until directory is removed)
  - [x] Verify no broken references remain in active files (re-run grep searches)
  - **Files**: All `.md` files, `DEVELOPMENT.md`, `.cursorrules` files
  - **Testing**: Re-run grep searches to confirm no old paths remain
  - **Notes**: Update both relative and absolute paths. Check for case variations.

## Files to Modify/Create

- **New Files**:
  - Bug reports in `plan/25W45/` and `plan/25W46/` (extracted from `bugs/`)
  - Implementation plans in `work/25W45/` and `work/25W46/` (extracted from `bugs/`)
- **Modified Files**:
  - All `.md` files with references to old paths
  - `DEVELOPMENT.md` (if it contains references)
  - `.cursorrules` files (if they contain references)
- **Renamed Files**:
  - All files in `plan/` directories (add `REQ_` or `BUG_` prefix)
  - All files in `work/` directories (match `plan/` filenames)
- **Removed Files**:
  - All files in `bugs/` directory (after splitting)

## Testing Strategy

- **Directory Verification**: List all directories and verify year-week format
- **File Prefix Verification**: Verify all files in `plan/` have `REQ_` or `BUG_` prefix
- **Filename Matching**: Verify filenames match between `plan/` and `work/` directories
- **Reference Verification**: Search for old paths and verify none remain
- **Content Verification**: Spot-check that bug files were properly split

## Breaking Changes

None - this is a structural reorganization that doesn't affect functionality.

## Migration Guide

N/A - this is the migration itself.

## Documentation Updates

- [ ] Update any documentation that references the old structure
- [ ] Verify `DEVELOPMENT.md` references are updated
- [ ] Verify `.cursorrules` references are updated

## Success Criteria

- [ ] All directories renamed to year-week format
- [ ] All files in `plan/` have `REQ_` or `BUG_` prefix
- [ ] All filenames match between `plan/` and `work/` directories
- [ ] All bug files split into bug reports (`plan/`) and implementation plans (`work/`)
- [ ] `bugs/` directory removed
- [ ] No references to old paths remain
- [ ] All references updated to new paths

## Risks and Mitigations

- **Risk**: Breaking references in documentation
  - **Mitigation**: Comprehensive search and update in Phase 4
- **Risk**: Losing content when splitting bug files
  - **Mitigation**: Careful extraction, verify both files contain appropriate content
- **Risk**: Missing files that should be renamed
  - **Mitigation**: Systematic approach, verify each directory

## References

- Related plan document: `plan/25W48/REQ_WORK_DOCUMENT_STRUCTURE.md`
- Template: `.cursor/templates/implementation_plan_template.md`

## Migration Complete

**All bug files processed**: All 42 bug files have been successfully split:
- 2 files from `bugs/00_Initial/done/` → `plan/25W45/` and `work/25W45/`
- 40 files from `bugs/01_Quality/done/` → `plan/25W46/` and `work/25W46/`

**bugs/ directory removed**: The `bugs/` directory has been successfully removed after all files were migrated.

All bug reports now have:
- `BUG_` prefix in `plan/` directories
- Status headers (`**Status**: ✅ Complete`)
- Cross-references to implementation plans

All implementation plans are in `work/` directories with:
- Proper headers and context sections
- Cross-references to bug reports
