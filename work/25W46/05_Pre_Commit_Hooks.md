# Phase 5: Pre-commit Hooks Implementation Plan

## Overview
Configure pre-commit hooks to enforce code quality standards before commits, including formatting, linting, testing, security checks, and commit message validation using the pre-commit framework.

## Goals
- Enforce code formatting with `cargo fmt`
- Run tests before allowing commits using `cargo nextest`
- Validate commit messages follow Conventional Commits format using `git-sumi`
- Catch issues early before they reach the repository
- Perform security checks (cargo-deny, cargo-audit, ripsecrets)
- Maintain code quality with clippy and general file checks

## Prerequisites
- Python 3.7+ installed (for pre-commit framework)
- Git repository initialized
- Rust toolchain installed
- Phase 2 (Test Runner) completed (cargo-nextest installed)
- Phase 3 (Error Handling) completed or in progress
- Phase 1 (Security) completed (cargo-deny and cargo-audit configured)

## Implementation Tasks

### 1. Install pre-commit Framework

#### Preferred Method: uv
- [x] Install pre-commit: `uv tool install pre-commit`
- [x] Verify installation: `pre-commit --version`

#### Alternative Installation Methods

**macOS (Homebrew)**:
- [x] Install via Homebrew: `brew install pre-commit`
- [x] Verify installation: `pre-commit --version`

**Using uv pip** (alternative if `uv tool` is not available):
- [x] Install via uv pip: `uv pip install pre-commit`
- [x] Verify installation: `pre-commit --version`

**Using pip**:
- [x] Install via pip: `pip install pre-commit`
- [x] Verify installation: `pre-commit --version`

### 2. Create Pre-commit Configuration

- [x] Create `.pre-commit-config.yaml` in project root
- [x] Copy the complete configuration from `../plan/25W46/REQ_PRE_COMMIT.md` (Configuration section)
- [x] The configuration includes:
  - `default_install_hook_types` (pre-commit and commit-msg)
  - `minimum_pre_commit_version: '3.0.0'`
  - `fail_fast: true`
  - All selected hooks (general file checks, Rust hooks, secret scanning, commit message validation)
- [x] Verify YAML syntax is correct: `pre-commit validate-config` (recommended)
- [x] Commit `.pre-commit-config.yaml` to repository

### 3. Configure git-sumi (Commit Message Validation)

- [x] Manually create `.config/sumi.toml` file (since git-sumi is managed by pre-commit hook)
- [x] Copy the `.config/sumi.toml` configuration from `../plan/25W46/PRE_COMMIT_HOOKS.md` (git-sumi Configuration section)
- [x] Review configuration options (see `../plan/25W46/PRE_COMMIT_HOOKS.md` for detailed explanations)
- [x] Update `.pre-commit-config.yaml` to include `args: [--config, .config/sumi.toml, --file]` for git-sumi hook
- [x] Commit `.config/sumi.toml` to repository

### 4. Install Pre-commit Hooks

- [x] Install hooks into `.git/hooks/`: `pre-commit install`
  - Note: With `default_install_hook_types` configured in `.pre-commit-config.yaml` (from Section 2), this automatically installs both `pre-commit` and `commit-msg` hook types
  - If `default_install_hook_types` is not configured, you'll need to run: `pre-commit install --hook-type commit-msg` separately
- [x] Verify hooks are installed: `ls -la .git/hooks/`
- [x] Verify pre-commit hook exists: `ls -la .git/hooks/pre-commit`
- [x] Verify commit-msg hook exists: `ls -la .git/hooks/commit-msg`

### 5. Test Pre-commit Hooks

- [x] Run all hooks on all files: `pre-commit run --all-files`
- [x] Review output and fix any issues:
  - [x] Fix formatting issues: `cargo fmt --all`
  - [x] Fix clippy warnings: Manually fix warnings, or use `cargo clippy --fix --all-features --all-targets` (note: only applies automatic fixes, manual fixes may be required)
  - [x] Fix test failures: Review test output, fix failing tests, ensure all tests pass
  - [x] Fix file check issues: Some hooks auto-fix issues when run manually (e.g., `trailing-whitespace`, `end-of-file-fixer`). Run `pre-commit run <hook-id> --all-files` (e.g., `pre-commit run trailing-whitespace --all-files`) to auto-fix, or fix manually
  - [x] Fix security issues: Review output from cargo-deny, cargo-audit, or ripsecrets. Update dependencies, fix license issues, or remove detected secrets as needed
- [x] Re-run hooks: `pre-commit run --all-files`
- [x] Verify all hooks pass

### 6. Test Individual Hooks

