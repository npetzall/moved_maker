# Bug: Workflow - pre-commit fails, local hooks expect software to be installed

## Description

The PR workflow `pre-commit` job fails because the pre-commit hooks require additional software to be installed (`cargo-nextest`, `cargo-deny`, `cargo-audit`), but the workflow does not install these dependencies before running `pre-commit run --all-files`.

## Current State

✅ **FIXED** - The pre-commit workflow job now installs all required tools before running pre-commit hooks.

**Previous (incorrect) configuration:**
```yaml
- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

**Current (correct) configuration:**
```yaml
- name: Install pre-commit dependencies
  run: cargo install cargo-nextest cargo-deny cargo-audit
```

**Fixed files:**
- `.github/workflows/pull_request.yaml` (line 162) - Replaced single tool installation with combined installation step

**Pre-commit hooks that require additional tools (from `.pre-commit-config.yaml`):**
- `cargo-nextest` - ✅ Installed (line 162)
- `cargo-deny` - ✅ Installed (line 162)
- `cargo-audit` - ✅ Installed (line 162)
- `cargo-fmt` - ✅ Available via rustfmt component
- `cargo-check` - ✅ Available via cargo
- `cargo-clippy` - ✅ Available via clippy component
- `git-sumi` - ✅ Handled automatically by pre-commit (from external repo)
- `ripsecrets` - ✅ Handled automatically by pre-commit (from external repo)

## Expected State

The pre-commit job should:
1. Install all required tools before running pre-commit
2. Successfully run all pre-commit hooks
3. Pass if all checks pass, fail if any check fails

## Impact

### CI/CD Impact
- **Severity**: High
- **Priority**: High

The pre-commit job fails completely, preventing:
- Pre-commit checks from running in CI
- Code quality validation
- Security scanning
- Commit message validation

### Functionality Impact
- **Severity**: Medium
- **Priority**: Medium

Pre-commit hooks cannot run, so code quality and security checks are not enforced in CI.

## Root Cause

The workflow installs `cargo-nextest` but does not install other required tools:
- `cargo-deny` - Required by `cargo-deny` hook
- `cargo-audit` - Required by `cargo-audit` hook
- `git-sumi` - Handled automatically by pre-commit (from external repo)
- `ripsecrets` - Handled automatically by pre-commit (from external repo)

## Steps to Fix

Add installation steps for all required tools before running pre-commit:

```yaml
- name: Install cargo-nextest
  run: cargo install cargo-nextest

- name: Install cargo-deny
  run: cargo install cargo-deny

- name: Install cargo-audit
  run: cargo install cargo-audit

- name: Run pre-commit
  run: pre-commit run --all-files
```

**Alternative: Install all tools in one step:**
```yaml
- name: Install pre-commit dependencies
  run: cargo install cargo-nextest cargo-deny cargo-audit
```

**Note:** `git-sumi` and `ripsecrets` are handled automatically by pre-commit when the hooks run (they come from external repos), so they don't need to be installed manually.

## Affected Files

- `.github/workflows/pull_request.yaml`
  - `pre-commit` job (lines 139-166)

## Investigation Needed

1. Verify which tools are actually required by checking pre-commit hook failures
2. ✅ Confirmed: `git-sumi` and `ripsecrets` are handled automatically by pre-commit (from external repos)
3. Check if any tools can be installed via GitHub Actions instead of cargo install

## Status

✅ **FIXED** - Pre-commit job now installs all required tool dependencies before running hooks

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/pull_request.yaml`

**File:** `.github/workflows/pull_request.yaml`

1. **Update `pre-commit` job (lines 139-167)**
   - [x] Locate the `pre-commit` job starting at line 139
   - [x] Find the existing `Install cargo-nextest` step (line 162)
   - [x] Replace the single tool installation step:
     ```yaml
     - name: Install cargo-nextest
       run: cargo install cargo-nextest
     ```
   - [x] With the combined installation step:
     ```yaml
     - name: Install pre-commit dependencies
       run: cargo install cargo-nextest cargo-deny cargo-audit
     ```
   - [x] Verify step placement (should be after `Install pre-commit` step, before `Run pre-commit` step)
   - [x] Ensure the step is placed after Rust installation and rust-cache setup
   - [x] Verify all required tools are included: `cargo-nextest`, `cargo-deny`, `cargo-audit`

