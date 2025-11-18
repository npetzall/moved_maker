# Bug: Release build workflow missing test results artifact upload

## Description

The `release-build.yaml` workflow's `build-and-release` job runs tests using `cargo nextest run` but does not upload test results as artifacts, unlike the PR workflow. This makes it difficult to debug test failures in release builds and prevents test result analysis tools from accessing the data.

## Current State

**Status:** ✅ **IMPLEMENTED** - Test results artifact upload has been added to the release build workflow.

**Current (fixed) state:**
- `build-and-release` job runs `cargo nextest run` (line 133)
- Test results are generated in `target/nextest/**/test-results.xml`
- **Test results are renamed** to include artifact name identifier (line 136-142) ✅
- **Test results are uploaded as artifacts** with unique names per matrix build (line 144-150) ✅
- Test results can be downloaded and analyzed from release builds
- Artifact names include OS and target for uniqueness: `test-results-{os}-{target}`
- File names inside artifacts are unique: `{artifact_name}-test.xml`

**Comparison with PR workflow:**
- PR workflow (`pull_request.yaml`) uploads test results as artifacts (lines 72-78)
- Release build workflow now uploads test results as artifacts (lines 144-150) ✅
- Both workflows use `if: always()` to upload even if tests fail
- Both workflows use `if-no-files-found: warn` for graceful handling
- Release workflow includes file renaming to avoid conflicts (not needed in PR workflow due to single OS)

**Naming conflict issue:**
- The test results XML file is always named `test-results.xml` by cargo-nextest
- When multiple matrix jobs upload artifacts, the file inside each artifact has the same name
- If artifacts are later downloaded and merged (e.g., in the release job), files would overwrite each other
- Need to rename the XML file before uploading to include OS and target identifiers

## Expected State

The `build-and-release` job should upload test results as artifacts, similar to the PR workflow:

```yaml
- name: Upload test results
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: test-results-${{ matrix.os }}-${{ matrix.target }}
    path: target/nextest/**/test-results.xml
    if-no-files-found: warn
```

**Note:** Test results should be included in the release artifacts, making them available for download with the release binaries. This allows users and developers to verify test results for each release.

## Impact

### Debugging Impact
- **Severity**: Medium
- **Priority**: Medium

**Impact if test results are missing:**
- Cannot debug test failures in release builds
- Cannot verify test results for specific release versions
- Test result analysis tools cannot access release build test data
- Difficult to compare test results between PR builds and release builds
- Test results are lost after job completion

### Release Quality Impact
- **Severity**: Low
- **Priority**: Low

- Test results should be available for each release for verification
- Users cannot verify that tests passed for the binaries they download
- Release artifacts should include test results for transparency

## Root Cause

The `build-and-release` job was created without test result artifact upload, likely because the focus was on building and releasing binaries. However, test results are valuable for debugging and verification, especially for release builds.

**Naming conflict consideration:**
- cargo-nextest always generates `test-results.xml` with a fixed filename
- Multiple matrix jobs (different OS/target combinations) would upload files with identical names
- When artifacts are downloaded and merged, files with the same name would conflict/overwrite
- Solution: Rename the XML file to include OS and target before uploading

## Affected Files

- `.github/workflows/release-build.yaml`
  - `build-and-release` job (after line 132, after "Run tests" step)

## Steps to Fix

### Step 1: Rename test results file to avoid naming conflicts

**File:** `.github/workflows/release-build.yaml`

1. **Locate the test step** (around line 133-134)
   - Find: `- name: Run tests` step
   - This step runs `cargo nextest run`

2. **Add rename step after test step**
   - Rename `test-results.xml` to include artifact name identifier
   - This prevents file name conflicts when artifacts are downloaded/merged
   - Use a unique filename pattern: `{artifact_name}-test.xml` (e.g., `move_maker-linux-x86_64-test.xml`)

**Expected code addition:**
```yaml
- name: Run tests
  run: cargo nextest run

- name: Rename test results to avoid conflicts
  run: |
    TEST_RESULTS=$(find target/nextest -name "test-results.xml" | head -n 1)
    if [ -n "$TEST_RESULTS" ]; then
      mv "$TEST_RESULTS" target/nextest/${{ matrix.artifact_name }}-test.xml
    fi
  if: always()
```

### Step 2: Add test results upload step

**File:** `.github/workflows/release-build.yaml`

1. **Add upload step after rename step**
   - Upload the renamed test results file
   - Include matrix variables in artifact name for uniqueness
   - Use `if: always()` to upload even if tests fail

