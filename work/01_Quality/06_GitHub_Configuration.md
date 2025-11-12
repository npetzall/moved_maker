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
- [ ] CI workflows created (pull_request.yaml, release.yaml)

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
  - [ ] Enable "Require branches to be up to date before merging"
  - [ ] Add required status checks (add all quality check jobs):
    - [ ] `security` (from pull_request.yaml)
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
- [ ] (Optional) Create additional labels for categorization:
  - [ ] `breaking` - Alternative to `version: major`
  - [ ] `feature` - Alternative to `version: minor`
  - [ ] `bug` - Bug fixes
  - [ ] `docs` - Documentation changes
  - [ ] `chore` - Maintenance tasks

### 4. Create PR Label Workflow

- [ ] Create `.github/workflows/pr-label.yml` file
- [ ] Add workflow to automatically apply version labels based on Conventional Commits:
  ```yaml
  name: PR Label
  
  on:
    pull_request:
      types: [opened, synchronize, reopened]
  
  permissions:
    contents: read
    pull-requests: write
  
  jobs:
    label:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
          with:
            fetch-depth: 0
        
        - name: Analyze commits and apply labels
          uses: actions/github-script@v7
          with:
            script: |
              // Analyze PR commits and apply version labels
              // Implementation details from VERSIONING.md
  ```
- [ ] Implement label logic:
  - [ ] Get PR commits
  - [ ] Analyze commit messages for Conventional Commits
  - [ ] Apply `version: major` if commits contain `BREAKING CHANGE:` or `!`
  - [ ] Apply `version: minor` if commits contain `feat:`
  - [ ] Leave unlabeled (patch) for all other commits
- [ ] Verify workflow syntax
- [ ] Commit and push `.github/workflows/pr-label.yml`
- [ ] Test workflow by creating a test PR
- [ ] Verify labels are applied automatically

### 5. Configure Workflow Permissions

- [ ] Navigate to repository Settings → Actions → General → Workflow permissions
- [ ] Configure "Workflow permissions":
  - [ ] Select "Read and write permissions"
  - [ ] Enable "Allow GitHub Actions to create and approve pull requests" (if needed for automation)
- [ ] Save settings
- [ ] Verify permissions are set correctly

### 6. Verify Required Status Checks

- [ ] Navigate to repository Settings → Branches → Branch protection rules
- [ ] Edit `main` branch protection rule
- [ ] Verify "Require status checks to pass before merging" is enabled
- [ ] Verify all required status checks are listed:
  - [ ] `security`
  - [ ] `test`
  - [ ] `coverage`
  - [ ] `pre-commit` (if configured)
- [ ] Note: Status checks must have run at least once to appear in the list
- [ ] If status checks don't appear:
  - [ ] Create a test PR to trigger workflows
  - [ ] Wait for workflows to complete
  - [ ] Return to branch protection settings
  - [ ] Status checks should now appear in the list
- [ ] Add all required status checks
- [ ] Save branch protection rule

### 7. Configure Repository Settings

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

### 8. Configure Actions Settings

- [ ] Navigate to repository Settings → Actions → General
- [ ] Configure "Actions permissions":
  - [ ] Select "Allow all actions and reusable workflows"
  - [ ] Or: "Allow local actions and reusable workflows" (more restrictive)
- [ ] Verify "Workflow permissions" are set (from step 5)
- [ ] Configure "Artifact and log retention":
  - [ ] Set retention period (e.g., 90 days) to manage storage
- [ ] Configure "Fork pull request workflows" (as needed for security)
- [ ] Save settings

### 9. Create CODEOWNERS File (Optional)

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

### 10. Configure Dependabot

- [ ] Create `.github/dependabot.yml` file
- [ ] Configure Cargo package ecosystem:
  - [ ] Set directory to `/`
  - [ ] Set schedule interval (e.g., `weekly`)
  - [ ] Set open pull requests limit (e.g., `10`)
  - [ ] Add reviewers (if applicable)
  - [ ] Add labels: `["dependencies", "security"]`
- [ ] Verify Dependabot configuration syntax
- [ ] Commit and push `.github/dependabot.yml`
- [ ] Navigate to repository Settings → Security → Dependabot
- [ ] Verify Dependabot is enabled
- [ ] Verify Dependabot alerts are enabled (if applicable)
- [ ] Check that Dependabot creates PRs for dependency updates

### 11. Test Branch Protection

- [ ] Create a test branch from `main`
- [ ] Make a small change
- [ ] Push branch and create pull request
- [ ] Verify PR cannot be merged until:
  - [ ] Required status checks pass
  - [ ] PR is approved (if required)
  - [ ] Conversation is resolved (if enabled)
- [ ] Verify only "Rebase and merge" option is available
- [ ] Verify "Create a merge commit" and "Squash and merge" are disabled
- [ ] Wait for status checks to complete
- [ ] Verify PR can be merged after all checks pass
- [ ] Test rebase and merge (or close PR without merging)

### 12. Test PR Label Workflow

- [ ] Create a test PR with a `feat:` commit message
- [ ] Verify `version: minor` label is applied automatically
- [ ] Create a test PR with a `fix:` commit message
- [ ] Verify no version label is applied (defaults to patch)
- [ ] Create a test PR with a `BREAKING CHANGE:` commit message
- [ ] Verify `version: major` label is applied automatically
- [ ] Test manual label override (add/remove labels manually)
- [ ] Verify manual labels are preserved

### 13. Document Configuration

- [ ] Update project README with GitHub configuration information:
  - [ ] Branch protection rules
  - [ ] Merge strategy
  - [ ] Version labels
  - [ ] PR workflow
- [ ] Document how version labels work
- [ ] Document how to create PRs
- [ ] Document required status checks
- [ ] Update CONTRIBUTING.md (if exists) with PR requirements

### 14. Verification Checklist

- [ ] Branch protection rules are active for `main`
- [ ] Only rebase and merge is allowed
- [ ] Required status checks are configured
- [ ] Version labels are created (`version: major`, `version: minor`, `version: patch`)
- [ ] PR label workflow exists and works
- [ ] PR label workflow has correct permissions
- [ ] Release workflow has correct permissions
- [ ] All quality check workflows are running on PRs
- [ ] Auto-merge is configured (optional)
- [ ] Dependabot is configured and enabled
- [ ] CODEOWNERS file exists (if applicable)
- [ ] All settings are saved and active

## Success Criteria

- [ ] Branch protection rules configured and active
- [ ] Only rebase and merge is allowed
- [ ] Required status checks configured
- [ ] Version labels created
- [ ] PR label workflow created and working
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

### Labels Not Auto-Applied
- **Issue**: PR labels not appearing automatically
- **Solution**: 
  - Check `.github/workflows/pr-label.yml` exists and is correct
  - Verify workflow has `pull-requests: write` permission
  - Check workflow runs in Actions tab
  - Manually trigger workflow if needed

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

## Notes

- Branch protection rules prevent direct pushes to `main`
- All changes must go through pull requests
- Version labels are automatically applied based on Conventional Commits
- Labels can be manually overridden if needed
- Linear git history is required for versioning strategy

## References

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Merge Methods](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github)
- [GitHub Labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)
- [GitHub Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token)
- [GitHub Dependabot](https://docs.github.com/en/code-security/dependabot)
- [GITHUB.md](../plan/01_Quality/GITHUB.md) - Detailed GitHub configuration documentation

