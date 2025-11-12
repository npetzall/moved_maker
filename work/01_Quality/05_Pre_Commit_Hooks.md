# Phase 5: Pre-commit Hooks Implementation Plan

## Overview
Configure pre-commit hooks to enforce code quality standards before commits, including formatting, linting, testing, and commit message validation.

## Goals
- Enforce code formatting with `cargo fmt`
- Run tests before allowing commits
- Validate commit messages follow Conventional Commits format
- Catch issues early before they reach the repository

## Prerequisites
- [ ] Python 3.7+ installed (for pre-commit framework)
- [ ] Git repository initialized
- [ ] Rust toolchain installed
- [ ] Phase 2 (Test Runner) completed (cargo-nextest installed)
- [ ] Phase 3 (Error Handling) completed or in progress

## Implementation Tasks

### 1. Install pre-commit Framework

#### macOS (Homebrew)
- [ ] Install via Homebrew: `brew install pre-commit`
- [ ] Verify installation: `pre-commit --version`

#### Using uv (Recommended for speed)
- [ ] Install uv (if not already installed): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Install pre-commit: `uv tool install pre-commit` or `uv pip install pre-commit`
- [ ] Verify installation: `pre-commit --version`

#### Using pip
- [ ] Install via pip: `pip install pre-commit`
- [ ] Verify installation: `pre-commit --version`

### 2. Create Pre-commit Configuration

- [ ] Create `.pre-commit-config.yaml` in project root
- [ ] Add general file checks:
  ```yaml
  repos:
    - repo: https://github.com/pre-commit/pre-commit-hooks
      rev: v4.5.0
      hooks:
        - id: trailing-whitespace
        - id: end-of-file-fixer
        - id: check-yaml
        - id: check-toml
        - id: check-json
        - id: check-added-large-files
          args: ['--maxkb=1000']
        - id: check-merge-conflict
        - id: check-case-conflict
  ```
- [ ] Add Rust formatting hook (local):
  ```yaml
    - repo: local
      hooks:
        - id: cargo-fmt
          name: cargo fmt
          entry: bash -c 'cargo fmt --all -- --check'
          language: system
          types: [rust]
          pass_filenames: false
          always_run: true
  ```
- [ ] Add Rust test hook (using cargo-nextest):
  ```yaml
        - id: cargo-test
          name: cargo test (nextest)
          entry: bash -c 'cargo nextest run --all-features --all-targets'
          language: system
          types: [rust]
          pass_filenames: false
          always_run: true
  ```
- [ ] Add Rust clippy hook:
  ```yaml
        - id: cargo-clippy
          name: cargo clippy
          entry: bash -c 'cargo clippy --all-features --all-targets -- -D warnings'
          language: system
          types: [rust]
          pass_filenames: false
          always_run: true
  ```
- [ ] Add commit message validation hook:
  ```yaml
    - repo: https://github.com/compilerla/conventional-pre-commit
      rev: v3.0.0
      hooks:
        - id: conventional-pre-commit
          stages: [commit-msg]
          args:
            - --types
            - 'feat,fix,docs,style,refactor,perf,test,chore,revert'
            - --scopes
            - 'optional'
  ```
- [ ] Verify YAML syntax is correct
- [ ] Commit `.pre-commit-config.yaml` to repository

### 3. Install Pre-commit Hooks

- [ ] Install hooks into `.git/hooks/`: `pre-commit install`
- [ ] Install commit-msg hook: `pre-commit install --hook-type commit-msg`
- [ ] Verify hooks are installed: `ls -la .git/hooks/`
- [ ] Verify pre-commit hook exists: `ls -la .git/hooks/pre-commit`
- [ ] Verify commit-msg hook exists: `ls -la .git/hooks/commit-msg`

### 4. Test Pre-commit Hooks

- [ ] Run all hooks on all files: `pre-commit run --all-files`
- [ ] Review output and fix any issues:
  - [ ] Fix formatting issues: `cargo fmt --all`
  - [ ] Fix clippy warnings: `cargo clippy --all-features --all-targets --fix`
  - [ ] Fix test failures
  - [ ] Fix file check issues (trailing whitespace, etc.)
- [ ] Re-run hooks: `pre-commit run --all-files`
- [ ] Verify all hooks pass

### 5. Test Individual Hooks

- [ ] Test formatting hook: `pre-commit run cargo-fmt --all-files`
- [ ] Test test hook: `pre-commit run cargo-test --all-files`
- [ ] Test clippy hook: `pre-commit run cargo-clippy --all-files`
- [ ] Test commit message hook:
  - [ ] Create test commit with invalid message: `git commit -m "invalid message" --allow-empty --no-verify`
  - [ ] Verify hook rejects invalid message
  - [ ] Create test commit with valid message: `git commit -m "feat: test commit" --allow-empty --no-verify`
  - [ ] Verify hook accepts valid message (or test manually)

### 6. Test Hook Execution on Commit