**Expected code addition:**
```yaml
- name: Upload test results
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: test-results-${{ matrix.os }}-${{ matrix.target }}
    path: target/nextest/${{ matrix.artifact_name }}-test.xml
    if-no-files-found: warn
```

2. **Verify artifact and file name uniqueness**
   - Artifact name should include both OS and target for uniqueness
   - Format: `test-results-{os}-{target}` (e.g., `test-results-ubuntu-latest-x86_64-unknown-linux-gnu`)
   - File inside artifact should use artifact_name for a cleaner, more consistent name
   - Format: `{artifact_name}-test.xml` (e.g., `move_maker-linux-x86_64-test.xml`)
   - This ensures artifacts from different matrix builds don't conflict and file names are consistent with binary artifact names

### Step 3: Consider including test results in release artifacts

**Optional enhancement:**
- Test results could be included in the GitHub release as downloadable files
- This would make test results available alongside binaries and checksums
- Users could verify test results for each release

**Note:** This is optional and can be done in a separate enhancement. The primary fix is to upload test results as workflow artifacts.

## Example Fix

### Before:
```yaml
- name: Run tests
  run: cargo nextest run

- name: Install cargo-auditable
  run: cargo install cargo-auditable
```

### After:
```yaml
- name: Run tests
  run: cargo nextest run

- name: Rename test results to avoid conflicts
  run: |
    TEST_RESULTS=$(find target/nextest -name "test-results.xml" | head -n 1)
    if [ -n "$TEST_RESULTS" ]; then
      mv "$TEST_RESULTS" target/nextest/${{ matrix.artifact_name }}-test.xml
    fi
  if: always()

- name: Upload test results
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: test-results-${{ matrix.os }}-${{ matrix.target }}
    path: target/nextest/${{ matrix.artifact_name }}-test.xml
    if-no-files-found: warn

- name: Install cargo-auditable
  run: cargo install cargo-auditable
```

## Verification

After implementing the fix:

- [x] Test results file is renamed to include OS and target identifiers
- [x] Rename step runs even if tests fail (`if: always()`)
- [x] Test results artifact is uploaded in release build workflow
- [x] Artifact name includes OS and target for uniqueness
- [x] File inside artifact has unique name to avoid conflicts when artifacts are merged
- [ ] Artifact can be downloaded from workflow run (pending CI testing)
- [ ] Test results XML file is present in artifact with correct name (pending CI testing)
- [x] Artifact upload doesn't fail workflow if tests fail (`if: always()`)
- [x] Artifact upload handles missing files gracefully (`if-no-files-found: warn`)

## Progress Summary

**Status:** ✅ Implementation Complete - Ready for CI Testing

**Completed:**
- ✅ Rename step added to `.github/workflows/release-build.yaml` after "Run tests" step (lines 136-142)
- ✅ Upload step added to `.github/workflows/release-build.yaml` after rename step (lines 144-150)
- ✅ Rename step uses `find` command to locate test-results.xml file
- ✅ Rename step renames file to `${{ matrix.artifact_name }}-test.xml` to avoid conflicts
- ✅ Rename step uses `if: always()` to ensure renaming happens even if tests fail
- ✅ Upload step uses `actions/upload-artifact@v5.0.0` (same version as PR workflow)
- ✅ Upload step uses `if: always()` to upload even if tests fail
- ✅ Artifact name includes both OS and target: `test-results-${{ matrix.os }}-${{ matrix.target }}`
- ✅ File path references renamed file: `target/nextest/${{ matrix.artifact_name }}-test.xml`
- ✅ Upload step includes `if-no-files-found: warn` for graceful handling
- ✅ Workflow YAML syntax validated (no linting errors)

**Pending:**
- ⏳ CI testing with release tag to verify rename step executes successfully
- ⏳ CI testing to verify test results file is renamed correctly
- ⏳ CI testing to verify upload step executes successfully
- ⏳ CI testing to verify test results artifact is created for each matrix build
- ⏳ CI testing to verify artifact names are unique per matrix combination
- ⏳ CI testing to verify artifact can be downloaded from workflow run
- ⏳ CI testing to verify test results XML file is present in artifact with correct name
- ⏳ CI testing to verify workflow doesn't fail if tests fail (artifact still uploaded)
- ⏳ CI testing to verify workflow handles missing test results gracefully (warn only)

## References

