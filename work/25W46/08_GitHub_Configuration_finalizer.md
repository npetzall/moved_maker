# Phase 8: GitHub Configuration Finalizer

## Overview
Complete GitHub repository configuration tasks that depend on Phase 7 (Continuous Delivery) workflows being in place.

## Goals
- Configure required status checks in branch protection rules
- Verify status checks are working correctly
- Complete documentation for status checks and version label workflows
- Final verification of all GitHub configurations

## Prerequisites
- [x] Phase 6 (GitHub Configuration) completed
- [x] Phase 7 (Continuous Delivery) completed - workflows must be created and have run at least once
- [x] GitHub repository access (admin or owner permissions)

## Implementation Tasks

### 1. Add Required Status Checks to Branch Protection

**Note**: Status checks will appear in the list after workflows run at least once. Complete Phase 7 first, then return here.

- [ ] Navigate to repository Settings → Branches → Branch protection rules
- [ ] Edit `main` branch protection rule
- [ ] Verify "Require status checks to pass before merging" is enabled
- [ ] If status checks don't appear:
  - [ ] Create a test PR to trigger workflows (after Phase 7 is complete)
  - [ ] Wait for workflows to complete
  - [ ] Return to branch protection settings
  - [ ] Status checks should now appear in the list
- [ ] Add required status checks (add all quality check jobs):
  - [ ] `security` (from pull_request.yaml) - **Note**: Actual status check name may differ from job name
  - [ ] `test` (from pull_request.yaml)
  - [ ] `coverage` (from pull_request.yaml)
  - [ ] `pre-commit` (if added to CI)
- [ ] Save branch protection rule
- [ ] Verify all required status checks are listed:
  - [ ] `security` (or actual status check name from workflow)
  - [ ] `test` (or actual status check name from workflow)
  - [ ] `coverage` (or actual status check name from workflow)
  - [ ] `pre-commit` (if configured)
- [ ] **Note**: Status checks must have run at least once to appear in the list

### 2. Verify Required Status Checks

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

### 3. Test Branch Protection with Status Checks

- [ ] Create a test branch from `main`
- [ ] Make a small change
- [ ] Push branch and create pull request
- [ ] Verify PR cannot be merged until:
  - [ ] Required status checks pass (workflows are now configured)
  - [ ] PR is approved (if required)
  - [ ] Conversation is resolved (if enabled)
- [ ] Verify only "Rebase and merge" option is available
- [ ] Verify "Create a merge commit" and "Squash and merge" are disabled
- [ ] Wait for status checks to complete
- [ ] Verify all status checks pass:
  - [ ] Security checks (cargo-deny, cargo-audit, cargo-geiger)
  - [ ] Tests (cargo-nextest)
  - [ ] Coverage (cargo-llvm-cov with thresholds)
  - [ ] Pre-commit (if configured)
- [ ] Verify PR can be merged after all checks pass
- [ ] Test rebase and merge (or close PR without merging)

### 4. Document Status Checks and Version Label Workflows

- [ ] Update project README with status check information:
  - [ ] Required status checks
  - [ ] How status checks work
  - [ ] What each status check validates
- [ ] Document required status checks:
  - [ ] Security checks (cargo-deny, cargo-audit, cargo-geiger)
  - [ ] Tests (cargo-nextest)
  - [ ] Coverage (cargo-llvm-cov with thresholds)
  - [ ] Pre-commit (if configured)
- [ ] Document how version labels work:
  - [ ] Labels are automatically applied by PR label workflow (Phase 7)
  - [ ] Labels are based on Conventional Commits in commit messages
  - [ ] Labels can be manually overridden if needed
- [ ] Document how to create PRs:
  - [ ] Use Conventional Commits format for commit messages
  - [ ] PR will automatically get version label applied
  - [ ] All status checks must pass before merging
  - [ ] Only rebase and merge is allowed
- [ ] Update CONTRIBUTING.md (if exists) with PR requirements
- [ ] Add troubleshooting section reference (see Section 6)

### 5. Final Verification Checklist

- [ ] Branch protection rules are active for `main`
- [ ] Only rebase and merge is allowed
- [ ] Required status checks are configured and active
- [ ] All required status checks are listed in branch protection:
  - [ ] `security` (or actual status check name)
  - [ ] `test` (or actual status check name)
  - [ ] `coverage` (or actual status check name)
  - [ ] `pre-commit` (if configured)
- [ ] Status checks are passing on test PR
- [ ] PR cannot be merged until all status checks pass
- [ ] Version labels are created (`version: major`, `version: minor`, `version: patch`)
- [ ] Version label workflow is working (auto-applying labels based on Conventional Commits)
- [ ] Workflow permissions are configured correctly
- [ ] Repository settings are configured
- [ ] Actions settings are configured
- [ ] Auto-merge is configured (optional)
- [ ] Dependabot is configured and enabled
- [ ] Dependabot security updates are enabled (if applicable)
- [ ] CODEOWNERS file exists (if applicable)
- [ ] All settings are saved and active
- [ ] Documentation is updated (see Section 4)

## Success Criteria

- [ ] Required status checks configured and active in branch protection
- [ ] All status checks are passing on test PRs
- [ ] PRs cannot be merged until all status checks pass
- [ ] Version label workflow is working correctly
- [ ] Test PRs verify all configurations work
- [ ] Documentation updated with status check and version label information

## Troubleshooting

### Status Checks Not Appearing
- **Issue**: Required status checks don't appear in branch protection settings
- **Solution**:
  - Status checks only appear after workflows have run at least once
  - Create a test PR to trigger workflows (after Phase 7 is complete)
  - Wait for workflows to complete
  - Return to branch protection settings - checks should now appear
  - If still not appearing, check workflow file names and job names match

### PR Cannot Be Merged
- **Issue**: "Required status checks must pass"
- **Solution**: Ensure all quality check workflows are passing
- Check workflow runs in Actions tab
- Verify branch protection rules include all required checks
- Check individual workflow runs to see which checks are failing

### Labels Not Auto-Applied
- **Issue**: PR labels not appearing automatically
- **Solution**:
  - Check `.github/workflows/pr-label.yml` exists and is correct (see Phase 7)
  - Verify workflow has `pull-requests: write` permission
  - Check workflow runs in Actions tab
  - Manually trigger workflow if needed
  - Verify commit messages follow Conventional Commits format

### Status Checks Failing
- **Issue**: One or more status checks are failing
- **Solution**:
  - Check workflow logs in Actions tab
  - Verify all dependencies are installed correctly
  - Check if thresholds are set too high (coverage)
  - Verify test files are in correct locations
  - Check security tool configurations

## Notes

- This phase should be completed after Phase 7 (Continuous Delivery) workflows are created
- Status checks must run at least once before they appear in branch protection settings
- Version label workflow is created in Phase 7 and should be working by the time you reach this phase
- All status checks must pass before PRs can be merged
- Linear git history is required for versioning strategy

## References

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Status Checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging)
- [GitHub Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token)
- Phase 6: GitHub Configuration Implementation Plan
- Phase 7: Continuous Delivery Implementation Plan
