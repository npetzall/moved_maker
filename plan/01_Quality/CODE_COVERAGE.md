# Code Coverage Tools

## Overview
Comparison of code coverage tools for Rust projects, focusing on compatibility with Apple Silicon (ARM) and Linux (GitHub Actions).

## Tool Comparison

### Option 1: cargo-llvm-cov (SELECTED)

**Overview**: Uses LLVM's source-based code coverage (same technology as Rust compiler)

**Compatibility**:
- ✅ Apple Silicon (ARM): Fully supported, available via Homebrew
- ✅ Linux (GitHub Actions): Fully supported

**Installation**:
```bash
# Apple Silicon
brew install cargo-llvm-cov

# Linux / GitHub Actions
cargo install cargo-llvm-cov
```

**Usage**:
```bash
# Generate coverage report
cargo llvm-cov --all-features

# Generate HTML report
cargo llvm-cov --html

# Generate LCOV format (for CI services)
cargo llvm-cov --lcov --output-path lcov.info

# Show coverage summary
cargo llvm-cov --summary-only
```

**Integration with cargo-nextest**:
```bash
cargo llvm-cov nextest --all-features
```

**Pros**:
- ✅ **Most accurate**: Uses LLVM's source-based coverage (same as compiler)
- ✅ **Fast**: Efficient coverage collection
- ✅ **Well-maintained**: Active development, widely used
- ✅ **Good CI integration**: Supports LCOV, JSON, HTML formats
- ✅ **Works with nextest**: Direct integration via `cargo llvm-cov nextest`
- ✅ **No nightly required**: Works on stable Rust
- ✅ **Branch coverage**: Supports branch coverage metrics
- ✅ **Easy setup**: Minimal configuration needed

**Cons**:
- ⚠️ Requires `llvm-tools-preview` component (but easy to install)
- ⚠️ Some advanced features may require specific Rust versions

**CI Integration Example**:
```yaml
- name: Install llvm-tools
  run: rustup component add llvm-tools-preview

- name: Install cargo-llvm-cov
  run: cargo install cargo-llvm-cov

- name: Generate coverage
  run: cargo llvm-cov nextest --all-features --lcov --output-path lcov.info

- name: Upload to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: lcov.info
```

---

### Option 2: cargo-tarpaulin

**Overview**: Rust-specific code coverage tool using source-based coverage

**Compatibility**:
- ✅ Apple Silicon (ARM): Supported (may require additional setup)
- ✅ Linux (GitHub Actions): Fully supported, commonly used

**Installation**:
```bash
cargo install cargo-tarpaulin
```

**Usage**:
```bash
# Generate coverage report
cargo tarpaulin --all-features

# Generate HTML report
cargo tarpaulin --out Html

# Generate XML report (for CI)
cargo tarpaulin --out Xml

# Exclude files
cargo tarpaulin --exclude-files 'tests/*'
```

**Pros**:
- ✅ **Rust-focused**: Designed specifically for Rust
- ✅ **Good CI support**: XML output for CI services
- ✅ **Configurable**: Many options for filtering and output
- ✅ **Stable**: Mature tool with good documentation
- ✅ **Works on stable Rust**: No nightly required

**Cons**:
- ⚠️ **Apple Silicon issues**: May have compatibility issues on ARM macOS (historically)
- ⚠️ **Slower**: Generally slower than cargo-llvm-cov
- ⚠️ **Less accurate**: May have some edge cases with coverage accuracy
- ⚠️ **No nextest integration**: Doesn't directly support cargo-nextest (need workarounds)

**CI Integration Example**:
```yaml
- name: Install cargo-tarpaulin
  run: cargo install cargo-tarpaulin

- name: Generate coverage
  run: cargo tarpaulin --out Xml --output-dir coverage

- name: Upload to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: coverage/cobertura.xml
```

---

### Option 3: grcov

**Overview**: Mozilla's code coverage tool, works with multiple languages including Rust

**Compatibility**:
- ✅ Apple Silicon (ARM): Compatible (requires proper setup)
- ✅ Linux (GitHub Actions): Fully supported, commonly used

**Installation**:
```bash
cargo install grcov
```