- [PR workflow test results upload](../done/WORKFLOWS_TEST_REPORT_PATH.md) - Similar implementation in PR workflow
- [GitHub Actions upload-artifact](https://github.com/actions/upload-artifact)
- [cargo-nextest documentation](https://nexte.st/)

## Notes

- Test results should be uploaded even if tests fail (`if: always()`)
- Artifact name should be unique per matrix build to avoid conflicts
- **File name conflict resolution:** The test results XML file must be renamed before uploading to avoid conflicts when artifacts are downloaded and merged. cargo-nextest always generates `test-results.xml` with a fixed name, so multiple matrix jobs would create files with identical names that would overwrite each other. The file is renamed to `{artifact_name}-test.xml` (e.g., `move_maker-linux-x86_64-test.xml`) to match the naming convention of the binary artifacts and ensure uniqueness.
- Rename step should also use `if: always()` to ensure renaming happens even if tests fail
- After renaming, the file path is deterministic and doesn't require wildcard pattern matching
- Artifact retention is handled by workflow-level settings (currently 1 day, see separate bug report)

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Add rename step after test execution

**File:** `.github/workflows/release-build.yaml`

1. **Add rename test results step**
   - [x] Locate the "Run tests" step (around line 133-134)
   - [x] Add new step after "Run tests" step
   - [x] Step name: "Rename test results to avoid conflicts"
   - [x] Use `find` command to locate test-results.xml file
   - [x] Rename file to `${{ matrix.artifact_name }}-test.xml`
   - [x] Use `if: always()` to ensure renaming happens even if tests fail
   - [x] Verify step is placed before "Install cargo-auditable" step

**Expected code addition:**
```yaml
- name: Run tests
  run: cargo nextest run

- name: Rename test results to avoid conflicts
  run: |
    TEST_RESULTS=$(find target/nextest -name "test-results.xml" | head -n 1)
    if [ -n "$TEST_RESULTS" ]; then
      mv "$TEST_RESULTS" target/nextest/${{ matrix.artifact_name }}-test.xml
    fi
  if: always()

- name: Install cargo-auditable
  run: cargo install cargo-auditable
```

2. **Verify rename step logic**
   - [x] Verify `find` command will locate test-results.xml in any subdirectory
   - [x] Verify `head -n 1` ensures only one file is selected if multiple exist
   - [x] Verify conditional check prevents errors if file doesn't exist
   - [x] Verify renamed file path uses `target/nextest/` directory
   - [x] Verify file name pattern matches artifact naming convention

#### Step 2: Add test results upload step

**File:** `.github/workflows/release-build.yaml`

1. **Add upload test results step**
   - [x] Add new step after "Rename test results to avoid conflicts" step
   - [x] Step name: "Upload test results"
   - [x] Use `actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4` (v5.0.0)
   - [x] Use `if: always()` to upload even if tests fail
   - [x] Set artifact name to `test-results-${{ matrix.os }}-${{ matrix.target }}`
   - [x] Set path to `target/nextest/${{ matrix.artifact_name }}-test.xml`
   - [x] Add `if-no-files-found: warn` to handle missing files gracefully

**Expected code addition:**
```yaml
- name: Rename test results to avoid conflicts
  run: |
    TEST_RESULTS=$(find target/nextest -name "test-results.xml" | head -n 1)
    if [ -n "$TEST_RESULTS" ]; then
      mv "$TEST_RESULTS" target/nextest/${{ matrix.artifact_name }}-test.xml
    fi
  if: always()

- name: Upload test results
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  if: always()
  with:
    name: test-results-${{ matrix.os }}-${{ matrix.target }}
    path: target/nextest/${{ matrix.artifact_name }}-test.xml
    if-no-files-found: warn

- name: Install cargo-auditable
  run: cargo install cargo-auditable
```

2. **Verify upload step configuration**
   - [x] Verify artifact name includes both OS and target for uniqueness
   - [x] Verify path references the renamed file (not original test-results.xml)
   - [x] Verify `if: always()` ensures upload happens even if tests fail
   - [x] Verify `if-no-files-found: warn` prevents workflow failure if file is missing
   - [x] Verify artifact name format matches pattern: `test-results-{os}-{target}`

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - [ ] Revert changes to `.github/workflows/release-build.yaml`
   - [ ] Remove rename step
   - [ ] Remove upload step
   - [ ] Verify workflow returns to previous state
   - [ ] Investigate the issue before retrying

2. **Partial Rollback Options**
   - [ ] If rename step fails: Keep upload step but use wildcard pattern for path
   - [ ] If upload step fails: Keep rename step but investigate upload-artifact action version
   - [ ] If file not found: Verify nextest output location in CI environment
   - [ ] If artifact name conflicts: Verify matrix variables are correctly referenced
   - [ ] If path resolution fails: Verify file location after rename step

3. **Alternative Approaches**
   - [ ] If rename doesn't work: Use wildcard pattern `target/nextest/**/test-results.xml` in upload step
   - [ ] If find command fails: Use explicit path based on nextest default output location
   - [ ] If artifact name format is wrong: Adjust naming pattern to match workflow conventions
   - [ ] If upload fails: Verify upload-artifact action version compatibility
   - [ ] If file conflicts persist: Consider using timestamp or job ID in filename

### Implementation Order

1. [x] Review PR workflow test results upload implementation (`.github/workflows/pull_request.yaml` lines 70-76)
2. [x] Locate "Run tests" step in release-build workflow (around line 133-134)
3. [x] Add "Rename test results to avoid conflicts" step after "Run tests" step
4. [x] Verify rename step logic handles file location correctly
5. [x] Add "Upload test results" step after rename step
6. [x] Verify upload step configuration matches PR workflow pattern
7. [x] Validate YAML syntax of workflow file
8. [ ] Test workflow changes locally (if possible) or create test branch
9. [ ] Create test tag to trigger release-build workflow
10. [ ] Verify rename step executes successfully in CI
11. [ ] Verify test results file is renamed correctly
12. [ ] Verify upload step executes successfully in CI
13. [ ] Verify test results artifact is created for each matrix build
14. [ ] Verify artifact names are unique per matrix combination
15. [ ] Verify artifact can be downloaded from workflow run
16. [ ] Verify test results XML file is present in artifact with correct name
17. [ ] Verify workflow doesn't fail if tests fail (artifact still uploaded)
18. [ ] Verify workflow handles missing test results gracefully (warn only)
19. [ ] Clean up test tag after verification
20. [ ] Merge changes to main branch

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:**
  - Test results artifact upload would still fail, but tests would continue to run
  - Workflow might fail if YAML syntax is incorrect
  - Artifact upload might fail if file path is incorrect
  - Rename step might fail if test results file location differs from expected
  - Artifact name conflicts might occur if matrix variables are incorrect
- **Mitigation:**
  - Changes are incremental and can be tested step-by-step
  - Can test with test tag before affecting production releases
  - Easy rollback (revert workflow file)
  - `if: always()` ensures steps run even if tests fail
  - `if-no-files-found: warn` prevents workflow failure if file is missing
  - Rename step includes conditional check to handle missing files
  - Artifact name includes both OS and target for uniqueness
  - File is renamed to match artifact naming convention, preventing conflicts
- **Testing:**
  - Can be fully tested via release tag before affecting production
  - Verification steps can confirm file location and naming
  - Artifact download can verify correct file structure
  - Can compare with PR workflow implementation for consistency
- **Dependencies:**
  - Relies on nextest generating JUnit XML output (already configured in `.config/nextest.toml`)
  - Requires `actions/upload-artifact@v5.0.0` (already in use)
  - Requires `find` command (available on all GitHub Actions runners)
  - No new dependencies required
- **Performance Considerations:**
  - Minimal performance impact: Rename operation is fast
  - Upload step adds minimal overhead (small XML file)
  - No impact on test execution time
  - Artifact upload happens asynchronously after tests complete

### Expected Outcomes

After successful implementation:

- **Test Results Available:** Test results artifacts are uploaded for each matrix build in release workflow
- **Unique Artifact Names:** Each artifact has a unique name including OS and target identifiers
- **Unique File Names:** Files inside artifacts have unique names to prevent conflicts when merged
- **Consistent Naming:** File names match artifact naming convention (e.g., `move_maker-linux-x86_64-test.xml`)
- **Failure Resilience:** Artifacts are uploaded even if tests fail (`if: always()`)
- **Graceful Handling:** Missing test results don't fail the workflow (`if-no-files-found: warn`)
- **Debugging Enabled:** Test results can be downloaded and analyzed for release builds
- **Consistency:** Release workflow matches PR workflow in test results handling
- **Transparency:** Test results available for verification alongside release binaries
- **Better Debugging:** Test failures in release builds can be investigated using test results artifacts
- **Quality Assurance:** Test results available for each release version for verification
- **Tool Integration:** Test result analysis tools can access release build test data
