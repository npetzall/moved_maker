# Phase 7.1: Pull Request Workflow Implementation

## Overview
Integrate security checks, test runner, code coverage, and pre-commit hooks into the pull request workflow to ensure code quality before merging.

## Goals
- Integrate security checks into pull request workflow (blocking)
- Integrate test runner (cargo-nextest) into pull request workflow with JUnit XML output
- Integrate code coverage into pull request workflow with threshold enforcement
- Integrate pre-commit hooks into pull request workflow

## Prerequisites
- [ ] Phase 1 (Security) completed
- [ ] Phase 2 (Test Runner) completed or in progress
- [ ] Phase 4 (Code Coverage) completed or in progress
- [ ] Phase 5 (Pre-commit Hooks) completed or in progress
- [ ] GitHub repository access (admin or owner permissions)

## Workflow File
- **File**: `.github/workflows/pull_request.yaml`
- **Trigger**: Pull requests (opened, synchronize, reopened)

## Implementation Tasks

### 1. Integrate Security Checks into Pull Request Workflow

#### Pull Request Workflow (`.github/workflows/pull_request.yaml`)
- [ ] Create or update `.github/workflows/pull_request.yaml`
- [ ] Add security job:
  - [ ] Set runs-on: `ubuntu-latest`
  - [ ] Add checkout step
  - [ ] Add Rust installation step
  - [ ] Add security tools installation step: `cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable`
  - [ ] Add cargo-deny check step (blocking): `cargo deny check --config .config/deny.toml`
  - [ ] Add cargo-audit update step: `cargo audit update`
  - [ ] Add cargo-audit check step (blocking): `cargo audit --deny warnings`
  - [ ] Add cargo-geiger scan step (blocking): `cargo geiger --output-format Json > geiger-report.json`
- [ ] Verify workflow syntax
- [ ] Test workflow locally (if possible) or create test PR
- [ ] Verify all security checks run and are blocking

### 2. Integrate Test Runner (cargo-nextest) into Pull Request Workflow

**Prerequisites**: Phase 2 (Test Runner) should be completed or in progress.

#### Pull Request Workflow (`.github/workflows/pull_request.yaml`)
- [ ] Open `.github/workflows/pull_request.yaml`
- [ ] Find or create test job
- [ ] Update test job:
  - [ ] Add matrix strategy for multiple OS (if not already present):
    ```yaml
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
    ```
  - [ ] Set runs-on: `${{ matrix.os }}`
  - [ ] Add cargo-nextest installation step:
    ```yaml
    - name: Install cargo-nextest
      uses: taiki-e/install-action@cargo-nextest
    ```
    - [ ] Note: `taiki-e/install-action@cargo-nextest` is a GitHub Action for CI/CD workflows. For local installation, use `cargo install cargo-nextest` (see Phase 2: Test Runner).
  - [ ] Update test step to use cargo-nextest:
    ```yaml
    - name: Run tests
      run: cargo nextest run --junit-xml test-results.xml
    ```
  - [ ] Add test results upload step:
    ```yaml
    - name: Upload test results
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: test-results-${{ matrix.os }}
        path: test-results.xml
    ```
  - [ ] Add doctest step (if applicable):
    ```yaml
    - name: Run doctests
      run: cargo test --doc
    ```
- [ ] Verify workflow syntax
- [ ] Remove old `cargo test` steps if present
- [ ] Commit and push changes

#### Verify Test Runner CI Integration
- [ ] Create test PR or push to branch
- [ ] Verify test job runs in GitHub Actions
- [ ] Verify cargo-nextest is used in CI logs
- [ ] Verify test results are uploaded as artifacts
- [ ] Verify JUnit XML output is generated
- [ ] Verify all tests pass in CI
- [ ] Compare test execution time (optional)

### 3. Integrate Code Coverage into Pull Request Workflow

**Prerequisites**: Phase 4 (Code Coverage) should be completed or in progress.

