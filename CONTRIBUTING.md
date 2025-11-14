# Contributing to Move Maker

Thank you for your interest in contributing to Move Maker! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. **Fork the repository** and clone your fork locally
2. **Set up the development environment** (see [DEVELOPMENT.md](DEVELOPMENT.md) for details)
3. **Install pre-commit hooks** (see Pre-commit Hooks section below)
4. **Create a branch** for your changes: `git checkout -b feat/your-feature-name`

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to enforce code quality standards before commits. **All contributors must install and use pre-commit hooks.**

### Installation

**Preferred method (using uv):**
```bash
uv tool install pre-commit
```

**Alternative methods:**
```bash
# macOS (Homebrew)
brew install pre-commit

# Using pip
pip install pre-commit
```

### Setup

After installing pre-commit, install the hooks:
```bash
pre-commit install
```

This automatically installs both `pre-commit` and `commit-msg` hooks.

### Running Hooks Manually

Before committing, run all hooks to catch issues early:
```bash
pre-commit run --all-files
```

Run a specific hook:
```bash
pre-commit run <hook-id> --all-files
# Example: pre-commit run cargo-fmt --all-files
```

### What the Hooks Do

The pre-commit hooks automatically:
- **Format code** with `cargo fmt`
- **Run tests** with `cargo nextest`
- **Lint code** with `cargo clippy`
- **Check compilation** with `cargo check`
- **Validate commit messages** (Conventional Commits format)
- **Scan for secrets** with `ripsecrets`
- **Check security** with `cargo-deny` and `cargo-audit`
- **Validate file formats** (YAML, TOML, JSON)
- **Check for common issues** (trailing whitespace, merge conflicts, etc.)

### Commit Message Format

All commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type** (required): One of `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert`

**Scope** (optional): The area of the codebase affected (e.g., `parser`, `processor`, `cli`)

**Subject** (required):
- Use imperative mood: "add" not "added" or "adds"
- First letter lowercase
- No period at the end
- Maximum 72 characters

**Examples:**
```
feat(parser): add support for data blocks
fix(processor): handle empty resource blocks correctly
docs: update README with installation instructions
test(cli): add integration tests for file discovery
chore: update dependencies
```

See `.config/sumi.toml` for complete configuration details.

### Bypassing Hooks (Not Recommended)

If you need to bypass hooks (e.g., for emergency fixes):
```bash
git commit --no-verify
```

**Warning**: Only use `--no-verify` in exceptional circumstances. It defeats the purpose of quality gates and may cause CI failures.

### Troubleshooting

**Formatting Hook Fails:**
```bash
# Auto-fix formatting
cargo fmt --all

# Then commit again
git add . && git commit -m "style: format code"
```

**Commit Message Validation Fails:**
- Check the format matches: `<type>(<scope>): <subject>`
- Ensure type is one of the allowed types (see `.config/sumi.toml`)
- Use imperative mood for the subject
- Ensure description starts with lowercase
- Ensure header doesn't end with a period
- Ensure header doesn't exceed 72 characters

**Pre-commit Not Running:**
```bash
# Reinstall hooks
pre-commit uninstall && pre-commit install

# Verify hooks are installed
ls -la .git/hooks/
```

For more detailed troubleshooting, see the [Pre-commit Hooks section in DEVELOPMENT.md](DEVELOPMENT.md#pre-commit-hooks).

## Development Workflow

1. **Create a feature branch** from `main`
2. **Make your changes** following the coding standards
3. **Run tests locally**: `cargo nextest run`
4. **Run pre-commit hooks**: `pre-commit run --all-files`
5. **Commit your changes** with a Conventional Commits message
6. **Push to your fork** and create a pull request

## Code Standards

### Rust Code Style

- Follow Rust standard formatting (enforced by `cargo fmt`)
- Follow clippy recommendations (enforced by `cargo clippy`)
- Use `anyhow::Result` for error handling (see [DEVELOPMENT.md](DEVELOPMENT.md#error-handling))
- Write tests for new functionality

### Testing

- All new features must include tests
- Use `cargo nextest` for running tests (faster than `cargo test`)
- Integration tests go in `tests/integration_test.rs`
- Test fixtures go in `tests/fixtures/`

### Error Handling

- Use `anyhow::Result<T>` for functions that can fail
- Add context at module boundaries using `.context()` or `.with_context()`
- Use the `?` operator for error propagation
- See [DEVELOPMENT.md](DEVELOPMENT.md#error-handling) for detailed patterns

## Pull Request Process

1. **Update documentation** if you're adding features or changing behavior
2. **Add tests** for new functionality
3. **Ensure all tests pass**: `cargo nextest run`
4. **Ensure pre-commit hooks pass**: `pre-commit run --all-files`
5. **Create a pull request** with a clear description
6. **Wait for CI/CD checks** to pass (tests, linting, security checks)
7. **Address review feedback** if requested
8. **Merge using rebase or squash merge** once approved

### Pull Request Requirements

**Branch Protection:**
- All changes must go through pull requests (no direct pushes to `main`)
- All CI/CD workflows must pass before merging
- All PR comments and discussions must be resolved before merging
- Code owner reviews may be required (if CODEOWNERS is enabled)

**Merge Strategy:**
- Use **rebase and merge** or **squash and merge** (both maintain linear history)
- Merge commits are disabled to maintain clean git history
- Ensure your PR branch is up to date with `main` before merging

**Version Labels:**
- Labels are automatically applied based on your commit messages
- Use [Conventional Commits](https://www.conventionalcommits.org/) format:
  - `feat:` → `version: minor` label
  - `fix:` → `version: patch` label
  - `feat!:` or `BREAKING CHANGE:` → `version: major` label
- You can manually override labels if needed

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] Pre-commit hooks pass
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow Conventional Commits format
- [ ] No merge conflicts with `main`
- [ ] PR branch is up to date with `main`
- [ ] All CI/CD checks pass
- [ ] All review comments addressed

## Security

- **Never commit secrets** (API keys, passwords, tokens, etc.)
- The `ripsecrets` hook will catch common secret patterns
- If you accidentally commit a secret, rotate it immediately
- See [SECURITY.md](SECURITY.md) for security reporting

## Questions?

- Check [DEVELOPMENT.md](DEVELOPMENT.md) for development workflows
- Check [TOOLING.md](TOOLING.md) for tooling information
- Open an issue for questions or clarifications

## Code of Conduct

Be respectful and constructive in all interactions. We welcome contributions from everyone.
