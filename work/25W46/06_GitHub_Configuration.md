# Phase 6: GitHub Configuration Implementation Plan

## Overview
Configure GitHub repository settings to support quality tooling, versioning strategy, and continuous delivery workflows.

## Goals
- Configure branch protection rules for `main` branch
- Set merge strategy to rebase and squash merge (both maintain linear history)
- Create version labels for PR-based versioning
- Set up workflow permissions
- Configure Dependabot for automated dependency updates
- **Note**: Configuring required status checks is moved to Phase 8 (GitHub Configuration Finalizer) as it depends on Phase 7 workflows being created.

## Prerequisites
- [x] GitHub repository access (admin or owner permissions)
- [x] Phase 1 (Security) completed or in progress
- [x] Phase 2 (Test Runner) completed or in progress
- [x] Phase 4 (Coverage) completed or in progress
- [x] Note: CI/CD workflows will be created in Phase 7 (Continuous Delivery)
- [x] **Important**: Tasks that depend on Phase 7 workflows (status checks configuration, status check testing, and related documentation) have been moved to Phase 8 (GitHub Configuration Finalizer). See `08_GitHub_Configuration_finalizer.md` for those tasks.

## Implementation Tasks

### 1. Configure Branch Protection Rules

- [x] Navigate to repository Settings → Branches → Branch protection rules
- [x] Click "Add rule" or edit existing rule for `main` branch
- [x] Set branch name pattern: `main`
- [x] Enable "Require a pull request before merging":
  - [x] Set required approvals: **0** (or more as needed)
  - [x] Enable "Dismiss stale pull request approvals when new commits are pushed"
  - [x] Enable "Require review from Code Owners" (if CODEOWNERS file exists)
- [x] Enable "Require status checks to pass before merging":
  - [x] Enable "Require branches to be up to date before merging" (PR branch must be rebased on latest `main`)
  - [x] Enable "Require status checks to pass before merging"
  - [-] **Note**: Adding specific required status checks is moved to Phase 8 (GitHub Configuration Finalizer) as it depends on Phase 7 workflows being created and run at least once.
- [x] Enable "Require conversation resolution before merging"
- [x] Enable "Require linear history":
  - [x] Enable "Enforce linear history" (prevents merge commits)
- [-] Configure "Restrict who can push to matching branches":
  - [-] Only allow repository administrators (or specific teams)
  - [x] Prevents direct pushes to `main`
- [x] Enable "Do not allow bypassing the above settings"
- [x] Save branch protection rule
- [x] Verify rule is active

### 2. Configure Merge Strategy

- [x] Navigate to repository Settings → General → Pull Requests
- [x] Find "Merge button" section
- [x] Configure merge button options:
  - [x] Enable "Allow rebase and merge" ✅
  - [x] Enable "Allow squash and merge" ✅
  - [x] Disable "Allow merge commits" ❌
- [x] Enable "Always suggest updating pull request branches"
- [x] Enable "Allow auto-merge" (optional, for automatic merging after checks pass)
- [x] Save settings
- [x] Verify both rebase and merge and squash and merge are available on test PR
- [x] **Note**: Both rebase merge and squash merge maintain linear history, which is the important requirement. Merge commits are disabled as they create non-linear history.

### 3. Create Version Labels

- [x] Navigate to repository Issues → Labels (or Settings → Labels)
- [x] Create "version: major" label:
  - [x] Click "New label"
  - [x] Name: `version: major`
  - [x] Color: `#d73a4a` (red)
  - [x] Description: `Major version bump - breaking changes`
  - [x] Click "Create label"
- [x] Create "version: minor" label:
  - [x] Click "New label"
  - [x] Name: `version: minor`
  - [x] Color: `#0075ca` (blue)
  - [x] Description: `Minor version bump - new features`
  - [x] Click "Create label"
- [x] Create "version: patch" label:
  - [x] Click "New label"
  - [x] Name: `version: patch`
  - [x] Color: `#cfd3d7` (gray)
  - [x] Description: `Patch version bump - bug fixes and minor changes`
  - [x] Click "Create label"
- [x] Verify all three labels are created
- [-] **Note**: These labels will be automatically applied by the PR label workflow created in Phase 7 (`.github/workflows/pr-label.yml`). The workflow analyzes commit messages using Conventional Commits and applies appropriate labels automatically.
- [x] (Optional) Create additional labels for categorization:
  - [-] `breaking` - Alternative to `version: major`
  - [-] `feature` - Alternative to `version: minor`
  - [x] `bug` - Bug fixes
  - [x] `docs` - Documentation changes
  - [x] `chore` - Maintenance tasks

