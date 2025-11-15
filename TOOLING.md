# Development Tooling

This document describes the development tools and configurations used in this project.

## Security

The project uses a comprehensive set of security tools to ensure dependency safety, license compliance, and vulnerability detection.

### cargo-deny

**Purpose**: Comprehensive security scanning for licenses, vulnerabilities, and banned dependencies.

**Installation**:
```bash
cargo install cargo-deny
```

**Configuration**: `.config/deny.toml`

**Key Configuration**:

- **Advisories**: Uses default behavior (vulnerabilities are denied, unmaintained/notices are warnings)
  - Advisory database: RustSec Advisory Database (default)
  - No ignored advisories configured

- **Licenses**:
  - Default policy: Deny unknown licenses (via default behavior in cargo-deny 0.18.5+)
  - Copyleft policy: Deny copyleft licenses (via default behavior)
  - Allowed licenses:
    - MIT
    - Apache-2.0
    - BSD-2-Clause
    - BSD-3-Clause
    - Unicode-3.0
  - Confidence threshold: 0.8

- **Bans**:
  - Multiple versions: Warn
  - Wildcards: Deny
  - No specific crate bans configured

**Usage**:
```bash
# Run all checks
cargo deny check --config .config/deny.toml

# Check specific categories
cargo deny check --config .config/deny.toml advisories
cargo deny check --config .config/deny.toml licenses
cargo deny check --config .config/deny.toml bans
cargo deny check --config .config/deny.toml sources
```

**CI/CD**: Blocking - all checks must pass before builds proceed.

### cargo-audit

**Purpose**: Vulnerability scanning using the RustSec Advisory Database.

**Installation**:
```bash
cargo install cargo-audit
```

**Configuration**: No configuration file required. Uses RustSec Advisory Database automatically.

**Usage**:
```bash
# Scan for vulnerabilities
cargo audit

# Scan with warnings treated as errors
cargo audit --deny warnings

# Output JSON format
cargo audit --json
```

**CI/CD**: Blocking - vulnerabilities must be resolved before builds proceed.

### cargo-geiger

**Purpose**: Detects unsafe code usage in the project and its dependencies.

**Installation**:
```bash
cargo install cargo-geiger
```

**Configuration**: No configuration file required.

**Usage**:
```bash
# Scan for unsafe code
cargo geiger

# Output JSON format (for CI/CD)
cargo geiger --output-format json > geiger-report.json

# Exclude test dependencies
cargo geiger --exclude-tests
```

**CI/CD**: Blocking - unsafe code detection is enforced in CI/CD workflows.

**Note**: Unsafe code in dependencies is expected and acceptable. The tool helps maintain awareness of unsafe code usage throughout the dependency tree.

### cargo-auditable

**Purpose**: Embeds dependency information in release binaries for post-deployment vulnerability auditing.

**Installation**:
```bash
cargo install cargo-auditable
```

**Configuration**: No configuration file required.

**Usage**:
```bash
# Build release binary with embedded dependency info
cargo auditable build --release

# Audit a compiled binary
cargo audit bin target/release/move_maker
```

**CI/CD**: Used in release builds to create auditable binaries. All release binaries are built with embedded dependency information.

### Running All Security Checks

To run all security checks locally:

```bash
# Run all security checks (cargo audit automatically updates the database)
cargo deny check --config .config/deny.toml && cargo audit --deny warnings && cargo geiger
```

### Security Tool Versions

The following versions are currently in use:

- cargo-deny: 0.18.5+
- cargo-audit: 0.21.2+
- cargo-geiger: 0.13.0+
- cargo-auditable: 0.7.2+

### Additional Notes

- All security tools are **blocking** in CI/CD workflows
- Security checks should be run locally before committing changes
- Binary auditing is required for all release builds
- License compliance is enforced via cargo-deny configuration
- The project license is specified in `Cargo.toml`: `MIT OR Apache-2.0`

## Pre-commit Hooks

The project uses [pre-commit](https://pre-commit.com/) to enforce code quality standards before commits. Pre-commit hooks automatically run checks on staged files before allowing commits.

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

### Configuration

The pre-commit configuration is defined in `.pre-commit-config.yaml`. The configuration includes:

- **Default hook types**: `pre-commit` and `commit-msg`
- **Minimum version**: `3.0.0`
- **Fail fast**: Enabled (stops on first failure)

### Configured Hooks

**Required Hooks:**
- `cargo-fmt`: Rust code formatting
- `cargo-test` (nextest): Run tests before commit
- `git-sumi`: Commit message validation (Conventional Commits)

**Recommended Hooks:**
- `cargo-clippy`: Rust linting and best practices
- `pre-commit-hooks`: General file checks (trailing whitespace, YAML/TOML/JSON validation, etc.)
- `cargo-check`: Fast compilation check
- `cargo-deny`: License compliance, vulnerability detection, banned dependencies
- `cargo-audit`: Vulnerability scanning using RustSec Advisory Database
- `ripsecrets`: Secret scanning to prevent accidental secret commits

### Commit Message Validation

Commit messages are validated using `git-sumi` with configuration in `.config/sumi.toml`. Messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- Format: `<type>(<scope>): <subject>`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert`
- Subject: Imperative mood, lowercase, no period, max 72 characters

### Usage

**Run all hooks on all files:**
```bash
pre-commit run --all-files
```

**Run a specific hook:**
```bash
pre-commit run <hook-id> --all-files
# Example: pre-commit run cargo-fmt --all-files
```

**Update hook versions:**
```bash
pre-commit autoupdate
```

Always review changes after updating:
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

### Performance

Hook execution time is approximately **5.7 seconds**, which is acceptable for pre-commit workflow. The hooks use `cargo nextest` for faster test execution.

### Security Best Practices

- **Pin versions**: Use specific tags (e.g., `v4.5.0`) rather than branches in configuration
- **Regular updates**: Run `pre-commit autoupdate` weekly/monthly
- **Review updates**: Always review changes after `pre-commit autoupdate` before committing
- **Monitor advisories**: Check for security advisories in hook repositories

### Additional Notes

- Pre-commit hooks run locally before commits
- Hooks can be bypassed with `--no-verify`, but this is not recommended
- CI integration is handled separately in CI/CD workflows
- All selected hooks have been verified for performance and compatibility

For detailed information about pre-commit hooks, see the [Pre-commit Hooks section in DEVELOPMENT.md](DEVELOPMENT.md#pre-commit-hooks) and [CONTRIBUTING.md](CONTRIBUTING.md#pre-commit-hooks).