#### Pull Request Workflow (`.github/workflows/pull_request.yaml`)
- [ ] Open `.github/workflows/pull_request.yaml`
- [ ] Add coverage job:
  - [ ] Set runs-on: `ubuntu-latest`
  - [ ] Add checkout step
  - [ ] Add Rust installation with llvm-tools-preview:
    ```yaml
    - name: Install Rust
      uses: dtolnay/rust-toolchain@stable
      with:
        components: llvm-tools-preview
    ```
  - [ ] Add cargo-nextest installation step:
    ```yaml
    - name: Install cargo-nextest
      uses: taiki-e/install-action@cargo-nextest
    ```
  - [ ] Add cargo-llvm-cov installation step:
    ```yaml
    - name: Install cargo-llvm-cov
      run: cargo install cargo-llvm-cov
    ```
  - [ ] Add coverage generation step:
    ```yaml
    - name: Generate coverage
      run: cargo llvm-cov nextest --all-features --lcov --output-path lcov.info
    ```
    - [ ] Note: This generates coverage in LCOV format for CI integration and coverage services
    - [ ] Verify `lcov.info` file is created in CI artifacts
    - [ ] Review LCOV file format (standard format for coverage services)
    - [ ] Test LCOV file can be uploaded to coverage services (if applicable)
  - [ ] Add coverage threshold check step:
    ```yaml
    - name: Install bc (for coverage threshold calculations)
      run: sudo apt-get update && sudo apt-get install -y bc

    - name: Check coverage thresholds
      run: |
        # Generate coverage and extract percentages
        cargo llvm-cov nextest --all-features --summary-only > coverage-summary.txt
        cat coverage-summary.txt

        # Extract coverage percentages from summary
        LINE_COV=$(grep -oP '^\s*Lines:\s+\K[\d.]+' coverage-summary.txt || echo "0")
        BRANCH_COV=$(grep -oP '^\s*Branches:\s+\K[\d.]+' coverage-summary.txt || echo "0")
        FUNC_COV=$(grep -oP '^\s*Functions:\s+\K[\d.]+' coverage-summary.txt || echo "0")

        # Check thresholds (Line > 80%, Branch > 70%, Function > 85%)
        FAILED=0
        if (( $(echo "$LINE_COV < 80" | bc -l) )); then
          echo "❌ Line coverage $LINE_COV% is below threshold of 80%"
          FAILED=1
        else
          echo "✅ Line coverage: $LINE_COV% (threshold: 80%)"
        fi

        if (( $(echo "$BRANCH_COV < 70" | bc -l) )); then
          echo "❌ Branch coverage $BRANCH_COV% is below threshold of 70%"
          FAILED=1
        else
          echo "✅ Branch coverage: $BRANCH_COV% (threshold: 70%)"
        fi

        if (( $(echo "$FUNC_COV < 85" | bc -l) )); then
          echo "❌ Function coverage $FUNC_COV% is below threshold of 85%"
          FAILED=1
        else
          echo "✅ Function coverage: $FUNC_COV% (threshold: 85%)"
        fi

        if [ $FAILED -eq 1 ]; then
          echo "Coverage thresholds not met. Failing CI."
          exit 1
        fi
    ```
    - [ ] Note: Alternative approach - create a separate script file (e.g., `scripts/check-coverage.sh`) for better maintainability (see Section 3.1)
  - [ ] Add coverage upload step (optional, only if using Codecov or similar service):
    ```yaml
    - name: Upload to Codecov
      if: env.CODECOV_TOKEN != '' || github.event_name == 'pull_request'
      uses: codecov/codecov-action@v3
      with:
        files: lcov.info
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: false  # Don't fail CI if upload fails
    ```
    - [ ] Note: This step is optional and only needed if you want to use Codecov for coverage visualization and tracking. Skip if not using a coverage service.
- [ ] Verify workflow syntax
- [ ] Commit and push changes

#### 3.1. Alternative: Coverage Threshold Script (Optional)

For better maintainability, create a separate script file:

