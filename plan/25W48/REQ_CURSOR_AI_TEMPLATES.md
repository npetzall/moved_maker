# Create Cursor AI Templates

**Status**: ✅ Complete

## Overview

This plan outlines the creation of standardized templates that Cursor AI can reference when generating requests (REQ_) and bug reports (BUG_) documents. These templates ensure consistency, completeness, and proper structure for project documentation and planning activities, following the work document structure defined in [REQ_WORK_DOCUMENT_STRUCTURE.md](REQ_WORK_DOCUMENT_STRUCTURE.md).

## Purpose

Templates provide Cursor AI with structured formats for:
- **REQ_ Documents**: Documenting requests from users, developers, architects, stakeholders, or product owners (feature requests, enhancements, or modifications)
- **BUG_ Documents**: Capturing bug details with sufficient context for reproduction and resolution
- **Implementation Plans**: Creating detailed, actionable plans for implementing features or fixes (created in `work/` folder with same filename as corresponding `plan/` document)

These templates will be referenced from `.cursorrules` files (see `CURSORRULES.md`) to guide AI-generated content. Both REQ_ and BUG_ documents get implementation plans in the `work/` folder (same filename, different location).

## Template Structure

### Template Location

Templates will be stored in a dedicated directory:
- **Location**: `/Users/nilspetzall/repos/npetzall/moved_maker/.cursor/templates/`
- **Rationale**: Centralized location for AI-accessible templates, separate from user-facing documentation

### Template File Naming

- `req_template.md` - Template for REQ_ documents (requests)
- `bug_template.md` - Template for BUG_ documents (bug reports)
- `implementation_plan_template.md` - Template for implementation plans (created in `work/` folder)

## Template Specifications

### 1. REQ_ Template

**File**: `.cursor/templates/req_template.md`

**Purpose**: Standardize the format for documenting requests from users, developers, architects, stakeholders, or product owners.

**Content**:
```markdown
# REQ: [Brief Title]

**Status**: 📋 Planned | 🟡 In Progress | ✅ Complete | ⏸️ Blocked

## Overview
[One-sentence description of the requested change]

## Motivation
[Why is this change needed? What problem does it solve?]

## Current Behavior
[Describe how things work currently]

## Proposed Behavior
[Describe the desired behavior after the change]

## Use Cases
- [Use case 1]
- [Use case 2]
- [Additional use cases as needed]

## Implementation Considerations
- [Technical consideration 1]
- [Technical consideration 2]
- [Dependencies or prerequisites]

## Alternatives Considered
- [Alternative approach 1 and why it was rejected]
- [Alternative approach 2 and why it was rejected]

## Impact
- **Breaking Changes**: [Yes/No - describe if applicable]
- **Documentation**: [What documentation needs updating?]
- **Testing**: [What tests need to be added or updated?]
- **Dependencies**: [Any new dependencies required?]

## References
- Related issues: #[issue-number]
- Related PRs: #[pr-number]
- External references: [links if applicable]
```

### 2. BUG_ Template

**File**: `.cursor/templates/bug_template.md`

**Purpose**: Ensure bug reports contain all necessary information for reproduction and resolution.

**Content**:
```markdown
# BUG: [Brief Description]

**Status**: 📋 Planned | 🟡 In Progress | ✅ Complete | ⏸️ Blocked

## Overview
[One-sentence description of the bug]

## Environment
- **OS**: [Operating system and version]
- **Rust Version**: [rustc version if relevant]
- **Tool Version**: [moved_maker version or commit]
- **Terraform Version**: [if relevant]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [Additional steps as needed]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Error Messages / Output
```
[Paste error messages, stack traces, or relevant output here]
```

## Minimal Reproduction Case
[Provide minimal Terraform files or code that reproduces the issue]

## Additional Context
- [Any additional information that might be helpful]
- [Workarounds if any]
- [Frequency: Always / Sometimes / Rarely]

## Related Issues
- Related issues: #[issue-number]
- Related PRs: #[pr-number]
```

### 3. Implementation Plan Template

**File**: `.cursor/templates/implementation_plan_template.md`

**Purpose**: Create structured, actionable implementation plans for features or fixes. These plans are created in the `work/` folder with the same filename as the corresponding REQ_ or BUG_ document in the `plan/` folder.