- [x] Test formatting hook: `pre-commit run cargo-fmt --all-files`
- [x] Test compilation check: `pre-commit run cargo-check --all-files`
- [x] Test clippy hook: `pre-commit run cargo-clippy --all-files`
- [x] Test test hook: `pre-commit run cargo-test --all-files`
- [x] Test cargo-deny hook: `pre-commit run cargo-deny --all-files`
- [x] Test cargo-audit hook: `pre-commit run cargo-audit --all-files`
- [x] Test ripsecrets hook: `pre-commit run ripsecrets --all-files`
- [x] Test general file checks: `pre-commit run trailing-whitespace --all-files`
- [x] Test commit message hook (optional but recommended - see Section 8 for comprehensive testing) (manual):
  - [x] Create test commit with invalid message: `git commit -m "invalid message" --allow-empty`
  - [x] Verify hook rejects invalid message (should fail with error)
  - [x] Create test commit with valid message: `git commit -m "feat: test commit" --allow-empty`
  - [x] Verify hook accepts valid message (should succeed)

### 7. Test Hook Execution on Commit (manual)

- [x] Make a small change to a Rust file (e.g., add a comment)
- [x] Stage the change: `git add <file>` (replace `<file>` with the actual file path)
- [x] Attempt to commit: `git commit -m "test: verify pre-commit hooks"`
- [x] Verify hooks run automatically
- [x] If hooks fail, fix issues and try again
- [x] Verify commit succeeds when hooks pass

### 8. Test Commit Message Validation (manual)

**Note**: This section provides comprehensive testing of commit message validation. Section 6 includes a quick test, but this section covers all validation scenarios.

- [x] Test invalid commit messages:
  - [x] Try: `git commit -m "invalid message" --allow-empty`
  - [x] Verify hook rejects it (should fail with error)
  - [x] Try: `git commit -m "feat" --allow-empty`
  - [x] Verify hook rejects it (missing subject - should fail with error)
- [x] Test valid commit messages:
  - [x] `git commit -m "feat: add new feature" --allow-empty`
  - [x] `git commit -m "fix: fix bug" --allow-empty`
  - [x] `git commit -m "docs: update documentation" --allow-empty`
  - [x] `git commit -m "feat(parser): add support for data blocks" --allow-empty`
  - [x] `git commit -m "fix(processor): handle empty resource blocks correctly" --allow-empty`
- [x] Verify all valid formats are accepted (should succeed)

### 9. Optimize Hook Performance (if needed)

**Note**: Only perform this step if hook execution takes more than 30-60 seconds or causes workflow disruption.

- [x] Measure hook execution time: `time pre-commit run --all-files`
  - **Result**: Execution time is **5.724 seconds**, which is well under the 30-60 second threshold
  - **Conclusion**: Optimization is **not needed** - hooks are running efficiently
- [x] If hooks are slow, consider optimizations:
  - [x] Use `cargo nextest` instead of `cargo test` (already configured)
  - [ ] Use `--fail-fast` to stop on first failure: Update the cargo-test hook entry to include `--fail-fast` flag (e.g., `cargo nextest run --all-features --all-targets --fail-fast`) - **Not needed** (performance is acceptable)
  - [ ] Run hooks only on changed files (more complex, optional) - **Not needed** (performance is acceptable)
  - [ ] Consider running tests only in CI, not in pre-commit (trade-off) - **Not needed** (performance is acceptable)
- [x] Document any performance considerations
  - **Performance**: Hooks execute in ~5.7 seconds, which is acceptable for pre-commit workflow

### 10. Update Hook Versions (During Initial Setup)

**Note**: This step updates hook versions to the latest during initial setup. For ongoing maintenance, see Section 11.

- [x] Update hook versions to latest: `pre-commit autoupdate`
- [x] Review updated versions: `git diff .pre-commit-config.yaml`
- [x] Test updated hooks: `pre-commit run --all-files`
- [x] Commit updated `.pre-commit-config.yaml` if changes were made: `git commit -m "chore: update pre-commit hooks"`

### 11. Security and Maintenance Setup

- [x] Document hook update workflow (for ongoing maintenance):
  - [x] Check current status: `pre-commit run --all-files`
  - [x] Update hooks: `pre-commit autoupdate`
  - [x] Review changes: `git diff .pre-commit-config.yaml`
  - [x] Test updated hooks: `pre-commit run --all-files`
  - [x] Commit updates: `git commit -m "chore: update pre-commit hooks"`
