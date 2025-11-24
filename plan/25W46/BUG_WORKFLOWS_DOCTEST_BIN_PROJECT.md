# BUG: Workflows - Trying to run cargo test --doc for a bin project

**Status**: ✅ Complete

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


## Related Implementation Plan

See `work/25W46/BUG_WORKFLOWS_DOCTEST_BIN_PROJECT.md` for the detailed implementation plan.