### 4. Configure Workflow Permissions

- [x] Navigate to repository Settings → Actions → General → Workflow permissions
- [x] Configure "Workflow permissions":
  - [-] Select "Read and write permissions"
  - [-] Enable "Allow GitHub Actions to create and approve pull requests" (optional, only needed if workflows will create/approve PRs automatically)
- [x] Save settings
- [x] Verify permissions are set correctly

### 5. Verify Required Status Checks

**Note**: This section has been moved to Phase 8 (GitHub Configuration Finalizer) as it depends on Phase 7 workflows being created and run at least once. See `08_GitHub_Configuration_finalizer.md` for these tasks.

### 6. Configure Repository Settings

- [x] Navigate to repository Settings → General
- [x] Configure "Features":
  - [x] Enable "Issues" (if needed)
  - [-] Enable "Projects" (optional)
  - [-] Enable "Wiki" (optional)
  - [-] Enable "Discussions" (optional)
- [x] Verify "Pull Requests" settings:
  - [x] "Allow merge commits" should be disabled (enforced by branch protection)
  - [x] "Allow squash merging" should be enabled (maintains linear history)
  - [x] "Allow rebase merging" should be enabled (maintains linear history)
  - [x] "Always suggest updating pull request branches" should be enabled
  - [x] "Allow auto-merge" should be enabled (optional)
- [x] Save settings

### 7. Configure Actions Settings

- [x] Navigate to repository Settings → Actions → General
- [x] Configure "Actions permissions":
  - [-] Select "Allow all actions and reusable workflows"
  - [x] Or: "Allow local actions and reusable workflows" (more restrictive)
- [x] Verify "Workflow permissions" are set (from step 4)
- [x] Configure "Artifact and log retention":
  - [x] Set retention period (e.g., 90 days) to manage storage
- [x] Configure "Fork pull request workflows" (as needed for security)
- [x] Save settings

### 8. Create CODEOWNERS File (Optional)

- [x] Create `.github/CODEOWNERS` file (if code ownership is needed)
- [x] Define code owners:
  ```
  # Default owners
  * @npetzall

  # Specific paths
  /src/ @npetzall
  /tests/ @npetzall
  # Configuration files, documentation, and GitHub workflows also owned by @npetzall
  ```
- [x] Commit and push `.github/CODEOWNERS` (ready to commit)
- [ ] Verify CODEOWNERS is recognized by GitHub (after pushing)
- [ ] Update branch protection to require CODEOWNERS review (if applicable, after verification)

### 9. Configure Dependabot

- [x] Create `.github/dependabot.yml` file
- [x] Add complete Dependabot configuration:
  ```yaml
  version: 2
  updates:
    - package-ecosystem: "cargo"
      directory: "/"
      schedule:
        interval: "weekly"
      open-pull-requests-limit: 10
      labels:
        - "dependencies"
        - "security"
      reviewers:
        - "username"  # Optional: add reviewers
      assignees:
        - "username"  # Optional: add assignees
  ```
- [x] **Note**: Dependabot security updates are configured separately in repository Settings → Security → Dependabot alerts. Enable "Dependabot alerts" and "Dependabot security updates" if you want automatic security PRs.
- [x] Verify Dependabot configuration syntax
- [x] Commit and push `.github/dependabot.yml`
- [x] Navigate to repository Settings → Security → Dependabot
- [x] Verify Dependabot is enabled
- [x] Verify Dependabot alerts are enabled (if applicable)
- [x] Verify Dependabot security updates are enabled (if applicable)
- [x] Check that Dependabot creates PRs for dependency updates

### 10. Test Branch Protection

- [x] Create a test branch from `main`
- [x] Make a small change
- [x] Push branch and create pull request
- [x] Verify PR cannot be merged until:
  - [x] PR is approved (if required)
  - [x] Conversation is resolved (if enabled)
- [x] Verify both "Rebase and merge" and "Squash and merge" options are available
- [x] Verify "Create a merge commit" is disabled
- [x] Test rebase and merge or squash and merge (or close PR without merging)
- [x] **Note**: Testing with status checks is moved to Phase 8 (GitHub Configuration Finalizer) as it depends on Phase 7 workflows being created. See `08_GitHub_Configuration_finalizer.md` for status check testing tasks.

### 11. Document Configuration

- [x] Update project DEVELOPMENT.md with GitHub configuration information:
  - [x] Branch protection rules
  - [x] Merge strategy (rebase and squash merge - both maintain linear history)
  - [x] PR workflow requirements
  - [x] Version label system (how labels are auto-applied from Conventional Commits)
  - [x] How to create PRs
