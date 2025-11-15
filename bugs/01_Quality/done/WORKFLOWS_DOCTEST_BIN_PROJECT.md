# Bug: Workflows - Trying to run cargo test --doc for a bin project

## Description

The PR workflow `test` job attempts to run `cargo test --doc` (doctests), but this project is a binary project (has `src/main.rs`). Doctests can only be run for library projects (projects with `src/lib.rs` or `[lib]` section in `Cargo.toml`). Running `cargo test --doc` on a binary project will fail or have no effect.

## Current State

✅ **FIXED** - The doctest step has been removed from the workflow since this is a binary-only project.

**Previous (broken) workflow configuration:**
```yaml
- name: Run doctests
  run: cargo test --doc
```

**Current (fixed) workflow configuration:**
The doctest step has been removed. The test job now ends with the "Upload test results" step.

**Project structure:**
- `src/main.rs` exists (binary project)
- No `src/lib.rs` or `[lib]` section in `Cargo.toml`
- This is a binary-only project

## Expected State

The test job should not attempt to run doctests since this project is a binary project without a library component.

## Impact

### CI/CD Impact
- **Severity**: Low
- **Priority**: Low

The doctest step either:
- Fails (if cargo treats it as an error)
- Runs but does nothing (wastes CI time)
- May cause confusion about test coverage

### Functionality Impact
- **Severity**: None
- **Priority**: Low

No functional impact, but the step is unnecessary and should be removed.

## Root Cause

The workflow was likely copied from a library project template or added without checking if the project has a library component. Binary projects cannot have doctests because doctests are embedded in library documentation.

## Steps to Fix

Remove the doctest step from the workflow (currently at lines 70-71):

**Current workflow (test job) - lines 59-71:**
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

**Remove lines 70-71:**
```yaml
- name: Run doctests
  run: cargo test --doc
```

**Updated workflow (test job) - after fix:**
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

## Affected Files

- `.github/workflows/pull_request.yaml`
  - `test` job (removed lines 70-71)

## Verification

To verify this is a binary-only project:
1. Check `Cargo.toml` - no `[lib]` section
2. Check `src/` directory - `main.rs` exists, no `lib.rs`
3. Run `cargo test --doc` locally - should show no doctests or error

## Status

✅ **IMPLEMENTED** - Doctest step has been removed from workflow

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