- [ ] Create `scripts/check-coverage.sh`:
  ```bash
  #!/bin/bash
  set -e

  # Check if bc is installed (required for threshold comparisons)
  if ! command -v bc &> /dev/null; then
    echo "Error: bc is required but not installed. Install with: sudo apt-get install bc"
    exit 1
  fi

  # Generate coverage summary
  cargo llvm-cov nextest --all-features --summary-only > coverage-summary.txt

  # Extract percentages (adjust regex based on actual output format)
  LINE_COV=$(grep -oP 'Lines:\s+\K[\d.]+' coverage-summary.txt || echo "0")
  BRANCH_COV=$(grep -oP 'Branches:\s+\K[\d.]+' coverage-summary.txt || echo "0")
  FUNC_COV=$(grep -oP 'Functions:\s+\K[\d.]+' coverage-summary.txt || echo "0")

  # Check thresholds
  THRESHOLDS_MET=true
  [ $(echo "$LINE_COV < 80" | bc -l) -eq 1 ] && echo "Line coverage $LINE_COV% < 80%" && THRESHOLDS_MET=false
  [ $(echo "$BRANCH_COV < 70" | bc -l) -eq 1 ] && echo "Branch coverage $BRANCH_COV% < 70%" && THRESHOLDS_MET=false
  [ $(echo "$FUNC_COV < 85" | bc -l) -eq 1 ] && echo "Function coverage $FUNC_COV% < 85%" && THRESHOLDS_MET=false

  [ "$THRESHOLDS_MET" = false ] && exit 1
  exit 0
  ```
- [ ] Make script executable: `chmod +x scripts/check-coverage.sh`
- [ ] Test script locally: `./scripts/check-coverage.sh`
- [ ] Update CI workflow to call script:
  ```yaml
  - name: Check coverage thresholds
    run: ./scripts/check-coverage.sh
  ```

#### Verify Coverage CI Integration
- [ ] Create test PR or push to branch
- [ ] Verify coverage job runs in GitHub Actions
- [ ] Verify coverage thresholds are enforced (CI fails if below thresholds)
- [ ] Verify coverage reports are generated (lcov.info)
- [ ] Verify coverage upload works (if using Codecov)
- [ ] Verify all coverage checks pass in CI

### 3.2. Configure Coverage Service (Optional)

**Note**: This section covers configuring external coverage services like Codecov. The upload step is already included in Section 3 above.

#### Codecov (Recommended)
- [ ] Sign up for Codecov account (if not already)
- [ ] Add repository to Codecov
- [ ] Get Codecov token (if required)
- [ ] Configure Codecov settings:
  - [ ] Set coverage thresholds
  - [ ] Configure coverage reports
  - [ ] Set up coverage badges (if desired)
- [ ] Note: Codecov upload step is already configured in CI workflow (see Section 3 above)
- [ ] Verify coverage reports appear in Codecov after PR is created/updated

#### Alternative: Coveralls, Code Climate, etc.
- [ ] Choose coverage service
- [ ] Configure service account and repository
- [ ] Get service token/credentials (if required)
- [ ] Update CI workflow upload step (see Section 3) to use chosen service
- [ ] Verify coverage reports appear in service dashboard

### 4. Integrate Pre-commit Hooks into Pull Request Workflow

**Prerequisites**: Phase 5 (Pre-commit Hooks) should be completed or in progress.

#### Pull Request Workflow (`.github/workflows/pull_request.yaml`)
- [ ] Open `.github/workflows/pull_request.yaml`
- [ ] Add pre-commit job:
  ```yaml
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: dtolnay/rust-toolchain@stable

      - name: Install pre-commit
        run: pip install pre-commit

      - name: Install cargo-nextest
        uses: taiki-e/install-action@cargo-nextest

      - name: Run pre-commit
        run: pre-commit run --all-files
  ```
- [ ] Verify workflow syntax
- [ ] Commit and push changes
- [ ] Verify pre-commit job runs in CI

#### Verify Pre-commit CI Integration
- [ ] Create test PR or push to branch
- [ ] Verify pre-commit job runs in GitHub Actions
- [ ] Verify all pre-commit hooks pass in CI
- [ ] Verify formatting checks run
- [ ] Verify clippy checks run
- [ ] Verify tests run via pre-commit
- [ ] Verify file checks (trailing whitespace, YAML, etc.) run

### 5. Test Workflow Locally with `act` (Optional)

**Note**: Testing workflows locally is optional but recommended before pushing to GitHub. The `act` tool allows you to run GitHub Actions workflows locally.

