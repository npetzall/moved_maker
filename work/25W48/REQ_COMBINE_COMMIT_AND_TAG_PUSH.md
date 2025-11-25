# Implementation Plan: Combine commit push and tag push into single git push

**Status**: ✅ Complete

## Overview
Combine the separate `git push` commands for the commit and tag into a single push operation in the release-version workflow to improve efficiency and simplify the workflow code.

## Checklist Summary

### Phase 1: Update Workflow
- [x] 1/1 tasks completed

## Context
Reference: `plan/25W48/REQ_COMBINE_COMMIT_AND_TAG_PUSH.md`

Currently, the release-version workflow performs two separate git push operations:
1. Push the commit to main branch: `git push origin HEAD:main`
2. Push the tag separately: `git push origin "${{ steps.version.outputs.tag_name }}"`

These can be combined into a single atomic push operation that pushes both the branch reference and the tag reference together.

## Goals
- Combine commit push and tag push into a single git push command
- Reduce the number of network operations
- Simplify the workflow code
- Make the intent clearer (both operations are atomic)
- Slightly improve workflow execution time

## Non-Goals
- Changing the order of operations (tag must still be created before pushing)
- Modifying other parts of the workflow
- Adding new features or functionality

## Design Decisions

**Important**: Document all key architectural and implementation decisions here. This section should explain the "why" behind major choices, not just the "what".

- **Single push with explicit refs**: Use `git push origin HEAD:main "${{ steps.version.outputs.tag_name }}"` to push both refs atomically
  - **Rationale**: This approach is explicit and clear - it shows exactly what is being pushed (the branch and the tag). Git supports pushing multiple refs in a single command, making this operation atomic.
  - **Alternatives Considered**:
    - `--follow-tags` flag: Rejected because it's less explicit and would push all reachable tags, not just the specific tag we created
    - Keeping separate pushes: Rejected because it's less efficient and more verbose
  - **Trade-offs**: None - this is a straightforward improvement with no downsides

## Implementation Steps

**Note**: Implementation steps should be organized into phases. Each phase contains multiple tasks with checkboxes to track progress. Each task should be broken down into detailed sub-tasks with individual checkboxes. Phases should be logically grouped and can be completed sequentially or in parallel where appropriate.

**Important**: An implementation plan is considered complete when all AI-actionable tasks are finished. Do NOT include human-only tasks such as:
- Manual testing (beyond what can be automated)
- Code review
- Merging to main
- Release activities

These are post-implementation activities handled by humans. Focus only on tasks the AI can directly execute (code changes, automated test creation, documentation updates, etc.). When all AI-actionable tasks are complete, update the status to "✅ Complete" even if human activities remain.

### Phase 1: Update Workflow

**Objective**: Modify the release-version workflow to combine the commit push and tag push into a single operation

- [x] **Task 1**: Update git push command in workflow
  - [x] Modify `.github/workflows/release-version.yaml` to combine the two push commands
  - [x] Replace `git push origin HEAD:main` and `git push origin "${{ steps.version.outputs.tag_name }}"` with a single command
  - [x] Ensure the tag is still created before the push (order: commit, tag, push)
  - **Files**: `.github/workflows/release-version.yaml`
  - **Dependencies**: None
  - **Testing**: Verify the workflow syntax is correct and the change follows the proposed behavior
  - **Notes**: The tag creation must remain before the push, but both refs can be pushed together

## Files to Modify/Create
- **Modified Files**:
  - `.github/workflows/release-version.yaml` - Combine the two separate git push commands into a single push operation that pushes both the branch and tag

## Testing Strategy
- **Unit Tests**: N/A (workflow changes don't have unit tests)
- **Integration Tests**: N/A (workflow testing requires GitHub Actions environment)
- **Manual Testing**: Verify the workflow still works correctly after the change by checking workflow syntax and ensuring the git push command format is correct

## Breaking Changes
- None (behavior is identical, just more efficient)

## Migration Guide
N/A - No breaking changes

## Documentation Updates
- [ ] No documentation changes needed (internal workflow change)

## Success Criteria
- The workflow uses a single `git push` command that pushes both the commit and tag
- The workflow syntax is valid
- The change reduces the number of push operations from 2 to 1
- The behavior remains functionally identical (both commit and tag are pushed)

## Risks and Mitigations
- **Risk**: The combined push command might not work as expected
  - **Mitigation**: Git natively supports pushing multiple refs in a single command, and this is a standard practice. The syntax is well-documented and widely used.

## References
- Related REQ_/BUG_ document: `plan/25W48/REQ_COMBINE_COMMIT_AND_TAG_PUSH.md`
- Related issues: N/A
- Related PRs: N/A
- Design documents: N/A
- External references:
  - Git push documentation for pushing multiple refs
  - Current workflow: `.github/workflows/release-version.yaml` (lines 72-76)
