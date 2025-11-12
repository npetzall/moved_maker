# Pre-commit Hooks - Considered but Not Selected

## Overview

This document contains information about pre-commit hooks that were investigated but not selected for use. See `PRE_COMMIT_HOOKS.md` for selected hooks and `PRE_COMMIT.md` for general pre-commit framework documentation.

## Rust Formatting and Linting

**⚠️ DONT USE - Use local hooks instead (see "Alternative: Local Hooks" section in PRE_COMMIT_HOOKS.md)**

**Repository**: `https://github.com/doublify/pre-commit-rust`  
**Version**: `v1.0`

**Why not to use**: This repository uses `cargo test` instead of `cargo nextest`, and local hooks provide better control and flexibility.

Pre-configured Rust hooks (for reference only - **DO NOT USE**):

```yaml
- repo: https://github.com/doublify/pre-commit-rust
  rev: v1.0
  hooks:
    - id: fmt
      args: [--all, --]
    - id: clippy
      args: [--all-features, --all-targets, --, -D, warnings]
    - id: test
      args: [--all-features, --all-targets]
```

**Available Hooks** (for reference only):
- `fmt`: Runs `cargo fmt` to check formatting
- `clippy`: Runs `cargo clippy` for linting
- `test`: Runs `cargo test` for testing (does not support `cargo nextest`)

## Commit Message Validation

### Deprecated Option

**⚠️ DEPRECATED - Use git-sumi instead (see PRE_COMMIT_HOOKS.md)**

**Repository**: `https://github.com/compilerla/conventional-pre-commit`  
**Version**: `v3.0.0`

Validates commit messages follow Conventional Commits format:

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

**Hook Details**:
- `conventional-pre-commit`: Validates commit message format
- **Format**: `<type>(<scope>): <subject>`
- **Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `revert`
- **Scopes**: Optional (can be configured as required or optional)

### Alternative Commit Message Validation Tools

Below are alternatives to `conventional-pre-commit`, focusing on Rust and Python options:

#### Rust Options

**conventional-commits** (Rust)
- **Repository**: `https://codeberg.org/slundi/conventional-commits`
- **Language**: Rust (51.4%), Shell (22.9%), Nix (17.9%), Makefile (7.8%)
- **Stars**: 0 stars (1 watcher)
- **Maintenance Status**: ✅ Actively maintained (recent commits Aug 2024)
- **Features**:
  - Lightweight Rust library and CLI for validating Conventional Commits v1.0.0
  - Configurable validation rules
  - Can be used as library or CLI tool
  - Minimal dependencies
  - Supports all standard commit types
  - Detects breaking changes
  - Helpful error messages and examples
- **Pre-commit Integration**: ✅ Yes (has `.pre-commit-config.yaml`)
- **Custom Types**: ✅ Supported via `--allow-custom-types` flag (default: true)
- **Installation**: `cargo install conventional-commits`
- **Configuration**: CLI flags (`--max-length`, `--allow-custom-types`, `--enforce-lowercase`, `--disallow-period`)
- **Documentation**: See repository README
- **Note**: Very new project (created Aug 2024), lightweight and focused on Conventional Commits spec

#### Python Options

**commitizen** (Python)
- **Repository**: `https://github.com/commitizen-tools/commitizen`
- **Language**: Python
- **GitHub Stars**: ~3,000-3,500
- **Maintenance Status**: ✅ Actively maintained
- **Features**:
  - Enforces consistent commit messages
  - Pre-commit hooks support
  - Interactive commit message creation
  - Conventional Commits support
- **Pre-commit Integration**: ✅ Yes
- **Custom Types**: ✅ Supported via configuration
- **Installation**: `pip install commitizen`

**commit-check** (Python)
- **Repository**: `https://github.com/commit-check/commit-check`
- **Language**: Python (100%)
- **GitHub Stars**: 31 stars
- **Maintenance Status**: ✅ Actively maintained (latest release v2.1.2 on Nov 5, 2024)
- **Features**:
  - Enforces commit metadata standards (commit messages, branch naming, committer name/email, commit signoff)
  - TOML configuration (`cchk.toml` or `commit-check.toml`)
  - Supports Conventional Commits specification
  - Supports Conventional Branch naming
  - Lightweight alternative to GitHub Enterprise Metadata restrictions
  - Modern validation engine (v2.0.0+)
  - CLI alias: `cchk`
