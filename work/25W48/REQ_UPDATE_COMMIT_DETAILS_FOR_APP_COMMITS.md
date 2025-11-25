# Implementation Plan: Update Commit Details for App Commits in Release-Version

**Status**: ✅ Complete

## Overview
Update the git commit author name and email in the `release-version` workflow to use the GitHub App's identity (`Moved maker Release App [bot]`) instead of the generic `github-actions[bot]` identity, following GitHub's recommended format for GitHub App commits.

## Checklist Summary

### Phase 1: Update Workflow Configuration
- [x] 1/1 tasks completed

## Context
- Related REQ document: `plan/25W48/REQ_UPDATE_COMMIT_DETAILS_FOR_APP_COMMITS.md`
- Current state: The `release-version` workflow configures git with the generic `github-actions[bot]` identity, but since it uses a GitHub App token (`moved_maker_release`) for all git operations, commits should be attributed to the GitHub App itself.
- Problem: Commits made by the workflow are not properly associated with the specific GitHub App, making it harder to identify automated commits in the repository history.

## Goals
- Update git configuration to use GitHub App identity for commit attribution
- Follow GitHub's recommended practices for GitHub App commit attribution
- Ensure commits are properly associated with the `moved_maker_release` GitHub App

## Non-Goals
- Changing the GitHub App token or authentication mechanism
- Modifying other aspects of the workflow
- Updating commit message format or content

## Design Decisions

**Important**: Document all key architectural and implementation decisions here. This section should explain the "why" behind major choices, not just the "what".

- **Use GitHub's recommended email format**: `<APP_ID>+<APP_NAME>[bot]@users.noreply.github.com`
  - **Rationale**: GitHub's documentation explicitly recommends this format for GitHub App commits. It ensures proper attribution and association with the app in GitHub's systems.
  - **Alternatives Considered**: Using a custom email format or keeping the generic `github-actions[bot]` email. Rejected because they don't follow GitHub's best practices and may not properly associate commits with the app.
  - **Trade-offs**: None - this is the standard format recommended by GitHub.

- **Convert spaces to hyphens in app name for email**: `"Moved maker Release App"` → `moved-maker-release-app`
  - **Rationale**: Email addresses cannot contain spaces, and GitHub's recommended format uses hyphens as separators. This is consistent with how GitHub handles app names in email addresses.
  - **Alternatives Considered**: Using underscores or removing spaces entirely. Rejected because hyphens are the standard convention for URL/email-friendly identifiers.
  - **Trade-offs**: None - this is a standard transformation.

- **Author name format**: `"Moved maker Release App [bot]"`
  - **Rationale**: This format clearly identifies the commit as being made by a bot associated with the specific GitHub App, while maintaining readability of the app name.
  - **Alternatives Considered**: Using just the app name without `[bot]` suffix. Rejected because the `[bot]` suffix is a GitHub convention that clearly indicates automated commits.
  - **Trade-offs**: None - this follows GitHub conventions.

## Implementation Steps

**Note**: Implementation steps should be organized into phases. Each phase contains multiple tasks with checkboxes to track progress. Each task should be broken down into detailed sub-tasks with individual checkboxes. Phases should be logically grouped and can be completed sequentially or in parallel where appropriate.

**Important**: An implementation plan is considered complete when all AI-actionable tasks are finished. Do NOT include human-only tasks such as:
- Manual testing (beyond what can be automated)
- Code review
- Merging to main
- Release activities

These are post-implementation activities handled by humans. Focus only on tasks the AI can directly execute (code changes, automated test creation, documentation updates, etc.). When all AI-actionable tasks are complete, update the status to "✅ Complete" even if human activities remain.

### Phase 1: Update Workflow Configuration

**Objective**: Update the git configuration in the release-version workflow to use the GitHub App's identity for commit attribution.

- [x] **Task 1**: Update git configuration in release-version workflow
  - [x] Update `user.name` from `"github-actions[bot]"` to `"Moved maker Release App [bot]"`
  - [x] Update `user.email` from `"github-actions[bot]@users.noreply.github.com"` to `"2296553+moved-maker-release-app[bot]@users.noreply.github.com"`
  - [x] Verify the changes are in the correct location (lines 38-41 of `.github/workflows/release-version.yaml`)
  - **Files**: `.github/workflows/release-version.yaml`
  - **Dependencies**: None
  - **Testing**: After implementation, verify that:
    - The workflow file has the correct git config values
    - The email format matches GitHub's recommended pattern (`<APP_ID>+<APP_NAME>[bot]@users.noreply.github.com`)
    - The author name includes the app name and `[bot]` suffix
  - **Notes**:
    - APP_ID: `2296553`
    - APP_NAME: `"Moved maker Release App"`
    - Email format requires converting spaces in app name to hyphens: `moved-maker-release-app`
    - The actual commit verification will happen when the workflow runs after merging (manual verification)

## Files to Modify/Create
- **Modified Files**:
  - `.github/workflows/release-version.yaml` - Update git user.name and user.email configuration in the "Configure git" step (lines 38-41)

## Testing Strategy
- **Unit Tests**: Not applicable - this is a workflow configuration change
- **Integration Tests**: Not applicable - workflow changes are tested through actual workflow execution
- **Manual Testing**: After the workflow runs, verify that commits created by the workflow show:
  - Author name: `Moved maker Release App [bot]`
  - Author email: `2296553+moved-maker-release-app[bot]@users.noreply.github.com`
  - Commits are properly associated with the GitHub App in the repository

## Breaking Changes
- None

## Migration Guide
- Not applicable - no breaking changes

## Documentation Updates
- [ ] No documentation updates required (per REQ document)

## Success Criteria
- Git configuration in the workflow uses the GitHub App identity
- Author name is set to `"Moved maker Release App [bot]"`
- Author email follows GitHub's recommended format: `2296553+moved-maker-release-app[bot]@users.noreply.github.com`
- The workflow file changes are syntactically correct and follow the existing code style

## Risks and Mitigations
- **Risk**: Incorrect email format may cause GitHub to not properly associate commits with the app
  - **Mitigation**: Follow GitHub's documented format exactly: `<APP_ID>+<APP_NAME>[bot]@users.noreply.github.com`, ensuring spaces in app name are converted to hyphens
- **Risk**: Typo in app name or ID could result in incorrect attribution
  - **Mitigation**: Double-check APP_ID (`2296553`) and APP_NAME (`"Moved maker Release App"`) against the REQ document before implementation

## References
- Related REQ_ document: `plan/25W48/REQ_UPDATE_COMMIT_DETAILS_FOR_APP_COMMITS.md`
- Related workflow: `.github/workflows/release-version.yaml`
- GitHub App: `moved_maker_release` (APP_ID: 2296553, APP_NAME: "Moved maker Release App")
- External references: [GitHub App commit attribution](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation#using-a-github-app-token-in-a-workflow)
