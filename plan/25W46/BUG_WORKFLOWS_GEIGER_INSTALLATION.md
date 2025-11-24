# BUG: cargo-geiger failing in CI due to installation method

**Status**: ✅ Complete

## Description

`cargo-geiger` is failing in CI workflows with a panic error when trying to parse the `--output-format json` argument. The error indicates that the argument parsing is failing, which may be due to the installation method. According to cargo-geiger documentation, it should be installed with the `--locked` argument to ensure reproducible builds and proper dependency resolution.

## Current State

✅ **FIXED** - `cargo-geiger` has been updated in both `.github/workflows/pull_request.yaml` and `.github/workflows/release-build.yaml` to be installed in a separate step with the `--locked` flag.

**Previous (broken) installation:**
```yaml
- name: Install security tools
  run: cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable
```

**Current (fixed) installation:**
```yaml
- name: Install security tools
  run: cargo install cargo-deny cargo-audit cargo-auditable

- name: Install cargo-geiger
  run: cargo install --locked cargo-geiger
```

The installation now:
- Separates `cargo-geiger` from other security tools
- Uses the `--locked` flag to ensure reproducible builds and proper dependency resolution
- Should resolve the argument parsing error that was causing the panic

**Note:** The geiger scan step was already fixed to be non-blocking (treats exit code 1 as OK) in a previous bug fix.

**Affected workflows:**
- `.github/workflows/pull_request.yaml` (lines 21-25 - installation steps)
- `.github/workflows/release-build.yaml` (lines 25-29 - installation steps)

## Expected State

`cargo-geiger` should be installed in its own separate step with the `--locked` flag to ensure:
1. Reproducible builds using exact dependency versions from Cargo.lock
2. Proper argument parsing and tool functionality
3. Consistent behavior across CI runs

The installation commands should be:
```yaml
- name: Install security tools
  run: cargo install cargo-deny cargo-audit cargo-auditable

- name: Install cargo-geiger
  run: cargo install --locked cargo-geiger
```

## Impact

### Functionality Impact
- **Severity**: High
- **Priority**: High

Current issues:
- `cargo-geiger` fails to run in CI workflows due to argument parsing error
- The `--output-format json` argument is not recognized by the installed version
- The installation method (without `--locked`) may be causing dependency resolution issues
- Security scanning job fails, potentially blocking downstream jobs
- Unable to generate geiger reports for review


## Related Implementation Plan

See `work/25W46/BUG_WORKFLOWS_GEIGER_INSTALLATION.md` for the detailed implementation plan.
