# Bug: Release Notes Not Found During GitHub Release Creation

**Status**: ✅ Complete

## Description

The GitHub Release creation step fails because it cannot find the `release_notes.md` file. The file is generated in the wrong location - it's created in `.github/scripts/release-notes/` directory instead of the workspace root where the `gh release create` command expects it.

## Current State

**File**: `.github/workflows/release-build.yaml` (lines 200-232)

The release job workflow:

1. **Generate release notes step** (lines 200-208):
   ```yaml
   - name: Generate release notes
     id: release_notes
     env:
       GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
       GITHUB_REPOSITORY: ${{ github.repository }}
       GITHUB_REF_NAME: ${{ github.ref_name }}
     run: |
       cd .github/scripts/release-notes
       uv run python -m release_notes
   ```

2. **Create GitHub Release step** (lines 224-232):
   ```yaml
   - name: Create GitHub Release
     env:
       GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
     run: |
       gh release create "${{ github.ref_name }}" \
         --title "Release ${{ github.ref_name }}" \
         --notes-file release_notes.md \
         --verify-tag \
         artifacts/*
   ```

**File**: `.github/scripts/release-notes/src/release_notes/__main__.py` (lines 100-103)

The Python script writes the release notes file using a relative path:
```python
# Write to release_notes.md file
output_file = Path("release_notes.md")
with output_file.open("w") as f:
    f.write(release_notes)
```

## Root Cause

The issue is a **working directory mismatch**:

1. The workflow step changes directory to `.github/scripts/release-notes` before running the Python script
2. The Python script creates `release_notes.md` using a relative path (`Path("release_notes.md")`)
3. Since the script runs from `.github/scripts/release-notes/`, the file is created at `.github/scripts/release-notes/release_notes.md`
4. The `gh release create` command runs from the workspace root and expects `release_notes.md` at the root level
5. The file is not found, causing the error: `open release_notes.md: no such file or directory`

## Expected State

The release notes file should be created at the workspace root (`release_notes.md`) so that the `gh release create` command can find it when using `--notes-file release_notes.md`.

## Solution

There are several possible approaches to fix this:

### Option 1: Write to absolute path in Python script ✅ **RECOMMENDED**

Modify the Python script to write the file to the workspace root using an absolute path with a recursive function to find the workspace root:

**File**: `.github/scripts/release-notes/src/release_notes/__main__.py`

**Before** (line 101):
```python
output_file = Path("release_notes.md")
```

**After** - Add helper functions before `main()`:
```python
def find_workspace_root(start_path: Path) -> Path | None:
    """
    Recursively traverse up the directory tree to find the workspace root.

    Looks for Cargo.toml as a marker file indicating the workspace root.
    Stops at filesystem root if not found.

    Args:
        start_path: Starting directory path to begin search from

    Returns:
        Path to workspace root directory if found, None otherwise
    """
    start_path = start_path.resolve()

    # Check if Cargo.toml exists in current directory
    cargo_toml = start_path / "Cargo.toml"
    if cargo_toml.exists():
        return start_path

    # Base case: reached filesystem root
    parent = start_path.parent
    if parent == start_path:  # At root directory (e.g., / on Unix, C:\ on Windows)
        return None

    # Recursive case: traverse up one level
    return find_workspace_root(parent)


def get_workspace_root() -> Path:
    """
    Get the workspace root directory.

    Priority:
    1. GITHUB_WORKSPACE environment variable (automatically set by GitHub Actions)
    2. Recursively find workspace root by traversing up from script location looking for Cargo.toml

    Returns:
        Path to workspace root directory

    Raises:
        RuntimeError: If workspace root cannot be determined
    """
    # First, try GITHUB_WORKSPACE (automatically set by GitHub Actions)
    workspace_env = os.environ.get("GITHUB_WORKSPACE")
    if workspace_env:
        workspace_path = Path(workspace_env)
        if workspace_path.exists() and workspace_path.is_dir():
            return workspace_path.resolve()
        print(
            f"Warning: GITHUB_WORKSPACE points to non-existent directory: {workspace_env}",
            file=sys.stderr
        )

    # Fallback: Recursively find workspace root from script location
    script_file = Path(__file__).resolve()
    workspace_root = find_workspace_root(script_file.parent)

    if workspace_root is None:
        raise RuntimeError(
            f"Could not determine workspace root. "
            f"Traversed up from {script_file} but could not find Cargo.toml. "
            f"Set GITHUB_WORKSPACE environment variable or ensure Cargo.toml exists in workspace root."
        )

    return workspace_root
```

