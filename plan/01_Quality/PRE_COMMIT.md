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

**macOS (Homebrew)**:
```bash
brew install pre-commit
```

**uv** (recommended for speed):
```bash
uv tool install pre-commit
# or
uv pip install pre-commit
```

### Initialize pre-commit

After installation, initialize pre-commit in the repository:

```bash
pre-commit install
```

This installs the git hooks into `.git/hooks/`.

## Configuration

Create a `.pre-commit-config.yaml` file in the project root:

```yaml
repos:
  # General file checks
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

  # Rust formatting
  - repo: https://github.com/doublify/pre-commit-rust
    rev: v1.0
    hooks:
      - id: fmt
        args: [--all, --]
      - id: clippy
        args: [--all-features, --all-targets, --, -D, warnings]
      - id: test
        args: [--all-features, --all-targets]

  # Commit message validation (Conventional Commits)
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

### Alternative: Using cargo-nextest for tests

If using `cargo-nextest` (recommended for this project), modify the test hook:

```yaml
  # Rust formatting and testing with cargo-nextest
  - repo: local
    hooks:
      - id: cargo-fmt
        name: cargo fmt
        entry: bash -c 'cargo fmt --all -- --check'
        language: system
        types: [rust]
        pass_filenames: false
        always_run: true

      - id: cargo-test
        name: cargo test (nextest)
        entry: bash -c 'cargo nextest run --all-features --all-targets'
        language: system
        types: [rust]
        pass_filenames: false
        always_run: true

      - id: cargo-clippy
        name: cargo clippy
        entry: bash -c 'cargo clippy --all-features --all-targets -- -D warnings'
        language: system
        types: [rust]
        pass_filenames: false
        always_run: true
```

## Hook Details

### Formatting Hook (`cargo fmt`)

- **Purpose**: Ensures all Rust code follows standard formatting
- **Command**: `cargo fmt --all -- --check`
- **Behavior**: Fails if code is not formatted correctly
- **Fix**: Run `cargo fmt --all` to auto-format

### Test Hook (`cargo test` / `cargo nextest`)

- **Purpose**: Runs all tests before allowing commit
- **Command**: `cargo nextest run --all-features --all-targets` (or `cargo test`)
- **Behavior**: Fails if any test fails
- **Note**: Can be slow for large test suites; consider using `--fail-fast` or running specific tests

### Commit Message Hook (Conventional Commits)

- **Purpose**: Validates commit messages follow Conventional Commits format
- **Format**: `<type>(<scope>): <subject>`
- **Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `revert`
- **Example**: `feat(parser): add support for data blocks`
- **Behavior**: Fails if commit message doesn't match format

### Clippy Hook (Optional but Recommended)

- **Purpose**: Catches common Rust mistakes and enforces best practices
- **Command**: `cargo clippy --all-features --all-targets -- -D warnings`
- **Behavior**: Fails on clippy warnings
- **Note**: Can be strict; may need to allow specific lints

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

Update hook versions:
```bash
pre-commit autoupdate
```

This updates all hook versions to their latest releases.

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
1. Use `cargo nextest` instead of `cargo test` (faster test runner)
2. Consider running tests only on changed files (more complex setup)
3. Use `--fail-fast` to stop on first failure

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
- Ensure type is one of the allowed types
- Use imperative mood for the subject

### Clippy Warnings

If clippy fails:
1. Fix the warnings manually
2. Or allow specific lints in `Cargo.toml`:
```toml
[lints.clippy]
# Allow specific lints if needed
```

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
2. **Keep hooks updated**: Regularly run `pre-commit autoupdate`
3. **Don't bypass hooks**: Avoid `--no-verify` unless absolutely necessary
4. **Fix issues immediately**: Don't accumulate formatting or test failures
5. **Document exceptions**: If a hook needs to be disabled, document why

## Implementation Steps

1. Install pre-commit framework
2. Create `.pre-commit-config.yaml` in project root
3. Configure hooks for:
   - Rust formatting (`cargo fmt`)
   - Tests (`cargo nextest` or `cargo test`)
   - Commit message validation (Conventional Commits)
   - Optional: Clippy checks
4. Install hooks: `pre-commit install`
5. Test hooks: `pre-commit run --all-files`
6. Add CI workflow to enforce hooks in CI
7. Document in project README

## References

- [pre-commit Documentation](https://pre-commit.com/)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)
- [pre-commit-rust](https://github.com/doublify/pre-commit-rust)
- [conventional-pre-commit](https://github.com/compilerla/conventional-pre-commit)
- [cargo-nextest Documentation](https://nexte.st/)