**Content**:
```markdown
# Implementation Plan: [Feature/Fix Name]

**Status**: 📋 Planned | 🟡 In Progress | ✅ Complete | ⏸️ Blocked

## Overview
[Brief description of what will be implemented]

## Checklist Summary

### Phase 1: [Phase Name]
- [ ] 0/2 tasks completed

### Phase 2: [Phase Name]
- [ ] 0/3 tasks completed

### Phase 3: [Phase Name]
- [ ] 0/2 tasks completed

[Add additional phases as needed. Update task counts as tasks (not sub-tasks) are completed. Each task may contain multiple sub-tasks with their own checkboxes.]

## Context
[Reference to corresponding REQ_ or BUG_ document in plan/ folder]
[Current state, problem statement, or requirements]

## Goals
- [Primary goal 1]
- [Primary goal 2]
- [Additional goals as needed]

## Non-Goals
- [What is explicitly out of scope]

## Design Decisions

**Important**: Document all key architectural and implementation decisions here. This section should explain the "why" behind major choices, not just the "what".

- **[Decision 1]**: [Description of the decision]
  - **Rationale**: [Why this approach was chosen]
  - **Alternatives Considered**: [What other options were evaluated and why they were rejected]
  - **Trade-offs**: [Any compromises or limitations]

- **[Decision 2]**: [Description of the decision]
  - **Rationale**: [Why this approach was chosen]
  - **Alternatives Considered**: [What other options were evaluated and why they were rejected]
  - **Trade-offs**: [Any compromises or limitations]

[Add additional design decisions as needed]

## Implementation Steps

**Note**: Implementation steps should be organized into phases. Each phase contains multiple tasks with checkboxes to track progress. Each task should be broken down into detailed sub-tasks with individual checkboxes. Phases should be logically grouped and can be completed sequentially or in parallel where appropriate.

**Important**: An implementation plan is considered complete when all AI-actionable tasks are finished. Do NOT include human-only tasks such as:
- Manual testing (beyond what can be automated)
- Code review
- Merging to main
- Release activities

These are post-implementation activities handled by humans. Focus only on tasks the AI can directly execute (code changes, automated test creation, documentation updates, etc.). When all AI-actionable tasks are complete, update the status to "✅ Complete" even if human activities remain.

### Phase 1: [Phase Name]

**Objective**: [What this phase accomplishes]

- [ ] **Task 1**: [Description]
  - [ ] [Sub-task 1: Specific action to take]
  - [ ] [Sub-task 2: Specific action to take]
  - [ ] [Sub-task 3: Specific action to take]
  - [ ] [Additional sub-tasks as needed]
  - **Files**: [List of files to modify/create]
  - **Dependencies**: [Any prerequisites]
  - **Testing**: [How to verify]
  - **Notes**: [Any additional context]

- [ ] **Task 2**: [Description]
  - [ ] [Sub-task 1: Specific action to take]
  - [ ] [Sub-task 2: Specific action to take]
  - [ ] [Sub-task 3: Specific action to take]
  - [ ] [Additional sub-tasks as needed]
  - **Files**: [List of files to modify/create]
  - **Dependencies**: [Any prerequisites]
  - **Testing**: [How to verify]
  - **Notes**: [Any additional context]

### Phase 2: [Phase Name]

**Objective**: [What this phase accomplishes]

- [ ] **Task 1**: [Description]
  - [ ] [Sub-task 1: Specific action to take]
  - [ ] [Sub-task 2: Specific action to take]
  - [ ] [Sub-task 3: Specific action to take]
  - [ ] [Additional sub-tasks as needed]
  - **Files**: [List of files to modify/create]
  - **Dependencies**: [Any prerequisites]
  - **Testing**: [How to verify]
  - **Notes**: [Any additional context]

- [ ] **Task 2**: [Description]
  - [ ] [Sub-task 1: Specific action to take]
  - [ ] [Sub-task 2: Specific action to take]
  - [ ] [Sub-task 3: Specific action to take]
  - [ ] [Additional sub-tasks as needed]
  - **Files**: [List of files to modify/create]
  - **Dependencies**: [Any prerequisites]
  - **Testing**: [How to verify]
  - **Notes**: [Any additional context]

[Repeat structure for additional phases as needed]

## Files to Modify/Create
- **New Files**:
  - `path/to/new_file.rs` - [Purpose]
  - `path/to/new_file.md` - [Purpose]
- **Modified Files**:
  - `path/to/existing_file.rs` - [What changes]
  - `path/to/existing_file.md` - [What changes]

## Testing Strategy
- **Unit Tests**: [What to test at unit level - AI can create these]
- **Integration Tests**: [What to test at integration level - AI can create these]
- **Manual Testing**: [What to verify manually - informational only, not part of AI tasks]

## Breaking Changes
- [List any breaking changes, or "None"]

## Migration Guide
[If breaking changes exist, provide migration steps]

## Documentation Updates
- [ ] Update README.md
- [ ] Update DEVELOPMENT.md
- [ ] Add/update doc comments
- [ ] Update examples (if applicable)

## Success Criteria
- [Criterion 1]
- [Criterion 2]
- [Additional criteria as needed]

## Risks and Mitigations
- **Risk**: [Description]
  - **Mitigation**: [How to address]

## References
- Related REQ_/BUG_ document: `plan/[week]/[REQ_|BUG_][name].md`
- Related issues: #[issue-number]
- Related PRs: #[pr-number]
- Design documents: [links if applicable]
- External references: [links if applicable]
```

## Integration with .cursorrules

The `.cursorrules` files should reference templates found in the `.cursor/templates/` directory. The following sections should be included in the appropriate `.cursorrules` files:

### Root `.cursorrules`

Include a section referencing templates:

