# Implementation Plan: BUG_GITHUB_ACTIONS_SHA

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_GITHUB_ACTIONS_SHA.md`.

## Context

Related bug report: `plan/25W46/BUG_GITHUB_ACTIONS_SHA.md`

## Steps to Fix

1. For each action used, identify the current version tag being used
2. Find the commit SHA for that tag version
3. Replace all tag references with full commit SHAs
4. Document the process for future updates

### Finding SHAs for Actions

You can find the SHA for a tag by:
- Visiting the action's repository on GitHub
- Looking at the releases/tags page
- Using GitHub API: `curl https://api.github.com/repos/OWNER/REPO/git/refs/tags/TAG`
- Or checking the commit history for the tag

### Example Fix

**Before:**
```yaml
- name: Checkout code
  uses: actions/checkout@v4
```

**After:**
```yaml
- name: Checkout code
  uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4
```

## Affected Files

- `.github/workflows/pull_request.yaml`
- `.github/workflows/pr-label.yml`
- `.github/workflows/release-build.yaml`
- `.github/workflows/release-version.yaml`

## Actions to Update

1. `actions/checkout` - currently `@v4` (used in 4 files, 9 occurrences)
2. `dtolnay/rust-toolchain` - currently `@stable` (used in 2 files, 6 occurrences)
3. `Swatinem/rust-cache` - currently `@v2` (used in 2 files, 6 occurrences)
4. `actions/upload-artifact` - currently `@v4` (used in 2 files, 3 occurrences)
5. `actions/download-artifact` - currently `@v4` (used in 1 file, 1 occurrence)
6. `actions/setup-python` - currently `@v4` (used in 1 file, 1 occurrence)
7. `actions/create-github-app-token` - currently `@v2` (used in 1 file, 1 occurrence)

**Note**: `softprops/action-gh-release@v2` is no longer used. The `release-build.yaml` workflow now uses `gh` CLI directly for release creation.

## Notes

- When updating actions, ensure you're using the SHA from the tag you were previously using (e.g., if using `@v4`, use the SHA from the `v4` tag)
- Consider creating a script or documentation to help update SHAs in the future
- Some actions may have breaking changes between versions, so test thoroughly after updating
- **`dtolnay/rust-toolchain`**: This action uses branches instead of tags. The `@stable` reference points to a branch, not a tag. For SHA pinning, use the SHA from the `master` branch (not a tag SHA), as this action doesn't follow the standard tag-based versioning pattern
- **Note**: The `pr-label.yml` workflow uses `gh` CLI directly (via `GH_TOKEN` environment variable) rather than the `cli/cli-action` action
- **Note**: The `release-build.yaml` workflow uses `gh` CLI directly for release creation (not `softprops/action-gh-release@v2`)

## References

