# Implementation Plan: Spell Checking with typos

## Overview

Integrate typos spell checking into the project to catch spelling mistakes in source code and commit messages before they reach the repository. This implementation will add typos to pre-commit hooks, configure it to run before git-sumi, and set up a configuration file to handle project-specific terminology.

## Goals

- Add spell checking for source code via pre-commit hooks
- Add spell checking for commit messages via commit-msg hooks
- Ensure typos runs before git-sumi in the hook sequence
- Configure typos to handle project-specific terms (terraform, hcl, moved, maker, etc.)
- Store configuration in `.config/typos.toml` for consistency with other project configs
- Fail on typos rather than auto-fix (requires manual fixes or config updates)

## Target State

**Configuration:**
- `.config/typos.toml` exists with project-specific word extensions
- Configuration includes common project terms and identifiers

**Pre-commit Integration:**
- typos hook runs in `pre-commit` stage (source code checking)
- typos hook runs in both `pre-commit` and `commit-msg` stages (source code and commit message checking)
- Both hooks configured to use `.config/typos.toml`
- typos hooks placed before git-sumi in `.pre-commit-config.yaml`
- Hooks fail on typos (no auto-fix in hooks)

**Usage:**
- Developers can run `typos --config .config/typos.toml` manually
- Developers can auto-fix with `typos --config .config/typos.toml --write-changes`
- Pre-commit hooks automatically check spelling on commit

---

## Phase 1: Create typos Configuration File

### 1.1 Create `.config/typos.toml` configuration file

**File**: `.config/typos.toml`

**Task**: Create the typos configuration file with project-specific word extensions

- [x] Create `.config/typos.toml` file
- [x] Add `[default.extend-words]` section
- [x] Add project-specific words:
  - `terraform = "terraform"`
  - `hcl = "hcl"`
  - `moved = "moved"`
  - `maker = "maker"`
- [x] Add `[default.extend-identifiers]` section (optional, for future use)
- [x] Verify TOML syntax is correct
- [x] Verify file is in `.config/` directory (consistent with other configs)

**Expected result:**
```toml
[default.extend-words]
# Add project-specific words
terraform = "terraform"
hcl = "hcl"
moved = "moved"
maker = "maker"

[default.extend-identifiers]
# Allow specific identifiers (add as needed)
# ResourceID = "ResourceID"
```

**Note**: The `extend-identifiers` section is included for future use. Add identifiers as false positives are discovered.

---

## Phase 2: Add typos to Pre-commit Configuration

### 2.1 Add typos repository to `.pre-commit-config.yaml`

**File**: `.pre-commit-config.yaml`

**Location**: Before the git-sumi repository (around line 85)

**Task**: Add typos repository and hooks, ensuring they run before git-sumi

- [x] Open `.pre-commit-config.yaml`
- [x] Locate the git-sumi repository section (starts around line 86)
- [x] Add typos repository section **before** git-sumi
- [x] Use repository URL: `https://github.com/crate-ci/typos`
- [x] Use version: `v1.39.2` (or latest stable version)
- [x] Add `typos` hook for source code and commit message checking:
  - `id: typos`
  - `args: [--config, .config/typos.toml]`
  - `stages: [pre-commit, commit-msg]`
- [x] Verify hooks are placed before git-sumi in the file
- [x] Verify YAML syntax is correct
- [x] Verify indentation matches other repository sections

**Expected result:**
```yaml
  # Spell checking (must run before git-sumi)
  - repo: https://github.com/crate-ci/typos
    rev: v1.39.2  # Use latest version
    hooks:
      - id: typos
        # Check source code and commit messages (fail on typos, don't auto-fix in hooks)
        args: [--config, .config/typos.toml]
        stages: [pre-commit, commit-msg]

  # Commit message validation (Conventional Commits)
  - repo: https://github.com/welpo/git-sumi
    rev: v0.2.0
    hooks:
      - id: git-sumi
        entry: git-sumi
        pass_filenames: true
        args: [--config, .config/sumi.toml, --file]
```

**Note**: The hooks are configured to fail on typos rather than auto-fix them. This ensures typos are caught before commit. Users must manually fix typos or update the configuration to add new words.

---

## Phase 3: Install and Test typos Locally

### 3.1 Install typos CLI tool

**Task**: Install typos using Cargo for local testing

- [x] Run `cargo install typos-cli --locked`
- [x] Verify installation: `typos --version`
- [x] Verify typos is in PATH

