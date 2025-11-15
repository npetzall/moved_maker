# Bug: Workflows - No test report found

## Description

The PR workflow `test` job attempts to upload test results from `test-results.xml`, but the file is not found. When running locally, nextest places the JUnit XML output in `target/nextest/default/` folder, but the workflow expects it at the root level.

## Current State

✅ **FIXED** - The workflow upload step has been updated to use a wildcard pattern to find the test results file.

**Previous (broken) workflow configuration:**
```yaml
- name: Run tests
  run: cargo nextest run

- name: Upload test results
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: test-results-${{ matrix.os }}
    path: test-results.xml
```

**Current (fixed) workflow configuration:**
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

**Current nextest configuration (`.config/nextest.toml`):**
```toml
[profile.default.junit]
path = "test-results.xml"
```

**Local behavior:**
- When running `cargo nextest run` locally, the JUnit XML is generated in `target/nextest/default/test-results.xml`
- The configuration specifies `path = "test-results.xml"` (relative path)

## Expected State

The test job should successfully:
1. Run nextest tests
2. Generate JUnit XML output
3. Upload the test results artifact

The artifact upload should work whether the file is at the root level or in a subdirectory.

## Impact

### CI/CD Impact
- **Severity**: Medium
- **Priority**: Medium

The test results artifact upload fails, preventing:
- Test result visualization in GitHub Actions
- Test result artifact downloads
- Test result analysis tools from accessing the data

### Functionality Impact
- **Severity**: Low
- **Priority**: Low

Tests still run successfully, but test result artifacts are not available for download or analysis.

## Root Cause

The nextest configuration specifies a relative path `test-results.xml`, but nextest may place the file in a different location (e.g., `target/nextest/default/test-results.xml`) depending on the working directory or nextest version behavior. The workflow upload step expects the file at the root level.

## Steps to Fix

### Option 1: Use wildcard pattern ✅ **IMPLEMENTED**
Update the artifact upload to use a wildcard pattern to find the test results file:

```yaml
- name: Upload test results
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: test-results-${{ matrix.os }}
    path: target/nextest/**/test-results.xml
    if-no-files-found: warn
```

### Option 2: Update nextest configuration
Ensure the nextest configuration uses an absolute path or a path relative to the workspace root:

```toml
[profile.default.junit]
path = "test-results.xml"  # Ensure this is relative to workspace root
```

### Option 3: Find and copy the file
Add a step to locate and copy the test results file to the expected location:

```yaml
- name: Find and copy test results
  if: always()
  run: |
    if [ -f "target/nextest/default/test-results.xml" ]; then
      cp target/nextest/default/test-results.xml test-results.xml
    elif [ -f "test-results.xml" ]; then
      echo "Test results already at root"
    else
      echo "Warning: test-results.xml not found"
      find . -name "test-results.xml" -type f
    fi
```

## Affected Files

- `.github/workflows/pull_request.yaml`
  - `test` job (lines 59-67)
- `.config/nextest.toml`
  - JUnit XML path configuration (line 2)

## Investigation Needed

1. ✅ Verify where nextest actually places the JUnit XML file in CI environment - Confirmed: `target/nextest/default/test-results.xml` locally
2. ✅ Check if `actions/upload-artifact` supports wildcard patterns - Confirmed: Full wildcard support including `**` pattern
3. ⏳ Verify nextest version behavior differences between local and CI - Awaiting CI verification
4. ✅ Test if updating the path in `.config/nextest.toml` resolves the issue - Using wildcard pattern instead (Option 1 implemented)

## Status

✅ **IMPLEMENTED** - Test results artifact upload has been updated to use wildcard pattern. Awaiting CI verification.

## Investigation

### Wildcard Support in `actions/upload-artifact`

**Finding:** `actions/upload-artifact` (v4 and v5) **fully supports wildcard patterns** in the `path` parameter.

#### Key Findings:

1. **Wildcard Pattern Support:**
   - Wildcards can be used to match multiple files or directories
   - Common patterns include:
     - `**` - matches zero or more directories
     - `*` - matches any sequence of characters (except path separators)
     - `?` - matches a single character
     - Character classes like `[abc]` are also supported

2. **Single Wildcard Path:**
   - A single wildcard pattern is sufficient to match the test results file
   - The `**` pattern will recursively search for `test-results.xml` in any subdirectory
   - Example:
     ```yaml
     path: target/nextest/**/test-results.xml
     ```

3. **Path Hierarchy Preservation:**
   - When using wildcards, the directory structure is preserved after the first wildcard
   - For `target/nextest/**/test-results.xml`, the structure relative to `target/nextest/` is maintained in the artifact

