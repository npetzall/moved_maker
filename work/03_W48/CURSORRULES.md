# Implementation Plan: Add Small but Effective .cursorrules Files

**Status**: ✅ Complete

## Overview
Implement a comprehensive set of `.cursorrules` files throughout the project to provide context and instructions to Cursor AI when working in specific directories. This will improve AI assistance, coding style consistency, and project-specific convention adherence.

## Checklist Summary

### Phase 1: Core .cursorrules Files
- [x] 3/3 tasks completed

### Phase 2: Directory-Specific .cursorrules Files
- [x] 5/5 tasks completed

### Phase 3: Verification and Testing
- [x] 1/1 tasks completed

## Context
Related plan document: `plan/03_W48/CURSORRULES.md`

The plan document outlines the need for `.cursorrules` files to guide Cursor AI behavior throughout the project. These files will be placed in strategic locations to provide context-specific guidance for:
- Project-wide Rust conventions (root `.cursorrules`)
- Source code implementation (`src/.cursorrules`)
- Test writing (`tests/.cursorrules`)
- GitHub Actions workflows (`.github/workflows/.cursorrules`)
- Python scripts (`.github/scripts/.cursorrules`)
- Terraform examples (`examples/.cursorrules`)
- Planning documents (`plan/.cursorrules`)
- Implementation plans (`work/.cursorrules`)

## Goals
- Create 8 `.cursorrules` files in appropriate directories
- Establish project-wide Rust conventions and coding standards
- Provide directory-specific guidance for different areas of the codebase
- Ensure templates are properly referenced and workflow is documented
- Verify that Cursor AI can successfully read and apply the rules

## Non-Goals
- Modifying existing code or functionality
- Creating new features or functionality
- Updating documentation beyond the `.cursorrules` files themselves
- Manual testing beyond verification that files exist and are readable

## Design Decisions

**Decision 1**: Place root `.cursorrules` at repository root
  - **Rationale**: Root-level rules serve as the base configuration that applies project-wide. Cursor searches from current directory up to root, so root rules provide fallback guidance.
  - **Alternatives Considered**: Placing rules only in specific directories, but this would miss the opportunity for project-wide conventions.
  - **Trade-offs**: Root rules are more general, but nested rules can override them for specific contexts.

**Decision 2**: Use nested `.cursorrules` files for directory-specific guidance
  - **Rationale**: Different directories have different needs (e.g., Python scripts vs Rust code vs Terraform examples). Nested rules allow context-specific guidance without cluttering root rules.
  - **Alternatives Considered**: Single root file with all rules, but this would be unwieldy and less maintainable.
  - **Trade-offs**: More files to maintain, but better organization and clearer context.

**Decision 3**: Reference templates explicitly in `.cursorrules` files
  - **Rationale**: Templates define document structure and formatting. Explicit references ensure AI always uses correct templates when generating documents.
  - **Alternatives Considered**: Relying on implicit knowledge, but explicit references are more reliable and maintainable.
  - **Trade-offs**: Slightly more verbose rules, but much clearer guidance for AI.

## Implementation Steps

### Phase 1: Core .cursorrules Files

**Objective**: Create the root `.cursorrules` file and the two most critical directory-specific files (`plan/` and `work/`) that define document workflow.

- [x] **Task 1**: Create root `.cursorrules` file
  - [x] Create `.cursorrules` file at repository root (`/Users/nilspetzall/repos/npetzall/moved_maker/.cursorrules`)
  - [x] Add project context section describing Move Maker
  - [x] Add templates section referencing `.cursor/templates/` directory
  - [x] Add work documents section with file creation guidelines
  - [x] Add Rust conventions section (project-wide)
  - [x] Add directory-specific rules section listing all nested `.cursorrules` files
  - [x] Verify file is readable and properly formatted
  - **Files**: `.cursorrules`
  - **Dependencies**: None
  - **Testing**: Verify file exists and contains expected content
  - **Notes**: This is the foundation file that other rules reference