**Then update the file writing code** (replace lines 100-103):
```python
# Write to release_notes.md file at workspace root
try:
    workspace_root = get_workspace_root()
    output_file = workspace_root / "release_notes.md"
    with output_file.open("w") as f:
        f.write(release_notes)
    print(f"   Release notes written to: {output_file}")
except RuntimeError as e:
    print(f"Error: {e}", file=sys.stderr)
    return 1
```

**Benefits of this approach:**
- Uses `__file__` instead of `Path.cwd()`, so it works regardless of current working directory
- Recursive function finds workspace root by traversing up looking for `Cargo.toml`
- No hardcoded path depths - works even if script is moved to different location
- Primary reliance on `GITHUB_WORKSPACE` (automatically set by GitHub Actions)
- Clear error handling with helpful error messages
- Resilient to script relocation, working directory changes, and different project structures

### Option 2: Change workflow to not cd into directory

Modify the workflow to run the script without changing directory:

**File**: `.github/workflows/release-build.yaml`

**Before** (lines 206-208):
```yaml
run: |
  cd .github/scripts/release-notes
  uv run python -m release_notes
```

**After**:
```yaml
run: |
  cd .github/scripts/release-notes
  uv run python -m release_notes
  # Move file to workspace root
  mv release_notes.md ../../release_notes.md || true
```

Or:
```yaml
run: |
  uv run --directory .github/scripts/release-notes python -m release_notes
  # Copy file from script directory to workspace root
  cp .github/scripts/release-notes/release_notes.md release_notes.md || true
```

### Option 3: Update gh command to use correct path

Change the `gh release create` command to look for the file in the correct location:

**File**: `.github/workflows/release-build.yaml`

**Before** (line 230):
```yaml
--notes-file release_notes.md \
```

**After**:
```yaml
--notes-file .github/scripts/release-notes/release_notes.md \
```

**Note**: This is less ideal as it couples the workflow to the script's internal directory structure.

### Option 4: Use GITHUB_WORKSPACE environment variable

The workflow can pass the workspace root to the script and use it:

**File**: `.github/workflows/release-build.yaml`

**Before** (lines 202-205):
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  GITHUB_REPOSITORY: ${{ github.repository }}
  GITHUB_REF_NAME: ${{ github.ref_name }}
```

**After**:
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  GITHUB_REPOSITORY: ${{ github.repository }}
  GITHUB_REF_NAME: ${{ github.ref_name }}
  GITHUB_WORKSPACE: ${{ github.workspace }}
```

Then in the Python script:
```python
workspace_root = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd().parent.parent.parent))
output_file = workspace_root / "release_notes.md"
```

## Recommended Solution

**Option 1** ✅ **SELECTED** - This option has been selected for implementation.

**Option 1** is recommended because:
- It fixes the issue at the source (the script that creates the file)
- It's the most robust solution (works regardless of where the script is run from or where it's located)
- It doesn't require workflow changes
- It makes the script's behavior explicit and predictable
- Uses `__file__` to determine script location, independent of current working directory
- Recursively finds workspace root by traversing up looking for `Cargo.toml` marker file
- No hardcoded path depths, making it resilient to script relocation

The script should write to an absolute path based on the workspace root, using a recursive function to find the workspace root by looking for `Cargo.toml`. This ensures the file is always created in the correct location, regardless of the current working directory or script location.

## Impact

- **Severity**: High (blocks release creation)
- **Priority**: High (prevents releases from being created)

**Consequences**:
1. GitHub Releases cannot be created automatically
2. Release workflow fails at the final step
3. Manual intervention required to create releases
4. Release artifacts are built but not published

## Affected Files

- `.github/workflows/release-build.yaml`
  - May need to pass `GITHUB_WORKSPACE` environment variable (if using Option 4)
  - May need to add file copy/move step (if using Option 2)
  - May need to update `--notes-file` path (if using Option 3)

- `.github/scripts/release-notes/src/release_notes/__main__.py`
  - Update `output_file` path to write to workspace root (Option 1 or 4)

## Verification

After fixing the configuration:
1. Verify the release notes file is created at the workspace root (`release_notes.md`)
2. Check that the `gh release create` command can find the file
3. Verify the release is created successfully with the notes
4. Confirm the release notes content is correct

## Investigation Notes

The script currently uses a relative path, which means the file location depends on the current working directory. When the workflow changes directory to `.github/scripts/release-notes` before running the script, the file is created in that subdirectory instead of the workspace root.

The `GITHUB_WORKSPACE` environment variable is automatically set by GitHub Actions and points to the workspace root, making it the ideal reference point for absolute paths.

## Status

🟡 **IN PROGRESS** - Option 1 selected, implementation plan created
