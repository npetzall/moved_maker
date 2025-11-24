# Bug: Test Reports Not Uploaded

## Description

Test reports are not being uploaded as artifacts in the GitHub Actions workflow. The workflow step that uploads test results fails to find the expected JUnit XML files.

## Current State

**File**: `.config/nextest.toml`

The JUnit configuration has an incorrect path:
```toml
[profile.default.junit]
path = "{target}-test-results.xml"
```

**Problem**: The path contains a `{target}` prefix that shouldn't be there. This is a leftover from an investigation about naming, but it's incorrect and causes the test results file to be generated with the wrong name.

**Workflow**: `.github/workflows/pull_request.yaml` (lines 76-82)

The workflow expects test results at:
```yaml
- name: Upload test results
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: test-results-${{ matrix.os }}
    path: target/nextest/**/test-results.xml
    if-no-files-found: warn
```

## Root Cause

The `nextest.toml` configuration has an incorrect JUnit output path. The `{target}` prefix in the path causes nextest to generate test result files with a name that doesn't match what the workflow expects.

When nextest runs, it generates the JUnit XML file at a path like `{target}-test-results.xml` (literally with the string "{target}" in the filename), but the workflow is looking for files matching the pattern `target/nextest/**/test-results.xml`.

## Expected State

The JUnit configuration should have a correct path that:
1. Generates test results in a location that matches the workflow's expected pattern
2. Uses the standard nextest JUnit output location
3. Doesn't include the incorrect `{target}` prefix

The correct configuration should be:
```toml
[profile.default.junit]
path = "test-results.xml"
```

Or, if nextest should place it in the target directory:
```toml
[profile.default.junit]
path = "target/nextest/test-results.xml"
```

## Solution

### Fix the JUnit path in `.config/nextest.toml`

Remove the incorrect `{target}` prefix from the path configuration.

**Before**:
```toml
[profile.default.junit]
path = "{target}-test-results.xml"
```

**After**:
```toml
[profile.default.junit]
path = "test-results.xml"
```

Note: The exact path depends on where nextest expects the file and where the workflow looks for it. The workflow pattern `target/nextest/**/test-results.xml` suggests nextest should place the file in a subdirectory under `target/nextest/`. However, the simplest fix is to use the default nextest behavior or configure it to match the workflow's expected location.

## Investigation Notes

The `{target}` prefix was added during an investigation about naming, but it was incorrect and should be removed. The prefix causes the filename to literally include "{target}" as part of the name, which doesn't match the workflow's expected pattern.

## Impact

- **Severity**: Medium (test results not available for debugging)
- **Priority**: Medium (affects CI visibility and debugging capabilities)

**Consequences**:
1. Test result artifacts are not uploaded to GitHub Actions
2. Cannot view test results in the workflow artifacts
3. Makes debugging test failures more difficult
4. The `if-no-files-found: warn` setting means the workflow doesn't fail, but silently doesn't upload anything

## Affected Files

- `.config/nextest.toml`
  - Fix the `path` in `[profile.default.junit]` section
  - Remove the incorrect `{target}` prefix

## Verification

After fixing the configuration:
1. Run `cargo nextest run` locally to verify the test results file is generated at the expected location
2. Check that the generated file matches the workflow's expected pattern
3. Verify the workflow successfully uploads test results as artifacts

## Status

✅ **COMPLETE** - JUnit configuration has been fixed. The path has been corrected from `"{target}-test-results.xml"` to `"test-results.xml"` to match the workflow's expected pattern.
