# Pre-commit Hooks

## Overview
Pre-commit hooks ensure code quality standards are enforced before commits are made. This includes running tests, checking code formatting, and validating commit messages follow the Conventional Commits specification.

The pre-commit framework provides a unified interface for managing git hooks across different tools and languages, ensuring consistent quality checks for all contributors.

## Goals

1. **Enforce Code Quality**: Run tests before allowing commits
2. **Maintain Formatting**: Ensure code is properly formatted with `cargo fmt`
3. **Validate Commit Messages**: Ensure commit messages follow Conventional Commits format
4. **Prevent Bad Commits**: Catch issues early before they reach the repository

## Status

✅ **Selected** - The pre-commit framework has been selected for the project. It will be configured and installed as part of the quality tooling implementation.

## Installation

### Prerequisites

- Python 3.7+ (for pre-commit framework)
- Git repository initialized
- Rust toolchain installed

### Install pre-commit

**uv** (preferred - fastest and most reliable):
```bash
uv tool install pre-commit
```

Alternative installation methods:

**macOS (Homebrew)**:
```bash
brew install pre-commit
```

**uv pip** (alternative if `uv tool` is not available):
```bash
uv pip install pre-commit
```

### Initialize pre-commit

After installation, initialize pre-commit in the repository:

```bash
pre-commit install
```

This installs the git hooks into `.git/hooks/`. With `default_install_hook_types` configured in `.pre-commit-config.yaml`, this command automatically installs both the `pre-commit` and `commit-msg` hook types.

## Configuration

Create a `.pre-commit-config.yaml` file in the project root with the following complete configuration based on selected hooks:

```yaml
default_install_hook_types:
  - pre-commit
  - commit-msg

minimum_pre_commit_version: '4.4.0'

fail_fast: true

repos:
  # General file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
        args: [--markdown-linebreak-ext=md]
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: check-case-conflict

  # Rust formatting, linting, and testing
  - repo: local
    hooks:
      - id: cargo-fmt
        name: cargo fmt
        entry: bash -c 'cargo fmt --all -- --check'
        language: system
        types: [rust]
        pass_filenames: false
        stages: [pre-commit]

      - id: cargo-check
        name: cargo check
        entry: bash -c 'cargo check --all-features --all-targets'
        language: system
        types: [rust]
        pass_filenames: false
        stages: [pre-commit]

      - id: cargo-clippy
        name: cargo clippy
        entry: bash -c 'cargo clippy --all-features --all-targets -- -D warnings'
        language: system
        types: [rust]
        pass_filenames: false
        stages: [pre-commit]

      - id: cargo-test
        name: cargo test (nextest)
        entry: bash -c 'cargo nextest run --all-features --all-targets'
        language: system
        types: [rust]
        pass_filenames: false
        always_run: true
        stages: [pre-commit]

      - id: cargo-deny
        name: cargo deny check
        entry: bash -c 'cargo deny check'
        language: system
        types: [rust]
        pass_filenames: false
        always_run: true
        stages: [pre-commit]

      - id: cargo-audit
        name: cargo audit
        entry: bash -c 'cargo audit --deny warnings'
        language: system
        types: [rust]
        pass_filenames: false
        always_run: true
        stages: [pre-commit]

  # Secret scanning
  - repo: https://github.com/sirwart/ripsecrets
    rev: v0.1.11
    hooks:
      - id: ripsecrets

  # Commit message validation (Conventional Commits)
  - repo: https://github.com/welpo/git-sumi
    rev: v0.2.0
    hooks:
      - id: git-sumi
        stages: [commit-msg]
        pass_filenames: true
```

See `PRE_COMMIT_HOOKS.md` for detailed hook information, selection criteria, configuration details, and the `sumi.toml` configuration for commit message validation.

## Usage

### Running Hooks Manually

Run all hooks on all files:
```bash
pre-commit run --all-files
```

Run a specific hook:
```bash
pre-commit run cargo-fmt --all-files
```

Run hooks on staged files only:
```bash
pre-commit run
```

### Bypassing Hooks (Not Recommended)

If you need to bypass hooks (e.g., for emergency fixes):
```bash
git commit --no-verify
```

**Warning**: Only use `--no-verify` in exceptional circumstances. It defeats the purpose of quality gates.

### Updating Hooks

#### Standard Update Method

Update hook versions to their latest releases:
```bash
pre-commit autoupdate
```

This updates all hook versions in `.pre-commit-config.yaml` to their latest releases. Always review changes before committing:
```bash
# 1. Update hooks
pre-commit autoupdate

# 2. Review changes
git diff .pre-commit-config.yaml

# 3. Test updated hooks
pre-commit run --all-files

# 4. Commit updates
git add .pre-commit-config.yaml
git commit -m "chore: update pre-commit hooks"
```

#### Advanced Update Tool (Optional)

For more control over updates, you can use `pre-commit-update` which provides additional features:
- Update by hash instead of tags
- Define custom tag prefixes
- Exclude specific repositories from updates
- Can be configured as a pre-commit hook itself

**Installation** (using uv):
```bash
uv tool install pre-commit-update
```

**Usage**:
```bash
pre-commit-update
```

**Note**: `pre-commit autoupdate` is the standard and recommended method. Use `pre-commit-update` only if you need its advanced features.

## Integration with CI/CD

Pre-commit hooks run locally, but they should also be enforced in CI:

### GitHub Actions Example

```yaml
name: Pre-commit Checks

on: [push, pull_request]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: dtolnay/rust-toolchain@stable

      - name: Install pre-commit
        run: pip install pre-commit

      - name: Install cargo-nextest
        uses: taiki-e/install-action@cargo-nextest

      - name: Run pre-commit
        run: pre-commit run --all-files
```

