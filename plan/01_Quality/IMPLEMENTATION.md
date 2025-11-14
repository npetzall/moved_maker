# Implementation Plan and CI/CD Integration

## Implementation Phases

### Phase 1: Security (cargo-deny, cargo-audit, cargo-geiger, cargo-auditable)
1. Install all security tools: cargo-deny, cargo-audit, cargo-geiger, cargo-auditable
2. Create `.config/deny.toml` configuration
3. Run initial security scans
4. Address any vulnerabilities or license issues
5. Integrate into CI workflows (all tools blocking)
6. Enable Dependabot for dependency updates
7. Configure binary auditing for release builds

See [SECURITY.md](SECURITY.md) for details.

### Phase 2: Test Runner (cargo-nextest) + Testing Utilities
1. Add `pretty_assertions` to `Cargo.toml` dev-dependencies
2. Update tests to use `pretty_assertions::assert_eq!`
3. Install cargo-nextest locally (Apple Silicon)
4. Update CI workflow to use cargo-nextest
5. Configure JUnit XML output for CI
6. Update documentation

See [TEST_RUNNER.md](TEST_RUNNER.md) for details.

### Phase 3: Error Handling (anyhow)
1. Add `anyhow` to `Cargo.toml` dependencies
2. Migrate error handling from `panic!` to `Result<T, anyhow::Error>`
3. Add context to error messages using `.context()` and `.with_context()`
4. Update `main()` to return `Result<()>`
5. Update tests to handle `Result` types
6. Verify error messages are user-friendly

See [ERROR_HANDLING.md](ERROR_HANDLING.md) for details.

### Phase 4: Coverage (cargo-llvm-cov - SELECTED)
1. Install cargo-llvm-cov locally
2. Add `llvm-tools-preview` component
3. Generate initial coverage report
4. Set coverage threshold goals
5. Integrate into CI workflow
6. Configure coverage reporting (e.g., Codecov)

See [CODE_COVERAGE.md](CODE_COVERAGE.md) for details.

### Phase 5: Pre-commit Hooks
1. Install pre-commit framework
2. Create `.pre-commit-config.yaml` file
3. Configure Rust formatting and linting hooks
4. Configure test hooks (using cargo-nextest)
5. Configure commit message validation (Conventional Commits)
6. Install hooks with `pre-commit install`
7. Test hooks locally
8. Integrate into CI workflow (optional)

See [PRE_COMMIT.md](PRE_COMMIT.md) for details.

### Phase 6: GitHub Configuration
1. Configure branch protection rules for `main` branch
2. Set merge strategy to rebase and merge only
3. Create version labels (version: major, version: minor, version: patch)
4. Configure required status checks
5. Set up workflow permissions
6. Verify repository settings

See [GITHUB.md](GITHUB.md) for details.

### Phase 7: Continuous Delivery (CD)
1. Create GitHub Actions workflow for CD
2. Set up multi-platform builds (Linux x86_64/ARM64, macOS Intel/Apple Silicon)
3. Configure version extraction from Cargo.toml
4. Set up release notes generation
5. Test release workflow
6. Add binary checksums
7. Document release process

See [CONTINUOUS_DELIVERY.md](CONTINUOUS_DELIVERY.md) for details.


---

## CI/CD Integration

### Complete Quality Checks Workflow

```yaml
name: Pull Request Checks

on:
  pull_request:

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Install security tools
        run: cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable

      - name: Run cargo-deny checks (blocking)
        run: cargo deny check --config .config/deny.toml

      - name: Update vulnerability database
        run: cargo audit update

      - name: Run cargo-audit checks (blocking)
        run: cargo audit --deny warnings

      - name: Run cargo-geiger scan (blocking)
        run: cargo geiger --output-format json > geiger-report.json

  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]

    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          components: llvm-tools-preview

      - name: Install cargo-nextest
        uses: taiki-e/install-action@cargo-nextest

      - name: Run tests
        run: cargo nextest run --junit-xml test-results.xml

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results-${{ matrix.os }}
          path: test-results.xml

  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          components: llvm-tools-preview

      - name: Install cargo-nextest
        uses: taiki-e/install-action@cargo-nextest

      - name: Install cargo-llvm-cov
        run: cargo install cargo-llvm-cov

      - name: Generate coverage
        run: cargo llvm-cov nextest --all-features --lcov --output-path lcov.info

      - name: Check coverage thresholds
        run: |
          # Extract coverage percentages and check against thresholds
          cargo llvm-cov nextest --all-features --lcov --output-path lcov.info --summary-only
          # Coverage thresholds: Line > 80%, Branch > 70%, Function > 85%
          # CI will fail if thresholds not met

      - name: Upload to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: lcov.info
          flags: unittests
          name: codecov-umbrella
```

---

## Local Development Setup

### All Platforms

```bash
# Install Rust components
rustup component add llvm-tools-preview

# Install cargo tools (all platforms)
cargo install cargo-nextest cargo-llvm-cov cargo-deny cargo-audit cargo-geiger cargo-auditable

# Add dependencies (if not already in Cargo.toml)
# cargo add anyhow
# cargo add --dev pretty_assertions

# Run tests
cargo nextest run

# Generate coverage
cargo llvm-cov nextest --all-features --html

# Run security checks
cargo deny check --config .config/deny.toml
cargo audit
cargo geiger
```

---

## Workflow File Locations

Create the following GitHub Actions workflow files:

- `.github/workflows/pull_request.yaml` - Quality checks for pull requests (tests, coverage, security)
- `.github/workflows/release.yaml` - Release workflow for pushes to main (security, build, release)

See [CONTINUOUS_DELIVERY.md](CONTINUOUS_DELIVERY.md) for the complete release workflow.
