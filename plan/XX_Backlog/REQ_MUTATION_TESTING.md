# REQ: Mutation Testing with cargo-mutants

**Status**: 📋 Planned

## Overview
Integrate mutation testing into the project using `cargo-mutants` to identify weaknesses in the test suite by introducing code mutations and verifying test coverage.

## Motivation
The current test suite may have gaps that aren't immediately apparent. Mutation testing helps identify:
- Untested code paths
- Weak or ineffective tests
- Dead code that isn't exercised
- Areas where test quality can be improved

By introducing small mutations (changes) to the code and verifying whether tests detect them, we can improve overall test quality and confidence in the codebase.

## Current Behavior
- Standard unit and integration tests exist
- Test coverage is measured, but coverage metrics don't reveal test quality
- No automated mechanism to identify untested code paths or weak tests
- Test effectiveness is evaluated manually or through code review

## Proposed Behavior
- Install and configure `cargo-mutants` for mutation testing
- Create a scheduled GitHub Actions workflow to run mutation testing weekly
- Configure mutation testing to exclude appropriate files (e.g., `main.rs`, test files)
- Store mutation test results as artifacts for analysis
- Optionally provide a non-blocking PR workflow for incremental mutation testing on changed files

## Use Cases
- **Scheduled Quality Checks**: Run comprehensive mutation testing weekly to identify test gaps
- **Test Quality Improvement**: Use mutation test results to identify and improve weak tests
- **Dead Code Detection**: Identify code that isn't exercised by any tests
- **PR Quality Assurance**: Optionally run limited mutation testing on changed files in PRs (non-blocking)

## Implementation Considerations
- **Compatibility**:
  - ✅ Apple Silicon (ARM): Compatible via `cargo install`
  - ✅ Linux (GitHub Actions): Compatible
- **Time Consumption**: Mutation testing is time-consuming (can take hours) and resource-intensive
- **Test Runner**: Use `cargo-nextest` for faster test execution
- **Scheduling**: Best run on a schedule (weekly) rather than on every commit or PR
- **Non-Blocking**: Should not block PRs or releases; it's a quality improvement tool
- **Configuration**: Create `mutants.toml` to exclude files like `src/main.rs` and `tests/`
- **Results Storage**: Store JSON results as artifacts with 30-day retention
- **Workflow Timeout**: Set appropriate timeouts (120 minutes for scheduled runs, 30 minutes for PR runs)

## Alternatives Considered
- **Running on Every PR**: Rejected because it significantly increases CI time and is resource-intensive
- **Including in Release Workflow**: Rejected because release workflows should be fast and reliable; mutation testing is a quality improvement tool, not a release gate
- **Blocking PRs on Mutation Failures**: Rejected because results may require manual interpretation and shouldn't block development workflow
- **Manual Mutation Testing**: Rejected because automation provides consistent, repeatable quality checks

## Impact
- **Breaking Changes**: No
- **Documentation**:
  - Update `DEVELOPMENT.md` or `TOOLING.md` with mutation testing information
  - Document how to run mutation testing locally
  - Document how to interpret results
- **Testing**:
  - No changes to existing tests required
  - Mutation testing will help identify areas where additional tests are needed
- **Dependencies**:
  - `cargo-mutants` (installed via `cargo install`, not a Cargo.toml dependency)
  - `cargo-nextest` (already used in project)
- **CI/CD**:
  - New scheduled workflow: `.github/workflows/mutation.yaml`
  - Optional PR workflow for incremental testing
  - Artifact storage for results

## Implementation Details

### Installation
```bash
cargo install cargo-mutants
```

### Configuration File
Create `mutants.toml` in project root:
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

### Scheduled Workflow
Create `.github/workflows/mutation.yaml`:
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
```

### Optional PR Workflow
If desired, create a non-blocking PR workflow for incremental testing:
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

## References
- [cargo-mutants Documentation](https://mutants.rs/)
- [Mutation Testing Guide](https://mutants.rs/guide/)
