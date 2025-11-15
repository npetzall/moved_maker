# Bug: Pre-commit fail_fast configuration - should be false locally, true in CI

## Description

The `.pre-commit-config.yaml` currently has `fail_fast: true` set globally. This means that pre-commit stops on the first failure both locally and in CI. However, for better developer experience, `fail_fast` should be `false` locally (so developers can see all failures at once), but `true` in CI (to fail fast and save CI resources).

## Current State

✅ **FIXED** - The pre-commit fail_fast configuration has been updated to use different behavior for local vs CI.

**Previous (incorrect) configuration:**
- `.pre-commit-config.yaml` (line 7): `fail_fast: true` (applied to both local and CI)
- `.github/workflows/pull_request.yaml` (line 126): `pre-commit run --all-files` (no override)

**Current (correct) configuration:**
- `.pre-commit-config.yaml` (line 7): `fail_fast: false` (default for local development)
- `.github/workflows/pull_request.yaml` (line 126): `pre-commit run --all-files --fail-fast` (overrides for CI)

**Fixed files:**
- `.pre-commit-config.yaml` (line 7) - Changed `fail_fast: true` to `fail_fast: false`
- `.github/workflows/pull_request.yaml` (line 126) - Added `--fail-fast` flag to pre-commit command

## Expected State

1. **Local Development:**
   - `fail_fast: false` in `.pre-commit-config.yaml` (or default behavior)
   - All hooks run even if some fail, showing all failures at once
   - Better developer experience - can fix multiple issues in one iteration

2. **CI Environment:**
   - `fail_fast: true` when running in CI
   - Stops on first failure to save CI resources and time
   - Faster feedback in CI pipelines

## Impact

### Developer Experience Impact
- **Severity**: Medium
- **Priority**: Medium

When `fail_fast: true` is set locally:
- Developers must fix issues one at a time
- Multiple iterations needed to see all failures
- Slower development workflow
- Frustrating when multiple unrelated issues exist

### CI/CD Impact
- **Severity**: Low
- **Priority**: Low

Current CI behavior (fail_fast: true) is actually desired, but we need to differentiate between local and CI environments.

## Root Cause

Pre-commit's `fail_fast` setting is a global configuration in `.pre-commit-config.yaml` that applies to all environments. However, pre-commit provides a command-line flag `--fail-fast` that can override the config file setting, allowing different behavior in local vs CI environments.

## Investigation Results

### ✅ Solution: Command-Line Flag Override

**Investigation completed:** Pre-commit supports a `--fail-fast` command-line flag that overrides the config setting.

**Verification:**
- ✅ Verified: `--fail-fast` flag exists in pre-commit CLI (confirmed via `pre-commit run --help`)
- ✅ Flag overrides config file setting when used
- ✅ Works with current pre-commit version (minimum: 4.4.0)
- ✅ This is the standard, recommended approach per pre-commit documentation

**How it works:**
- The `fail_fast` setting in `.pre-commit-config.yaml` applies by default
- The `--fail-fast` command-line flag overrides the config file setting
- This allows setting `fail_fast: false` in config (for local) and using `--fail-fast` flag in CI

**Implementation:**
1. Update `.pre-commit-config.yaml`: Set `fail_fast: false` (default for local development)
2. Update `.github/workflows/pull_request.yaml`: Add `--fail-fast` flag to the pre-commit command

```bash
# Local (uses config: fail_fast: false)
pre-commit run --all-files

# CI (overrides with --fail-fast flag)
pre-commit run --all-files --fail-fast
```

**Why this approach:**
- ✅ Simple and clean - no environment variables needed
- ✅ No separate config files to maintain
- ✅ Standard pre-commit feature, well-documented
- ✅ Easy to understand and maintain

## Steps to Fix

### Implementation Steps

**Use the command-line flag approach:**

1. [x] **Update `.pre-commit-config.yaml`**
   - Change line 7 from `fail_fast: true` to `fail_fast: false`
   - This sets the default behavior for local development

2. [x] **Update `.github/workflows/pull_request.yaml`**
   - Modify line 126 to add `--fail-fast` flag
   - Change from: `pre-commit run --all-files`
   - Change to: `pre-commit run --all-files --fail-fast`
   - This overrides the config for CI to fail fast

3. [ ] **Test locally**
   - Create multiple pre-commit failures (e.g., formatting + linting issues)
   - Run `pre-commit run --all-files`
   - Verify all hooks run and all failures are shown (fail_fast: false behavior)

4. [ ] **Test in CI**
   - Create a PR with multiple pre-commit failures
   - Verify CI stops on first failure (fail_fast: true behavior via flag)
   - Confirm CI job fails quickly and shows only the first failure

### Verification

After implementation, verify:

1. [ ] **Local behavior** - All hooks run even if some fail (shows all failures)
2. [ ] **CI behavior** - Stops on first failure (saves CI resources)
3. [ ] **Documentation** - Update `TOOLING.md` if needed to document the fail_fast behavior

