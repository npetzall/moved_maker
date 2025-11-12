# Quality Tooling Plan

## Overview
This plan outlines the integration of quality assurance tools and continuous delivery (CD) for the move_maker project, focusing on test execution, code coverage, and automated releases. All tools must be compatible with Apple Silicon (ARM) and Linux (GitHub Actions).


The CD strategy automates the release process so that each push to the `main` branch creates a new GitHub release with compiled binaries for multiple platforms (Linux x86_64/ARM64, macOS Intel/Apple Silicon).

## Document Structure

This plan is organized into the following documents:

- **[GitHub Configuration](GITHUB.md)** - Repository settings, branch protection, label management, and merge strategy
- **[Pre-commit Hooks](PRE_COMMIT.md)** - Pre-commit framework setup for tests, formatting, and commit message validation
- **[Test Runner](TEST_RUNNER.md)** - cargo-nextest setup and usage, including pretty_assertions
- **[Error Handling](ERROR_HANDLING.md)** - anyhow for improved error handling
- **[Code Coverage](CODE_COVERAGE.md)** - Coverage tools comparison and selection
- **[Security](SECURITY.md)** - Vulnerability scanning, license compliance, and secure practices
- **[Continuous Delivery](CONTINUOUS_DELIVERY.md)** - Automated release workflow
- **[Implementation](IMPLEMENTATION.md)** - Implementation plan, CI/CD workflows, and setup guides


## Quick Start

### Dependencies

**Note**: The following dependencies are selected and will be added when implementing Phase 1 and Phase 1.5:

Add to `Cargo.toml`:
```toml
[dependencies]
anyhow = "1.0"  # ✅ Selected - Will be added in Phase 1.5

[dev-dependencies]
pretty_assertions = "1.4"  # ✅ Selected - Will be added in Phase 1
tempfile = "3.10"  # Already present
```

### Local Development Setup (Apple Silicon)

```bash
# Install Homebrew packages
brew install pre-commit cargo-nextest cargo-llvm-cov llvm

# Install Rust components
rustup component add llvm-tools-preview

# Install cargo tools
cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable

# Install pre-commit hooks
pre-commit install

# Run tests
cargo nextest run

# Generate coverage
cargo llvm-cov nextest --all-features --html

# Run security checks
cargo deny check
cargo audit
cargo geiger
```

## Implementation Phases

0. **Phase 0**: GitHub Configuration - See [GITHUB.md](GITHUB.md)
0.5. **Phase 0.5**: Pre-commit Hooks - See [PRE_COMMIT.md](PRE_COMMIT.md)
1. **Phase 1**: Test Runner (cargo-nextest) + Testing Utilities (pretty_assertions) - See [TEST_RUNNER.md](TEST_RUNNER.md)
2. **Phase 1.5**: Error Handling (anyhow) - See [ERROR_HANDLING.md](ERROR_HANDLING.md)
3. **Phase 2**: Coverage (cargo-llvm-cov - SELECTED) - See [CODE_COVERAGE.md](CODE_COVERAGE.md)
4. **Phase 2.5**: Security (cargo-deny, cargo-audit, cargo-geiger, cargo-auditable) - See [SECURITY.md](SECURITY.md)
5. **Phase 3**: Continuous Delivery - See [CONTINUOUS_DELIVERY.md](CONTINUOUS_DELIVERY.md)


For detailed implementation steps, see [IMPLEMENTATION.md](IMPLEMENTATION.md).

## References

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Merge Methods](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github)
- [pre-commit Documentation](https://pre-commit.com/)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [cargo-nextest Documentation](https://nexte.st/)
- [pretty_assertions Documentation](https://docs.rs/pretty_assertions/)
- [anyhow Documentation](https://docs.rs/anyhow/)
- [cargo-llvm-cov Documentation](https://github.com/taiki-e/cargo-llvm-cov)
- [cargo-tarpaulin Documentation](https://github.com/xd009642/tarpaulin)
- [grcov Documentation](https://github.com/mozilla/grcov)
- [cargo-deny Documentation](https://github.com/EmbarkStudios/cargo-deny)
- [cargo-audit Documentation](https://github.com/rustsec/rustsec/tree/main/cargo-audit)
- [softprops/action-gh-release](https://github.com/softprops/action-gh-release)
- [ncipollo/release-action](https://github.com/ncipollo/create-release)
- [cargo-release Documentation](https://github.com/crate-ci/cargo-release)
- [GitHub Actions: Creating Releases](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#release)