This ensures that even if someone bypasses local hooks, CI will catch issues.

## Security and Maintenance

### Checking for Vulnerabilities

Pre-commit hooks should be regularly checked for vulnerabilities and kept up-to-date:

#### 1. Regular Hook Updates

Keep hooks updated to receive security patches:
```bash
# Update all hooks to latest versions
pre-commit autoupdate

# Review changes
git diff .pre-commit-config.yaml

# Test updated hooks
pre-commit run --all-files
```

#### 2. Vulnerability Scanning

Scan pre-commit dependencies for known vulnerabilities:

**Using Snyk** (if available):
```bash
# Scan Python dependencies (if pre-commit is installed via pip)
snyk test --file=requirements.txt
```

**Using GitHub Dependabot**:
- Enable Dependabot alerts in your repository settings
- Configure it to monitor Python dependencies if pre-commit is installed via pip

**Using Security Advisories**:
- Monitor security advisories for hook repositories:
  - `pre-commit/pre-commit-hooks`
  - `welpo/git-sumi`
  - `sirwart/ripsecrets`
  - Any other hook repositories you use

#### 3. Verify Hook Integrity

Pre-commit uses pinned revisions (tags/commits) for security. Always pin specific versions in your configuration:
```yaml
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0  # ✅ Pinned version (secure)
  hooks:
    ...
```

**Avoid**:
```yaml
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: main  # ❌ Branch reference (less secure)
```

#### 4. Check Installed Hook Versions

Verify what versions are currently installed:
```bash
# See what versions are running
pre-commit run --all-files --verbose

# Check the cache location
ls -la ~/.cache/pre-commit/
```

### Best Practices for Security

1. **Regular Updates**: Run `pre-commit autoupdate` periodically (weekly/monthly)
2. **Review Changes**: Always review what changed after autoupdate
3. **Pin Versions**: Use specific tags (e.g., `v4.5.0`) rather than branches
4. **CI/CD Integration**: Add a check in CI to verify hooks are up-to-date
5. **Security Scanning**: Include pre-commit dependencies in your security scanning pipeline
6. **Monitor Advisories**: Subscribe to security advisories for hook repositories

### Recommended Update Workflow

```bash
# 1. Check current status
pre-commit run --all-files

# 2. Update hooks
pre-commit autoupdate

# 3. Review the changes
git diff .pre-commit-config.yaml

# 4. Test updated hooks
pre-commit run --all-files

# 5. Commit the updates
git add .pre-commit-config.yaml
git commit -m "chore: update pre-commit hooks"
```

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

The scope specifies the area of the codebase affected:
- `parser`: Parser-related changes
- `processor`: Processing logic
- `cli`: CLI interface
- `tests`: Test-related changes

### Subject

- Use imperative mood: "add" not "added" or "adds"
- First letter lowercase
- No period at the end
- Maximum 72 characters

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

If hooks are slow:
1. `cargo nextest` is already configured (faster than `cargo test`)
2. Consider running tests only on changed files (more complex setup)
3. Use `--fail-fast` to stop on first failure: `cargo nextest run --fail-fast`
4. Consider running tests only in CI, not in pre-commit (trade-off)

### Formatting Hook Fails

If formatting fails:
```bash
# Auto-fix formatting
cargo fmt --all

# Then commit again
git add .
git commit -m "style: format code"
```

### Commit Message Validation Fails

If commit message validation fails:
- Check the format matches: `<type>(<scope>): <subject>`
- Ensure type is one of the allowed types (configured in `sumi.toml`)
- Use imperative mood for the subject
- Initialize configuration if needed: `git sumi --init` (creates `sumi.toml`)
- Review `sumi.toml` for custom rules and type definitions

### Clippy Warnings

If clippy fails:
1. Fix the warnings manually
2. Or allow specific lints in `Cargo.toml`:
```toml
[lints.clippy]
# Allow specific lints if needed
```

See `PRE_COMMIT_HOOKS.md` for more detailed troubleshooting information for specific hooks.

### Pre-commit Not Running

If hooks aren't running:
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Verify hooks are installed
ls -la .git/hooks/
```

## Best Practices

1. **Run hooks before pushing**: Always run `pre-commit run --all-files` before pushing
2. **Keep hooks updated**: Regularly run `pre-commit autoupdate` (weekly/monthly)
3. **Review updates**: Always review changes after `pre-commit autoupdate` before committing
4. **Check for vulnerabilities**: Regularly scan for vulnerabilities in hook dependencies
5. **Pin versions**: Use specific tags (e.g., `v4.5.0`) rather than branches in configuration
6. **Don't bypass hooks**: Avoid `--no-verify` unless absolutely necessary
7. **Fix issues immediately**: Don't accumulate formatting or test failures
8. **Document exceptions**: If a hook needs to be disabled, document why

## Implementation Steps

1. Install pre-commit framework
2. Create `.pre-commit-config.yaml` in project root
3. Configure hooks for:
   - Rust formatting (`cargo fmt`)
   - Tests (`cargo nextest`)
   - Commit message validation (Conventional Commits via `git-sumi`)
   - Recommended: Clippy checks (`cargo clippy`)
   - Recommended: General file checks (`pre-commit-hooks`)
   - Recommended: Security hooks (`cargo-deny`, `cargo-audit`, `ripsecrets`)

   See `PRE_COMMIT_HOOKS.md` for complete configuration examples.
4. Install hooks: `pre-commit install`
5. Test hooks: `pre-commit run --all-files`
6. Add CI workflow to enforce hooks in CI
7. Document in project README

## Related Documents

- `PRE_COMMIT_HOOKS.md` - Detailed hook information for investigation and selection

## References

- [pre-commit Documentation](https://pre-commit.com/)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- See `PRE_COMMIT_HOOKS.md` for hook-specific references
