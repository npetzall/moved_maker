# Phase 7.2: PR Label Workflow Implementation

## Overview
Automatically apply version labels to pull requests based on Conventional Commits in commit messages. This workflow analyzes commit messages and applies appropriate version labels (`version: major`, `version: minor`, or defaults to patch).

## Goals
- Create PR label workflow to automatically apply version labels based on Conventional Commits
- Ensure labels are applied correctly for major, minor, and patch version bumps
- Support manual label overrides

## Prerequisites
- [ ] Phase 6 (GitHub Configuration) completed (version labels created in GitHub UI)
- [ ] GitHub repository access (admin or owner permissions)
- [ ] Version labels exist in repository:
  - `version: major` (required)
  - `version: minor` (required)
  - `version: patch` (optional, used as default)
  - `breaking` (required - alternative label for major version)
  - `feature` (required - alternative label for minor version)

## Workflow File
- **File**: `.github/workflows/pr-label.yml`
- **Trigger**: Pull requests (opened, synchronize, reopened)

## Required Permissions
- `contents: read` - To checkout code
- `pull-requests: write` - To add/remove labels on PRs

## Implementation Tasks

### 1. Create PR Label Workflow File

- [ ] Verify `.github/workflows/` directory exists (create if needed: `mkdir -p .github/workflows`)
- [ ] Create `.github/workflows/pr-label.yml` file
- [ ] Add complete workflow implementation:
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
        - name: Checkout code
          uses: actions/checkout@v4
          with:
            fetch-depth: 0

        - name: Setup GitHub CLI
          uses: cli/cli-action@v2
          with:
            github-token: ${{ secrets.GITHUB_TOKEN }}

        - name: Analyze commits and apply labels
          run: |
            PR_NUM=${{ github.event.pull_request.number }}

            # Get all commit messages in this PR
            COMMITS=$(gh pr view $PR_NUM --json commits --jq '.commits[].message')

            # Determine version bump type from commits
            VERSION_LABEL=""
            ALT_LABEL=""
            if echo "$COMMITS" | grep -qE "(BREAKING CHANGE|!:)"; then
              VERSION_LABEL="version: major"
              ALT_LABEL="breaking"
            elif echo "$COMMITS" | grep -qE "^feat:"; then
              VERSION_LABEL="version: minor"
              ALT_LABEL="feature"
            fi

            # Remove existing version labels (both primary and alternative)
            gh pr edit $PR_NUM --remove-label "version: major" "version: minor" "version: patch" "breaking" "feature" 2>/dev/null || true

            # Apply new labels if determined
            if [ -n "$VERSION_LABEL" ]; then
              gh pr edit $PR_NUM --add-label "$VERSION_LABEL"
              if [ -n "$ALT_LABEL" ]; then
                gh pr edit $PR_NUM --add-label "$ALT_LABEL"
              fi
              echo "Applied labels: $VERSION_LABEL${ALT_LABEL:+ and $ALT_LABEL}"
            else
              echo "No version label applied (patch bump)"
            fi
  ```
- [ ] Verify workflow syntax
- [ ] Commit and push `.github/workflows/pr-label.yml`
- [ ] Verify workflow file is created in correct location

### 2. Test PR Label Workflow

- [ ] Create a test branch from `main`
- [ ] Make a commit with `feat:` prefix (e.g., `feat: add new feature`)
- [ ] Push branch and create pull request
- [ ] Verify both `version: minor` and `feature` labels are applied automatically
- [ ] Create another test PR with a `fix:` commit message
- [ ] Verify no version label is applied (defaults to patch)
- [ ] Create another test PR with a `BREAKING CHANGE:` in commit message
- [ ] Verify both `version: major` and `breaking` labels are applied automatically
- [ ] Test manual label override (add/remove labels manually)
- [ ] Verify manual labels are preserved after workflow runs
- [ ] Test PR with multiple commits (mixed types) - should take highest priority
- [ ] Verify workflow runs on PR updates (synchronize event)

### 3. Handle Edge Cases

- [ ] Test PR with no commits (empty PR)
- [ ] Test PR with non-conventional commit messages
- [ ] Test PR with multiple commits of different types
- [ ] Verify highest priority label is applied (major > minor > patch)
- [ ] Test PR label removal and re-application
- [ ] Verify workflow handles PRs with existing labels correctly

## Label Priority

The workflow applies labels based on the highest priority found in commit messages:

1. **Major** (`version: major` and `breaking`): Triggered by:
   - `BREAKING CHANGE:` in commit message
   - `!:` in commit type (e.g., `feat!: breaking change`)
   - Both `version: major` and `breaking` labels are applied for compatibility

2. **Minor** (`version: minor` and `feature`): Triggered by:
   - `feat:` commit type
   - Both `version: minor` and `feature` labels are applied for compatibility

3. **Patch** (default, no label): Triggered by:
   - `fix:` commit type
   - `chore:` commit type
   - `docs:` commit type
   - Any other commit type
   - No matching pattern

## Conventional Commits Reference

The workflow recognizes the following Conventional Commits patterns:

- `feat:` - New feature (minor bump)
- `fix:` - Bug fix (patch bump)
- `BREAKING CHANGE:` or `!:` - Breaking change (major bump)
- Other types (`chore:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`) - Patch bump

## Verification

- [ ] PR label workflow exists and is correct
- [ ] PR label workflow applies labels automatically
- [ ] Workflow runs on PR opened, synchronize, and reopened events
- [ ] Labels are applied correctly for major, minor, and patch commits
- [ ] Both primary labels (`version: major`, `version: minor`) and alternative labels (`breaking`, `feature`) are applied
- [ ] Manual label overrides work correctly
- [ ] Workflow handles edge cases correctly

## Success Criteria

- [x] PR label workflow created (`.github/workflows/pr-label.yml`)
- [x] PR label workflow automatically applies version labels
- [ ] PR label workflow tested and working (needs testing)
- [ ] Labels are applied correctly for all commit types (needs testing)
- [x] Manual label overrides are supported

## Troubleshooting

### Workflow Doesn't Run
- Verify workflow file is in `.github/workflows/` directory
- Check workflow trigger events are correct
- Verify PR event types match workflow configuration

### Labels Not Applied
- Check GitHub CLI has correct permissions (`pull-requests: write`)
- Verify version labels exist in repository (created in Phase 6)
- Check workflow logs for errors
- Verify commit messages match Conventional Commits format

### Permission Errors
- Verify workflow has `pull-requests: write` permission
- Check repository Settings → Actions → General → Workflow permissions
- Ensure "Read and write permissions" is selected
- Approve workflow permissions if prompted in Actions tab

### Wrong Label Applied
- Verify commit message format matches expected patterns
- Check workflow logic for label priority
- Review workflow logs to see which commits were analyzed

## References

- [Main Continuous Delivery Plan](./07_Continuous_Delivery.md) - Overview and architecture
- [Pull Request Workflow Plan](./07_01_Pull_Request_Workflow.md) - PR quality checks
- [Release Workflow Plan](./07_03_Release_Workflow.md) - Uses labels for version calculation
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit message format specification