- [x] **Note**: Documentation for status checks and version label workflows is moved to Phase 8 (GitHub Configuration Finalizer) as it depends on Phase 7 workflows. See `08_GitHub_Configuration_finalizer.md` for those documentation tasks.
- [x] Update CONTRIBUTING.md (if exists) with basic PR requirements
- [x] Add troubleshooting section reference (see Section 12)

### 12. Verification Checklist

- [x] Branch protection rules are active for `main`
- [x] Both rebase and merge and squash and merge are allowed (linear history maintained)
- [x] Merge commits are disabled
- [x] Version labels are created (`version: major`, `version: minor`, `version: patch`)
- [x] **Note**: Verification of required status checks is moved to Phase 8 (GitHub Configuration Finalizer). See `08_GitHub_Configuration_finalizer.md` for status check verification tasks.
- [x] Workflow permissions are configured correctly
- [x] Repository settings are configured
- [x] Actions settings are configured
- [x] Auto-merge is configured (optional)
- [x] Dependabot is configured and enabled
- [x] Dependabot security updates are enabled (if applicable)
- [x] CODEOWNERS file exists (created, ready to commit and push)
- [ ] All settings are saved and active
- [x] Documentation is updated (see Section 11)

## Success Criteria

- [ ] Branch protection rules configured and active
- [ ] Both rebase and merge and squash and merge are allowed (linear history maintained)
- [ ] Merge commits are disabled
- [ ] Version labels created
- [ ] Workflow permissions configured
- [ ] Repository settings configured
- [ ] Dependabot configured and enabled
- [ ] Basic test PRs verify merge strategy and branch protection work
- [ ] Basic documentation updated
- [ ] **Note**: Status checks configuration, status check testing, and related documentation are moved to Phase 8 (GitHub Configuration Finalizer). See `08_GitHub_Configuration_finalizer.md` for those success criteria.

## Troubleshooting

### PR Cannot Be Merged
- **Issue**: "Required status checks must pass"
- **Solution**: Ensure all quality check workflows are passing
- Check workflow runs in Actions tab
- Verify branch protection rules include all required checks
- **Note**: If workflows haven't been created yet (Phase 7), status checks won't appear. This is expected.

### Labels Not Auto-Applied
- **Issue**: PR labels not appearing automatically
- **Solution**:
  - Check `.github/workflows/pr-label.yml` exists and is correct (see Phase 7)
  - Verify workflow has `pull-requests: write` permission
  - Check workflow runs in Actions tab
  - Manually trigger workflow if needed
  - **Note**: PR label workflow is created in Phase 7. If you're configuring before Phase 7, labels won't auto-apply until the workflow is created.

### Cannot Rebase or Squash Merge
- **Issue**: Rebase and merge or squash and merge options not available
- **Solution**:
  - Verify repository settings allow rebase merging and squash merging
  - Check branch protection rules don't restrict merge types
  - Ensure PR is up to date with base branch
  - Note: Both rebase merge and squash merge maintain linear history, so either can be used

### Workflow Permission Errors
- **Issue**: Workflows failing with permission errors
- **Solution**:
  - Check workflow `permissions` section
  - Verify repository Actions settings allow required permissions
  - Check if workflow needs `GITHUB_TOKEN` with specific permissions
  - See Section 4 for workflow permissions configuration

### Status Checks Not Appearing
- **Issue**: Required status checks don't appear in branch protection settings
- **Solution**:
  - Status checks only appear after workflows have run at least once
  - Create a test PR to trigger workflows (after Phase 7 is complete)
  - Wait for workflows to complete
  - Return to branch protection settings - checks should now appear
  - If still not appearing, check workflow file names and job names match

## Notes

- Branch protection rules prevent direct pushes to `main`
- All changes must go through pull requests
- Version labels are created here but automatically applied by workflow (see Phase 7)
- Labels can be manually overridden if needed
- Linear git history is required for versioning strategy
- CI/CD workflow implementation is in Phase 7 (Continuous Delivery)
- **Important**: Tasks that depend on Phase 7 workflows (status checks configuration, status check testing, and related documentation) have been moved to Phase 8 (GitHub Configuration Finalizer). See `08_GitHub_Configuration_finalizer.md` for those tasks.

## References

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Merge Methods](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github)
- [GitHub Labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)
- [GitHub Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token)
- [GitHub Dependabot](https://docs.github.com/en/code-security/dependabot)
- [REQ_GITHUB.md](../plan/25W46/REQ_GITHUB.md) - Detailed GitHub configuration documentation
- Phase 8: GitHub Configuration Finalizer - Tasks that depend on Phase 7 workflows