```cursorrules
## Templates
When generating REQ_, BUG_, or implementation plan documents, always reference and use the templates found in `.cursor/templates/`:
- REQ_ documents: Read and follow `.cursor/templates/req_template.md` as a guide
- BUG_ documents: Read and follow `.cursor/templates/bug_template.md` as a guide
- Implementation plans: Read and follow `.cursor/templates/implementation_plan_template.md` as a guide
Follow the template structure while adapting to the specific context.
All documents should include a status header at the top (📋 Planned | 🟡 In Progress | ✅ Complete | ⏸️ Blocked).
Implementation plans are created in `work/` folder with the same filename as the corresponding `plan/` document.
```

### `plan/.cursorrules`

Include template usage guidance:

```cursorrules
# Planning Documents Rules

## Document Structure
- Use REQ_ prefix for requests, BUG_ prefix for bug reports
- Include status header at the top: **Status**: 📋 Planned | 🟡 In Progress | ✅ Complete | ⏸️ Blocked
- Start with Overview section: current state, problem statement, or requirements
- Include clear task breakdowns
- Provide implementation details and examples
- Document benefits and considerations

## Template Usage
- Always read and reference templates from `.cursor/templates/` directory before generating documents
- For REQ_ documents, read `.cursor/templates/req_template.md` and use it as a starting point
- For BUG_ documents, read `.cursor/templates/bug_template.md` and use it as a starting point
- For implementation plans, read `.cursor/templates/implementation_plan_template.md` and use it as a starting point
- Adapt templates to the specific context while maintaining structure
- Implementation plans are created in `work/` folder with the same filename as the `plan/` document

## Markdown Formatting
- Use clear headings (## for main sections, ### for subsections)
- Use code blocks with language identifiers
- Include file paths and line numbers when referencing code
- Use lists for task items and considerations

## Content Guidelines
- Be specific and actionable
- Include references to GitHub issues when applicable
- Document file locations that need changes
- Provide examples of expected outcomes
- Note any breaking changes or migration steps
```

## Implementation Steps

1. **Create template directory**
   - Create `.cursor/templates/` directory
   - Ensure directory is accessible (not in `.gitignore` if templates should be versioned)

2. **Create REQ_ template**
   - Write `req_template.md` with the specified structure
   - Include status header format
   - Include all sections with clear placeholders
   - Use `# REQ: [Title]` format

3. **Create BUG_ template**
   - Write `bug_template.md` with the specified structure
   - Include status header format
   - Focus on reproducibility and context
   - Use `# BUG: [Title]` format

4. **Create implementation plan template**
   - Write `implementation_plan_template.md` with the specified structure
   - Include status header format
   - Emphasize actionable steps and file references
   - Reference relationship to corresponding `plan/` document
   - Add clarification that plans only include AI-actionable tasks (exclude human-only activities like code review, manual testing, merging)
   - Do NOT include Rollout Plan section (human activities are post-implementation)

5. **Document template usage**
   - Add brief documentation in README or DEVELOPMENT.md about template availability
   - Explain when and how to use templates
   - Reference work document structure (see REQ_WORK_DOCUMENT_STRUCTURE.md)

## Benefits

- **Consistency**: All AI-generated REQ_, BUG_, and implementation plan documents follow the same structure
- **Completeness**: Templates ensure important information is not omitted (including status headers)
- **Efficiency**: AI can generate well-structured documents faster
- **Maintainability**: Centralized templates are easier to update than scattered examples
- **Onboarding**: New contributors see consistent documentation patterns
- **Alignment**: Templates align with work document structure (REQ_/BUG_ prefixes, status tracking, `plan/` and `work/` folder relationship)

## Maintenance

- Review templates quarterly or when documentation needs change
- Update templates based on feedback from actual usage
- Keep templates focused and avoid over-engineering
- Ensure templates remain aligned with work document structure (REQ_WORK_DOCUMENT_STRUCTURE.md)
- Ensure status header format remains consistent

## Considerations

- **Version Control**: Decide whether templates should be committed to git (recommended: yes)
- **Flexibility**: Templates are guides, not strict requirements - allow adaptation
- **Accessibility**: Ensure templates are in a location Cursor AI can access
- **Documentation**: Consider adding a README in `.cursor/templates/` explaining template usage

## Notes

- Templates use markdown for readability and version control
- Placeholders use `[brackets]` to indicate required information
- Templates can be extended with project-specific sections as needed
- All documents must include status header: `**Status**: 📋 Planned | 🟡 In Progress | ✅ Complete | ⏸️ Blocked`
- REQ_ and BUG_ documents are created in `plan/` folder
- Implementation plans are created in `work/` folder with the same filename as the corresponding `plan/` document
- Implementation plans should reference their corresponding REQ_ or BUG_ document in the Context section
- **Implementation plan scope**: Plans should only include AI-actionable tasks. A plan is complete when all AI tasks are finished, even if human activities (code review, manual testing, merging) remain. Do NOT include Rollout Plan section in templates.

## Related Documents

- [CURSORRULES.md](CURSORRULES.md) - Complete .cursorrules setup guide
- [REQ_WORK_DOCUMENT_STRUCTURE.md](REQ_WORK_DOCUMENT_STRUCTURE.md) - Work document structure, naming conventions, and organization guidelines