**Usage**:
```bash
# Setup environment
export CARGO_INCREMENTAL=0
export RUSTFLAGS="-Cinstrument-coverage"
export LLVM_PROFILE_FILE="cargo-test-%p-%m.profraw"

# Build and test
cargo build
cargo test

# Generate coverage
grcov . -s . --binary-path ./target/debug/ \
  -t lcov --branch --ignore-not-existing \
  -o lcov.info
```

**Pros**:
- ✅ **Flexible**: Supports multiple coverage formats (LCOV, Cobertura, etc.)
- ✅ **Mature**: Well-established tool from Mozilla
- ✅ **CI integration**: Good support for Codecov, Coveralls, etc.
- ✅ **Branch coverage**: Supports branch coverage

**Cons**:
- ⚠️ **Complex setup**: Requires environment variable configuration
- ⚠️ **Manual configuration**: More setup steps than cargo-llvm-cov
- ⚠️ **No direct nextest support**: Requires manual test execution
- ⚠️ **More verbose**: More commands needed for setup

**CI Integration Example**:
```yaml
- name: Setup coverage environment
  run: |
    export CARGO_INCREMENTAL=0
    export RUSTFLAGS="-Cinstrument-coverage"
    export LLVM_PROFILE_FILE="cargo-test-%p-%m.profraw"

- name: Install grcov
  run: cargo install grcov

- name: Build and test
  run: |
    cargo build
    cargo test

- name: Generate coverage
  run: |
    grcov . -s . --binary-path ./target/debug/ \
      -t lcov --branch --ignore-not-existing \
      -o lcov.info
```

---

## Decision

### Selected: cargo-llvm-cov

**Status**: ✅ **SELECTED** - This tool has been chosen for the project.

**Rationale**:
1. **Best compatibility**: Works seamlessly on both Apple Silicon and Linux
2. **Accuracy**: Uses LLVM's source-based coverage (most accurate)
3. **Integration**: Direct support for cargo-nextest via `cargo llvm-cov nextest`
4. **Ease of use**: Simplest setup and usage
5. **Performance**: Fastest coverage collection
6. **Active development**: Well-maintained and widely adopted

### Alternative: cargo-tarpaulin

**Use if**:
- You prefer a Rust-specific tool
- You need specific features only tarpaulin provides
- You're okay with potential ARM macOS issues

### Alternative: grcov

**Use if**:
- You need maximum flexibility in output formats
- You're already using grcov in other projects
- You don't mind more complex setup

## Coverage Goals

### Initial Goals (Enforced in CI)
- **Line coverage**: > 80%
- **Branch coverage**: > 70%
- **Function coverage**: > 85%

### Target Goals (Long-term)
- **Line coverage**: > 90%
- **Branch coverage**: > 80%
- **Function coverage**: > 95%

### Coverage Exclusions
- Test code (`tests/` directory)
- Main entry point (`src/main.rs` - minimal logic)
- Error handling paths that are difficult to test

## Coverage Threshold Enforcement

**Status**: ✅ **Enforced in CI** - Coverage thresholds are checked in CI and will fail builds if not met.

### Implementation

Coverage thresholds are enforced in the CI workflow. The coverage job will:
1. Generate coverage report with `cargo llvm-cov`
2. Extract coverage percentages (line, branch, function)
3. Compare against thresholds
4. Fail CI if thresholds are not met

### CI Integration

```yaml
- name: Generate coverage
  run: cargo llvm-cov nextest --all-features --lcov --output-path lcov.info

- name: Check coverage thresholds
  run: |
    # Extract coverage percentages and check against thresholds
    cargo llvm-cov nextest --all-features --summary-only
    # Coverage thresholds: Line > 80%, Branch > 70%, Function > 85%
    # CI will fail if thresholds not met
```

### Threshold Adjustment

If thresholds need to be adjusted:
1. Update thresholds in `CODE_COVERAGE.md`
2. Update threshold checks in CI workflow
3. Document reason for adjustment

**Note**: Thresholds should be adjusted upward over time as coverage improves, not downward.

## References

- [cargo-llvm-cov Documentation](https://github.com/taiki-e/cargo-llvm-cov)
- [cargo-tarpaulin Documentation](https://github.com/xd009642/tarpaulin)
- [grcov Documentation](https://github.com/mozilla/grcov)