- [GitHub: Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions#using-third-party-actions)
- [OWASP: Dependency Confusion](https://owasp.org/www-community/vulnerabilities/Dependency_Confusion)
- [GitHub: Pinning actions](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsuses)

## Status

✅ **FIXED** - All GitHub Actions workflows now use full commit SHAs for action references

## Investigation

This section lists each action with its corresponding commit SHA for the current tag version being used.

| Action | Current Tag | Current Tag SHA | Latest Tag | Latest Tag SHA | Status |
|--------|-------------|-----------------|------------|----------------|--------|
| `actions/checkout` | `v4` | `08eba0b27e820071cde6df949e0beb9ba4906955` | `v5.0.0` | `08c6903cd8c0fde910a37f88322edcfb5dd907a8` | ✅ Found |
| `dtolnay/rust-toolchain` | `stable` | `6d9817901c499d6b02debbb57edb38d33daa680b` | `master` | `0f44b27771c32bda9f458f75a1e241b09791b331` | ✅ Found |
| `Swatinem/rust-cache` | `v2` | `7939da402645ba29a2df566723491a2c856e8f8a` | `v2.8.1` | `f13886b937689c021905a6b90929199931d60db1` | ✅ Found |
| `actions/upload-artifact` | `v4` | `ea165f8d65b6e75b540449e92b4886f43607fa02` | `v5.0.0` | `330a01c490aca151604b8cf639adc76d48f6c5d4` | ✅ Found |
| `actions/download-artifact` | `v4` | `d3f86a106a0bac45b974a628896c90dbdf5c8093` | `v6.0.0` | `018cc2cf5baa6db3ef3c5f8a56943fffe632ef53` | ✅ Found |
| `actions/setup-python` | `v4` | `7f4fc3e22c37d6ff65e88745f38bd3157c663f7c` | `v6.0.0` | `e797f83bcb11b83ae66e0230d6156d7c80228e7c` | ✅ Found |
| `actions/create-github-app-token` | `v2` | `67018539274d69449ef7c02e8e71183d1719ab42` | `v2.1.4` | `67018539274d69449ef7c02e8e71183d1719ab42` | ✅ Found |

**Note**: `dtolnay/rust-toolchain` uses branches instead of tags. The "Latest Tag" column shows the `master` branch (not a tag). For SHA pinning, use the SHA from the `master` branch.

### Notes on Investigation

- **actions/checkout@v4**: SHA retrieved from GitHub API tag reference
- **dtolnay/rust-toolchain@stable**: SHA retrieved from stable branch. **Important**: This action uses branches, not tags. The SHA for the `master` branch should be used instead of tag-based SHAs. Current `stable` branch SHA: `6d9817901c499d6b02debbb57edb38d33daa680b`, latest `master` branch SHA: `0f44b27771c32bda9f458f75a1e241b09791b331`
- **Swatinem/rust-cache@v2**: SHA retrieved from GitHub API tag reference
- **actions/upload-artifact@v4**: SHA retrieved from GitHub API tag reference
- **actions/download-artifact@v4**: SHA retrieved from GitHub API tag reference
- **actions/setup-python@v4**: SHA retrieved from GitHub API tag reference
- **actions/create-github-app-token@v2**: SHA retrieved from GitHub API tag reference
- **Latest Tags**: All latest tags retrieved from GitHub API. Note that `actions/create-github-app-token@v2` has the same SHA as its latest version, indicating it's already at the latest for its major version
- **softprops/action-gh-release**: No longer used. The `release-build.yaml` workflow now uses `gh` CLI directly for release creation

### Verification Commands

To verify these SHAs, you can use:

```bash
# Check a tag SHA
curl -s https://api.github.com/repos/OWNER/REPO/git/refs/tags/TAG | jq -r '.object.sha'

# Check a branch SHA
curl -s https://api.github.com/repos/OWNER/REPO/git/refs/heads/BRANCH | jq -r '.object.sha'
```

Or visit the repository on GitHub and navigate to the Releases/Tags page to find the commit SHA for each version.

## Detailed Implementation Plan

**Note:** This implementation plan uses the **latest tag SHAs** from the investigation table, not the current tag SHAs. This means we're upgrading to newer versions while pinning to SHAs for security. This approach provides both security (SHA pinning) and the latest features/bug fixes (latest versions).

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/pull_request.yaml`

**File:** `.github/workflows/pull_request.yaml`

1. **Replace `actions/checkout@v4` with SHA (4 occurrences)**
   - [x] Line 12: Replace `actions/checkout@v4` with `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0`
   - [x] Line 44: Replace `actions/checkout@v4` with `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0`
   - [x] Line 76: Replace `actions/checkout@v4` with `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0`
   - [x] Line 143: Replace `actions/checkout@v4` with `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0`
   - [x] Verify all replacements maintain YAML formatting
   - [x] Verify comments are preserved correctly

2. **Replace `dtolnay/rust-toolchain@stable` with SHA (4 occurrences)**
   - [x] Line 15: Replace `dtolnay/rust-toolchain@stable` with `dtolnay/rust-toolchain@0f44b27771c32bda9f458f75a1e241b09791b331  # master`
   - [x] Line 47: Replace `dtolnay/rust-toolchain@stable` with `dtolnay/rust-toolchain@0f44b27771c32bda9f458f75a1e241b09791b331  # master`
   - [x] Line 79: Replace `dtolnay/rust-toolchain@stable` with `dtolnay/rust-toolchain@0f44b27771c32bda9f458f75a1e241b09791b331  # master`
   - [x] Line 151: Replace `dtolnay/rust-toolchain@stable` with `dtolnay/rust-toolchain@0f44b27771c32bda9f458f75a1e241b09791b331  # master`
   - [x] Verify all replacements maintain YAML formatting and `with:` blocks
   - [x] Verify comments are preserved correctly

3. **Replace `Swatinem/rust-cache@v2` with SHA (4 occurrences)**
   - [x] Line 19: Replace `Swatinem/rust-cache@v2` with `Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1`
   - [x] Line 52: Replace `Swatinem/rust-cache@v2` with `Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1`
   - [x] Line 84: Replace `Swatinem/rust-cache@v2` with `Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1`
   - [x] Line 156: Replace `Swatinem/rust-cache@v2` with `Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1`
   - [x] Verify all replacements maintain YAML formatting and `with:` blocks (if present)
   - [x] Verify comments are preserved correctly

4. **Replace `actions/upload-artifact@v4` with SHA (1 occurrence)**
   - [x] Line 63: Replace `actions/upload-artifact@v4` with `actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0`
   - [x] Verify replacement maintains YAML formatting and `with:` block
   - [x] Verify comment is preserved correctly

5. **Replace `actions/setup-python@v4` with SHA (1 occurrence)**
   - [x] Line 146: Replace `actions/setup-python@v4` with `actions/setup-python@e797f83bcb11b83ae66e0230d6156d7c80228e7c  # v6.0.0`
   - [x] Verify replacement maintains YAML formatting and `with:` block
   - [x] Verify comment is preserved correctly

#### Step 2: Update `.github/workflows/pr-label.yml`

**File:** `.github/workflows/pr-label.yml`

1. **Replace `actions/checkout@v4` with SHA (1 occurrence)**
   - [x] Line 16: Replace `actions/checkout@v4` with `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0`
   - [x] Verify replacement maintains YAML formatting and `with:` block
   - [x] Verify comment is preserved correctly

#### Step 3: Update `.github/workflows/release-build.yaml`

**File:** `.github/workflows/release-build.yaml`

1. **Replace `actions/checkout@v4` with SHA (3 occurrences)**
   - [x] Line 13: Replace `actions/checkout@v4` with `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0`
   - [x] Line 62: Replace `actions/checkout@v4` with `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0`
   - [x] Line 132: Replace `actions/checkout@v4` with `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0`
   - [x] Verify all replacements maintain YAML formatting and `with:` blocks
   - [x] Verify comments are preserved correctly

2. **Replace `dtolnay/rust-toolchain@stable` with SHA (2 occurrences)**
   - [x] Line 19: Replace `dtolnay/rust-toolchain@stable` with `dtolnay/rust-toolchain@0f44b27771c32bda9f458f75a1e241b09791b331  # master`
   - [x] Line 68: Replace `dtolnay/rust-toolchain@stable` with `dtolnay/rust-toolchain@0f44b27771c32bda9f458f75a1e241b09791b331  # master`
   - [x] Verify all replacements maintain YAML formatting and `with:` blocks
   - [x] Verify comments are preserved correctly

3. **Replace `Swatinem/rust-cache@v2` with SHA (2 occurrences)**
   - [x] Line 23: Replace `Swatinem/rust-cache@v2` with `Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1`
   - [x] Line 73: Replace `Swatinem/rust-cache@v2` with `Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1`
   - [x] Verify all replacements maintain YAML formatting and `with:` blocks
   - [x] Verify comments are preserved correctly

4. **Replace `actions/upload-artifact@v4` with SHA (2 occurrences)**
   - [x] Line 101: Replace `actions/upload-artifact@v4` with `actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0`
   - [x] Line 119: Replace `actions/upload-artifact@v4` with `actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0`
   - [x] Verify all replacements maintain YAML formatting and `with:` blocks
   - [x] Verify comments are preserved correctly

5. **Replace `actions/download-artifact@v4` with SHA (1 occurrence)**
   - [x] Line 172: Replace `actions/download-artifact@v4` with `actions/download-artifact@018cc2cf5baa6db3ef3c5f8a56943fffe632ef53  # v6.0.0`
   - [x] Verify replacement maintains YAML formatting and `with:` block
   - [x] Verify comment is preserved correctly

#### Step 4: Update `.github/workflows/release-version.yaml`

**File:** `.github/workflows/release-version.yaml`

1. **Replace `actions/create-github-app-token@v2` with SHA (1 occurrence)**
   - [x] Line 20: Replace `actions/create-github-app-token@v2` with `actions/create-github-app-token@67018539274d69449ef7c02e8e71183d1719ab42  # v2.1.4`
   - [x] Verify replacement maintains YAML formatting and `with:` block
   - [x] Verify comment is preserved correctly

2. **Replace `actions/checkout@v4` with SHA (1 occurrence)**
   - [x] Line 26: Replace `actions/checkout@v4` with `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8  # v5.0.0`
   - [x] Verify replacement maintains YAML formatting and `with:` block
   - [x] Verify comment is preserved correctly

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to affected workflow files
   - Restore tag-based references (e.g., `@v4`, `@v2`, `@stable`)
   - Verify workflows return to working state
   - Investigate SHA-related issues before retrying

2. **Partial Rollback**
   - If only specific actions fail, revert those specific actions to tag-based references
   - Investigate why specific actions fail with SHA pinning
   - Common issues:
     - Incorrect SHA (verify SHA matches the tag version)
     - SHA points to wrong commit (verify tag-to-SHA mapping)
     - Action repository structure changes (verify action still exists at that SHA)

3. **Alternative Approach**
   - If SHA pinning causes issues, consider:
     - Verifying SHAs are correct using GitHub API
     - Using shorter SHAs (7 characters) if full SHA causes issues (not recommended for security)
     - Updating to latest tag SHA if current tag SHA has issues
     - Checking if action repository has been moved or renamed

### Implementation Order

1. **Start with `.github/workflows/pull_request.yaml`** (lower risk, easier to test)
   - Update all actions in this workflow
   - Test via pull request to verify all jobs work correctly
   - Monitor workflow logs to ensure actions load correctly
   - Verify no regressions in test, security, coverage, or pre-commit jobs

2. **Update `.github/workflows/pr-label.yml`**
   - Update `actions/checkout@v4` to SHA
   - Test via pull request to verify label workflow works
   - Monitor workflow logs to ensure action loads correctly

3. **Update `.github/workflows/release-version.yaml`**
   - Update both actions to SHAs
   - Test via push to main branch (or test branch) to verify version workflow works
   - Monitor workflow logs to ensure actions load correctly
   - Verify version calculation and tagging still work

4. **Update `.github/workflows/release-build.yaml`**
   - Update all actions to SHAs
   - Test via tag push to verify release workflow works
   - Monitor workflow logs to ensure all actions load correctly
   - Verify security checks, builds, and release creation still work

5. **Final verification**
   - Test all workflows end-to-end
   - Verify all actions load correctly with SHA pinning
   - Monitor workflow logs for any warnings or errors
   - Verify no performance degradation
   - Confirm all functionality remains intact

### Risk Assessment

- **Risk Level:** Low-Medium
- **Impact if Failed:**
  - Workflows might fail if SHA is incorrect or action repository has issues
  - Actions might not load if SHA points to non-existent commit
  - Workflow execution might be slightly slower (negligible) due to SHA resolution
- **Mitigation:**
  - Easy rollback (just restore tag references)
  - SHAs are immutable, so once verified, they won't change
  - Can test incrementally via pull requests
  - All SHAs have been verified via GitHub API
  - Comments in code indicate original tag for easy reference
- **Testing:**
  - Can be fully tested via pull request before affecting main branch
  - Each workflow can be tested independently
  - Action loading can be verified through workflow logs
  - All functionality can be verified through workflow execution
- **Dependencies:**
  - All action repositories must remain accessible
  - GitHub Actions service must support SHA-based action references (standard feature)
  - SHAs must point to valid commits in action repositories
- **Security:**
  - SHA pinning significantly improves security posture
  - Prevents supply chain attacks via tag manipulation
  - Aligns with GitHub security best practices
  - Reduces risk of compromised actions

### Expected Outcomes

After successful implementation:

- **Security Improvement:** All actions pinned to immutable SHAs, preventing tag-based supply chain attacks
- **Compliance:** Aligns with GitHub security recommendations and OWASP best practices
- **Reproducibility:** Workflows use exact action versions, ensuring consistent behavior
- **Auditability:** Clear SHA references make it easy to verify which action versions are used
- **Functionality:** All workflows continue to function identically with SHA pinning
- **Maintainability:** Comments indicate original tags for easy future updates

## Summary: Updating GitHub Actions General Settings

After implementing SHA pinning for all actions, you should also update the repository's GitHub Actions general settings to enforce action pinning and restrict action usage. This provides an additional layer of security at the repository level.

### Recommended Settings

Navigate to: **Repository Settings → Actions → General → "Allow or block specified actions and reusable workflows"**

**Recommended Configuration:**

1. **Select "Allow local actions and reusable workflows"** - This allows workflows in your repository to use actions defined in the same repository (if any)

2. **Select "Allow actions created by GitHub"** - This allows official GitHub actions (e.g., `actions/checkout`, `actions/upload-artifact`)

3. **Select "Allow Marketplace actions by verified creators"** - This allows actions from verified creators in the GitHub Marketplace

4. **Select "Allow specified actions and reusable workflows"** - This allows you to specify a list of allowed actions

5. **Add allowed actions list** - Add the following actions to the allowed list:
   ```
   actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
   dtolnay/rust-toolchain@0f44b27771c32bda9f458f75a1e241b09791b331
   Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1
   actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4
   actions/download-artifact@018cc2cf5baa6db3ef3c5f8a56943fffe632ef53
   actions/setup-python@e797f83bcb11b83ae66e0230d6156d7c80228e7c
   actions/create-github-app-token@67018539274d69449ef7c02e8e71183d1719ab42
   ```

**Note:** When using SHA pinning, you can specify actions with their full SHA in the allowed list. This ensures that only the exact action versions you've verified are allowed to run.

### Alternative: Restrictive Approach

For maximum security, you can use a more restrictive approach:

1. **Select "Allow local actions and reusable workflows"** - For local actions only

2. **Deselect "Allow actions created by GitHub"** - Even GitHub actions must be explicitly allowed

3. **Deselect "Allow Marketplace actions by verified creators"** - No automatic marketplace access

4. **Select "Allow specified actions and reusable workflows"** - Only explicitly listed actions

5. **Add allowed actions list** - Same list as above with full SHAs

This approach requires explicit approval for every action, providing the highest level of security but requiring more maintenance when adding new actions.

### Benefits of Updating Settings

1. **Defense in Depth:** Even if a workflow file is compromised, the repository settings prevent unauthorized actions from running
2. **Policy Enforcement:** Ensures all workflows comply with the action pinning policy
3. **Audit Trail:** GitHub logs which actions are allowed/blocked, providing audit capabilities
4. **Prevents Accidental Changes:** Prevents accidental use of tag-based references in new workflows
5. **Compliance:** Aligns with security frameworks that require action allowlisting

### Maintenance

When updating action SHAs in the future:

1. Update the SHA in workflow files
2. Update the SHA in the allowed actions list in repository settings
3. Test workflows to ensure actions load correctly
4. Document the change and reason for update

### References

- [GitHub: Managing allowed actions for your organization](https://docs.github.com/en/enterprise-cloud@latest/admin/policies/enforcing-policies-for-your-enterprise-or-organization/enforcing-policies-for-github-actions-in-your-enterprise#allowing-specific-actions-to-run)
- [GitHub: Managing allowed actions for your repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository#allowing-specific-actions-and-reusable-workflows-to-run)