- [x] Verify hook versions are pinned (not using branch references)
- [x] Document security best practices:
  - [x] Regular updates (weekly/monthly)
  - [x] Review changes after autoupdate
  - [x] Pin versions (use tags, not branches)
  - [x] Monitor security advisories for hook repositories

### 12. Document Pre-commit Usage

- [x] Update project README with pre-commit information:
  - [x] How to install pre-commit (preferred: `uv tool install pre-commit`)
  - [x] How hooks work
  - [x] How to run hooks manually: `pre-commit run --all-files`
  - [x] How to run specific hook: `pre-commit run <hook-id> --all-files` (e.g., `pre-commit run cargo-fmt --all-files`)
  - [x] How to bypass hooks (not recommended): `git commit --no-verify`
  - [x] How to update hooks: `pre-commit autoupdate`
- [x] Document Conventional Commits format:
  - [x] Commit message format: `<type>(<scope>): <subject>`
  - [x] Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert` (configured in `.config/sumi.toml`)
  - [x] Scope is optional
  - [x] Examples of valid commit messages
  - [x] Reference to `.config/sumi.toml` for complete configuration (see `../plan/25W46/PRE_COMMIT_HOOKS.md` - git-sumi Configuration section)
  - [x] Note that `.config/sumi.toml` must be manually created (git-sumi is managed by pre-commit)
  - [x] Pre-commit hook configured with `args: [--config, .config/sumi.toml, --file]` to use the config file
- [x] Update CONTRIBUTING.md with pre-commit requirements (create file if it doesn't exist)
- [x] Document troubleshooting steps (see Troubleshooting section below)

### 13. Verification

- [x] All hooks installed and working: `pre-commit run --all-files`
- [x] Hooks run automatically on commit
- [x] Commit message validation works (manual)
- [x] Security hooks (cargo-deny, cargo-audit, ripsecrets) are working
- [x] All team members can install and use pre-commit
- [x] Documentation is complete

## Success Criteria

- [x] pre-commit framework installed
- [x] `.pre-commit-config.yaml` created and configured with all selected hooks
- [x] `.config/sumi.toml` manually created and configured with Conventional Commits rules
- [x] Hooks installed in `.git/hooks/`
- [x] All hooks pass on existing codebase
- [x] Hooks run automatically on commit
- [x] Commit message validation works with git-sumi (manual)
- [x] Security hooks (cargo-deny, cargo-audit, ripsecrets) are functional
- [x] Documentation updated

## Conventional Commits Format

Commit messages must follow this format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Note**: The commit message format is enforced by `git-sumi` using the configuration in `.config/sumi.toml`. See the `.config/sumi.toml` configuration in `../plan/25W46/PRE_COMMIT_HOOKS.md` (git-sumi Configuration section) for the complete configuration.

### Type
Allowed types are configured in `.config/sumi.toml` (see `../plan/25W46/PRE_COMMIT_HOOKS.md`). Standard types include:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes
- `revert`: Reverting a previous commit

### Scope (Optional)
The scope specifies the area of the codebase affected:
- `parser`: Parser-related changes
- `processor`: Processing logic
- `cli`: CLI interface
- `tests`: Test-related changes

### Subject
Subject rules are enforced by `.config/sumi.toml` configuration (see `../plan/25W46/PRE_COMMIT_HOOKS.md` for complete configuration):
- Use imperative mood: "add" not "added" or "adds" (enforced by `imperative = true`)
- First letter lowercase (enforced by `description_case = "lower"`)
- No period at the end (enforced by `no_period = true`)
- Maximum 72 characters (enforced by `max_header_length = 72`)

### Examples
```
feat(parser): add support for data blocks
fix(processor): handle empty resource blocks correctly
docs: update README with installation instructions
test(cli): add integration tests for file discovery
chore: update dependencies
```

## Selected Hooks Summary

### Required Hooks
1. **cargo-fmt**: Rust code formatting
2. **cargo-test** (nextest): Run tests before commit
3. **git-sumi**: Commit message validation (Conventional Commits)

### Recommended Hooks
4. **cargo-clippy**: Rust linting and best practices
5. **pre-commit-hooks**: General file checks (trailing whitespace, YAML/TOML/JSON validation, etc.)

### Optional but Recommended Hooks
6. **cargo-check**: Fast compilation check
7. **cargo-deny**: License compliance, vulnerability detection, banned dependencies
8. **cargo-audit**: Vulnerability scanning using RustSec Advisory Database
9. **ripsecrets**: Secret scanning to prevent accidental secret commits

## Troubleshooting

### Hooks Running Too Slowly
- `cargo nextest` is already configured (faster than `cargo test`)
- Consider running tests only on changed files (more complex setup)
- Use `--fail-fast` to stop on first failure: `cargo nextest run --fail-fast`
- Consider running tests only in CI, not in pre-commit (trade-off)

### Formatting Hook Fails (`cargo fmt`)
- Auto-fix formatting: `cargo fmt --all`
- Then commit again: `git add . && git commit -m "style: format code"`

### Commit Message Validation Fails (`git-sumi`)
- Check the format matches: `<type>(<scope>): <subject>` (e.g., `feat(parser): add support for data blocks`)
- Ensure type is one of the allowed types (see `.config/sumi.toml` configuration in `../plan/25W46/PRE_COMMIT_HOOKS.md`)
- Use imperative mood for the subject (e.g., "add feature" not "added feature")
- Ensure description starts with lowercase (if `description_case = "lower"` is set)
- Ensure header doesn't end with a period (if `no_period = true` is set)
- Ensure header doesn't exceed 72 characters (if `max_header_length = 72` is set)
- Manually create `.config/sumi.toml` file if it doesn't exist (since git-sumi is managed by pre-commit)
- Copy the `.config/sumi.toml` configuration from `../plan/25W46/PRE_COMMIT_HOOKS.md` (git-sumi Configuration section)
- Ensure `.pre-commit-config.yaml` includes `args: [--config, .config/sumi.toml, --file]` for git-sumi hook
- Review `.config/sumi.toml` for custom rules and type definitions
- Test your commit message: If git-sumi is in PATH, use `git sumi --display`. Otherwise, test via pre-commit by attempting a commit: `git commit -m "your message" --allow-empty` (the hook will validate it)

### Clippy Warnings (`cargo clippy`)
- Fix warnings manually
- Or allow specific lints in `Cargo.toml`:
  ```toml
  [lints.clippy]
  # Allow specific lints if needed
  ```

### Security Hook Failures
- **cargo-deny**: Review `.config/deny.toml` configuration, fix license or vulnerability issues
- **cargo-audit**: Update dependencies or add exceptions if needed
- **ripsecrets**: Review detected secrets, ensure they are false positives or remove actual secrets

### Pre-commit Not Running
- Verify pre-commit is installed: `pre-commit --version`
- Reinstall hooks: `pre-commit uninstall && pre-commit install`
- Verify hooks are installed: `ls -la .git/hooks/`
- Check if hooks are executable: `chmod +x .git/hooks/pre-commit`

### Hook Update Issues
- Review changes after `pre-commit autoupdate`: `git diff .pre-commit-config.yaml`
- Test updated hooks before committing: `pre-commit run --all-files`
- If issues occur, revert to previous version

## Best Practices

1. **Run hooks before pushing**: Always run `pre-commit run --all-files` before pushing
2. **Keep hooks updated**: Regularly run `pre-commit autoupdate` (weekly/monthly)
3. **Review updates**: Always review changes after `pre-commit autoupdate` before committing
4. **Check for vulnerabilities**: Regularly scan for vulnerabilities in hook dependencies
5. **Pin versions**: Use specific tags (e.g., `v4.5.0`) rather than branches in configuration
6. **Don't bypass hooks**: Avoid `--no-verify` unless absolutely necessary
7. **Fix issues immediately**: Don't accumulate formatting or test failures
8. **Document exceptions**: If a hook needs to be disabled, document why

## Notes

- Pre-commit hooks run locally before commits
- CI integration is handled in Phase 7 (Continuous Delivery)
- Hooks can be bypassed with `--no-verify`, but this is not recommended
- Keep hooks updated with `pre-commit autoupdate` (weekly/monthly recommended)
- Commit message validation uses git-sumi (Rust-native tool)
- Security hooks (cargo-deny, cargo-audit, ripsecrets) are fast enough for pre-commit
- All selected hooks have been verified for performance and compatibility

## References

- [pre-commit Documentation](https://pre-commit.com/)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [git-sumi Documentation](https://sumi.rs/) - Commit message validation (Rust-native)
- [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks) - General file checks
- [ripsecrets](https://github.com/sirwart/ripsecrets) - Secret scanning
- [cargo-deny](https://github.com/embarkstudios/cargo-deny) - Security scanning
- [cargo-audit](https://github.com/rustsec/rustsec/tree/main/cargo-audit) - Vulnerability scanning
- [REQ_PRE_COMMIT.md](../plan/25W46/REQ_PRE_COMMIT.md) - Detailed pre-commit framework documentation
- [PRE_COMMIT_HOOKS.md](../plan/25W46/PRE_COMMIT_HOOKS.md) - Detailed hook selection and configuration
