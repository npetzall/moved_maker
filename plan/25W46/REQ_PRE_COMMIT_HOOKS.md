# Pre-commit Hooks - Selected Hooks

## Overview

This document contains information about selected pre-commit hooks for this project. See `PRE_COMMIT.md` for general pre-commit framework documentation. For hooks that were considered but not selected, see `PRE_COMMIT_HOOK_CONSIDERATION.md`.

## Selected Hook Repositories

### General File Checks ✅ Selected

**Repository**: `https://github.com/pre-commit/pre-commit-hooks`  
**Version**: `v6.0.0`

Common hooks for file validation and basic checks:

```yaml
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
```

**Available Hooks**:
- `trailing-whitespace`: Trims trailing whitespace (preserves trailing whitespace in markdown files where it's used for line breaks via `--markdown-linebreak-ext=md`)
- `end-of-file-fixer`: Ensures files end with a newline
- `check-yaml`: Validates YAML syntax
- `check-toml`: Validates TOML syntax
- `check-json`: Validates JSON syntax
- `check-added-large-files`: Prevents committing large files (configurable size)
- `check-merge-conflict`: Detects merge conflict markers
- `check-case-conflict`: Detects case conflicts in filenames

### Commit Message Validation

**git-sumi** (Rust) ✅ Selected
- **Repository**: `https://github.com/welpo/git-sumi`
- **Language**: Rust (89.8%)
- **GitHub Stars**: 29 stars
- **Maintenance Status**: ✅ Actively maintained (latest release 0.2.0 on Aug 30, 2024)
- **Features**:
  - Non-opinionated Rust-based commit message linter
  - Customizable rules (Conventional Commits, length limits, Gitmoji, etc.)
  - Clear error reporting with detailed messages
  - Single binary for easy integration
  - GitHub Action available
- **Pre-commit Integration**: ✅ Yes (has `.pre-commit-hooks.yaml` - can be used as pre-commit repository)
- **Custom Types**: ✅ Supported via `.config/sumi.toml` configuration
- **Installation**: Pre-commit handles installation automatically when used as repository. Can also be installed manually: `cargo install git-sumi`, `pip install git-sumi`, `uv tool install git-sumi`, or via Chocolatey
- **Configuration**: Uses `.config/sumi.toml` file (can be initialized with `git sumi --init config`)
- **Documentation**: https://sumi.rs/
- **Note**: Small but active project with good documentation. When used as pre-commit repository, installation is handled automatically by the pre-commit framework.

#### git-sumi Configuration (`.config/sumi.toml`)

Recommended `.config/sumi.toml` configuration for enforcing Conventional Commits:

```toml
# Enable Conventional Commits specification
conventional = true

# Enforce imperative mood in commit descriptions
# Matches Git's own built-in messages (e.g., "Merge" not "Merged")
imperative = true

# Ensure commit descriptions are lowercase
description_case = "lower"

# Prohibit ending commit headers with a period
no_period = true

# Restrict commit header to 72 characters (Git standard)
max_header_length = 72

# Limit commit types to standard Conventional Commits types
# Automatically enables the 'conventional' rule
types_allowed = [
  "feat",     # New feature
  "fix",      # Bug fix
  "docs",     # Documentation changes
  "style",    # Code style changes (formatting, missing semicolons, etc.)
  "refactor", # Code refactoring
  "test",     # Adding or updating tests
  "chore",    # Maintenance tasks
  "perf",     # Performance improvements
  "ci",       # CI/CD changes
  "build",    # Build system changes
  "revert",   # Revert previous commit
]

# Disallow leading/trailing whitespace and consecutive spaces
whitespace = true

# Suppress progress messages (optional, set to false for verbose output)
quiet = false
```

**Configuration Options Explained**:
- `conventional = true`: Enforces the [Conventional Commits](https://www.conventionalcommits.org/) specification format: `<type>(<scope>): <subject>`
- `imperative = true`: Requires imperative mood (e.g., "Add feature" not "Added feature") to match Git's conventions
- `description_case = "lower"`: Ensures commit descriptions start with lowercase (common convention)
- `no_period = true`: Prevents periods at the end of commit headers (like email subject lines)
- `max_header_length = 72`: Enforces Git's recommended header length limit
- `types_allowed`: Restricts commit types to standard Conventional Commits types (automatically enables `conventional`)
- `whitespace = true`: Prevents whitespace issues that can affect tooling

**Initialization**: Since `git-sumi` is installed and managed by the pre-commit hook, manually create a `.config/sumi.toml` file with the configuration above. The pre-commit hook is configured to use this configuration file via `--config .config/sumi.toml --file` arguments when validating commit messages.

**References**:
- [git-sumi Configuration Documentation](https://sumi.rs/docs/configuration)
- [git-sumi Rules Documentation](https://sumi.rs/docs/rules)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)

**Note**: For information about alternative commit message validation tools that were considered but not selected, see `PRE_COMMIT_HOOK_CONSIDERATION.md`.

## Alternative: Local Hooks (cargo-nextest) ✅ Selected

For more control or when using `cargo-nextest`, use local hooks:

```yaml
- repo: local
  hooks:
    - id: cargo-fmt
      name: cargo fmt
      entry: bash -c 'cargo fmt --all -- --check'
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

    - id: cargo-clippy
      name: cargo clippy
      entry: bash -c 'cargo clippy --all-features --all-targets -- -D warnings'
      language: system
      types: [rust]
      pass_filenames: false
      stages: [pre-commit]
```

## Additional Rust Hooks

### Compilation Check (`cargo check`) ✅ Selected

A fast compilation check that verifies code compiles without producing binaries:

```yaml
- repo: local
  hooks:
    - id: cargo-check
      name: cargo check
      entry: bash -c 'cargo check --all-features --all-targets'
      language: system
      types: [rust]
      pass_filenames: false
      stages: [pre-commit]
```

**Benefits**:
- ✅ Faster than full build (no code generation)
- ✅ Catches compilation errors early
- ✅ Useful for quick validation before tests

**Note**: Can be redundant if running `cargo nextest` (which also compiles), but useful for faster feedback.

### Security Hooks

#### cargo-deny ✅ Selected

Comprehensive security scanning for licenses, vulnerabilities, and banned dependencies:

```yaml
- repo: local
  hooks:
      - id: cargo-deny
        name: cargo deny check
        entry: bash -c 'cargo deny check --config .config/deny.toml'
        language: system
        types: [rust]
        pass_filenames: false
        always_run: true
        stages: [pre-commit]
```

**Configuration**: Requires `.config/deny.toml` file (already configured in this project)

**Benefits**:
- ✅ License compliance checking
- ✅ Vulnerability detection
- ✅ Banned dependency detection
- ✅ Source registry validation

**Performance**: ~0.67 seconds (measured) - **Fast enough for pre-commit** ✅

#### cargo-audit ✅ Selected

Vulnerability scanning using RustSec Advisory Database:

```yaml
- repo: local
  hooks:
    - id: cargo-audit
      name: cargo audit
      entry: bash -c 'cargo audit --deny warnings'
      language: system
      types: [rust]
      pass_filenames: false
      always_run: true
      stages: [pre-commit]
```

**Benefits**:
- ✅ Fast vulnerability scanning
- ✅ Uses RustSec Advisory Database
- ✅ Can be used alongside cargo-deny for redundancy

**Performance**: ~1.09 seconds (measured) - **Fast enough for pre-commit** ✅

### Secret Scanning (ripsecrets) ✅ Selected

Scans codebase for secrets and sensitive information:

```yaml
- repo: https://github.com/sirwart/ripsecrets
  rev: v0.1.11
  hooks:
    - id: ripsecrets
```

**Installation**: Pre-commit handles installation automatically when used as repository. Can also be installed manually: `cargo install --git https://github.com/sirwart/ripsecrets --branch main`, `brew install ripsecrets`, or download pre-built binaries.

**Benefits**:
- ✅ Prevents accidental secret commits
- ✅ Scans for API keys, passwords, tokens
- ✅ Extremely fast execution (95x faster than alternatives)
- ✅ Always local operation (never sends data to 3rd party services)
- ✅ Low rate of false positives
- ✅ Single binary with no dependencies

**Note**: Highly recommended for security-sensitive projects. The pre-commit hook automatically sets up a Rust environment to compile and run ripsecrets.

## Hook Selection Criteria

### Required Hooks

1. **Formatting** (`cargo fmt`)
   - ✅ Essential for code consistency
   - ✅ Auto-fixable
   - ✅ Fast execution

2. **Tests** (`cargo nextest`)
   - ✅ Prevents broken code from being committed
   - ✅ Faster than `cargo test`
   - ⚠️ Can be slow for large test suites; consider `--fail-fast`

3. **Commit Message Validation** (`git-sumi`)
   - ✅ Enforces consistent commit history
   - ✅ Helps with automated changelog generation
   - ✅ Improves code review process
   - ✅ Rust-native tool matching project ecosystem

### Recommended Hooks

4. **Clippy** (`cargo clippy`)
   - ✅ Catches common mistakes
   - ✅ Enforces best practices
   - ⚠️ Can be strict (may need lint exceptions)

5. **General File Checks** (`pre-commit-hooks`)
   - ✅ Prevents common file issues
   - ✅ Fast execution
   - ✅ Low maintenance

### Optional Hooks

6. **Large File Check** (`check-added-large-files`)
   - Useful for preventing accidental commits of large files
   - Configurable size limit

7. **YAML/TOML/JSON Validation** (`check-yaml`, `check-toml`, `check-json`)
   - Useful if project contains configuration files
   - Fast execution

8. **Compilation Check** (`cargo check`)
   - ✅ Fast compilation validation
   - ⚠️ Redundant if running tests (which also compile)
   - 💡 Useful for faster feedback before running tests

9. **Security Hooks** (`cargo-deny`, `cargo-audit`)
   - ✅ Important for security-sensitive projects
   - ✅ Fast enough for pre-commit (see individual hook sections for performance details)
   - 💡 `cargo-deny` and `cargo-audit` are already configured in this project

10. **Secret Scanning** (`ripsecrets`)
    - ✅ Prevents accidental secret commits
    - ✅ Extremely fast execution (95x faster than alternatives)
    - ✅ Always local operation (never sends data to 3rd party services)
    - ✅ Pre-commit repository available (automatic installation)
    - 💡 Highly recommended for any project handling sensitive data

**Note**: Documentation check (`cargo doc`) is not included as this is a binary project, not a library. Documentation checks are primarily useful for library projects with public APIs.

## Configuration Examples

### Minimal Configuration

```yaml
default_install_hook_types:
  - pre-commit
  - commit-msg

minimum_pre_commit_version: '4.4.0'

fail_fast: true

repos:
  - repo: local
    hooks:
      - id: cargo-fmt
        name: cargo fmt
        entry: bash -c 'cargo fmt --all -- --check'
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

  # Commit message validation (Conventional Commits)
  - repo: https://github.com/welpo/git-sumi
    rev: v0.2.0
    hooks:
      - id: git-sumi
        stages: [commit-msg]
        pass_filenames: true
```

### Recommended Configuration

Includes all selected hooks. All hooks are fast enough for pre-commit:

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
        entry: bash -c 'cargo deny check --config .config/deny.toml'
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

**Note**: `cargo-geiger` was considered but is too slow (~12s) for pre-commit and should run in CI only - see `PRE_COMMIT_HOOK_CONSIDERATION.md`.

## Troubleshooting Specific Hooks

### Formatting Hook Fails (`cargo fmt`)

If formatting fails:
```bash
# Auto-fix formatting
cargo fmt --all

# Then commit again
git add .
git commit -m "style: format code"
```

### Test Hook Too Slow (`cargo nextest`)

If tests are slow:
1. `cargo nextest` is already being used (faster than `cargo test`)
2. Consider running tests only on changed files (more complex setup)
3. Use `--fail-fast` to stop on first failure: `cargo nextest run --fail-fast`
4. Consider running tests only in CI, not in pre-commit (trade-off)

### Commit Message Validation Fails (`git-sumi`)

If commit message validation fails:
- Check the format matches: `<type>(<scope>): <subject>` (e.g., `feat(parser): add support for data blocks`)
- Ensure type is one of the allowed types (see `.config/sumi.toml` configuration section above)
- Use imperative mood for the subject (e.g., "add feature" not "added feature")
- Ensure description starts with lowercase (if `description_case = "lower"` is set)
- Ensure header doesn't end with a period (if `no_period = true` is set)
- Ensure header doesn't exceed 72 characters (if `max_header_length = 72` is set)
- Initialize configuration if needed: `git sumi --init config` (creates `.config/sumi.toml`)
- Review `.config/sumi.toml` for custom rules and type definitions
- Test your commit message: `git sumi --display` (shows parsed commit message)

### Clippy Warnings (`cargo clippy`)

If clippy fails:
1. Fix the warnings manually
2. Or allow specific lints in `Cargo.toml`:
```toml
[lints.clippy]
# Allow specific lints if needed
```

## References

### Pre-commit Frameworks
- [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks) - General file checks (✅ **SELECTED**)
- [git-sumi](https://github.com/welpo/git-sumi) - Commit message validation (✅ **SELECTED** - Rust-native)

### Rust Tools
- [cargo-nextest Documentation](https://nexte.st/) - Faster test runner (✅ **SELECTED**)
- [cargo-deny](https://github.com/embarkstudios/cargo-deny) - Security scanning (licenses, vulnerabilities, bans) (✅ **SELECTED**)
- [cargo-audit](https://github.com/rustsec/rustsec/tree/main/cargo-audit) - Vulnerability scanning (✅ **SELECTED**)
- [ripsecrets](https://github.com/sirwart/ripsecrets) - Secret scanning (✅ **SELECTED** - pre-commit repository available)

**Note**: For references to tools that were considered but not selected, see `PRE_COMMIT_HOOK_CONSIDERATION.md`.
