# BUG: release-version workflow uses incorrect path to Cargo.toml

**Status**: ✅ Complete

## Description

The `release-version` workflow changes the working directory to `.github/scripts/release-version` before running the Python script, but the script attempts to read and update `Cargo.toml` using a relative path. Since `Cargo.toml` is located at the repository root, not in the script directory, the script will fail to find the file.

## Current State

✅ **FIXED** - Environment variable `CARGO_TOML_PATH` implemented to use absolute path.

**Previous (incorrect) state:**
- Workflow changes directory to `.github/scripts/release-version` before running the script
- Script uses relative path `"Cargo.toml"` which resolves to `.github/scripts/release-version/Cargo.toml`
- `Cargo.toml` is actually located at the repository root
- Script will fail with `FileNotFoundError: Cargo.toml not found at Cargo.toml`

**Current (correct) state:**
- Workflow sets `CARGO_TOML_PATH: ${{ github.workspace }}/Cargo.toml` environment variable
- Script reads `CARGO_TOML_PATH` from environment variable (defaults to `"Cargo.toml"` for local development)
- Script uses absolute path to locate and update `Cargo.toml` regardless of working directory
- Script passes repository root to `calculate_new_version()` for reading current version
- Script passes full Cargo.toml path to `update_cargo_version()` for updating

**Previous workflow step:**
```yaml
- name: Calculate version from PR labels
  id: version
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITHUB_REPOSITORY: ${{ github.repository }}
  run: |
    cd .github/scripts/release-version
    uv run python -m release_version
```

**Current workflow step:**
```yaml
- name: Calculate version from PR labels
  id: version
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITHUB_REPOSITORY: ${{ github.repository }}
    CARGO_TOML_PATH: ${{ github.workspace }}/Cargo.toml
  run: |
    cd .github/scripts/release-version
    uv run python -m release_version
```

**Previous script code (__main__.py):**
```python
update_cargo_version("Cargo.toml", version)  # Uses relative path
```

**Current script code (__main__.py):**
```python
# Get Cargo.toml path from environment or default
cargo_toml_path = os.environ.get("CARGO_TOML_PATH", "Cargo.toml")
repo_root = os.path.dirname(cargo_toml_path) or "."

# Calculate version (pass repo_root for reading current version)
version, tag_name = calculate_new_version(github_client, repo_path=repo_root)

# Update Cargo.toml (use full path)
update_cargo_version(cargo_toml_path, version)
```

**Script code (version.py):**
```python
def calculate_new_version(github_client, repo_path: str = ".") -> Tuple[str, str]:
    # ...
    cargo_path = f"{repo_path}/Cargo.toml" if repo_path != "." else "Cargo.toml"
    version = read_cargo_version(cargo_path)
```

The `calculate_new_version` function accepts a `repo_path` parameter, but `__main__.py` doesn't pass it, so it defaults to `"."` which becomes the current working directory (`.github/scripts/release-version`).

## Expected State

The script should correctly locate `Cargo.toml` at the repository root regardless of the current working directory.

**Chosen Solution: Environment Variable with Absolute Path**

- Workflow sets environment variable `CARGO_TOML_PATH` to `${{ github.workspace }}/Cargo.toml`
- Script reads `CARGO_TOML_PATH` from environment variable
- Script uses the absolute path to locate and update `Cargo.toml`
- This approach is explicit, testable, and doesn't require changing the workflow's working directory structure

## Impact

### Workflow Failure Impact
- **Severity**: Critical
- **Priority**: High

The workflow will fail every time it runs because:
- Script cannot find `Cargo.toml` file
- Version calculation fails
- No version bump occurs
- No release tag is created
- Release process is completely broken

### Developer Experience Impact
- **Severity**: High
- **Priority**: High

- Workflow failures are confusing without clear error messages
- Release process is non-functional
- Blocks all releases until fixed

## Root Cause

The workflow changes the working directory to the script directory for convenience (to run `uv run python -m release_version`), but the script uses relative paths that assume it's running from the repository root. The `calculate_new_version()` function has a `repo_path` parameter to handle this, but it's not being used by `__main__.py`.

## Affected Files

- `.github/workflows/release-version.yaml` (workflow file)
- `.github/scripts/release-version/src/release_version/__main__.py` (script entry point)
- `.github/scripts/release-version/src/release_version/cargo.py` (may need path parameter support)
- `.github/scripts/release-version/src/release_version/version.py` (already supports repo_path parameter)

## Investigation Summary

1. [x] Confirmed: Script fails when run from `.github/scripts/release-version` directory
2. [x] Verified: `calculate_new_version()` already supports `repo_path` parameter
3. [x] Chosen Solution: Environment variable `CARGO_TOML_PATH` with absolute path `${{ github.workspace }}/Cargo.toml`
4. [x] Testing: Implementation completed - ready for workflow testing

## Status

✅ **IMPLEMENTED** - Solution implemented: Using `CARGO_TOML_PATH` environment variable with `${{ github.workspace }}/Cargo.toml`. Code changes completed, ready for workflow testing.


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_VERSION_CARGO_TOML_PATH.md` for the detailed implementation plan.
