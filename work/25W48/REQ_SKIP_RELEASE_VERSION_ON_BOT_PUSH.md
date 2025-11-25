# Implementation Plan: Skip Release Version Workflow on Bot Pushes

**Status**: ✅ Complete

## Overview
Add a conditional check to the `release-version` workflow to prevent it from running when pushes are made by the `moved-maker-release-app[bot]` GitHub App/bot, preventing recursive workflow triggers.

## Checklist Summary

### Phase 1: Add Workflow-Level Conditional
- [x] 1/1 tasks completed

## Context
Reference: `plan/25W48/REQ_SKIP_RELEASE_VERSION_ON_BOT_PUSH.md`

The `release-version` workflow currently triggers on all pushes to the `main` branch. When the workflow commits version changes and pushes them back to `main` using the `moved-maker-release-app[bot]` app token, this push triggers the workflow again, potentially causing an infinite loop or unnecessary workflow runs.

## Goals
- Prevent recursive workflow triggers when the bot commits and pushes version updates
- Reduce unnecessary workflow runs and resource usage
- Maintain workflow execution for legitimate pushes from human developers or other sources
- Skip the entire workflow before any jobs are evaluated when the bot is the actor

## Non-Goals
- Changing the workflow trigger conditions (still triggers on pushes to main)
- Modifying the commit/push logic within the workflow
- Adding additional workflow triggers or events
- Changing how the bot authenticates or commits

## Design Decisions

**Important**: Document all key architectural and implementation decisions here. This section should explain the "why" behind major choices, not just the "what".

- **Job-Level Conditional (Workflow-Level Effect)**: Add an `if` condition to the job that checks `github.actor != 'moved-maker-release-app[bot]'`
  - **Rationale**: GitHub Actions doesn't have a true "workflow-level" conditional that runs before jobs are evaluated. However, since this workflow has only one job (`version`), adding the conditional to that job effectively prevents the entire workflow from executing when the condition fails. This achieves the desired behavior of skipping the workflow before any jobs run, as the job won't be scheduled if the condition is false.
  - **Alternatives Considered**:
    - Using a separate "guard" job that checks the condition and sets an output: Rejected because it adds unnecessary complexity and still requires the job to be evaluated
    - Adding the check at the step level: Rejected because we want to skip the entire workflow, not just individual steps
    - Using workflow-level `concurrency` groups: Rejected because this doesn't prevent execution, only limits concurrent runs
  - **Trade-offs**: If additional jobs are added to this workflow in the future, the conditional would need to be added to each job. However, this is a simple maintenance task and the current workflow structure only has one job.

- **Actor Name Format**: Use exact string match `'moved-maker-release-app[bot]'` for the actor check
  - **Rationale**: GitHub App actors are identified by their exact name format `[app-name][bot]`. The `github.actor` context variable contains the exact actor name, so a direct string comparison is the most reliable method.
  - **Alternatives Considered**:
    - Pattern matching or regex: Rejected because exact string match is simpler and more reliable
    - Checking for `[bot]` suffix: Rejected because this could match other bots unintentionally
  - **Trade-offs**: If the app name changes in the future, this string would need to be updated. However, app names are stable and unlikely to change.

## Implementation Steps

**Note**: Implementation steps should be organized into phases. Each phase contains multiple tasks with checkboxes to track progress. Each task should be broken down into detailed sub-tasks with individual checkboxes. Phases should be logically grouped and can be completed sequentially or in parallel where appropriate.

**Important**: An implementation plan is considered complete when all AI-actionable tasks are finished. Do NOT include human-only tasks such as:
- Manual testing (beyond what can be automated)
- Code review
- Merging to main
- Release activities

These are post-implementation activities handled by humans. Focus only on tasks the AI can directly execute (code changes, automated test creation, documentation updates, etc.). When all AI-actionable tasks are complete, update the status to "✅ Complete" even if human activities remain.

### Phase 1: Add Workflow-Level Conditional

**Objective**: Add a conditional check to the `version` job to skip execution when the actor is `moved-maker-release-app[bot]`

- [x] **Task 1**: Add conditional check to version job
  - [x] Read the current workflow file `.github/workflows/release-version.yaml` to understand the structure
  - [x] Add `if: github.actor != 'moved-maker-release-app[bot]'` condition to the `version` job (at the job level, not step level)
  - [x] Verify the condition uses exact string match with single quotes: `'moved-maker-release-app[bot]'`
  - [x] Verify the condition is placed at the job level (indented under `jobs.version:` but before `runs-on:`)
  - [x] Ensure proper YAML indentation (2 spaces for job-level properties)
  - **Files**: `.github/workflows/release-version.yaml`
  - **Dependencies**: None
  - **Testing**:
    - Verify YAML syntax is valid (can use yamllint or similar)
    - Verify the conditional syntax matches GitHub Actions requirements
    - Confirm the actor name matches exactly (case-sensitive)
  - **Notes**:
    - The condition should be: `if: github.actor != 'moved-maker-release-app[bot]'`
    - This will cause the job (and effectively the entire workflow) to be skipped when the bot is the actor
    - The workflow will still run normally for all other actors (human developers, other bots, etc.)

## Files to Modify/Create
- **Modified Files**:
  - `.github/workflows/release-version.yaml` - Add `if` condition to `version` job to skip when actor is `moved-maker-release-app[bot]`

## Testing Strategy
- **Unit Tests**: N/A (workflow files are not unit tested)
- **Integration Tests**: N/A (workflow behavior must be verified in GitHub Actions environment)
- **Manual Testing**:
  - Verify workflow skips when `moved-maker-release-app[bot]` makes a push to main
  - Verify workflow still runs for pushes from other actors (human developers, other bots, etc.)
  - Verify workflow behavior after bot commits and pushes version updates
  - Monitor workflow runs to ensure no infinite loops occur

## Breaking Changes
- None

## Migration Guide
N/A (no breaking changes)

## Documentation Updates
- [ ] No documentation updates required (per REQ document)

## Success Criteria
- Workflow file contains `if: github.actor != 'moved-maker-release-app[bot]'` condition on the `version` job
- YAML syntax is valid and workflow file parses correctly
- Workflow skips execution when `moved-maker-release-app[bot]` makes a push to main
- Workflow still runs normally for pushes from other actors
- No infinite loops occur when bot commits and pushes version updates

## Risks and Mitigations
- **Risk**: Incorrect actor name format could cause the condition to never match or match incorrectly
  - **Mitigation**: Use exact string match with the documented app name `moved-maker-release-app[bot]` and verify the format matches GitHub's actor naming convention
- **Risk**: YAML syntax error could break the workflow
  - **Mitigation**: Validate YAML syntax before committing, ensure proper indentation (2 spaces for job-level properties)
- **Risk**: If additional jobs are added to the workflow in the future, they would also need the conditional
  - **Mitigation**: Document this requirement in the implementation plan, and consider adding a comment in the workflow file noting this requirement
- **Risk**: The condition might not work as expected if GitHub changes how actor names are formatted
  - **Mitigation**: This is unlikely, but can be verified by testing the workflow after implementation

## References
- Related REQ_ document: `plan/25W48/REQ_SKIP_RELEASE_VERSION_ON_BOT_PUSH.md`
- Related workflow: `.github/workflows/release-version.yaml`
- GitHub App: `moved-maker-release-app[bot]`
- GitHub Actions context: `github.actor` - https://docs.github.com/en/actions/learn-github-actions/contexts#github-context