- [x] **Task 2**: Create `plan/.cursorrules` file
  - [x] Create `plan/.cursorrules` file
  - [x] Add document naming and organization section
  - [x] Add workflow section (Discovery → Planning → Implementation → Completion)
  - [x] Add template usage instructions
  - [x] Reference REQ_WORK_DOCUMENT_STRUCTURE.md for complete guidelines
  - [x] Verify file is readable and properly formatted
  - **Files**: `plan/.cursorrules`
  - **Dependencies**: Root `.cursorrules` should exist (for consistency)
  - **Testing**: Verify file exists and contains expected content
  - **Notes**: Critical for document workflow and template usage

- [x] **Task 3**: Create `work/.cursorrules` file
  - [x] Create `work/.cursorrules` file
  - [x] Add document naming and organization section
  - [x] Add relationship to plan documents section
  - [x] Add template usage instructions
  - [x] Reference REQ_WORK_DOCUMENT_STRUCTURE.md for complete guidelines
  - [x] Verify file is readable and properly formatted
  - **Files**: `work/.cursorrules`
  - **Dependencies**: Root `.cursorrules` should exist (for consistency)
  - **Testing**: Verify file exists and contains expected content
  - **Notes**: Critical for implementation plan workflow and template usage

### Phase 2: Directory-Specific .cursorrules Files

**Objective**: Create remaining directory-specific `.cursorrules` files for source code, tests, GitHub workflows, scripts, and examples.

- [x] **Task 1**: Create `src/.cursorrules` file
  - [x] Create `src/.cursorrules` file
  - [x] Add module structure section
  - [x] Add error handling section
  - [x] Add type safety section
  - [x] Add performance section
  - [x] Add testing section
  - [x] Verify file is readable and properly formatted
  - **Files**: `src/.cursorrules`
  - **Dependencies**: Root `.cursorrules` should exist
  - **Testing**: Verify file exists and contains expected content
  - **Notes**: Provides Rust-specific source code guidance

- [x] **Task 2**: Create `tests/.cursorrules` file
  - [x] Create `tests/.cursorrules` file
  - [x] Add test organization section
  - [x] Add test fixtures section
  - [x] Add assertions section
  - [x] Add test data section
  - [x] Verify file is readable and properly formatted
  - **Files**: `tests/.cursorrules`
  - **Dependencies**: Root `.cursorrules` should exist
  - **Testing**: Verify file exists and contains expected content
  - **Notes**: Provides test writing conventions

- [x] **Task 3**: Create `.github/workflows/.cursorrules` file
  - [x] Create `.github/workflows/.cursorrules` file
  - [x] Add workflow structure section
  - [x] Add best practices section
  - [x] Add Rust-specific section
  - [x] Add artifacts section
  - [x] Verify file is readable and properly formatted
  - **Files**: `.github/workflows/.cursorrules`
  - **Dependencies**: Root `.cursorrules` should exist
  - **Testing**: Verify file exists and contains expected content
  - **Notes**: Provides GitHub Actions workflow guidance

- [x] **Task 4**: Create `.github/scripts/.cursorrules` file
  - [x] Create `.github/scripts/.cursorrules` file
  - [x] Add Python package management section (uv)
  - [x] Add testing section (pytest)
  - [x] Add code style section
  - [x] Add script structure section
  - [x] Add dependencies section
  - [x] Add Dependabot configuration section
  - [x] Verify file is readable and properly formatted
  - **Files**: `.github/scripts/.cursorrules`
  - **Dependencies**: Root `.cursorrules` should exist
  - **Testing**: Verify file exists and contains expected content
  - **Notes**: Provides Python script development guidance

- [x] **Task 5**: Create `examples/.cursorrules` file
  - [x] Create `examples/.cursorrules` file
  - [x] Add example structure section
  - [x] Add file organization section
  - [x] Add documentation section
  - [x] Add testing examples section
  - [x] Verify file is readable and properly formatted
  - **Files**: `examples/.cursorrules`
  - **Dependencies**: Root `.cursorrules` should exist
  - **Testing**: Verify file exists and contains expected content
  - **Notes**: Provides Terraform example file guidelines

