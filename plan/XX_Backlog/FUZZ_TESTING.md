# Fuzz Testing: cargo-fuzz

## Purpose
Automated fuzz testing to find edge cases and crashes

## Features
- Uses LLVM's libFuzzer
- Generates random inputs automatically
- Finds panics, crashes, and undefined behavior
- Continuous test case generation

## Compatibility
- ✅ Apple Silicon (ARM): Compatible (requires `libclang` via Homebrew)
- ✅ Linux (GitHub Actions): Compatible

## Installation

### Apple Silicon: Install libclang first
```bash
brew install llvm
```

### Then install cargo-fuzz
```bash
cargo install cargo-fuzz
```

## Usage

```bash
# Initialize fuzzing
cargo fuzz init

# Add a fuzz target (e.g., for HCL parsing)
cargo fuzz add parse_hcl

# Run fuzzer
cargo fuzz run parse_hcl

# Run with time limit
cargo fuzz run parse_hcl -- -max_total_time=300
```

## Integration Notes
- Requires writing fuzz targets (specific functions to fuzz)
- Good targets for this project:
  - HCL parsing (`parser.rs`)
  - Block extraction (`processor.rs`)
- Can be resource intensive
- Best run with time limits in CI

## Pros
- Effective at finding edge cases
- Automated test case generation
- Finds real bugs and vulnerabilities
- Integrates with LLVM toolchain

## Cons
- Requires writing fuzz targets
- Setup complexity
- Resource intensive (CPU/memory)
- May generate many test cases requiring management
- Requires understanding of fuzzing strategies

## Recommendation
Start with fuzzing the HCL parser, as it's the most critical and error-prone component.

## CI Integration

### Scheduled Workflow (Recommended)

Fuzz testing is resource-intensive and should run on a schedule rather than on every PR or push. Create a scheduled workflow:

**Workflow File**: `.github/workflows/fuzz.yaml`

```yaml
name: Fuzz Testing

on:
  schedule:
    # Run weekly on Sunday at 2 AM UTC
    - cron: '0 2 * * 0'
  workflow_dispatch:  # Allow manual triggering

jobs:
  fuzz:
    runs-on: ubuntu-latest
    timeout-minutes: 60  # Limit total job time
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
      
      - name: Install LLVM (for libFuzzer)
        run: |
          sudo apt-get update
          sudo apt-get install -y llvm-dev libclang-dev clang
      
      - name: Install cargo-fuzz
        run: cargo install cargo-fuzz
      
      - name: Initialize fuzz directory (if needed)
        run: |
          if [ ! -d "fuzz" ]; then
            cargo fuzz init
          fi
        continue-on-error: true
      
      - name: Run fuzz targets with time limits
        run: |
          # Run each fuzz target for 5 minutes
          for target in $(cargo fuzz list); do
            echo "Running fuzz target: $target"
            timeout 300 cargo fuzz run $target -- -max_total_time=300 || true
          done
      
      - name: Upload fuzz artifacts
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: fuzz-artifacts
          path: fuzz/artifacts/
          retention-days: 7
```

### Pull Request Workflow (Optional)

If you want to run fuzz testing on PRs with strict time limits:

```yaml
name: Fuzz Testing (PR)

on:
  pull_request:
    paths:
      - 'src/parser/**'
      - 'src/processor/**'
      - 'fuzz/**'

jobs:
  fuzz-quick:
    runs-on: ubuntu-latest
    timeout-minutes: 10  # Very short timeout for PRs
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
      
      - name: Install LLVM
        run: |
          sudo apt-get update
          sudo apt-get install -y llvm-dev libclang-dev clang
      
      - name: Install cargo-fuzz
        run: cargo install cargo-fuzz
      
      - name: Quick fuzz run (1 minute per target)
        run: |
          for target in $(cargo fuzz list); do
            timeout 60 cargo fuzz run $target -- -max_total_time=60 || true
          done
        continue-on-error: true  # Don't block PRs on fuzz failures
```

### Best Practices for CI

1. **Time Limits**: Always set `-max_total_time` to prevent infinite runs
2. **Scheduled Runs**: Use scheduled workflows for comprehensive fuzzing
3. **Resource Management**: Fuzzing is CPU/memory intensive; consider using larger runners
4. **Artifact Storage**: Store interesting test cases for analysis
5. **Non-Blocking**: Consider making fuzz tests non-blocking for PRs (use `continue-on-error: true`)

### Integration with Continuous Delivery

Fuzz testing is **not** included in the release workflow (`release.yaml`) because:
- It's resource-intensive and time-consuming
- It's better suited for scheduled runs
- Release workflows should be fast and reliable
- Fuzz testing is a quality improvement tool, not a release gate

If fuzz testing finds issues, they should be addressed before the next release, but fuzzing doesn't need to block releases.

## References
- [cargo-fuzz Documentation](https://github.com/rust-fuzz/cargo-fuzz)
- [libFuzzer Documentation](https://llvm.org/docs/LibFuzzer.html)

