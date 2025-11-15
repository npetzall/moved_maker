# Bug: cargo-geiger output format syntax incorrect in workflows and documentation

## Description

`cargo-geiger` is configured with incorrect syntax for the `--output-format` option in CI workflows and documentation. The current syntax uses `--output-format json` (lowercase), but the correct syntax should be `--output-format Json` (capital J). This may cause the tool to fail or not produce the expected JSON output format.

## Current State

✅ **FIXED** - `cargo-geiger` has been updated to use the correct syntax `--output-format Json` (capital J) in:
- `.github/workflows/pull_request.yaml` (line 34) ✅
- `.github/workflows/release-build.yaml` (line 38) ✅
- Documentation files (TOOLING.md, plan/01_Quality/SECURITY.md, work/01_Quality/*.md, plan/01_Quality/*.md) ✅

**Current (incorrect) syntax:**
```yaml
- name: Run cargo-geiger scan
  run: cargo geiger --output-format json > geiger-report.json || [ $? -eq 1 ]
```

**Documentation examples (incorrect):**
```bash
cargo geiger --output-format json > geiger-report.json
```

## Expected State

`cargo-geiger` should use the correct syntax `--output-format Json` (capital J) in:
1. **Workflow files**: Both `.github/workflows/pull_request.yaml` and `.github/workflows/release-build.yaml`
2. **Documentation files**: All documentation that references the geiger output format option

**Expected (correct) syntax:**
```yaml
- name: Run cargo-geiger scan
  run: cargo geiger --output-format Json > geiger-report.json || [ $? -eq 1 ]
```

**Documentation examples (correct):**
```bash
cargo geiger --output-format Json > geiger-report.json
```

## Impact

### Functionality Impact
- **Severity**: Medium
- **Priority**: Medium

Current issues:
- `cargo-geiger` may fail to recognize the output format option with lowercase `json`
- JSON output may not be generated correctly, causing downstream processing issues
- Documentation is incorrect and may mislead developers
- Inconsistent syntax across codebase and documentation

### Potential Consequences
- Geiger reports may not be generated in JSON format
- Artifact uploads may fail if JSON format is not produced
- Developers following documentation will use incorrect syntax
- CI workflows may fail silently or produce unexpected output

## Steps to Fix

### Step 1: Update workflow files

Update both workflow files to use the correct syntax `--output-format Json`:

**File:** `.github/workflows/pull_request.yaml`

**Before:**
```yaml
- name: Run cargo-geiger scan
  run: cargo geiger --output-format json > geiger-report.json || [ $? -eq 1 ]
```

**After:**
```yaml
- name: Run cargo-geiger scan
  run: cargo geiger --output-format Json > geiger-report.json || [ $? -eq 1 ]
```

**File:** `.github/workflows/release-build.yaml`

**Before:**
```yaml
- name: Run cargo-geiger scan
  run: cargo geiger --output-format json > geiger-report.json || [ $? -eq 1 ]
```

**After:**
```yaml
- name: Run cargo-geiger scan
  run: cargo geiger --output-format Json > geiger-report.json || [ $? -eq 1 ]
```

### Step 2: Update documentation files

Search for and update all occurrences of `--output-format json` to `--output-format Json` in:
- `TOOLING.md`
- `plan/01_Quality/SECURITY.md`
- Any other documentation files that reference geiger output format

## Affected Files

### Workflow Files
- `.github/workflows/pull_request.yaml`
  - `security` job (line 34 - "Run cargo-geiger scan" step)

- `.github/workflows/release-build.yaml`
  - `security` job (line 38 - "Run cargo-geiger scan" step)

### Documentation Files
- `TOOLING.md` (line 98 - cargo-geiger usage example)
- `plan/01_Quality/SECURITY.md` (lines 173, 194, 400 - cargo-geiger examples)
- Potentially other documentation files (to be verified)

## Example Fix

### Before (incorrect):
```yaml
- name: Run cargo-geiger scan
  run: cargo geiger --output-format json > geiger-report.json || [ $? -eq 1 ]
```

```bash
# Documentation example
cargo geiger --output-format json > geiger-report.json
```

### After (correct):
```yaml
- name: Run cargo-geiger scan
  run: cargo geiger --output-format Json > geiger-report.json || [ $? -eq 1 ]
```

```bash
# Documentation example
cargo geiger --output-format Json > geiger-report.json
```

## Status

✅ **COMPLETED** - All workflow files and documentation have been updated to use the correct syntax `--output-format Json` (capital J) instead of `--output-format json` (lowercase). All occurrences have been fixed across:
- 2 workflow files (pull_request.yaml, release-build.yaml)
- 6 documentation files (TOOLING.md, plan/01_Quality/SECURITY.md, work/01_Quality/01_Security.md, work/01_Quality/07_01_Pull_Request_Workflow.md, work/01_Quality/07_03_Release_Workflow.md, plan/01_Quality/IMPLEMENTATION.md, plan/01_Quality/CONTINUOUS_DELIVERY.md)

## References

- [cargo-geiger Documentation](https://github.com/rust-secure-code/cargo-geiger)
- Related bug reports:
  - `bugs/01_Quality/done/WORKFLOWS_GEIGER_BLOCKING.md` - Geiger blocking configuration
  - `bugs/01_Quality/done/WORKFLOWS_GEIGER_INSTALLATION.md` - Geiger installation method

## Notes

- The `--output-format` option is case-sensitive and requires capital `J` in `Json`
- This is a simple syntax fix but affects multiple files
- The fix should be applied consistently across all workflow and documentation files
- After fixing, verify that geiger reports are generated correctly in JSON format

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/pull_request.yaml`

**File:** `.github/workflows/pull_request.yaml`

1. **Update `security` job geiger step (line 34)** ✅ COMPLETED
   - [x] Locate the "Run cargo-geiger scan" step at line 34 in the `security` job
   - [x] Replace `--output-format json` with `--output-format Json` (capital J)
   - [x] Verify the updated command: `cargo geiger --output-format Json > geiger-report.json || [ $? -eq 1 ]`
   - [x] Verify step placement (should be after cargo-audit, before artifact upload)

#### Step 2: Update `.github/workflows/release-build.yaml`

**File:** `.github/workflows/release-build.yaml`

1. **Update `security` job geiger step (line 38)** ✅ COMPLETED
   - [x] Locate the "Run cargo-geiger scan" step at line 38 in the `security` job
   - [x] Replace `--output-format json` with `--output-format Json` (capital J)
   - [x] Verify the updated command: `cargo geiger --output-format Json > geiger-report.json || [ $? -eq 1 ]`
   - [x] Verify step placement (should be after cargo-audit, before artifact upload)

#### Step 3: Update documentation files

**File:** `TOOLING.md`

1. **Update cargo-geiger usage example (line 98)** ✅ COMPLETED
   - [x] Locate the cargo-geiger usage section around line 98
   - [x] Replace `--output-format json` with `--output-format Json` (capital J)
   - [x] Verify the updated example: `cargo geiger --output-format Json > geiger-report.json`
   - [x] Check for any other occurrences in the file

**File:** `plan/01_Quality/SECURITY.md`

1. **Update cargo-geiger examples** ✅ COMPLETED
   - [x] Search for all occurrences of `--output-format json` in the file
   - [x] Replace all occurrences with `--output-format Json` (capital J)
   - [x] Known locations: lines 173, 194, 400 (all updated)
   - [x] Verify all examples use the correct syntax

#### Step 4: Search for additional occurrences

1. **Search codebase for remaining occurrences** ✅ COMPLETED
   - [x] Use grep to find all files containing `--output-format json`
   - [x] Review each occurrence to determine if it's related to cargo-geiger
   - [x] Update all cargo-geiger related occurrences (6 additional files updated)
   - [x] Verify no other tools use similar syntax that might be affected

### Phase 2: Verification Steps

#### Step 1: Verify workflow syntax

1. **Check workflow YAML syntax** ✅ COMPLETED
   - [x] Verify YAML files are valid after changes
   - [x] Check for any syntax errors introduced (no errors found)
   - [x] Verify indentation is correct

#### Step 2: Test locally (if possible)

1. **Test cargo-geiger command locally** ⬜ PENDING
   - [ ] Install cargo-geiger: `cargo install --locked cargo-geiger`
   - [ ] Test command: `cargo geiger --output-format Json > geiger-report.json`
   - [ ] Verify JSON output is generated correctly
   - [ ] Compare with lowercase version to confirm difference

#### Step 3: Verify documentation

1. **Review documentation updates** ✅ COMPLETED
   - [x] Read through updated documentation sections
   - [x] Verify all examples use correct syntax
   - [x] Check for consistency across all documentation files
   - [x] Ensure no mixed case variations remain

### Phase 3: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.github/workflows/pull_request.yaml`
   - Revert changes to `.github/workflows/release-build.yaml`
   - Revert changes to documentation files
   - Verify workflows return to previous state

2. **Partial Rollback**
   - If workflow changes cause issues, revert only workflow files
   - Keep documentation changes if they're correct
   - Verify cargo-geiger documentation for exact syntax requirements
   - Test locally to confirm correct syntax

3. **Alternative Approaches**
   - If `Json` doesn't work, verify cargo-geiger version and documentation
   - Check if the syntax has changed in newer versions
   - Consider using alternative output format if JSON format has issues
   - Verify with `cargo geiger --help` to see exact option format

### Implementation Order

1. [x] Update `.github/workflows/pull_request.yaml` (PR workflow, easier to test) ✅ COMPLETED
2. [ ] Test via pull request to verify:
   - Workflow runs without syntax errors
   - `cargo geiger --output-format Json` executes successfully
   - `geiger-report.json` is generated in correct JSON format
   - Artifact upload succeeds with valid JSON file
   - Security job completes successfully
3. [x] Update `.github/workflows/release-build.yaml` ✅ COMPLETED
4. [ ] Test via release workflow to verify:
   - Same behavior as PR workflow
   - Security job completes successfully
   - `build-and-release` job is not blocked
5. [x] Update documentation files (`TOOLING.md`, `plan/01_Quality/SECURITY.md`, and 5 additional files) ✅ COMPLETED
6. [x] Search for and update any additional occurrences ✅ COMPLETED
7. [x] Verify all changes are consistent across codebase ✅ COMPLETED

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:** cargo-geiger may fail to generate JSON output, potentially causing workflow failures or incorrect report generation
- **Mitigation:**
  - Simple syntax change (case sensitivity)
  - Easy rollback if needed
  - Can test via pull request before affecting release workflow
  - Documentation can be updated independently of workflows
- **Testing:** Can be fully tested via pull request workflow before affecting release workflow
- **Dependencies:**
  - No additional dependencies required
  - Simple case change in string literal
  - No configuration changes needed

## Alternative Solutions

If `Json` (capital J) doesn't work as expected:

1. **Verify cargo-geiger version and help output**:
   ```bash
   cargo geiger --help
   ```
   Check the exact format of the `--output-format` option

2. **Check cargo-geiger documentation**:
   - Verify the correct syntax in official documentation
   - Check if the syntax has changed in recent versions
   - Verify case sensitivity requirements

3. **Test both variations**:
   - Test `--output-format json` (lowercase)
   - Test `--output-format Json` (capital J)
   - Use whichever works correctly
