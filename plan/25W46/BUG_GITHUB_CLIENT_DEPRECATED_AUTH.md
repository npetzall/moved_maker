# BUG: GitHub client using deprecated authentication method

**Status**: ✅ Complete

## Description

The `GitHubClient` class in `.github/scripts/release-version/src/release_version/github_client.py` uses the deprecated `login_or_token` argument when initializing the PyGithub `Github` client. The current implementation passes the token directly to the `Github()` constructor, which triggers a deprecation warning. The modern approach is to use the `auth` parameter with `github.Auth.Token()`.

## Current State

✅ **FIXED** - Deprecated authentication method updated to use modern API.

**Previous (incorrect) state:**
- Line 20 in `github_client.py` used: `self.github = Github(token)`
- This triggered a deprecation warning:
  ```
  DeprecationWarning: Argument login_or_token is deprecated, please use auth=github.Auth.Token(...) instead
  ```
- The code still worked but would break in future versions of PyGithub

**Current (correct) state:**
- Line 5: Added `Auth` to imports: `from github import Auth, Github, GithubException`
- Line 20: Updated to: `self.github = Github(auth=Auth.Token(token))`
- All tests pass (5/5 tests passing)
- No deprecation warnings
- Code uses modern PyGithub API

**Project structure:**
- `.github/scripts/release-version/src/release_version/github_client.py` (lines 5, 20)
- Uses PyGithub version `>=2.0.0` (from `pyproject.toml`)

## Expected State

Update the `Github` initialization to use the modern authentication API:

```python
from github import Github, Auth

# In __init__ method:
self.github = Github(auth=Auth.Token(token))
```

This eliminates the deprecation warning and ensures compatibility with future PyGithub versions.

## Impact

### Code Quality Impact
- **Severity**: Medium
- **Priority**: Medium

- Deprecation warnings indicate code will break in future versions
- Code quality tools may flag deprecation warnings as issues
- Future PyGithub versions may remove support for the deprecated API

### Developer Experience Impact
- **Severity**: Low
- **Priority**: Low

- Deprecation warnings create noise in test output and logs
- Developers may be confused by warnings during development
- Warnings may be hidden or ignored, leading to future breakage

### CI/CD Impact
- **Severity**: Low
- **Priority**: Low

- Deprecation warnings may appear in CI/CD logs
- Future PyGithub updates may cause workflow failures if deprecated API is removed
- No immediate functional impact (code still works)

## Root Cause

The code was written using the older PyGithub API pattern where tokens were passed directly to the `Github()` constructor. PyGithub version 2.0.0+ introduced a new authentication API using `github.Auth.Token()` to provide better type safety and clearer authentication methods.


## Related Implementation Plan

See `work/25W46/BUG_GITHUB_CLIENT_DEPRECATED_AUTH.md` for the detailed implementation plan.
