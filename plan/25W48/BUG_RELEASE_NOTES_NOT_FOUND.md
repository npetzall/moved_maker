# Bug: Release Notes Not Found During GitHub Release Creation

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

Modify the Python script to write the file to the workspace root using an absolute path:

**File**: `.github/scripts/release-notes/src/release_notes/__main__.py`

**Before** (line 101):
```python
output_file = Path("release_notes.md")
```

**After**:
```python
# Get workspace root from GITHUB_WORKSPACE or use absolute path
workspace_root = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd().parent.parent.parent))
output_file = workspace_root / "release_notes.md"
```

Or use a more robust approach:
```python
# Get workspace root - go up from .github/scripts/release-notes to workspace root
# Current dir is .github/scripts/release-notes, so go up 3 levels
workspace_root = Path.cwd().parent.parent.parent
output_file = workspace_root / "release_notes.md"
```

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

**Option 1** is recommended because:
- It fixes the issue at the source (the script that creates the file)
- It's the most robust solution (works regardless of where the script is run from)
- It doesn't require workflow changes
- It makes the script's behavior explicit and predictable

The script should write to an absolute path based on the workspace root, ensuring the file is always created in the correct location.

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

🔴 **OPEN** - Release notes file path needs to be fixed
