# Create Cursor AI Templates

## Overview

This plan outlines the creation of standardized templates that Cursor AI can reference when generating change requests, bug reports, and implementation plans. These templates ensure consistency, completeness, and proper structure for project documentation and planning activities.

## Purpose

Templates provide Cursor AI with structured formats for:
- **Change Requests**: Documenting feature requests, enhancements, or modifications
- **Bug Reports**: Capturing bug details with sufficient context for reproduction and resolution
- **Implementation Plans**: Creating detailed, actionable plans for implementing features or fixes

These templates will be referenced from `.cursorrules` files (see `CURSORRULES.md`) to guide AI-generated content.

## Template Structure

### Template Location

Templates will be stored in a dedicated directory:
- **Location**: `/Users/nilspetzall/repos/npetzall/moved_maker/.cursor/templates/`
- **Rationale**: Centralized location for AI-accessible templates, separate from user-facing documentation

### Template File Naming

- `change_request.md` - Template for change requests
- `bug_report.md` - Template for bug reports
- `implementation_plan.md` - Template for implementation plans

## Template Specifications

### 1. Change Request Template

**File**: `.cursor/templates/change_request.md`

**Purpose**: Standardize the format for documenting feature requests, enhancements, or modifications.

**Content**:
```markdown
# Change Request: [Brief Title]

## Summary
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

### 2. Bug Report Template

**File**: `.cursor/templates/bug_report.md`

**Purpose**: Ensure bug reports contain all necessary information for reproduction and resolution.

**Content**:
```markdown
# Bug Report: [Brief Description]

## Summary
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

**File**: `.cursor/templates/implementation_plan.md`

**Purpose**: Create structured, actionable implementation plans for features or fixes.

**Content**:
```markdown
# Implementation Plan: [Feature/Fix Name]

## Overview
[Brief description of what will be implemented]

## Context
[Current state, problem statement, or requirements]

## Goals
- [Primary goal 1]
- [Primary goal 2]
- [Additional goals as needed]

## Non-Goals
- [What is explicitly out of scope]

## Design Decisions
- [Key design decision 1 and rationale]
- [Key design decision 2 and rationale]

## Implementation Steps

### Phase 1: [Phase Name]
1. **Task**: [Description]
   - **Files**: [List of files to modify/create]
   - **Dependencies**: [Any prerequisites]
   - **Testing**: [How to verify]

2. **Task**: [Description]
   - **Files**: [List of files to modify/create]
   - **Dependencies**: [Any prerequisites]
   - **Testing**: [How to verify]

### Phase 2: [Phase Name]
[Repeat structure as needed]

## Files to Modify/Create
- **New Files**:
  - `path/to/new_file.rs` - [Purpose]
  - `path/to/new_file.md` - [Purpose]
- **Modified Files**:
  - `path/to/existing_file.rs` - [What changes]
  - `path/to/existing_file.md` - [What changes]

## Testing Strategy
- **Unit Tests**: [What to test at unit level]
- **Integration Tests**: [What to test at integration level]
- **Manual Testing**: [What to verify manually]

## Breaking Changes
- [List any breaking changes, or "None"]

## Migration Guide
[If breaking changes exist, provide migration steps]

## Documentation Updates
- [ ] Update README.md
- [ ] Update DEVELOPMENT.md
- [ ] Add/update doc comments
- [ ] Update examples (if applicable)

## Rollout Plan
- [ ] Implementation
- [ ] Testing
- [ ] Code review
- [ ] Merge to main
- [ ] Release notes

## Success Criteria
- [Criterion 1]
- [Criterion 2]
- [Additional criteria as needed]

## Risks and Mitigations
- **Risk**: [Description]
  - **Mitigation**: [How to address]

## References
- Related issues: #[issue-number]
- Related PRs: #[pr-number]
- Design documents: [links if applicable]
- External references: [links if applicable]
```

## Integration with .cursorrules

### Update Root `.cursorrules`

Add a section referencing templates:

```cursorrules
## Templates
When generating change requests, bug reports, or implementation plans, reference the templates in `.cursor/templates/`:
- Change requests: Use `.cursor/templates/change_request.md` as a guide
- Bug reports: Use `.cursor/templates/bug_report.md` as a guide
- Implementation plans: Use `.cursor/templates/implementation_plan.md` as a guide
Follow the template structure while adapting to the specific context.
```

### Update Plan Documents `.cursorrules`

Enhance the existing `plan/.cursorrules` to reference templates:

```cursorrules
# Planning Documents Rules

## Document Structure
- Start with context: current state, problem statement, or requirements
- Include clear task breakdowns
- Provide implementation details and examples
- Document benefits and considerations

## Template Usage
- For implementation plans, use `.cursor/templates/implementation_plan.md` as a starting point
- For change requests, use `.cursor/templates/change_request.md` as a starting point
- Adapt templates to the specific context while maintaining structure

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

2. **Create change request template**
   - Write `change_request.md` with the specified structure
   - Include all sections with clear placeholders

3. **Create bug report template**
   - Write `bug_report.md` with the specified structure
   - Focus on reproducibility and context

4. **Create implementation plan template**
   - Write `implementation_plan.md` with the specified structure
   - Emphasize actionable steps and file references

5. **Update root `.cursorrules`**
   - Add template reference section
   - Ensure templates are discoverable by Cursor AI

6. **Update `plan/.cursorrules`**
   - Add template usage guidance
   - Reference implementation plan template specifically

7. **Test template usage**
   - Verify Cursor AI can access and reference templates
   - Test generating content using template structure
   - Refine templates based on initial usage

8. **Document template usage**
   - Add brief documentation in README or DEVELOPMENT.md about template availability
   - Explain when and how to use templates

## Benefits

- **Consistency**: All AI-generated change requests, bug reports, and plans follow the same structure
- **Completeness**: Templates ensure important information is not omitted
- **Efficiency**: AI can generate well-structured documents faster
- **Maintainability**: Centralized templates are easier to update than scattered examples
- **Onboarding**: New contributors see consistent documentation patterns

## Maintenance

- Review templates quarterly or when documentation needs change
- Update templates based on feedback from actual usage
- Add new template types as needed (e.g., RFC template, design doc template)
- Keep templates focused and avoid over-engineering
- Ensure templates remain aligned with project conventions

## Considerations

- **Version Control**: Decide whether templates should be committed to git (recommended: yes)
- **Flexibility**: Templates are guides, not strict requirements - allow adaptation
- **Accessibility**: Ensure templates are in a location Cursor AI can access
- **Documentation**: Consider adding a README in `.cursor/templates/` explaining template usage

## Notes

- Templates use markdown for readability and version control
- Placeholders use `[brackets]` to indicate required information
- Templates can be extended with project-specific sections as needed
- Consider creating template variations for different contexts (e.g., simple vs. complex implementation plans)

## Related Documents

- [CURSORRULES.md](CURSORRULES.md) - Complete .cursorrules setup guide
- [REQ_WORK_DOCUMENT_STRUCTURE.md](REQ_WORK_DOCUMENT_STRUCTURE.md) - Work document structure, naming conventions, and organization guidelines