#### Install `act`

**macOS (Homebrew)**:
```bash
brew install act
```

**Linux**:
```bash
# Download from releases: https://github.com/nektos/act/releases
# Or use a package manager if available
```

**Windows**:
```bash
# Use WSL or download from releases: https://github.com/nektos/act/releases
```

#### Basic Usage

**List available workflows**:
```bash
act -l
```

**Run a specific workflow**:
```bash
# Run pull request workflow
act pull_request
```

**Run a specific job**:
```bash
# Run only the security job from pull_request workflow
act pull_request -j security

# Run test job
act pull_request -j test

# Run coverage job
act pull_request -j coverage

# Run pre-commit job
act pull_request -j pre-commit
```

#### Limitations and Considerations

**Limitations**:
- `act` runs workflows in Docker containers, so some actions may behave differently
- Secrets need to be provided via `.secrets` file or environment variables
- Some actions may not be fully compatible with `act`

**What works well**:
- Testing workflow syntax and structure
- Testing shell scripts and commands
- Validating job dependencies
- Testing build steps locally

**What doesn't work well**:
- Actions that depend on GitHub context
- Some GitHub-specific actions

#### Providing Secrets

Create a `.secrets` file in the project root (add to `.gitignore`):
```
GITHUB_TOKEN=your_token_here
```

Then run:
```bash
act pull_request --secret-file .secrets
```

#### Recommended Testing Strategy

1. **Test workflow syntax**: Use `act -l` to verify workflows are parseable
2. **Test individual jobs**: Test each job independently before testing full workflow
3. **Test on GitHub**: Always verify workflows work on GitHub Actions after local testing
4. **Use test PRs**: Create test PRs to verify PR workflows work correctly

#### Troubleshooting `act`

**Issue**: `act` can't find Docker
- **Solution**: Ensure Docker is installed and running

**Issue**: Workflow fails with "action not found"
- **Solution**: Some actions may not be compatible with `act`. Test on GitHub Actions instead.

**Issue**: Workflow runs but behaves differently
- **Solution**: `act` is an approximation. Always verify workflows work on GitHub Actions.

#### References

- [act Documentation](https://github.com/nektos/act)
- [act Installation Guide](https://github.com/nektos/act#installation)

## Verification

- [ ] PR workflow includes security checks
- [ ] PR workflow includes test runner (cargo-nextest) with JUnit XML output
- [ ] Test results are uploaded as artifacts in PR workflow
- [ ] PR workflow includes coverage job with threshold enforcement
- [ ] Coverage thresholds are enforced in CI (blocking)
- [ ] PR workflow includes pre-commit job
- [ ] Pre-commit hooks run in CI and pass
- [ ] All jobs are blocking (must pass before merge)

## Success Criteria

- [x] Security checks integrated into PR workflow (blocking)
- [x] Test runner (cargo-nextest) integrated into PR workflow with JUnit XML output
- [x] Test results uploaded as artifacts in PR workflow
- [x] Code coverage integrated into PR workflow (blocking)
- [x] Coverage thresholds enforced in CI (Line > 80%, Branch > 70%, Function > 85%)
- [x] Pre-commit hooks integrated into PR workflow
- [ ] Pre-commit job runs in CI and passes (needs testing)
- [ ] Workflow tested and working (needs testing)

## Troubleshooting

### Security Checks Fail
- Verify all security tools are installed correctly
- Check security tool outputs for specific failures
- Fix security issues before retrying

### Test Job Fails
- Check test output for specific test failures
- Verify cargo-nextest is installed correctly
- Review test logs for errors

### Coverage Job Fails
- Verify coverage thresholds are met
- Check coverage generation output
- Review coverage summary for issues

### Pre-commit Job Fails
- Check which pre-commit hook failed
- Review hook output for specific issues
- Fix issues locally and re-run

## References

- [Main Continuous Delivery Plan](./07_Continuous_Delivery.md) - Overview and architecture
- [PR Label Workflow Plan](./07_02_PR_Label_Workflow.md) - PR label workflow
- [Release Workflow Plan](./07_03_Release_Workflow.md) - Release workflow
