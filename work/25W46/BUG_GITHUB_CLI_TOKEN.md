# Implementation Plan: BUG_GITHUB_CLI_TOKEN

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_GITHUB_CLI_TOKEN.md`.

## Context

Related bug report: `plan/25W46/BUG_GITHUB_CLI_TOKEN.md`

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
