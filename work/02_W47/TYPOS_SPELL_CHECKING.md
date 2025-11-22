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
- typos-commit hook runs in `commit-msg` stage (commit message checking)
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

- [ ] Create `.config/typos.toml` file
- [ ] Add `[default.extend-words]` section
- [ ] Add project-specific words:
  - `terraform = "terraform"`
  - `hcl = "hcl"`
  - `moved = "moved"`
  - `maker = "maker"`
- [ ] Add `[default.extend-identifiers]` section (optional, for future use)
- [ ] Verify TOML syntax is correct
- [ ] Verify file is in `.config/` directory (consistent with other configs)

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

- [ ] Open `.pre-commit-config.yaml`
- [ ] Locate the git-sumi repository section (starts around line 86)
- [ ] Add typos repository section **before** git-sumi
- [ ] Use repository URL: `https://github.com/crate-ci/typos`
- [ ] Use version: `v1.39.2` (or latest stable version)
- [ ] Add `typos` hook for source code checking:
  - `id: typos`
  - `args: [--config, .config/typos.toml]`
  - `stages: [pre-commit]`
- [ ] Add `typos-commit` hook for commit message checking:
  - `id: typos-commit`
  - `args: [--config, .config/typos.toml]`
  - `stages: [commit-msg]`
- [ ] Verify hooks are placed before git-sumi in the file
- [ ] Verify YAML syntax is correct
- [ ] Verify indentation matches other repository sections

**Expected result:**
```yaml
  # Spell checking (must run before git-sumi)
  - repo: https://github.com/crate-ci/typos
    rev: v1.39.2  # Use latest version
    hooks:
      - id: typos
        # Check source code (fail on typos, don't auto-fix in hooks)
        args: [--config, .config/typos.toml]
        stages: [pre-commit]
      - id: typos-commit
        # Check commit messages (fail on typos)
        args: [--config, .config/typos.toml]
        stages: [commit-msg]

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

- [ ] Run `cargo install typos-cli --locked`
- [ ] Verify installation: `typos --version`
- [ ] Verify typos is in PATH

**Note**: Installation may take a few minutes. The `--locked` flag ensures reproducible builds.

### 3.2 Test typos configuration

**Task**: Verify the configuration file works correctly

- [ ] Run `typos --config .config/typos.toml` to check for typos
- [ ] Review any typos found (if any)
- [ ] Verify configuration file is being read correctly
- [ ] Test with a known typo to ensure it's caught (optional)

**Note**: If typos are found, they should be fixed manually or added to the configuration.

### 3.3 Test pre-commit hook integration

**Task**: Verify pre-commit hooks work correctly

- [ ] Update pre-commit hooks: `pre-commit install --install-hooks`
- [ ] Test pre-commit hook: `pre-commit run typos --all-files`
- [ ] Verify hook runs and uses correct config file
- [ ] Test commit-msg hook: `pre-commit run typos-commit --hook-stage commit-msg`
- [ ] Verify hook order (typos should run before git-sumi)

**Note**: The `--all-files` flag checks all files, not just staged files. This is useful for initial testing.

### 3.4 Test with a real commit

**Task**: Test the full commit flow

- [ ] Make a small change to a file (e.g., add a comment)
- [ ] Stage the change: `git add <file>`
- [ ] Attempt to commit: `git commit -m "test: verify typos integration"`
- [ ] Verify typos hook runs during pre-commit
- [ ] Verify typos-commit hook runs during commit-msg
- [ ] Verify commit succeeds if no typos found
- [ ] Test with a typo in commit message (should fail)

**Note**: If a typo is found, the commit will fail. Fix the typo or add the word to `.config/typos.toml` and retry.

---

## Phase 4: Update Configuration Based on Initial Results

### 4.1 Review initial typos findings

**Task**: Review any typos found during initial testing

- [ ] Run `typos --config .config/typos.toml` on the entire codebase
- [ ] Review all reported typos
- [ ] Categorize typos:
  - Actual spelling errors (fix in code)
  - False positives (add to config)
  - Technical terms (add to config)
  - Identifiers/variable names (add to extend-identifiers if needed)

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

- [ ] Fix spelling errors in source code
- [ ] Use `typos --config .config/typos.toml --write-changes` to auto-fix (optional)
- [ ] Review auto-fixes before committing
- [ ] Commit fixes separately from typos integration

**Note**: Auto-fix should be reviewed carefully. Some fixes may not be appropriate for technical terms or context-specific words.

---

## Phase 5: Verify GitHub Actions Integration

### 5.1 Check pre-commit hook execution in CI

**Task**: Verify typos runs in GitHub Actions workflows

- [ ] Check which workflows run pre-commit hooks
- [ ] Verify pre-commit hooks are installed in workflows
- [ ] Confirm typos will run automatically as part of pre-commit hooks
- [ ] Note: No separate typos step needed (handled by pre-commit hooks)

**Note**: Since pre-commit hooks are already run in GitHub Actions workflows, typos will be automatically checked. There is no need to add a separate typos step.

### 5.2 Test in a pull request

**Task**: Create a test PR to verify CI integration

- [ ] Create a feature branch
- [ ] Make a small change
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

- [ ] Review `.pre-commit-config.yaml` to confirm typos is before git-sumi
- [ ] Test hook order: `pre-commit run --all-files`
- [ ] Verify output shows typos running before git-sumi
- [ ] Confirm commit-msg hooks run in correct order

**Expected order:**
1. typos (pre-commit stage)
2. typos-commit (commit-msg stage)
3. git-sumi (commit-msg stage)

### 6.3 Final testing

**Task**: Comprehensive final test

- [ ] Run `typos --config .config/typos.toml` on clean codebase
- [ ] Verify no unexpected typos found
- [ ] Test commit with valid commit message
- [ ] Test commit with typo in commit message (should fail)
- [ ] Test commit with typo in source code (should fail)
- [ ] Verify all hooks work correctly

---

## Checklist Summary

### Phase 1: Create typos Configuration File
- [ ] Create `.config/typos.toml` configuration file

### Phase 2: Add typos to Pre-commit Configuration
- [ ] Add typos repository to `.pre-commit-config.yaml`
- [ ] Add typos hooks (pre-commit and commit-msg)
- [ ] Verify hooks are before git-sumi

### Phase 3: Install and Test typos Locally
- [ ] Install typos CLI tool
- [ ] Test typos configuration
- [ ] Test pre-commit hook integration
- [ ] Test with a real commit

### Phase 4: Update Configuration Based on Initial Results
- [ ] Review initial typos findings
- [ ] Update configuration file
- [ ] Fix actual spelling errors

### Phase 5: Verify GitHub Actions Integration
- [ ] Check pre-commit hook execution in CI
- [ ] Test in a pull request

### Phase 6: Documentation and Cleanup
- [ ] Update project documentation (if needed)
- [ ] Verify hook order
- [ ] Final testing

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
- typos (pre-commit) → typos-commit (commit-msg) → git-sumi (commit-msg)

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
- `plan/02_W47/TYPOS_SPELL_CHECKING.md` - Decision document

## References

- Decision document: `plan/02_W47/TYPOS_SPELL_CHECKING.md`
- [typos Documentation](https://github.com/crate-ci/typos)
- [typos GitHub Action](https://github.com/crate-ci/typos-action)