**Note**: Installation may take a few minutes. The `--locked` flag ensures reproducible builds.

### 3.2 Test typos configuration

**Task**: Verify the configuration file works correctly

- [x] Run `typos --config .config/typos.toml` to check for typos
- [x] Review any typos found (if any) - Found: `release` typo in VERSION_WORKFLOW_BASH_COMPLEXITY.md (fixed)
- [x] Verify configuration file is being read correctly
- [x] Test with a known typo to ensure it's caught (optional)

**Note**: If typos are found, they should be fixed manually or added to the configuration.

### 3.3 Test pre-commit hook integration

**Task**: Verify pre-commit hooks work correctly

- [x] Update pre-commit hooks: `pre-commit install --install-hooks`
- [x] Test pre-commit hook: `pre-commit run typos --all-files`
- [x] Verify hook runs and uses correct config file
- [x] Test commit-msg hook: `pre-commit run typos --hook-stage commit-msg` (same hook, different stage)
- [x] Verify hook order (typos should run before git-sumi)

**Note**: The `--all-files` flag checks all files, not just staged files. This is useful for initial testing.

### 3.4 Test with a real commit

**Task**: Test the full commit flow

- [ ] Make a small change to a file (e.g., add a comment)
- [ ] Stage the change: `git add <file>`
- [ ] Attempt to commit: `git commit -m "test: verify typos integration"`
- [ ] Verify typos hook runs during pre-commit
- [x] Verify typos hook runs during commit-msg stage
- [ ] Verify commit succeeds if no typos found
- [ ] Test with a typo in commit message (should fail)

**Note**: If a typo is found, the commit will fail. Fix the typo or add the word to `.config/typos.toml` and retry.

---

## Phase 4: Update Configuration Based on Initial Results

### 4.1 Review initial typos findings

**Task**: Review any typos found during initial testing

- [x] Run `typos --config .config/typos.toml` on the entire codebase
- [x] Review all reported typos
- [x] Categorize typos:
  - Actual spelling errors (fix in code) - Fixed typo in VERSION_WORKFLOW_BASH_COMPLEXITY.md
  - False positives (add to config) - None found
  - Technical terms (add to config) - Already configured
  - Identifiers/variable names (add to extend-identifiers if needed) - None needed

### 4.2 Update configuration file

**File**: `.config/typos.toml`

**Task**: Add any necessary words to the configuration

- [ ] Add false positives to `[default.extend-words]`
- [ ] Add technical terms to `[default.extend-words]`
- [ ] Add identifiers to `[default.extend-identifiers]` if needed
- [ ] Verify TOML syntax remains correct
- [ ] Re-run typos to verify false positives are resolved

**Note**: Keep the configuration file organized. Group related words together with comments if helpful.

### 4.3 Fix actual spelling errors

**Task**: Fix any real spelling errors found

- [x] Fix spelling errors in source code
- [x] Use `typos --config .config/typos.toml --write-changes` to auto-fix (optional) - Not needed, fixed manually
- [x] Review auto-fixes before committing
- [ ] Commit fixes separately from typos integration

**Note**: Auto-fix should be reviewed carefully. Some fixes may not be appropriate for technical terms or context-specific words.

---

## Phase 5: Verify GitHub Actions Integration

### 5.1 Check pre-commit hook execution in CI

**Task**: Verify typos runs in GitHub Actions workflows

- [x] Check which workflows run pre-commit hooks - Found: `.github/workflows/pull_request.yaml` has pre-commit job
- [x] Verify pre-commit hooks are installed in workflows - Verified: pre-commit job runs `pre-commit run --all-files --fail-fast`
- [x] Confirm typos will run automatically as part of pre-commit hooks - Confirmed: typos hook is in `.pre-commit-config.yaml` and will run automatically
- [x] Note: No separate typos step needed (handled by pre-commit hooks)

**Note**: Since pre-commit hooks are already run in GitHub Actions workflows, typos will be automatically checked. There is no need to add a separate typos step.

### 5.2 Test in a pull request

**Task**: Create a test PR to verify CI integration

- [ ] Create a feature branch (will be done when committing these changes)
- [ ] Make a small change (typos integration changes)
- [ ] Push branch and create a pull request
- [ ] Verify pre-commit job runs in GitHub Actions
- [ ] Verify typos hook executes successfully
- [ ] Verify no errors related to typos configuration

