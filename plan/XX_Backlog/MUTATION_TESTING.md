# Mutation Testing: cargo-mutants

## Purpose
Identify weaknesses in test suite by introducing code mutations

## Features
- Introduces small changes (mutations) to code
- Verifies if tests detect the mutations
- Identifies untested code paths
- Helps improve test quality

## Compatibility
- ✅ Apple Silicon (ARM): Compatible via `cargo install`
- ✅ Linux (GitHub Actions): Compatible

## Installation

```bash
cargo install cargo-mutants
```

## Usage

```bash
# Run mutation testing
cargo mutants

# Run with specific test runner
cargo mutants --test-runner cargo-nextest

# Run with timeout
cargo mutants --timeout 300
```

## Integration Notes
- Works with standard Rust tests
- Can be time-consuming (runs many test iterations)
- Best run in CI on a schedule rather than every commit
- Results may require manual review

## Pros
- Reveals untested code paths
- Encourages writing more effective tests
- Helps identify dead code
- No code changes required

## Cons
- Time-consuming (can take significant time)
- May produce false positives requiring review
- Resource intensive
- Best used periodically, not on every CI run

## Recommendation
Run on a schedule (e.g., nightly or weekly) rather than on every PR.

## CI Integration

### Scheduled Workflow (Recommended)

Mutation testing is time-consuming and should run on a schedule rather than on every PR or push. Create a scheduled workflow:

**Workflow File**: `.github/workflows/mutation.yaml`

```yaml
name: Mutation Testing

on:
  schedule:
    # Run weekly on Monday at 3 AM UTC
    - cron: '0 3 * * 1'
  workflow_dispatch:  # Allow manual triggering

jobs:
  mutation:
    runs-on: ubuntu-latest
    timeout-minutes: 120  # Allow up to 2 hours for mutation testing
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
      
      - name: Install cargo-nextest
        uses: taiki-e/install-action@cargo-nextest
      
      - name: Install cargo-mutants
        run: cargo install cargo-mutants
      
      - name: Run mutation testing
        run: |
          cargo mutants --test-runner cargo-nextest \
            --timeout 300 \
            --output json > mutation-results.json || true
      
      - name: Upload mutation results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: mutation-results
          path: mutation-results.json
          retention-days: 30
      
      - name: Comment on PR (if applicable)
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('mutation-results.json', 'utf8'));
            // Generate comment with mutation test results
            // This is optional and requires custom implementation
```

### Pull Request Workflow (Optional)

If you want to run mutation testing on PRs with limited scope:

```yaml
name: Mutation Testing (PR)

on:
  pull_request:
    paths:
      - 'src/**'
      - 'tests/**'

jobs:
  mutation-quick:
    runs-on: ubuntu-latest
    timeout-minutes: 30  # Shorter timeout for PRs
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
      
      - name: Install cargo-nextest
        uses: taiki-e/install-action@cargo-nextest
      
      - name: Install cargo-mutants
        run: cargo install cargo-mutants
      
      - name: Quick mutation test (changed files only)
        run: |
          # Only test mutations in changed files
          cargo mutants --test-runner cargo-nextest \
            --timeout 120 \
            --files-changed || true
        continue-on-error: true  # Don't block PRs on mutation failures
```

### Best Practices for CI

1. **Scheduled Runs**: Use scheduled workflows for comprehensive mutation testing
2. **Time Limits**: Set appropriate timeouts to prevent infinite runs
3. **Test Runner**: Use `cargo-nextest` for faster test execution
4. **Non-Blocking**: Consider making mutation tests non-blocking for PRs
5. **Results Storage**: Store results as artifacts for analysis
6. **Incremental Testing**: For PRs, consider testing only changed files

### Integration with Continuous Delivery

Mutation testing is **not** included in the release workflow (`release.yaml`) because:
- It's time-consuming and resource-intensive
- It's better suited for scheduled runs
- Release workflows should be fast and reliable
- Mutation testing is a quality improvement tool, not a release gate

If mutation testing reveals test gaps, they should be addressed, but mutation testing doesn't need to block releases.

### Integration with Pull Request Checks

Mutation testing is **not** included in the pull request workflow (`pull_request.yaml`) by default because:
- It significantly increases CI time
- It's resource-intensive
- Results may require manual interpretation

If you want to include mutation testing in PR checks:
1. Make it non-blocking (`continue-on-error: true`)
2. Use shorter timeouts
3. Consider testing only changed files
4. Add it as an optional job that can be triggered manually

## Configuration

### Mutation Testing Configuration File

Create `mutants.toml` in the project root to configure mutation testing:

```toml
# Exclude specific files or directories from mutation testing
exclude = [
    "src/main.rs",  # Main entry point
    "tests/",       # Test files themselves
]

# Set default timeout per mutation
timeout = 300

# Test runner to use
test-runner = "cargo-nextest"
```

## References
- [cargo-mutants Documentation](https://mutants.rs/)
- [Mutation Testing Guide](https://mutants.rs/guide/)

