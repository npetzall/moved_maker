# Implementation Plan: BUG_WORKFLOWS_DOCTEST_BIN_PROJECT

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_WORKFLOWS_DOCTEST_BIN_PROJECT.md`.

## Context

Related bug report: `plan/25W46/BUG_WORKFLOWS_DOCTEST_BIN_PROJECT.md`

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/pull_request.yaml`

**File:** `.github/workflows/pull_request.yaml`

1. **Update `test` job (lines 59-71)**
   - [x] Locate the `test` job starting at line 36
   - [x] Find the "Run doctests" step at lines 70-71
   - [x] Remove the doctest step:
     ```yaml
     - name: Run doctests
       run: cargo test --doc
     ```
   - [x] Verify step placement (should be after "Upload test results" step)
   - [x] Verify the workflow ends with the "Upload test results" step after removal
   - [x] Ensure proper YAML indentation is maintained after removal

2. **Verify project structure**
   - [x] Confirm `Cargo.toml` has no `[lib]` section
   - [x] Confirm `src/main.rs` exists and `src/lib.rs` does not exist
   - [x] Verify this is a binary-only project

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.github/workflows/pull_request.yaml`
   - Restore the "Run doctests" step (even if it doesn't work, for reference)
   - Verify workflows return to previous state

2. **Partial Rollback**
   - If workflow syntax errors occur, verify YAML indentation
   - Check that no other steps were accidentally removed
   - Verify the workflow file is valid YAML

3. **Alternative Approaches**
   - If there's concern about removing the step, it could be conditionally disabled:
     ```yaml
     - name: Run doctests
       run: cargo test --doc
       continue-on-error: true
     ```
   - However, complete removal is preferred since it's unnecessary for binary projects

### Implementation Order

1. [x] Start with `.github/workflows/pull_request.yaml` `test` job (only affected file)
2. [x] Remove the "Run doctests" step (lines 70-71)
3. [x] Verify YAML syntax is valid
4. [x] Verify step placement and indentation are correct
5. [ ] Test via pull request to verify workflow runs successfully
6. [ ] Verify test job passes without the doctest step
7. [ ] Confirm no errors or warnings about missing doctest step
8. [ ] Verify test results are still uploaded correctly

### Risk Assessment

- **Risk Level:** Very Low
- **Impact if Failed:** Minimal - the doctest step doesn't work anyway, so removing it can't break functionality
- **Mitigation:**
  - Simple change (removing 2 lines)
  - Easy rollback if needed
  - Can test via pull request before affecting main branch
  - No dependencies on other changes
  - YAML validation can catch syntax errors immediately
- **Testing:** Can be fully tested via pull request before affecting main branch
- **Dependencies:** None - this is a standalone change

## Example Fix

### Before:
```yaml
- name: Run tests
  run: cargo nextest run

- name: Upload test results
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: test-results-${{ matrix.os }}
    path: target/nextest/**/test-results.xml
    if-no-files-found: warn

- name: Run doctests
  run: cargo test --doc
```

### After:
```yaml
- name: Run tests
  run: cargo nextest run

- name: Upload test results
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: test-results-${{ matrix.os }}
    path: target/nextest/**/test-results.xml
    if-no-files-found: warn
```

## References

- Current workflow: `.github/workflows/pull_request.yaml` (lines 70-71)
- Project structure: `Cargo.toml` (no `[lib]` section), `src/main.rs` exists
- Cargo documentation: Doctests are only available for library projects
- GitHub Actions workflow syntax: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