## Affected Files

- `.pre-commit-config.yaml` (line 7) - Change `fail_fast: true` to `fail_fast: false`
- `.github/workflows/pull_request.yaml` (line 126) - Add `--fail-fast` flag to pre-commit command

## References

- Pre-commit configuration documentation: https://pre-commit.com/#configuration
- Pre-commit CLI documentation: https://pre-commit.com/#cli
- Current pre-commit config: `.pre-commit-config.yaml`
- Current CI workflow: `.github/workflows/pull_request.yaml`
- Minimum pre-commit version: 4.4.0 (as specified in config)

## Status

✅ **FIXED** - Pre-commit fail_fast configuration has been updated. The `fail_fast: false` setting in `.pre-commit-config.yaml` provides better developer experience locally (shows all failures), while the `--fail-fast` flag in the CI workflow ensures CI fails fast to save resources.

## Recommended Fix

**File 1: `.pre-commit-config.yaml`**
```yaml
# Change line 7 from:
fail_fast: true
# To:
fail_fast: false
```

**File 2: `.github/workflows/pull_request.yaml`**
```yaml
# Change line 126 from:
- name: Run pre-commit
  run: pre-commit run --all-files
# To:
- name: Run pre-commit
  run: pre-commit run --all-files --fail-fast
```

This provides:
- **Local**: `fail_fast: false` - All hooks run, showing all failures
- **CI**: `--fail-fast` flag - Stops on first failure, saving CI resources

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.pre-commit-config.yaml`

**File:** `.pre-commit-config.yaml`

1. **Update `fail_fast` setting (line 7)**
   - [x] Locate the `fail_fast: true` setting at line 7
   - [x] Change from `fail_fast: true` to `fail_fast: false`
   - [x] Verify the change is on the correct line and indentation is correct
   - [x] Ensure no other `fail_fast` settings exist in the file

**Change to make:**
```yaml
# Line 7: Change from
fail_fast: true
# To
fail_fast: false
```

#### Step 2: Update `.github/workflows/pull_request.yaml`

**File:** `.github/workflows/pull_request.yaml`

1. **Update `pre-commit` job `Run pre-commit` step (line 126)**
   - [x] Locate the `pre-commit` job in the workflow
   - [x] Find the `Run pre-commit` step at line 126
   - [x] Update the command from `pre-commit run --all-files` to `pre-commit run --all-files --fail-fast`
   - [x] Verify the step name remains `Run pre-commit`
   - [x] Ensure proper YAML indentation is maintained

**Change to make:**
```yaml
# Line 126: Change from
- name: Run pre-commit
  run: pre-commit run --all-files
# To
- name: Run pre-commit
  run: pre-commit run --all-files --fail-fast
```

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.pre-commit-config.yaml` (restore `fail_fast: true`)
   - Revert changes to `.github/workflows/pull_request.yaml` (remove `--fail-fast` flag)
   - Verify workflows return to previous state

2. **Partial Rollback**
   - If CI fails unexpectedly, verify the `--fail-fast` flag syntax is correct
   - If local behavior is incorrect, verify `fail_fast: false` is set correctly in config
   - Check pre-commit version compatibility (minimum: 4.4.0)

3. **Alternative Approach**
   - If command-line flag doesn't work as expected, verify pre-commit version
   - Check pre-commit documentation for any version-specific flag behavior
   - Consider testing with `pre-commit run --help` to confirm flag availability

### Implementation Order

1. [x] Update `.pre-commit-config.yaml`: Change `fail_fast: true` to `fail_fast: false` (line 7)
2. [x] Update `.github/workflows/pull_request.yaml`: Add `--fail-fast` flag to pre-commit command (line 126)
3. [x] Verify YAML syntax is correct in both files
4. [ ] Create pull request to test changes in CI

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:**
  - If config change fails: Local behavior might not improve (still fail_fast: true)
  - If CI flag fails: CI might not fail fast (runs all hooks, uses more resources)
  - Both are non-breaking - worst case is current behavior maintained
- **Mitigation:**
  - Simple configuration change with minimal risk
  - Easy rollback if needed
  - Can test via pull request before affecting main branch
  - Changes are isolated to two files
  - Pre-commit flag is a standard feature, well-tested
- **Testing:** Can be fully tested via pull request before affecting main branch
- **Dependencies:**
  - Pre-commit version 4.4.0 or higher (already specified in config)
  - No additional tools or dependencies required
  - Standard pre-commit CLI feature

## Example Fix

### Before:

**`.pre-commit-config.yaml` (line 7):**
```yaml
fail_fast: true
```

**`.github/workflows/pull_request.yaml` (line 126):**
```yaml
- name: Run pre-commit
  run: pre-commit run --all-files
```

### After:

**`.pre-commit-config.yaml` (line 7):**
```yaml
fail_fast: false
```

**`.github/workflows/pull_request.yaml` (line 126):**
```yaml
- name: Run pre-commit
  run: pre-commit run --all-files --fail-fast
```