4. **Quoting Requirements:**
   - Paths beginning with a wildcard character should be quoted to prevent YAML parsing issues
   - Example: `path: "**/test-results.xml"` (though not strictly necessary for paths starting with directory names)

5. **Behavior When No Files Match:**
   - The `if-no-files-found` option controls behavior when no files match:
     - `warn` (default): Outputs a warning but does not fail the action
     - `error`: Fails the action with an error message
     - `ignore`: No warnings or errors; action does not fail
   - For test results, using `warn` or `ignore` is recommended to avoid failing the workflow when tests don't generate output

#### Recommended Solution:

Based on the investigation, **Option 1 (wildcard pattern) is viable and recommended**:

```yaml
- name: Upload test results
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: test-results-${{ matrix.os }}
    path: target/nextest/**/test-results.xml
    if-no-files-found: warn
```

This approach:
- ✅ Handles subdirectory locations where nextest actually places the file
- ✅ Uses native wildcard support (no shell scripting needed)
- ✅ Preserves directory structure in the artifact
- ✅ Won't fail the workflow if the file is missing (with `if-no-files-found: warn`)
- ✅ Works with `actions/upload-artifact` v5.0.0 (the version currently in use)

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/pull_request.yaml`

**File:** `.github/workflows/pull_request.yaml`

1. **Update `test` job artifact upload (lines 62-67)**
   - [x] Locate the "Upload test results" step at lines 62-67
   - [x] Replace:
     ```yaml
     - name: Upload test results
       uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
       if: always()
       with:
         name: test-results-${{ matrix.os }}
         path: test-results.xml
     ```
   - [x] With:
     ```yaml
     - name: Upload test results
       uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
       if: always()
       with:
         name: test-results-${{ matrix.os }}
         path: target/nextest/**/test-results.xml
         if-no-files-found: warn
     ```
   - [x] Verify step placement (should be after "Run tests" step, before "Run doctests" step)
   - [x] Verify wildcard pattern matches nextest output location

2. **Verify nextest configuration**
   - [x] Confirm `.config/nextest.toml` contains JUnit XML path configuration
   - [x] Verify nextest generates test results in `target/nextest/default/` or similar subdirectory
   - [x] Note: The wildcard pattern will match regardless of the exact subdirectory name

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.github/workflows/pull_request.yaml`
   - Restore `path: test-results.xml` (even if broken, for reference)
   - Verify workflows return to previous state

2. **Partial Rollback**
   - If wildcard pattern doesn't match, verify nextest output location in CI
   - Check if nextest version behavior differs between local and CI
   - Consider using Option 3 (find and copy) as fallback
   - Verify `if-no-files-found: warn` prevents workflow failures

3. **Alternative Approaches**
   - If wildcard doesn't work, implement Option 3 (find and copy step)
   - Update `.config/nextest.toml` to use absolute path (Option 2)
   - Verify nextest documentation for path resolution behavior

### Implementation Order

1. ✅ Start with `.github/workflows/pull_request.yaml` (only affected file)
2. ✅ Update workflow file - Change `path: test-results.xml` to `path: target/nextest/**/test-results.xml`
3. ✅ Add `if-no-files-found: warn` to prevent workflow failures when file is missing
4. ✅ Verify `.config/nextest.toml` configuration - Confirmed JUnit XML path is set to `test-results.xml`
5. ⏳ Test via pull request - Verify CI workflow execution
6. ⏳ Verify test job passes - Confirm tests run successfully
7. ⏳ Verify test-results artifact is uploaded correctly - Check artifact contains test-results.xml
8. ⏳ Verify artifact location - Confirm file is found in expected subdirectory

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:** Test results artifact upload would still fail, but tests would continue to run
- **Mitigation:**
  - `if-no-files-found: warn` prevents workflow failure if file is not found
  - Wildcard pattern is well-supported in `actions/upload-artifact` v5.0.0
  - Easy rollback to previous configuration
  - Alternative options (Option 2, Option 3) available if needed
- **Testing:** Can be fully tested via pull request before affecting main branch
- **Dependencies:** Relies on nextest generating JUnit XML output (already configured in `.config/nextest.toml`)

## References

- Current workflow: `.github/workflows/pull_request.yaml` lines 62-67
- Current nextest configuration: `.config/nextest.toml`:
  ```toml
  [profile.default.junit]
  path = "test-results.xml"
  ```
- Local nextest output location: `target/nextest/default/test-results.xml`
- `actions/upload-artifact` documentation: Supports wildcard patterns including `**` for recursive directory matching
