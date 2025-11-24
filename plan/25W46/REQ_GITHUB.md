# GitHub Repository Configuration

## Overview
This document outlines all GitHub repository configuration requirements to support the quality tooling, versioning strategy, and continuous delivery workflows for the move_maker project.

## Requirements Summary

1. **Branch Protection**: Require pull requests for `main` branch
2. **Merge Strategy**: Only allow rebase and merge (linear git history)
3. **Label Management**: Configure version labels for PR-based versioning
4. **Status Checks**: Require all quality checks to pass before merging
5. **Workflow Permissions**: Configure GitHub Actions permissions

## Branch Protection Rules

### Main Branch Protection

Configure branch protection for the `main` branch with the following settings:

**Location**: Repository Settings → Branches → Branch protection rules → Add rule

**Branch name pattern**: `main`

**Settings to enable**:

1. ✅ **Require a pull request before merging**
   - ✅ Require approvals: **1** (or more as needed)
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require review from Code Owners (if CODEOWNERS file exists)

2. ✅ **Require status checks to pass before merging**
   - ✅ Require branches to be up to date before merging
   - **Required status checks** (add all quality check jobs):
     - `security` (from pull_request.yaml)
     - `test` (from pull_request.yaml)
     - `coverage` (from pull_request.yaml)
     - `pre-commit` (if added to CI)
   - ✅ Require status checks to pass before merging

3. ✅ **Require conversation resolution before merging**
   - Ensures all PR comments are addressed

4. ✅ **Require linear history**
   - ✅ Enforce linear history (prevents merge commits)

5. ✅ **Restrict who can push to matching branches**
   - Only allow repository administrators (or specific teams)
   - Prevents direct pushes to `main`

6. ✅ **Do not allow bypassing the above settings**
   - Even administrators must follow these rules

### Merge Strategy Configuration

**Location**: Repository Settings → General → Pull Requests

**Merge button configuration**:
- ✅ Allow **Rebase and merge**
- ❌ Disallow **Create a merge commit**
- ❌ Disallow **Squash and merge**

**Rationale**:
- Linear git history required for versioning strategy (see [VERSIONING.md](VERSIONING.md))
- Rebase and merge maintains clean, linear commit history
- Each commit in PR history is preserved
- Version calculation relies on linear history

## Label Management

### Version Labels

Labels are used for automatic version bump signaling. See [VERSIONING.md](VERSIONING.md) for details on how labels are auto-applied from Conventional Commits.

**Location**: Repository Settings → Labels (or Issues → Labels)

**Required Labels**:

1. **version: major**
   - Color: `#d73a4a` (red)
   - Description: `Major version bump - breaking changes`
   - Auto-applied when PR contains `BREAKING CHANGE:` or `!` in commit messages

2. **version: minor**
   - Color: `#0075ca` (blue)
   - Description: `Minor version bump - new features`
   - Auto-applied when PR contains `feat:` commits

3. **version: patch**
   - Color: `#cfd3d7` (gray)
   - Description: `Patch version bump - bug fixes and minor changes`
   - Default (no label = patch)

**Optional Labels** (for categorization):

- `breaking` - Alternative to `version: major`
- `feature` - Alternative to `version: minor`
- `bug` - Bug fixes
- `docs` - Documentation changes
- `chore` - Maintenance tasks

### Label Configuration Steps

1. Go to Issues → Labels
2. For each required label:
   - Click "New label"
   - Enter label name (e.g., `version: major`)
   - Choose color
   - Add description
   - Click "Create label"

### Label Auto-Application

Labels are automatically applied by the workflow defined in [VERSIONING.md](VERSIONING.md):

**Workflow**: `.github/workflows/pr-label.yml`

This workflow:
- Runs on PR open, update, and reopen
- Analyzes commit messages using Conventional Commits
- Automatically applies appropriate version labels
- Can be manually overridden by adding/removing labels

## Pull Request Requirements

### PR Workflow

All changes to `main` must go through pull requests:

1. Create feature branch from `main`
2. Make changes and commit (following Conventional Commits)
3. Push branch and create pull request
4. PR automatically gets version label applied
5. Quality checks run automatically (tests, coverage, security)
6. After approval and passing checks, merge via rebase

### PR Title and Description

**PR Title**: Should follow Conventional Commits format (optional but recommended):
```
feat(parser): add support for data blocks
```

**PR Description**: Should include:
- Summary of changes
- Related issues (if any)
- Testing notes
- Breaking changes (if any)

### Required Status Checks

The following checks must pass before a PR can be merged:

1. **Security Checks** (`security` job)
   - cargo-deny check
   - cargo-audit check
   - cargo-geiger scan

2. **Tests** (`test` job)
   - cargo-nextest run (all platforms)

