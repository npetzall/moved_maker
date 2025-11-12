# Phase 6: GitHub Configuration Implementation Plan

## Overview
Configure GitHub repository settings to support quality tooling, versioning strategy, and continuous delivery workflows.

## Goals
- Configure branch protection rules for `main` branch
- Set merge strategy to rebase and merge only
- Create version labels for PR-based versioning
- Configure required status checks
- Set up workflow permissions
- Configure Dependabot for automated dependency updates

## Prerequisites
- [ ] GitHub repository access (admin or owner permissions)
- [ ] Phase 1 (Security) completed or in progress
- [ ] Phase 2 (Test Runner) completed or in progress
- [ ] Phase 4 (Coverage) completed or in progress
- [ ] Note: CI/CD workflows will be created in Phase 7 (Continuous Delivery)
- [ ] **Important**: Status checks referenced in this document will not be available until Phase 7 workflows are created. You can configure branch protection now, but you'll need to update it once workflows are in place, or wait until Phase 7 is complete.

## Implementation Tasks

### 1. Configure Branch Protection Rules

- [ ] Navigate to repository Settings → Branches → Branch protection rules
- [ ] Click "Add rule" or edit existing rule for `main` branch
- [ ] Set branch name pattern: `main`
- [ ] Enable "Require a pull request before merging":
  - [ ] Set required approvals: **1** (or more as needed)
  - [ ] Enable "Dismiss stale pull request approvals when new commits are pushed"
  - [ ] Enable "Require review from Code Owners" (if CODEOWNERS file exists)
- [ ] Enable "Require status checks to pass before merging":
  - [ ] Enable "Require branches to be up to date before merging" (PR branch must be rebased on latest `main`)
  - [ ] **Note**: Status checks will appear in the list after workflows run at least once. If you're configuring this before Phase 7, you'll need to:
    - [ ] Create a test PR to trigger workflows (after Phase 7 is complete)
    - [ ] Wait for workflows to complete
    - [ ] Return to branch protection settings
    - [ ] Add required status checks (they should now appear in the list)
  - [ ] Add required status checks (add all quality check jobs):
    - [ ] `security` (from pull_request.yaml) - **Note**: Actual status check name may differ from job name
    - [ ] `test` (from pull_request.yaml)
    - [ ] `coverage` (from pull_request.yaml)
    - [ ] `pre-commit` (if added to CI)
  - [ ] Enable "Require status checks to pass before merging"
- [ ] Enable "Require conversation resolution before merging"
- [ ] Enable "Require linear history":
  - [ ] Enable "Enforce linear history" (prevents merge commits)
- [ ] Configure "Restrict who can push to matching branches":
  - [ ] Only allow repository administrators (or specific teams)
  - [ ] Prevents direct pushes to `main`
- [ ] Enable "Do not allow bypassing the above settings"
- [ ] Save branch protection rule
- [ ] Verify rule is active

### 2. Configure Merge Strategy

- [ ] Navigate to repository Settings → General → Pull Requests
- [ ] Find "Merge button" section
- [ ] Configure merge button options:
  - [ ] Enable "Allow rebase and merge" ✅
  - [ ] Disable "Allow merge commits" ❌
  - [ ] Disable "Allow squash and merge" ❌
- [ ] Enable "Always suggest updating pull request branches"
- [ ] Enable "Allow auto-merge" (optional, for automatic merging after checks pass)
- [ ] Save settings
- [ ] Verify only rebase and merge is available on test PR
- [ ] **Note**: Disabling merge commits and squash merging in settings is redundant if branch protection enforces linear history, but it's still good practice for clarity.

### 3. Create Version Labels

- [ ] Navigate to repository Issues → Labels (or Settings → Labels)
- [ ] Create "version: major" label:
  - [ ] Click "New label"
  - [ ] Name: `version: major`
  - [ ] Color: `#d73a4a` (red)
  - [ ] Description: `Major version bump - breaking changes`
  - [ ] Click "Create label"
- [ ] Create "version: minor" label:
  - [ ] Click "New label"
  - [ ] Name: `version: minor`
  - [ ] Color: `#0075ca` (blue)
  - [ ] Description: `Minor version bump - new features`
  - [ ] Click "Create label"
