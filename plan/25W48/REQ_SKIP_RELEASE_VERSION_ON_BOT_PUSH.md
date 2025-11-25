# REQ: Skip Release Version Workflow on Bot Pushes

**Status**: ✅ Complete

## Overview
Add a conditional check in the `release-version` workflow to prevent it from running when pushes are made by the `moved-maker-release-app[bot]` GitHub App/bot. Prefer a workflow-level if statement if supported by GitHub Actions; if workflow-level conditionals are not supported, apply the conditional at the job level.

## Motivation
The `release-version` workflow currently triggers on all pushes to the `main` branch. When the workflow itself commits and pushes version updates using the `moved-maker-release-app[bot]` GitHub App token, this creates a new push event that triggers the workflow again, potentially causing an infinite loop or unnecessary workflow runs. By skipping the workflow when the push is made by the bot, we prevent this recursive triggering.

## Current Behavior
The `release-version` workflow runs on every push to the `main` branch, regardless of who or what made the push. When the workflow commits version changes and pushes them back to `main` using the `moved-maker-release-app[bot]` app token, this push triggers the workflow again.

## Proposed Behavior
Add a conditional check that skips the workflow if the push was made by the `moved-maker-release-app[bot]` GitHub App. This can be done by checking `github.actor` against the app name to identify bot pushes. Prefer applying the conditional at the workflow level (above the jobs section) if supported by GitHub Actions, as this ensures the entire workflow is skipped before any jobs are evaluated. If workflow-level conditionals are not supported, apply the conditional at the job level to all jobs in the workflow.

## Use Cases
- Prevent recursive workflow triggers when the bot commits and pushes version updates
- Reduce unnecessary workflow runs and resource usage
- Maintain workflow execution for legitimate pushes from human developers or other sources

## Implementation Considerations
- Use `github.actor` to check if the actor is `moved-maker-release-app[bot]` (this is the correct way to identify GitHub App/bot pushes)
- Prefer placing the conditional at the workflow level (above the jobs section) if supported by GitHub Actions, to skip the entire workflow before any jobs are evaluated
- If workflow-level conditionals are not supported, apply the conditional at the job level to all jobs in the workflow
- Verify that the app name matches exactly (case-sensitive)
- Test that legitimate pushes from other sources still trigger the workflow correctly

## Alternatives Considered
- Adding the check at the job level: Accepted as a fallback if workflow-level conditionals are not supported; preferred approach is workflow-level to skip before any jobs are evaluated
- Adding the check at the step level: Rejected because it's more efficient to skip at the workflow or job level rather than running steps that will be skipped
- Using a different event trigger: Rejected because we still want the workflow to run on legitimate pushes to main
- Checking commit message patterns: Rejected because it's less reliable and more complex than checking the actor

## Impact
- **Breaking Changes**: No
- **Documentation**: No documentation updates required
- **Testing**: Verify that:
  - Workflow skips when `moved-maker-release-app[bot]` makes a push
  - Workflow still runs for pushes from other actors (human developers, other bots, etc.)
- **Dependencies**: No new dependencies required

## References
- Related workflow: `.github/workflows/release-version.yaml`
- GitHub App: `moved-maker-release-app[bot]`