**Note**: If typos finds errors in CI, the workflow will fail. Fix errors locally and push again.

---

## Phase 6: Documentation and Cleanup

### 6.1 Update project documentation (if needed)

**Task**: Check if any documentation needs updates

- [ ] Check `README.md` for any mention of spell checking
- [ ] Check `CONTRIBUTING.md` or similar files
- [ ] Add note about typos if helpful for contributors
- [ ] Document how to add words to `.config/typos.toml`

**Note**: Documentation updates are optional. The pre-commit hooks will guide users automatically.

### 6.2 Verify hook order

**Task**: Final verification of hook execution order

- [x] Review `.pre-commit-config.yaml` to confirm typos is before git-sumi - Verified: typos is at line 86, git-sumi is at line 95
- [x] Test hook order: `pre-commit run --all-files` - Verified: typos runs after ripsecrets and before git-sumi
- [x] Verify output shows typos running before git-sumi - Verified in hook execution
- [x] Confirm commit-msg hooks run in correct order - Verified: typos (commit-msg) → git-sumi (commit-msg)

**Expected order:**
1. typos (pre-commit stage - source code)
2. typos (commit-msg stage - commit messages)
3. git-sumi (commit-msg stage)

### 6.3 Final testing

**Task**: Comprehensive final test

- [x] Run `typos --config .config/typos.toml` on clean codebase - No typos found
- [x] Verify no unexpected typos found - All typos fixed
- [ ] Test commit with valid commit message (will be done when committing changes)
- [ ] Test commit with typo in commit message (should fail) (can be tested later)
- [ ] Test commit with typo in source code (should fail) (can be tested later)
- [x] Verify all hooks work correctly - All hooks pass

---

## Checklist Summary

### Phase 1: Create typos Configuration File
- [x] Create `.config/typos.toml` configuration file

### Phase 2: Add typos to Pre-commit Configuration
- [x] Add typos repository to `.pre-commit-config.yaml`
- [x] Add typos hooks (pre-commit and commit-msg)
- [x] Verify hooks are before git-sumi

### Phase 3: Install and Test typos Locally
- [ ] Install typos CLI tool
- [ ] Test typos configuration
- [ ] Test pre-commit hook integration
- [ ] Test with a real commit

### Phase 4: Update Configuration Based on Initial Results
- [x] Review initial typos findings
- [x] Update configuration file
- [x] Fix actual spelling errors

### Phase 5: Verify GitHub Actions Integration
- [x] Check pre-commit hook execution in CI
- [ ] Test in a pull request (will be done when changes are committed and PR is created)

### Phase 6: Documentation and Cleanup
- [x] Update project documentation (if needed) - No documentation updates needed, hooks guide users automatically
- [x] Verify hook order - Verified: typos runs before git-sumi
- [x] Final testing - Completed: typos runs successfully, no typos found in codebase

---

## Notes

**Configuration Location:**
- Configuration stored in `.config/typos.toml` for consistency with other project configs
- Must use `--config .config/typos.toml` flag in all typos commands

**Hook Behavior:**
- Hooks are configured to **fail** on typos (no auto-fix)
- Users must manually fix typos or update configuration
- This ensures typos are caught before commit

**Hook Order:**
- typos must run **before** git-sumi
- Order in `.pre-commit-config.yaml` determines execution order
- typos (pre-commit) → typos (commit-msg) → git-sumi (commit-msg)

**CI Integration:**
- No separate typos step needed in GitHub Actions
- Pre-commit hooks already run in workflows
- typos will be checked automatically

**Adding Words:**
- Add false positives to `[default.extend-words]`
- Add identifiers to `[default.extend-identifiers]` if needed
- Keep configuration organized and documented

**Manual Usage:**
- Check: `typos --config .config/typos.toml`
- Auto-fix: `typos --config .config/typos.toml --write-changes`
- Diff: `typos --config .config/typos.toml --diff`

## Related Files

- `.config/typos.toml` - typos configuration file (to be created)
- `.pre-commit-config.yaml` - Pre-commit hooks configuration (to be updated)
- `plan/25W47/TYPOS_SPELL_CHECKING.md` - Decision document

## References

- Decision document: `plan/25W47/TYPOS_SPELL_CHECKING.md`
- [typos Documentation](https://github.com/crate-ci/typos)
- [typos GitHub Action](https://github.com/crate-ci/typos-action)