- [ ] Create "version: patch" label:
  - [ ] Click "New label"
  - [ ] Name: `version: patch`
  - [ ] Color: `#cfd3d7` (gray)
  - [ ] Description: `Patch version bump - bug fixes and minor changes`
  - [ ] Click "Create label"
- [ ] Verify all three labels are created
- [ ] **Note**: These labels will be automatically applied by the PR label workflow created in Phase 7 (`.github/workflows/pr-label.yml`). The workflow analyzes commit messages using Conventional Commits and applies appropriate labels automatically.
- [ ] (Optional) Create additional labels for categorization:
  - [ ] `breaking` - Alternative to `version: major`
  - [ ] `feature` - Alternative to `version: minor`
  - [ ] `bug` - Bug fixes
  - [ ] `docs` - Documentation changes
  - [ ] `chore` - Maintenance tasks

### 4. Configure Workflow Permissions

- [ ] Navigate to repository Settings → Actions → General → Workflow permissions
- [ ] Configure "Workflow permissions":
  - [ ] Select "Read and write permissions"
  - [ ] Enable "Allow GitHub Actions to create and approve pull requests" (optional, only needed if workflows will create/approve PRs automatically)
- [ ] Save settings
- [ ] Verify permissions are set correctly

### 5. Verify Required Status Checks

**Note**: This section can be completed after Phase 7 workflows are created, or you can return here after workflows have run at least once.

- [ ] Navigate to repository Settings → Branches → Branch protection rules
- [ ] Edit `main` branch protection rule
- [ ] Verify "Require status checks to pass before merging" is enabled
- [ ] Verify all required status checks are listed:
  - [ ] `security` (or actual status check name from workflow)
  - [ ] `test` (or actual status check name from workflow)
  - [ ] `coverage` (or actual status check name from workflow)
  - [ ] `pre-commit` (if configured)
- [ ] **Note**: Status checks must have run at least once to appear in the list
- [ ] If status checks don't appear:
  - [ ] Create a test PR to trigger workflows (after Phase 7 is complete)
  - [ ] Wait for workflows to complete
  - [ ] Return to branch protection settings
  - [ ] Status checks should now appear in the list
- [ ] Add all required status checks
- [ ] Save branch protection rule

### 6. Configure Repository Settings

- [ ] Navigate to repository Settings → General
- [ ] Configure "Features":
  - [ ] Enable "Issues" (if needed)
  - [ ] Enable "Projects" (optional)
  - [ ] Enable "Wiki" (optional)
  - [ ] Enable "Discussions" (optional)
- [ ] Verify "Pull Requests" settings:
  - [ ] "Allow merge commits" should be disabled (enforced by branch protection)
  - [ ] "Allow squash merging" should be disabled (enforced by branch protection)
  - [ ] "Allow rebase merging" should be enabled (required)
  - [ ] "Always suggest updating pull request branches" should be enabled
  - [ ] "Allow auto-merge" should be enabled (optional)
- [ ] Save settings

### 7. Configure Actions Settings

- [ ] Navigate to repository Settings → Actions → General
- [ ] Configure "Actions permissions":
  - [ ] Select "Allow all actions and reusable workflows"
  - [ ] Or: "Allow local actions and reusable workflows" (more restrictive)
- [ ] Verify "Workflow permissions" are set (from step 4)
- [ ] Configure "Artifact and log retention":
  - [ ] Set retention period (e.g., 90 days) to manage storage
- [ ] Configure "Fork pull request workflows" (as needed for security)
- [ ] Save settings

### 8. Create CODEOWNERS File (Optional)

- [ ] Create `.github/CODEOWNERS` file (if code ownership is needed)
- [ ] Define code owners:
  ```
  # Default owners
  * @username
  
  # Specific paths
  /src/parser/ @parser-team
  /tests/ @test-team
  ```
- [ ] Commit and push `.github/CODEOWNERS`
- [ ] Verify CODEOWNERS is recognized by GitHub
- [ ] Update branch protection to require CODEOWNERS review (if applicable)

### 9. Configure Dependabot

