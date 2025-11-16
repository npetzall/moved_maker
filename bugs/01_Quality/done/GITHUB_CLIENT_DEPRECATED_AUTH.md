# Bug: GitHub client using deprecated authentication method

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

## Steps to Fix

1. Import `Auth` from `github` module
2. Update `Github(token)` to `Github(auth=Auth.Token(token))` on line 20
3. Verify the change works correctly
4. Run tests to ensure no regressions
5. Verify deprecation warning is eliminated

## Affected Files

- `.github/scripts/release-version/src/release_version/github_client.py`
  - Line 5: Add `Auth` to imports
  - Line 20: Update `Github(token)` to `Github(auth=Auth.Token(token))`

**Test files to verify:**
- `.github/scripts/release-version/tests/test_github_client.py` (should still pass after change)

## Investigation Needed

1. ✅ Confirmed: Deprecation warning was present in current code
2. ✅ Confirmed: PyGithub version `>=2.0.0` supports new `Auth.Token()` API
3. ✅ Verified: Tests pass with new authentication method (5/5 tests passing)
4. ✅ Verified: No other files use deprecated `Github(token)` pattern

## Status

✅ **FIXED** - Deprecated authentication method updated to use modern API, all tests passing

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update imports

**File:** `.github/scripts/release-version/src/release_version/github_client.py`

1. **Add `Auth` to imports (line 5)**
   - [x] Locate the import statement: `from github import Github, GithubException`
   - [x] Update to: `from github import Auth, Github, GithubException`
   - [x] Verify import order follows Python conventions (alphabetical or logical grouping)
   - [x] Ensure `Auth` is imported from `github` module

#### Step 2: Update Github initialization

**File:** `.github/scripts/release-version/src/release_version/github_client.py`

1. **Update `Github` constructor call (line 20)**
   - [x] Locate the line: `self.github = Github(token)`
   - [x] Replace with: `self.github = Github(auth=Auth.Token(token))`
   - [x] Verify the change maintains the same functionality
   - [x] Ensure `token` parameter is still passed correctly (now wrapped in `Auth.Token()`)

2. **Verify method signature compatibility**
   - [x] Confirm `Auth.Token(token)` accepts string tokens
   - [x] Verify the `Github` client works identically with new authentication method
   - [x] Check that all existing methods (`get_repo()`, `get_merged_prs_since()`) work unchanged

#### Step 3: Run tests

**File:** `.github/scripts/release-version/tests/test_github_client.py`

1. **Execute test suite**
   - [x] Run tests: `pytest tests/test_github_client.py` (or equivalent test command)
   - [x] Verify all tests pass (5/5 tests passing)
   - [x] Confirm no deprecation warnings appear in test output
   - [x] Check that test coverage remains the same

2. **Verify integration**
   - [x] Run the full test suite for the release-version script
   - [x] Verify no other tests are affected
   - [x] Confirm GitHub API interactions work correctly

#### Step 4: Verify deprecation warning is eliminated

1. **Check for warnings**
   - [x] Run the code and verify no deprecation warnings appear
   - [x] Check test output for any remaining warnings
   - [x] Verify Python warnings are not suppressed elsewhere
   - [x] Confirm the fix resolves the specific warning mentioned in the bug report

2. **Code review**
   - [x] Review the change for correctness
   - [x] Verify the new API usage follows PyGithub best practices
   - [x] Check that error handling remains unchanged
   - [x] Ensure the change is minimal and focused

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `github_client.py`
   - Restore original `Github(token)` call
   - Verify code returns to working state
   - Investigate why new API doesn't work (if applicable)

2. **Partial Rollback**
   - If tests fail, investigate the specific failure
   - Check if `Auth.Token()` requires different token format
   - Verify PyGithub version compatibility
   - Consider if token needs to be validated or formatted differently

3. **Alternative Approach**
   - If `Auth.Token()` doesn't work as expected:
     - Verify PyGithub version supports the new API
     - Check PyGithub documentation for correct usage
     - Consider updating PyGithub version if needed
     - Verify token format is correct (should be string)

### Implementation Order

1. **Update imports** (Step 1)
   - Add `Auth` to the import statement
   - Verify import syntax is correct
   - Check for any import-related errors

2. **Update Github initialization** (Step 2)
   - Replace `Github(token)` with `Github(auth=Auth.Token(token))`
   - Verify syntax is correct
   - Check for any immediate syntax errors

3. **Run tests** (Step 3)
   - Execute test suite to verify functionality
   - Check for any test failures
   - Verify deprecation warning is gone

4. **Final verification** (Step 4)
   - Run code manually if possible
   - Verify no warnings in output
   - Confirm all functionality works as before

### Risk Assessment

- **Risk Level:** Very Low
- **Impact if Failed:**
  - Tests might fail if new API usage is incorrect (easily fixable)
  - GitHub API calls might fail if authentication is broken (unlikely, same underlying mechanism)
  - Code might not work if PyGithub version doesn't support new API (version check shows `>=2.0.0` supports it)
- **Mitigation:**
  - Easy rollback (just revert the change)
  - Can test locally before committing
  - Well-documented API change in PyGithub
  - Same underlying authentication mechanism
- **Testing:**
  - Can be fully tested locally before committing
  - Test suite will catch any issues
  - Can verify with actual GitHub API if needed
- **Dependencies:**
  - PyGithub `>=2.0.0` (already specified in `pyproject.toml`)
  - No external services required for testing (can mock if needed)

### Expected Outcomes

After successful implementation:

- **No Deprecation Warnings:** Code runs without deprecation warnings
- **Future Compatibility:** Code will work with future PyGithub versions
- **Code Quality:** Code follows modern PyGithub best practices
- **Functionality:** All existing functionality works identically
- **Maintainability:** Code uses supported API that won't be removed

### Code Changes Summary

**Before:**
```python
from github import Github, GithubException

class GitHubClient:
    def __init__(self, token: str, repo_name: str):
        self.github = Github(token)  # ❌ Deprecated
```

**After:**
```python
from github import Auth, Github, GithubException

class GitHubClient:
    def __init__(self, token: str, repo_name: str):
        self.github = Github(auth=Auth.Token(token))  # ✅ Modern API
```

## References

- [PyGithub Authentication Documentation](https://pygithub.readthedocs.io/en/latest/github.html#github.MainClass.Github)
- [PyGithub Auth Module](https://pygithub.readthedocs.io/en/latest/github.html#github.Auth)
- [PyGithub Changelog](https://pygithub.readthedocs.io/en/latest/changes.html) (for deprecation timeline)