3. **Coverage** (`coverage` job)
   - cargo-llvm-cov with threshold checks

4. **Pre-commit** (if configured in CI)
   - Formatting checks
   - Commit message validation

## GitHub Actions Permissions

### Workflow Permissions

Configure workflow permissions to allow:
- Reading repository contents
- Writing to pull requests (for labels)
- Creating releases
- Writing workflow files

**Location**: Repository Settings → Actions → General → Workflow permissions

**Settings**:
- ✅ Read and write permissions
- ✅ Allow GitHub Actions to create and approve pull requests (if needed for automation)

### Required Permissions by Workflow

#### PR Label Workflow (`.github/workflows/pr-label.yml`)

```yaml
permissions:
  contents: read
  pull-requests: write  # Required to add/remove labels
```

#### Release Workflow (`.github/workflows/release.yaml`)

```yaml
permissions:
  contents: write  # Required to create releases and tags
  pull-requests: read  # Required to read PR labels
```

#### Pull Request Checks (`.github/workflows/pull_request.yaml`)

```yaml
permissions:
  contents: read
  pull-requests: read
```

## Repository Settings

### General Settings

**Location**: Repository Settings → General

**Recommended Settings**:

1. **Features**
   - ✅ Issues
   - ✅ Projects (optional)
   - ✅ Wiki (optional)
   - ✅ Discussions (optional)

2. **Pull Requests**
   - ✅ Allow merge commits: **Disabled** (enforced by branch protection)
   - ✅ Allow squash merging: **Disabled** (enforced by branch protection)
   - ✅ Allow rebase merging: **Enabled** (required)
   - ✅ Always suggest updating pull request branches
   - ✅ Allow auto-merge: **Enabled** (optional, for automatic merging after checks pass)

3. **Archive this repository**: **Disabled** (unless archiving)

### Actions Settings

**Location**: Repository Settings → Actions → General

**Settings**:

1. **Actions permissions**
   - ✅ Allow all actions and reusable workflows
   - Or: Allow local actions and reusable workflows (more restrictive)

2. **Workflow permissions**
   - ✅ Read and write permissions (as configured above)

3. **Artifact and log retention**
   - Set retention period (e.g., 90 days) to manage storage

4. **Fork pull request workflows**
   - Configure as needed for security

## Dependabot Configuration

**Location**: `.github/dependabot.yml`

Dependabot should be configured to automatically update dependencies. See [SECURITY.md](SECURITY.md) for configuration details.

**Example**:
```yaml
version: 2
updates:
  - package-ecosystem: "cargo"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

## CODEOWNERS File (Optional)

**Location**: `.github/CODEOWNERS`

Define code owners for automatic PR review requests:

```
# Default owners
* @username

# Specific paths
/src/parser/ @parser-team
/tests/ @test-team
```

## Verification Checklist

After configuring GitHub settings, verify:

- [ ] Branch protection rules are active for `main`
- [ ] Only rebase and merge is allowed
- [ ] Required status checks are configured
- [ ] Version labels are created (`version: major`, `version: minor`, `version: patch`)
- [ ] PR label workflow has correct permissions
- [ ] Release workflow has correct permissions
- [ ] All quality check workflows are running on PRs
- [ ] Auto-merge is configured (optional)
- [ ] Dependabot is enabled (if using)

## Troubleshooting

### PR Cannot Be Merged

**Issue**: "Required status checks must pass"
- **Solution**: Ensure all quality check workflows are passing
- Check workflow runs in Actions tab
- Verify branch protection rules include all required checks

### Labels Not Auto-Applied

**Issue**: PR labels not appearing automatically
- **Solution**:
  - Check `.github/workflows/pr-label.yml` exists and is correct
  - Verify workflow has `pull-requests: write` permission
  - Check workflow runs in Actions tab
  - Manually trigger workflow if needed

### Cannot Rebase and Merge

**Issue**: Rebase and merge option not available
- **Solution**:
  - Verify repository settings allow rebase merging
  - Check branch protection rules don't restrict merge types
  - Ensure PR is up to date with base branch

### Workflow Permission Errors

**Issue**: Workflows failing with permission errors
- **Solution**:
  - Check workflow `permissions` section
  - Verify repository Actions settings allow required permissions
  - Check if workflow needs `GITHUB_TOKEN` with specific permissions

## References

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Merge Methods](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github)
- [GitHub Labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)
- [GitHub Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token)
- [VERSIONING.md](VERSIONING.md) - Versioning strategy and label usage
- [CONTINUOUS_DELIVERY.md](CONTINUOUS_DELIVERY.md) - Release workflow details
- [IMPLEMENTATION.md](IMPLEMENTATION.md) - CI/CD workflow files