- [ ] Create `.github/dependabot.yml` file
- [ ] Add complete Dependabot configuration:
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
- [ ] **Note**: Dependabot security updates are configured separately in repository Settings → Security → Dependabot alerts. Enable "Dependabot alerts" and "Dependabot security updates" if you want automatic security PRs.
- [ ] Verify Dependabot configuration syntax
- [ ] Commit and push `.github/dependabot.yml`
- [ ] Navigate to repository Settings → Security → Dependabot
- [ ] Verify Dependabot is enabled
- [ ] Verify Dependabot alerts are enabled (if applicable)
- [ ] Verify Dependabot security updates are enabled (if applicable)
- [ ] Check that Dependabot creates PRs for dependency updates

### 10. Test Branch Protection

- [ ] Create a test branch from `main`
- [ ] Make a small change
- [ ] Push branch and create pull request
- [ ] Verify PR cannot be merged until:
  - [ ] Required status checks pass (if workflows are configured)
  - [ ] PR is approved (if required)
  - [ ] Conversation is resolved (if enabled)
- [ ] Verify only "Rebase and merge" option is available
- [ ] Verify "Create a merge commit" and "Squash and merge" are disabled
- [ ] **Note**: If workflows aren't configured yet (Phase 7), status checks won't appear. This is expected.
- [ ] Wait for status checks to complete (if workflows are configured)
- [ ] Verify PR can be merged after all checks pass
- [ ] Test rebase and merge (or close PR without merging)

### 11. Document Configuration

- [ ] Update project README with GitHub configuration information:
  - [ ] Branch protection rules
  - [ ] Merge strategy (rebase only)
  - [ ] PR workflow requirements
  - [ ] Version label system (how labels are auto-applied from Conventional Commits)
  - [ ] How to create PRs
  - [ ] Required status checks
  - [ ] How version labels work (auto-applied by workflow in Phase 7)
- [ ] Document how version labels work:
  - [ ] Labels are automatically applied by PR label workflow (Phase 7)
  - [ ] Labels are based on Conventional Commits in commit messages
  - [ ] Labels can be manually overridden if needed
- [ ] Document how to create PRs:
  - [ ] Use Conventional Commits format for commit messages
  - [ ] PR will automatically get version label applied
  - [ ] All status checks must pass before merging
  - [ ] Only rebase and merge is allowed
- [ ] Document required status checks:
  - [ ] Security checks (cargo-deny, cargo-audit, cargo-geiger)
  - [ ] Tests (cargo-nextest)
  - [ ] Coverage (cargo-llvm-cov with thresholds)
  - [ ] Pre-commit (if configured)
- [ ] Update CONTRIBUTING.md (if exists) with PR requirements
- [ ] Add troubleshooting section reference (see Section 12)

### 12. Verification Checklist

- [ ] Branch protection rules are active for `main`
- [ ] Only rebase and merge is allowed
- [ ] Required status checks are configured (after Phase 7 workflows are created)
- [ ] Version labels are created (`version: major`, `version: minor`, `version: patch`)
- [ ] Workflow permissions are configured correctly
- [ ] Repository settings are configured
- [ ] Actions settings are configured
- [ ] Auto-merge is configured (optional)
- [ ] Dependabot is configured and enabled
- [ ] Dependabot security updates are enabled (if applicable)
- [ ] CODEOWNERS file exists (if applicable)
- [ ] All settings are saved and active
- [ ] Documentation is updated (see Section 11)

## Success Criteria

- [ ] Branch protection rules configured and active
- [ ] Only rebase and merge is allowed
- [ ] Required status checks configured (after Phase 7)
- [ ] Version labels created
- [ ] Workflow permissions configured
- [ ] Repository settings configured
- [ ] Dependabot configured and enabled
- [ ] Test PRs verify all configurations work
- [ ] Documentation updated

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

### Cannot Rebase and Merge
- **Issue**: Rebase and merge option not available
- **Solution**:
  - Verify repository settings allow rebase merging
  - Check branch protection rules don't restrict merge types
  - Ensure PR is up to date with base branch

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
- **Important**: Some configuration steps (especially status checks) depend on workflows created in Phase 7. You can configure most settings now, but you'll need to return to update status checks after Phase 7 workflows are created and have run at least once.

## References

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Merge Methods](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github)
- [GitHub Labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)
- [GitHub Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token)
- [GitHub Dependabot](https://docs.github.com/en/code-security/dependabot)
- [GITHUB.md](../plan/01_Quality/GITHUB.md) - Detailed GitHub configuration documentation
