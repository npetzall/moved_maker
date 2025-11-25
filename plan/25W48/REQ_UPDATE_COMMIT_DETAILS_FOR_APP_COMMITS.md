# REQ: Update Commit Details for App Commits in Release-Version

**Status**: ✅ Complete

## Overview
Update the git commit author name and email in the `release-version` workflow to use the GitHub App's identity instead of the generic `github-actions[bot]` identity, following GitHub's recommended format for GitHub App commits.

## Motivation
The `release-version` workflow currently configures git to use `github-actions[bot]` as the commit author, but since the workflow uses a GitHub App token (`moved_maker_release`) for all git operations, commits should be attributed to the GitHub App itself. This follows GitHub's best practices and ensures commits are properly associated with the app, making it easier to identify which commits were made by the release automation.

## Current Behavior
The workflow configures git with:
- `user.name`: `"github-actions[bot]"`
- `user.email`: `"github-actions[bot]@users.noreply.github.com"`

This is the default GitHub Actions bot identity, not the specific GitHub App identity.

## Proposed Behavior
Update the git configuration to use the GitHub App's identity:
- `user.name`: `"Moved maker Release App [bot]"`
- `user.email`: `"2296553+moved-maker-release-app[bot]@users.noreply.github.com"`

The email format follows GitHub's recommended pattern: `<APP_ID>+<APP_NAME>[bot]@users.noreply.github.com`, where spaces in the app name are converted to hyphens.

## Use Cases
- Commits made by the release-version workflow will be properly attributed to the GitHub App
- Better traceability of automated commits in the repository history
- Follows GitHub's recommended practices for GitHub App commit attribution

## Implementation Considerations
- Update the "Configure git" step in `.github/workflows/release-version.yaml` (lines 37-40)
- APP_ID: `2296553`
- APP_NAME: `"Moved maker Release App"`
- Email format: Spaces in app name must be converted to hyphens (`moved-maker-release-app`)
- Author name format: App name followed by ` [bot]` (e.g., `"Moved maker Release App [bot]"`)
- Verify that commits created after this change show the correct author information

## Alternatives Considered
- Keeping the generic `github-actions[bot]` identity: Rejected because it doesn't properly identify the specific GitHub App making the commits
- Using a different email format: Rejected because GitHub's recommended format ensures proper attribution and association with the app

## Impact
- **Breaking Changes**: No
- **Documentation**: No documentation updates required
- **Testing**: Verify that:
  - Commits created by the workflow show the correct author name and email
  - The email format matches GitHub's recommended pattern
  - Commits are properly associated with the GitHub App in the repository
- **Dependencies**: No new dependencies required

## References
- Related workflow: `.github/workflows/release-version.yaml`
- GitHub App: `moved_maker_release` (APP_ID: 2296553, APP_NAME: "Moved maker Release App")
- GitHub documentation: [GitHub App commit attribution](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation#using-a-github-app-token-in-a-workflow)
