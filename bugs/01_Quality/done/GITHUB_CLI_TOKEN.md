# GitHub CLI Token Configuration Issue

## Summary

Workflows use `cli/cli-action@v2` which is unnecessary since GitHub CLI (`gh`) is already pre-installed in GitHub Actions runners. However, steps that use the GitHub CLI need to have the `GH_TOKEN` environment variable set to authenticate with the GitHub API.

## Affected Files

- `.github/workflows/release.yaml`
- `.github/workflows/pr-label.yml`

## Current Behavior

### release.yaml

1. **Line 52-55**: Uses `cli/cli-action@v2` to "setup" GitHub CLI (unnecessary)
2. **Line 86**: Uses `gh pr list` command without `GH_TOKEN` environment variable
3. **Line 93**: Uses `gh pr view` command without `GH_TOKEN` environment variable

### pr-label.yml

1. **Line 20-23**: Uses `cli/cli-action@v2` to "setup" GitHub CLI (unnecessary)
2. **Line 30**: Uses `gh pr view` command (relies on token from action, but should be explicit)
3. **Line 44**: Uses `gh pr edit` command (relies on token from action, but should be explicit)
4. **Line 48**: Uses `gh pr edit` command (relies on token from action, but should be explicit)
5. **Line 50**: Uses `gh pr edit` command (relies on token from action, but should be explicit)

## Expected Behavior

1. Remove the `cli/cli-action@v2` step from both workflows (GitHub CLI is already installed)
2. Add `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` environment variable to all steps that use `gh` commands
3. Ensure proper authentication for all GitHub CLI operations

## Impact

- Unnecessary action usage (minor performance overhead)
- Potential authentication issues if the action's token handling changes
- Inconsistent approach to GitHub CLI authentication

## Fix Required

1. Remove `cli/cli-action@v2` setup steps
2. Add `env: GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` to all steps using `gh` commands
3. Verify that all `gh` commands have proper authentication

## References

- GitHub Actions runners include GitHub CLI by default: https://github.com/actions/runner-images
- GitHub CLI authentication: https://cli.github.com/manual/gh_auth

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/release.yaml`

**File:** `.github/workflows/release.yaml`

1. **Remove `cli/cli-action@v2` setup step (lines 52-55)**
   - [x] Locate the "Setup GitHub CLI" step at lines 52-55
   - [x] Remove the entire step:
     ```yaml
     - name: Setup GitHub CLI
       uses: cli/cli-action@v2
       with:
         github-token: ${{ secrets.GITHUB_TOKEN }}
     ```
   - [x] Verify step removal (should be in `version` job)

2. **Add `GH_TOKEN` environment variable to step using `gh pr list` (line 86)**
   - [x] Locate the step "Calculate version from PR labels" (starts around line 60)
   - [x] Add `env:` section to the step:
     ```yaml
     - name: Calculate version from PR labels
       id: version
       env:
         GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
       run: |
         # ... existing script ...
     ```
   - [x] Verify the `gh pr list` command at line 86 will now have access to `GH_TOKEN`
   - [x] Verify the `gh pr view` command at line 93 will also have access to `GH_TOKEN`

#### Step 2: Update `.github/workflows/pr-label.yml`

**File:** `.github/workflows/pr-label.yml`

1. **Remove `cli/cli-action@v2` setup step (lines 20-23)**
   - [x] Locate the "Setup GitHub CLI" step at lines 20-23
   - [x] Remove the entire step:
     ```yaml
     - name: Setup GitHub CLI
       uses: cli/cli-action@v2
       with:
         github-token: ${{ secrets.GITHUB_TOKEN }}
     ```
   - [x] Verify step removal (should be in `label` job)

2. **Add `GH_TOKEN` environment variable to step using `gh` commands (line 25)**
   - [x] Locate the step "Analyze commits and apply labels" (starts at line 25)
   - [x] Add `env:` section to the step:
     ```yaml
     - name: Analyze commits and apply labels
       env:
         GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
       run: |
         # ... existing script ...
     ```
   - [x] Verify all `gh pr view` and `gh pr edit` commands (lines 30, 44, 48, 50) will now have access to `GH_TOKEN`

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to affected workflow files
   - Restore `cli/cli-action@v2` setup steps
   - Remove `GH_TOKEN` environment variables
   - Verify workflows return to working state

2. **Partial Rollback**
   - If only specific jobs fail, revert only those changes
   - Investigate why specific jobs fail without the action
   - Consider job-specific solutions or token permission issues

3. **Alternative Approach**
   - If `GH_TOKEN` environment variable doesn't work, consider:
     - Using `gh auth login --with-token` with a heredoc to authenticate
     - Verifying that `secrets.GITHUB_TOKEN` has sufficient permissions
     - Checking if job-level permissions need adjustment
     - Using explicit authentication: `echo "${{ secrets.GITHUB_TOKEN }}" | gh auth login --with-token`

### Implementation Order

1. **Start with `.github/workflows/pr-label.yml`** (lower risk, easier to test)
   - Remove `cli/cli-action@v2` setup step
   - Add `GH_TOKEN` environment variable to the step using `gh` commands
   - Test via pull request to verify label workflow still works
   - Monitor workflow logs to ensure authentication succeeds

2. **Test via pull request**
   - Create a test PR to verify pr-label.yml workflow works
   - Verify labels are applied correctly
   - Check workflow logs for authentication success

3. **Update `.github/workflows/release.yaml`**
   - Once pr-label.yml is verified, update release.yaml
   - Remove `cli/cli-action@v2` setup step from `version` job
   - Add `GH_TOKEN` environment variable to the step using `gh` commands
   - Test release workflow (can be done via test branch or after merge)

4. **Final verification**
   - Test release workflow end-to-end
   - Verify version calculation works correctly with `gh pr list` and `gh pr view`
   - Monitor workflow logs to ensure all GitHub CLI operations succeed

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:**
  - Workflows might fail if `GH_TOKEN` is not properly set or accessible
  - GitHub CLI commands might fail with authentication errors
  - Version calculation in release workflow might fail
  - PR labeling might fail
- **Mitigation:**
  - Easy rollback (just restore the action setup step)
  - GitHub CLI is pre-installed, so no installation issues
  - `secrets.GITHUB_TOKEN` is automatically available in all workflows
  - Can test incrementally via pull requests
  - Well-documented authentication method
- **Testing:**
  - Can be fully tested via pull request before affecting main branch
  - Each workflow can be tested independently
  - Authentication behavior can be verified through workflow logs
- **Dependencies:**
  - `secrets.GITHUB_TOKEN` must be available (standard in all workflows)
  - GitHub CLI must be available (pre-installed in runners)
  - Job-level permissions must allow `pull-requests: read` (already configured)
- **Permissions:**
  - Verify that `secrets.GITHUB_TOKEN` has sufficient permissions for:
    - Reading PRs (`pull-requests: read` - already configured)
    - Editing PRs (`pull-requests: write` - already configured in pr-label.yml)
    - Reading contents (`contents: read` - already configured)

### Expected Outcomes

After successful implementation:

- **Simplified Workflows:** Removed unnecessary action dependency
- **Consistent Authentication:** All GitHub CLI operations use explicit `GH_TOKEN` environment variable
- **Better Maintainability:** No reliance on action's token handling behavior
- **Improved Performance:** Slight reduction in workflow overhead (removed action setup step)
- **Explicit Configuration:** Clear authentication method for all GitHub CLI operations