2. **Verify pre-commit hook configuration**
   - [x] Check `.pre-commit-config.yaml` to confirm all hooks that require these tools
   - [x] Verify `ripsecrets` is handled automatically by pre-commit (from external repo)
   - [x] Verify `git-sumi` is handled automatically by pre-commit (from external repo)
   - [x] Confirm that only `cargo-nextest`, `cargo-deny`, and `cargo-audit` need manual installation

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.github/workflows/pull_request.yaml`
   - Restore the original `Install cargo-nextest` step
   - Verify workflows return to previous state (even if broken, for reference)

2. **Partial Rollback**
   - If specific tools fail to install, try installing them individually:
     ```yaml
     - name: Install cargo-nextest
       run: cargo install cargo-nextest
     - name: Install cargo-deny
       run: cargo install cargo-deny
     - name: Install cargo-audit
       run: cargo install cargo-audit
     ```
   - If `cargo-audit` fails, check if it requires additional setup (e.g., vulnerability database update)
   - If `cargo-deny` fails, verify configuration file exists at `.config/deny.toml`

3. **Alternative Approach**
   - If combined installation is too slow or fails, split into separate steps with error handling:
     ```yaml
     - name: Install pre-commit dependencies
       run: |
         cargo install cargo-nextest cargo-deny cargo-audit || {
           echo "Combined install failed, trying individual installs"
           cargo install cargo-nextest
           cargo install cargo-deny
           cargo install cargo-audit
         }
     ```
   - Consider caching installed binaries if installation time becomes an issue
   - Verify `ripsecrets` and `git-sumi` installation if pre-commit fails to install them automatically (though they should be handled by pre-commit)

### Implementation Order

1. [x] Start with `.github/workflows/pull_request.yaml` `pre-commit` job (only affected file)
2. [x] Replace `Install cargo-nextest` step with combined `Install pre-commit dependencies` step
3. [x] Verify step placement and indentation are correct
4. ⏳ Test via pull request to verify all tools install correctly - Awaiting CI verification
5. ⏳ Verify pre-commit job passes with all hooks running successfully - Awaiting CI verification
6. ⏳ Confirm `cargo-deny` hook runs (requires `.config/deny.toml`) - Awaiting CI verification
7. ⏳ Confirm `cargo-audit` hook runs (may require vulnerability database update) - Awaiting CI verification
8. ⏳ Verify `git-sumi` hook runs (handled automatically by pre-commit, requires `.config/sumi.toml`) - Awaiting CI verification
9. ⏳ Verify `ripsecrets` hook runs (handled automatically by pre-commit) - Awaiting CI verification
10. ⏳ Verify all other hooks continue to work (cargo-fmt, cargo-check, cargo-clippy, cargo-test) - Awaiting CI verification

### Risk Assessment

- **Risk Level:** Low to Medium
- **Impact if Failed:** Pre-commit job would still fail, but with clearer error messages about which specific tool failed to install
- **Mitigation:**
  - Easy rollback to individual installation steps if combined approach fails
  - Can test via pull request before affecting main branch
  - Individual tools can be verified separately if needed
  - `ripsecrets` and `git-sumi` are handled by pre-commit automatically, reducing risk
- **Testing:** Can be fully tested via pull request before affecting main branch
- **Dependencies:**
  - All tools must be available on crates.io
  - `cargo-audit` may require vulnerability database update before first use
  - `cargo-deny` requires `.config/deny.toml` configuration file
  - `git-sumi` requires `.config/sumi.toml` configuration file (but is installed automatically by pre-commit)
- **Performance Considerations:**
  - Combined installation may be faster than individual installations (single cargo invocation)
  - Installation time depends on tool sizes and network speed
  - Consider caching if installation becomes a bottleneck

## Example Fix

### Before:
```yaml
- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

### After:
```yaml
- name: Install pre-commit dependencies
  run: cargo install cargo-nextest cargo-deny cargo-audit
```

## References

- Pre-commit hooks configuration: `.pre-commit-config.yaml`
- Current workflow: `.github/workflows/pull_request.yaml` (lines 139-167)
- Cargo deny configuration: `.config/deny.toml`
- Git sumi configuration: `.config/sumi.toml` (if exists)
- Pre-commit documentation: https://pre-commit.com/
- Cargo install documentation: https://doc.rust-lang.org/cargo/commands/cargo-install.html
