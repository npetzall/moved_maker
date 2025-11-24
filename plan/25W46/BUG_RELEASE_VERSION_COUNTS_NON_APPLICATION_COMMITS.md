# BUG: release-version counts commits that don't modify application code

**Status**: ✅ Complete

## Description

The `release-version` script counts all commits since the last tag when calculating patch version bumps, regardless of whether those commits modify application code. This causes the application version to be incremented even when there are no changes to the actual application (e.g., only documentation, CI/CD workflows, or scripts were modified).

## Current State

🟢 **FIXED** - Implementation complete. Version is now bumped based only on commits that modify application code.

**Current (incorrect) state:**
- `get_commit_count()` function uses `git rev-list --count {since_tag}..HEAD`
- This counts ALL commits between the tag and HEAD, regardless of which files they modify
- Commits that only modify non-application files are included in the count:
  - Documentation files (README, CONTRIBUTING, SECURITY.md, etc.)
  - CI/CD workflows (`.github/workflows/*`)
  - Scripts (`.github/scripts/*`)
  - Bug reports (`plan/25W46/` directory with `BUG_` prefix)
  - Planning documents (`plan/` directory)
  - Work tracking files (`work/` directory)
  - Configuration files
  - Test files
  - Application code (`src/` directory)
- When bump type is `PATCH`, patch version is incremented by total commit count
- Example: If there are 5 commits since last tag, and 3 only touch documentation/workflows, patch version still increases by 5

**Code location:**
- `.github/scripts/release-version/src/release_version/version.py`
- Function: `get_commit_count(since_tag: str) -> int` (lines 61-86)
- Current implementation:
  ```python
  result = subprocess.run(
      ["git", "rev-list", "--count", f"{since_tag}..HEAD"],
      capture_output=True,
      text=True,
      check=True,
  )
  ```

**Example scenario:**
- Last tag: `v1.0.0`
- Commits since tag:
  1. `docs: update README` (only modifies README.md)
  2. `chore: update workflow` (only modifies .github/workflows/*)
  3. `fix: bug in parser` (modifies src/parser.rs)
  4. `docs: fix typo` (only modifies CONTRIBUTING.md)
  5. `chore: update script` (only modifies .github/scripts/*)
- Current behavior: Patch version becomes `1.0.5` (counts all 5 commits)
- Expected behavior: Patch version should be `1.0.1` (only counts commit #3 that modifies application code)

## Expected State

The `get_commit_count()` function should only count commits that modify application-related files:
- `src/` directory (application source code)
- `Cargo.toml` (project configuration and dependencies)
- `Cargo.lock` (dependency lock file)

**Expected implementation:**
- Use `git rev-list --count {since_tag}..HEAD -- src/ Cargo.toml Cargo.lock`
- This filters commits to only those that modify at least one of the specified paths
- Commits that only modify other files (docs, workflows, scripts, etc.) are excluded
- Version is only bumped when there are actual changes to the application or its dependencies

**Expected behavior:**
- If no commits modify `src/`, `Cargo.toml`, or `Cargo.lock`, commit count should be 0
- Patch version should only increment based on commits that affect the application
- Documentation-only changes should not trigger version bumps

## Impact

### Version Accuracy Impact
- **Severity**: High
- **Priority**: High

Without path filtering:
- Version numbers don't accurately reflect application changes
- Versions are incremented even when application code hasn't changed
- Users may see version bumps that don't correspond to actual application updates
- Semantic versioning principles are violated (version should reflect application changes)

### Release Management Impact
- **Severity**: Medium
- **Priority**: Medium

- Releases may be created with no actual application changes
- Version history becomes cluttered with non-functional changes
- Difficult to track which versions contain actual application updates
- Release notes may be generated for versions with no application changes

### Developer Experience Impact
- **Severity**: Medium
- **Priority**: Medium

- Confusing version numbers that don't match application changes
- Unclear which versions contain actual code changes
- May lead to unnecessary releases or deployments
- Version numbers become less meaningful

## Root Cause

The `get_commit_count()` function uses `git rev-list --count` without path filtering. The `git rev-list` command by default counts all commits in the specified range, regardless of which files they modify. To count only commits that modify specific paths, the paths must be specified after the `--` separator.

The current implementation assumes all commits are relevant to versioning, but in practice, only commits that modify application code or dependencies should affect the version number.


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_VERSION_COUNTS_NON_APPLICATION_COMMITS.md` for the detailed implementation plan.
