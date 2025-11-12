# Quality Setup Guide

## Overview
This guide consolidates all setup instructions for quality tooling in the move_maker project. Follow these steps to set up the complete quality assurance environment.

## Prerequisites

- Rust toolchain installed (stable)
- Git repository access

## Quick Setup

### 1. Install Rust Components

```bash
rustup component add llvm-tools-preview
```

### 2. Install Cargo Tools

```bash
# Install all quality tools via cargo
cargo install cargo-nextest cargo-llvm-cov cargo-deny cargo-audit cargo-geiger cargo-auditable
```

### 4. Initialize Security Configuration

```bash
cargo deny init
```

Edit `deny.toml` to configure license and vulnerability policies (see [SECURITY.md](SECURITY.md)).

### 5. Add Dependencies (When Implementing Phases)

**Phase 1** - Add to `Cargo.toml`:
```toml
[dev-dependencies]
pretty_assertions = "1.4"  # ✅ Selected
```

**Phase 1.5** - Add to `Cargo.toml`:
```toml
[dependencies]
anyhow = "1.0"  # ✅ Selected
```

**Note**: These dependencies are selected but will be added when implementing their respective phases.

## Tool Installation Summary

### Required Tools

| Tool | Installation Method | Purpose |
|------|-------------------|---------|
| **cargo-nextest** | `cargo install` | Fast test runner |
| **cargo-llvm-cov** | `cargo install` | Code coverage |
| **llvm-tools-preview** | `rustup component add` | Required for coverage |
| **cargo-deny** | `cargo install` | Security scanning (blocking) |
| **cargo-audit** | `cargo install` | Vulnerability scanning (blocking) |
| **cargo-geiger** | `cargo install` | Unsafe code detection (blocking) |
| **cargo-auditable** | `cargo install` | Binary auditing (blocking) |

### Selected Dependencies

| Dependency | Type | Phase | Status |
|------------|------|-------|--------|
| **pretty_assertions** | dev-dependency | Phase 1 | ✅ Selected |
| **anyhow** | dependency | Phase 1.5 | ✅ Selected |
| **tempfile** | dev-dependency | - | Already present |

## Workflow Files

Create the following GitHub Actions workflow files:

### `.github/workflows/pull_request.yaml`

Runs on pull requests. Includes:
- Security checks (cargo-deny, cargo-audit, cargo-geiger)
- Tests (cargo-nextest)
- Coverage (cargo-llvm-cov with threshold enforcement)

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for complete workflow definition.

### `.github/workflows/release.yaml`

Runs on pushes to `main`. Includes:
- Security checks (all tools, blocking)
- Multi-platform builds
- Binary auditing
- Release creation

See [CONTINUOUS_DELIVERY.md](CONTINUOUS_DELIVERY.md) for complete workflow definition.

## Verification

### Test Installation

```bash
# Verify test runner
cargo nextest run

# Verify coverage
cargo llvm-cov nextest --all-features --html

# Verify security tools
cargo deny check
cargo audit
cargo geiger
cargo auditable build --release
cargo audit bin target/release/move_maker
```

### Verify Workflows

1. Create a test pull request
2. Verify `pull_request.yaml` workflow runs
3. Push to `main` (carefully!)
4. Verify `release.yaml` workflow runs

## Configuration Files

### `deny.toml`

Security policy configuration for cargo-deny. Created with `cargo deny init`.

**Location**: Project root

**Configuration**: See [SECURITY.md](SECURITY.md) for policy examples.

### `.github/dependabot.yml`

Automated dependency updates.

**Location**: `.github/dependabot.yml`

**Configuration**: See [SECURITY.md](SECURITY.md) for example configuration.

## Implementation Phases

Follow these phases in order:

1. **Phase 1**: Test Runner (cargo-nextest) + Testing Utilities (pretty_assertions)
2. **Phase 1.5**: Error Handling (anyhow)
3. **Phase 2**: Coverage (cargo-llvm-cov)
4. **Phase 2.5**: Security (all security tools)
5. **Phase 3**: Continuous Delivery (release workflow)


See [IMPLEMENTATION.md](IMPLEMENTATION.md) for detailed phase instructions.

## Troubleshooting

### Apple Silicon Issues

If you encounter issues on Apple Silicon:
- Ensure all tools are installed: `cargo install cargo-nextest cargo-llvm-cov`
- Verify Rust toolchain: `rustup show`
- Check LLVM tools: `rustup component list | grep llvm`
- Ensure `llvm-tools-preview` is installed: `rustup component add llvm-tools-preview`

### Coverage Not Working

- Verify `llvm-tools-preview` is installed: `rustup component add llvm-tools-preview`
- Check cargo-llvm-cov installation: `cargo llvm-cov --version`
- Ensure tests run successfully: `cargo nextest run`

### Security Tools Failing

- Update vulnerability database: `cargo audit update`
- Review `deny.toml` configuration
- Check for known false positives in security tool documentation

## Documentation

- [QUALITY_TOOLING.md](QUALITY_TOOLING.md) - Overview of all quality tools
- [TEST_RUNNER.md](TEST_RUNNER.md) - Test runner setup
- [ERROR_HANDLING.md](ERROR_HANDLING.md) - Error handling with anyhow
- [CODE_COVERAGE.md](CODE_COVERAGE.md) - Coverage tools and thresholds
- [SECURITY.md](SECURITY.md) - Security tools and practices
- [CONTINUOUS_DELIVERY.md](CONTINUOUS_DELIVERY.md) - Release workflow
- [IMPLEMENTATION.md](IMPLEMENTATION.md) - Implementation phases
- [VERSIONING.md](VERSIONING.md) - Versioning strategy proposals

## Updating README.md

After implementing quality tooling, update the project README.md with the following sections:

### Testing Section

```markdown
## Testing

Run all tests:
```bash
cargo nextest run
```

Run with coverage:
```bash
cargo llvm-cov nextest --all-features --html
```

### Security Section

```markdown
## Security

Security checks are run automatically in CI. To run locally:

```bash
cargo deny check
cargo audit
cargo geiger
```

See [plan/01_Quality/SECURITY.md](plan/01_Quality/SECURITY.md) for details.
```

### CI/CD Section

```markdown
## CI/CD

- **Pull Requests**: Quality checks run automatically (tests, coverage, security)
- **Releases**: Pushes to `main` trigger automatic releases with multi-platform binaries

See [plan/01_Quality/CONTINUOUS_DELIVERY.md](plan/01_Quality/CONTINUOUS_DELIVERY.md) for release details.
```

### Installation Section Update

If binaries are available from releases, add:

```markdown
## Installation

### From Source
```bash
cargo build --release
```

### From Releases
Download the latest release from [GitHub Releases](https://github.com/your-org/move_maker/releases).
```

## Next Steps

1. Review [VERSIONING.md](VERSIONING.md) and select versioning strategy
2. Implement Phase 1 (Test Runner)
3. Implement Phase 1.5 (Error Handling)
4. Implement Phase 2 (Coverage)
5. Implement Phase 2.5 (Security)
6. Implement Phase 3 (Continuous Delivery)
7. Update README.md with quality tooling information

## Support

For issues or questions:
- Review documentation in `plan/01_Quality/`
- Check tool-specific documentation (links in each document)
- Review [REVIEW_ISSUES.md](REVIEW_ISSUES.md) for known issues