- [ ] Make a small change to a Rust file
- [ ] Stage the change: `git add <file>`
- [ ] Attempt to commit: `git commit -m "test: verify pre-commit hooks"`
- [ ] Verify hooks run automatically
- [ ] If hooks fail, fix issues and try again
- [ ] Verify commit succeeds when hooks pass

### 7. Test Commit Message Validation

- [ ] Test invalid commit message:
  - [ ] Try: `git commit -m "invalid message" --allow-empty`
  - [ ] Verify hook rejects it
- [ ] Test valid commit messages:
  - [ ] `git commit -m "feat: add new feature" --allow-empty`
  - [ ] `git commit -m "fix: fix bug" --allow-empty`
  - [ ] `git commit -m "docs: update documentation" --allow-empty`
  - [ ] `git commit -m "feat(parser): add support for data blocks" --allow-empty`
- [ ] Verify all valid formats are accepted

### 8. Optimize Hook Performance (if needed)

- [ ] If hooks are slow, consider optimizations:
  - [ ] Use `cargo nextest` instead of `cargo test` (already configured)
  - [ ] Use `--fail-fast` to stop on first failure (if needed)
  - [ ] Run hooks only on changed files (more complex, optional)
- [ ] Test hook execution time
- [ ] Document any performance considerations

### 9. Update Hook Versions

- [ ] Update hook versions to latest: `pre-commit autoupdate`
- [ ] Review updated versions
- [ ] Test updated hooks: `pre-commit run --all-files`
- [ ] Commit updated `.pre-commit-config.yaml` if changes were made

### 10. Handle Doctests (if applicable)

- [ ] Verify if project has doctests: `cargo test --doc`
- [ ] If doctests exist and need to be tested:
  - [ ] Add doctest hook (optional):
    ```yaml
        - id: cargo-doctest
          name: cargo test --doc
          entry: bash -c 'cargo test --doc'
          language: system
          types: [rust]
          pass_filenames: false
          always_run: true
    ```
  - [ ] Or document that doctests should be run separately
- [ ] Test doctest hook (if added)

### 11. Document Pre-commit Usage

- [ ] Update project README with pre-commit information:
  - [ ] How to install pre-commit
  - [ ] How hooks work
  - [ ] How to run hooks manually
  - [ ] How to bypass hooks (not recommended)
- [ ] Document Conventional Commits format:
  - [ ] Commit message format: `<type>(<scope>): <subject>`
  - [ ] Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `revert`
  - [ ] Scope is optional
  - [ ] Examples of valid commit messages
- [ ] Update CONTRIBUTING.md (if exists) with pre-commit requirements
- [ ] Document troubleshooting steps

### 12. Verification

- [ ] All hooks installed and working: `pre-commit run --all-files`
- [ ] Hooks run automatically on commit
- [ ] Commit message validation works
- [ ] All team members can install and use pre-commit
- [ ] Documentation is complete

## Success Criteria

- [ ] pre-commit framework installed
- [ ] `.pre-commit-config.yaml` created and configured
- [ ] Hooks installed in `.git/hooks/`
- [ ] All hooks pass on existing codebase
- [ ] Hooks run automatically on commit
- [ ] Commit message validation works
- [ ] Documentation updated

## Conventional Commits Format

Commit messages must follow this format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `revert`: Reverting a previous commit

### Scope (Optional)
- `parser`: Parser-related changes
- `processor`: Processing logic
- `cli`: CLI interface
- `tests`: Test-related changes

### Examples
```
feat(parser): add support for data blocks
fix(processor): handle empty resource blocks correctly
docs: update README with installation instructions
test(cli): add integration tests for file discovery
chore: update dependencies
```

## Troubleshooting

### Hooks Running Too Slowly
- Use `cargo nextest` instead of `cargo test` (already configured)
- Consider running tests only on changed files (more complex setup)
- Use `--fail-fast` to stop on first failure

### Formatting Hook Fails
- Auto-fix formatting: `cargo fmt --all`
- Then commit again

### Commit Message Validation Fails
- Check the format matches: `<type>(<scope>): <subject>`
- Ensure type is one of the allowed types
- Use imperative mood for the subject

### Clippy Warnings
- Fix warnings manually
- Or allow specific lints in `Cargo.toml` if needed

### Pre-commit Not Running
- Reinstall hooks: `pre-commit uninstall && pre-commit install`
- Verify hooks are installed: `ls -la .git/hooks/`

## Notes

- Pre-commit hooks run locally before commits
- CI integration is handled in Phase 7 (Continuous Delivery)
- Hooks can be bypassed with `--no-verify`, but this is not recommended
- Keep hooks updated with `pre-commit autoupdate`
- Commit message validation uses Conventional Commits format

## References

- [pre-commit Documentation](https://pre-commit.com/)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)
- [conventional-pre-commit](https://github.com/compilerla/conventional-pre-commit)
- [PRE_COMMIT.md](../plan/01_Quality/PRE_COMMIT.md) - Detailed pre-commit documentation

