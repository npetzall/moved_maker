# BUG: Release build workflow missing test results artifact upload

**Status**: ✅ Complete

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


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_BUILD_MISSING_TEST_RESULTS.md` for the detailed implementation plan.
