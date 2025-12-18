# BUG: Missing uv.lock files in Python projects

**Status**: ✅ Fixed

## Overview
Two Python projects in `.github/scripts/` are missing `uv.lock` files: `create-checksum/` and `test-summary/`. These projects have `pyproject.toml` files with dependencies but lack lock files for reproducible builds.

## Environment
- **OS**: All platforms (affects CI/CD and local development)
- **Python Version**: 3.13
- **Tool Version**: uv (package manager)
- **Terraform Version**: N/A

## Steps to Reproduce
1. Navigate to `.github/scripts/create-checksum/` or `.github/scripts/test-summary/`
2. Check for the presence of `uv.lock` file
3. Observe that the file is missing

## Expected Behavior
All Python projects in `.github/scripts/` that have `pyproject.toml` files with dependencies should have corresponding `uv.lock` files to ensure reproducible builds and consistent dependency versions across environments.

## Actual Behavior
The following projects are missing `uv.lock` files:
- `.github/scripts/create-checksum/` - has `pyproject.toml` with dev dependencies but no `uv.lock`
- `.github/scripts/test-summary/` - has `pyproject.toml` with dev dependencies but no `uv.lock`

Other projects correctly have `uv.lock` files:
- `.github/scripts/coverage-summary/` ✓
- `.github/scripts/pr-labels/` ✓
- `.github/scripts/release-notes/` ✓
- `.github/scripts/version/` ✓

## Error Messages / Output
N/A - This is a missing file issue, not a runtime error.

## Minimal Reproduction Case
```bash
cd .github/scripts/create-checksum
ls -la uv.lock  # File does not exist
```

## Additional Context
- **Affected files**:
  - `.github/scripts/create-checksum/` - missing `uv.lock`
  - `.github/scripts/test-summary/` - missing `uv.lock`
- **Root cause**: Lock files were not generated when these projects were created or dependencies were added
- **Impact**:
  - Inconsistent dependency versions across environments
  - Potential build failures in CI/CD if dependency versions change
  - Difficulty reproducing exact build environments
- **Frequency**: Always - these files are permanently missing
- **Workaround**: Manually run `uv lock` in each affected directory, but this should be automated

## Related Issues
- Related PRs: N/A
