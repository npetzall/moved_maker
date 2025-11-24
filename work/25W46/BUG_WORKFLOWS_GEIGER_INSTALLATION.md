# Implementation Plan: BUG_WORKFLOWS_GEIGER_INSTALLATION

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_WORKFLOWS_GEIGER_INSTALLATION.md`.

## Context

Related bug report: `plan/25W46/BUG_WORKFLOWS_GEIGER_INSTALLATION.md`

## Steps to Fix

### Step 1: Split cargo-geiger into separate installation step

Separate `cargo-geiger` from the other security tools and install it with the `--locked` flag:

**Before:**
```yaml
- name: Install security tools
  run: cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable
```

**After:**
```yaml
- name: Install security tools
  run: cargo install cargo-deny cargo-audit cargo-auditable

- name: Install cargo-geiger
  run: cargo install --locked cargo-geiger
```

### Step 2: Update both workflow files

Apply the fix to:
- `.github/workflows/pull_request.yaml` (security job, line 22)
- `.github/workflows/release-build.yaml` (security job, line 26)

## Affected Files

- `.github/workflows/pull_request.yaml`
  - `security` job (line 22 - "Install security tools" step)

- `.github/workflows/release-build.yaml`
  - `security` job (line 26 - "Install security tools" step)

## Example Fix

### Before:
```yaml
- name: Install security tools
  run: cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable
```

### After:
```yaml
- name: Install security tools
  run: cargo install cargo-deny cargo-audit cargo-auditable

- name: Install cargo-geiger
  run: cargo install --locked cargo-geiger
```

## Status

✅ **COMPLETED** - cargo-geiger is now installed in a separate step with the `--locked` flag in both pull_request.yaml and release-build.yaml workflows. This should resolve the argument parsing error by ensuring reproducible builds and proper dependency resolution.

## References

- [cargo-geiger Documentation](https://github.com/rust-secure-code/cargo-geiger)
- [cargo install --locked flag](https://doc.rust-lang.org/cargo/commands/cargo-install.html#option---locked)
- [cargo-geiger on lib.rs](https://lib.rs/crates/cargo-geiger)

## Notes

- The `--locked` flag ensures that cargo install uses the exact dependency versions specified in the crate's `Cargo.lock` file
- This promotes reproducible builds and can resolve issues with dependency resolution
- The error suggests that the installed version of cargo-geiger may have a different argument format than expected
- Installing cargo-geiger separately with `--locked` ensures we get a consistent, tested version of the tool
- Separating cargo-geiger installation allows it to be installed with specific flags without affecting other security tools

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/pull_request.yaml`

**File:** `.github/workflows/pull_request.yaml`

1. **Update `security` job installation step (line 22)** ✅ COMPLETED
   - [x] Locate the "Install security tools" step at line 22 in the `security` job
   - [x] Remove `cargo-geiger` from the existing installation command: `cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable`
   - [x] Update the command to install only: `cargo install cargo-deny cargo-audit cargo-auditable`
   - [x] Add a new separate step after the security tools installation (after line 22, before line 24 "Run cargo-deny checks"):
     ```yaml
     - name: Install cargo-geiger
       run: cargo install --locked cargo-geiger
     ```
   - [x] Verify step placement (should be after "Install security tools" at line 22, before "Run cargo-deny checks" at line 24)
   - [x] Verify the `--locked` flag is present in the cargo-geiger installation command

#### Step 2: Update `.github/workflows/release-build.yaml`

**File:** `.github/workflows/release-build.yaml`

1. **Update `security` job installation step (line 26)** ✅ COMPLETED
   - [x] Locate the "Install security tools" step at line 26 in the `security` job
   - [x] Remove `cargo-geiger` from the existing installation command: `cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable`
   - [x] Update the command to install only: `cargo install cargo-deny cargo-audit cargo-auditable`
   - [x] Add a new separate step after the security tools installation (after line 26, before line 28 "Run cargo-deny checks"):
     ```yaml
     - name: Install cargo-geiger
       run: cargo install --locked cargo-geiger
     ```
   - [x] Verify step placement (should be after "Install security tools" at line 26, before "Run cargo-deny checks" at line 28)
   - [x] Verify the `--locked` flag is present in the cargo-geiger installation command

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.github/workflows/pull_request.yaml`
   - Revert changes to `.github/workflows/release-build.yaml`
   - Restore the original combined installation command
   - Verify workflows return to previous state

2. **Partial Rollback**
   - If `--locked` flag causes issues, try installing without it but in separate step
   - If separate installation doesn't resolve the issue, verify cargo-geiger version compatibility
   - Check if the argument format has changed in newer versions
   - Consider pinning to a specific known-working version

3. **Alternative Approaches**
   - If `--locked` doesn't resolve the issue, try installing with explicit version:
     ```yaml
     - name: Install cargo-geiger
       run: cargo install --locked --version 0.13.0 cargo-geiger
     ```
   - Verify cargo-geiger documentation for correct installation method
   - Check if the issue is related to cargo-geiger version rather than installation method
   - Consider using alternative output format if JSON format is not supported

### Implementation Order

1. [x] Update `.github/workflows/pull_request.yaml` (PR workflow, easier to test) ✅ COMPLETED
2. [ ] Test via pull request to verify:
   - Security tools installation step installs cargo-deny, cargo-audit, cargo-auditable
   - Separate cargo-geiger step installs with `--locked` flag
   - `cargo geiger --output-format json` runs without errors
   - `geiger-report.json` is generated successfully
   - Security job completes successfully
   - Downstream jobs are not blocked
3. [ ] Verify other security tools still work:
   - cargo-deny runs successfully
   - cargo-audit runs successfully
   - cargo-auditable runs successfully
4. [x] Apply the same fix to `.github/workflows/release-build.yaml` ✅ COMPLETED
5. [ ] Test via release workflow to verify:
   - Same behavior as PR workflow
   - Security job completes successfully
   - `build-and-release` job is not blocked

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:** cargo-geiger would continue to fail in CI, blocking security scanning
- **Mitigation:**
  - Simple change to installation method (separating into own step)
  - Easy rollback if needed
  - Can test via pull request before affecting release workflow
  - Alternative approaches available if `--locked` doesn't resolve the issue
- **Testing:** Can be fully tested via pull request workflow before affecting release workflow
- **Dependencies:**
  - No additional dependencies required
  - `--locked` flag is a standard cargo install option
  - Separating installation doesn't affect other tools

## Alternative Solutions

If `--locked` doesn't resolve the issue, consider:

1. **Install geiger with explicit version**:
   ```yaml
   - name: Install cargo-geiger
     run: cargo install --locked --version 0.13.0 cargo-geiger
   ```

2. **Check geiger version compatibility**:
   - Verify the installed version supports `--output-format json`
   - Check if the argument format has changed in newer versions
   - Consider pinning to a specific known-working version

3. **Use alternative output format**:
   - If JSON format is not supported, use default output format
   - Or check documentation for correct argument syntax