- **Pre-commit Integration**: ✅ Yes (has `.pre-commit-hooks.yaml`)
- **Custom Types**: ✅ Supported via TOML configuration
- **Installation**: `pip install commit-check` or `pip install git+https://github.com/commit-check/commit-check.git@main`
- **Configuration**: Uses `cchk.toml` or `commit-check.toml` (default configuration is lenient)
- **Documentation**: https://commit-check.github.io/commit-check/
- **Note**: Comprehensive tool that validates more than just commit messages (also branch names, committer info, signoff). Version 2.0.0+ is a major rewrite with improved architecture.

**commit-msg-hook** (Python)
- **Repository**: Available on PyPI
- **Language**: Python
- **GitHub Stars**: Needs verification
- **Maintenance Status**: ✅ Actively maintained
- **Features**:
  - Pre-commit hook for commit message validation
  - Configurable commit rules
- **Pre-commit Integration**: ✅ Yes
- **Custom Types**: ✅ Supported
- **Installation**: `pip install commit-msg-hook`

#### Comparison Summary

| Tool | Language | Stars | Maintained | Custom Types | Pre-commit | Notes |
|------|----------|-------|------------|--------------|------------|-------|
| **conventional-pre-commit** | Python | ~100-200 | ✅ Yes | ✅ Yes | ✅ Yes | Deprecated - use git-sumi |
| **conventional-commits** | Rust | 0 | ✅ Yes | ✅ Yes | ✅ Yes | Very new, lightweight, focused |
| **commitizen** | Python | ~3,000-3,500 | ✅ Yes | ✅ Yes | ✅ Yes | Most popular Python option |
| **commit-check** | Python | 31 | ✅ Yes | ✅ Yes | ✅ Yes | Comprehensive validation (messages, branches, committer) |
| **commit-msg-hook** | Python | Unknown | ✅ Yes | ✅ Yes | ✅ Yes | Simple and focused |

**Recommendation Notes**: 
- For **Python preference**: `commitizen` is the most popular (~3,000-3,500 stars) and well-maintained option with extensive features
- `conventional-commits` (0 stars) is a very new, lightweight option focused strictly on Conventional Commits spec. Good for minimal dependencies but very new (created Aug 2024).
- `conventional-pre-commit` was previously used but has been replaced by `git-sumi` for better Rust ecosystem consistency

**Note**: GitHub star counts and maintenance status should be verified directly from repositories for the most current information.

## Security Hooks

### cargo-geiger

Detects unsafe code usage in project and dependencies:

```yaml
- repo: local
  hooks:
    - id: cargo-geiger
      name: cargo geiger
      entry: bash -c 'cargo geiger --all-features --all-targets'
      language: system
      types: [rust]
      pass_filenames: false
      always_run: true
```

**Benefits**:
- ✅ Visibility into unsafe code usage
- ✅ Security auditing awareness
- ✅ Helps track unsafe code patterns

**Performance**: ~12.24 seconds (measured) - **Too slow for pre-commit** ⚠️  
**Recommendation**: Run in CI only, not in pre-commit hooks. The tool compiles the entire project, making it significantly slower than other security tools.

## References

### Pre-commit Frameworks
- [pre-commit-rust](https://github.com/doublify/pre-commit-rust) - Rust-specific hooks (⚠️ **NOT RECOMMENDED** - use local hooks instead)
- [conventional-pre-commit](https://github.com/compilerla/conventional-pre-commit) - Commit message validation (⚠️ **DEPRECATED** - use git-sumi instead)

### Rust Tools
- [cargo-geiger](https://github.com/rust-secure-code/cargo-geiger) - Unsafe code detection (⚠️ **Too slow for pre-commit** - run in CI only)