### Phase 3: Verification and Testing

**Objective**: Verify all `.cursorrules` files are created correctly and can be read by Cursor AI.

- [x] **Task 1**: Verify all `.cursorrules` files exist and are readable
  - [x] Verify root `.cursorrules` exists and is readable
  - [x] Verify `src/.cursorrules` exists and is readable
  - [x] Verify `tests/.cursorrules` exists and is readable
  - [x] Verify `.github/workflows/.cursorrules` exists and is readable
  - [x] Verify `.github/scripts/.cursorrules` exists and is readable
  - [x] Verify `examples/.cursorrules` exists and is readable
  - [x] Verify `plan/.cursorrules` exists and is readable
  - [x] Verify `work/.cursorrules` exists and is readable
  - [x] Verify all files contain expected content sections
  - [x] Check that template references are correct (`.cursor/templates/` paths)
  - [x] Verify no syntax errors or formatting issues
  - **Files**: All `.cursorrules` files created in previous phases
  - **Dependencies**: All previous tasks must be complete
  - **Testing**: Read each file and verify structure and content
  - **Notes**: This is a verification step to ensure all files are properly created

## Files to Modify/Create
- **New Files**:
  - `.cursorrules` - Root project-wide rules
  - `src/.cursorrules` - Source code implementation guidelines
  - `tests/.cursorrules` - Test writing conventions
  - `.github/workflows/.cursorrules` - GitHub Actions workflow guidance
  - `.github/scripts/.cursorrules` - Python script development guidance
  - `examples/.cursorrules` - Terraform example file guidelines
  - `plan/.cursorrules` - Planning document structure and workflow
  - `work/.cursorrules` - Implementation plan structure and workflow

## Testing Strategy
- **Unit Tests**: Not applicable - these are configuration files, not code
- **Integration Tests**: Not applicable - these are configuration files, not code
- **Manual Testing**:
  - Verify all 8 `.cursorrules` files exist in correct locations
  - Verify each file is readable and contains expected content
  - Verify template references point to correct paths (`.cursor/templates/`)
  - Verify no syntax errors or formatting issues
  - Test that Cursor AI can read and access the files (informational - AI behavior verification)

## Breaking Changes
None - these are new configuration files that don't affect existing functionality.

## Migration Guide
N/A - no migration needed for new configuration files.

## Documentation Updates
- [ ] No documentation updates required - `.cursorrules` files are self-documenting
- [ ] Consider adding note to README.md about `.cursorrules` files (optional, not required)

## Success Criteria
- All 8 `.cursorrules` files are created in correct locations
- All files contain expected content sections as specified in plan document
- Template references are correct and point to `.cursor/templates/` directory
- Files are readable and properly formatted
- No syntax errors or formatting issues
- Root `.cursorrules` includes project-wide Rust conventions
- Directory-specific rules complement root rules without contradiction

## Risks and Mitigations
- **Risk**: Cursor AI may not recognize or apply `.cursorrules` files correctly
  - **Mitigation**: Follow Cursor's documented file discovery hierarchy. Place files in correct locations and use standard format.
- **Risk**: Rules may conflict between root and nested files
  - **Mitigation**: Ensure nested rules complement rather than contradict root rules. Test with sample AI interactions.
- **Risk**: Template references may be incorrect
  - **Mitigation**: Verify template paths exist before referencing them. Use relative paths from repository root.

## References
- Related plan document: `plan/03_W48/CURSORRULES.md`
- Template files: `.cursor/templates/req_template.md`, `.cursor/templates/bug_template.md`, `.cursor/templates/implementation_plan_template.md`
- Related documents: `plan/03_W48/CURSOR_AI_TEMPLATES.md`, `plan/03_W48/REQ_WORK_DOCUMENT_STRUCTURE.md`
