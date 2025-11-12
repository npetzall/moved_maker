# Phase 7: Continuous Delivery Implementation Plan

## Overview
Automate the release process so that each push to the `main` branch creates a new GitHub release with compiled binaries for multiple platforms.

## Goals
- Integrate security checks into pull request workflow
- Integrate test runner (cargo-nextest) into pull request workflow with JUnit XML output
- Automate release creation on pushes to `main`
- Build binaries for multiple platforms (Linux x86_64/ARM64, macOS Intel/Apple Silicon)
- Calculate version from PR labels (from Phase 6)
- Generate release notes automatically
- Include binary checksums for verification
- Integrate security checks into release process

## Prerequisites
- [ ] Phase 1 (Security) completed
- [ ] Phase 2 (Test Runner) completed or in progress (for PR workflow integration)
- [ ] Phase 4 (Coverage) completed or in progress
- [ ] Phase 6 (GitHub Configuration) completed (version labels and PR label workflow)
- [ ] GitHub repository access (admin or owner permissions)
- [ ] CI workflows created (pull_request.yaml)

## Implementation Tasks

### 1. Integrate Security Checks into Pull Request Workflow

#### Pull Request Workflow (`.github/workflows/pull_request.yaml`)
- [ ] Create or update `.github/workflows/pull_request.yaml`
- [ ] Add security job:
  - [ ] Set runs-on: `ubuntu-latest`
  - [ ] Add checkout step
  - [ ] Add Rust installation step
  - [ ] Add security tools installation step: `cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable`
  - [ ] Add cargo-deny check step (blocking): `cargo deny check`
  - [ ] Add cargo-audit update step: `cargo audit update`
  - [ ] Add cargo-audit check step (blocking): `cargo audit --deny warnings`
  - [ ] Add cargo-geiger scan step (blocking): `cargo geiger --output-format json > geiger-report.json`
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

### 3. Create Release Workflow File

- [ ] Create `.github/workflows/release.yaml` file
- [ ] Add workflow name and trigger:
  ```yaml
  name: Release
  
  on:
    push:
      branches:
        - main
  ```
- [ ] Verify workflow file is created in correct location

### 4. Add Security Job to Release Workflow

- [ ] Add security job (must run before builds):
  ```yaml
  jobs:
    security:
      runs-on: ubuntu-latest
      steps:
        - name: Checkout code
          uses: actions/checkout@v4
        
        - name: Install Rust
          uses: dtolnay/rust-toolchain@stable
        
        - name: Install security tools
          run: cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable
        
        - name: Run cargo-deny checks (blocking)
          run: cargo deny check
        
        - name: Update vulnerability database
          run: cargo audit update
        
        - name: Run cargo-audit checks (blocking)
          run: cargo audit --deny warnings
        
        - name: Run cargo-geiger scan (blocking)
          run: cargo geiger --output-format json > geiger-report.json
  ```
- [ ] Add binary build step: `cargo auditable build --release`
- [ ] Add binary audit step: `cargo audit bin target/release/move_maker`
- [ ] Ensure build-and-release job depends on security job: `needs: [security]`
- [ ] Verify security job blocks release if checks fail
- [ ] Verify workflow syntax
- [ ] Document that security checks block releases
- [ ] Commit security job to workflow

### 5. Add Version Calculation Job

- [ ] Add version job (depends on security):
  ```yaml
    version:
      needs: security
      runs-on: ubuntu-latest
      permissions:
        contents: read
        pull-requests: read
      outputs:
        version: ${{ steps.version.outputs.version }}
        tag_name: ${{ steps.version.outputs.tag_name }}
      steps:
        - name: Checkout code
          uses: actions/checkout@v4
          with:
            fetch-depth: 0
  ```
- [ ] Add GitHub CLI setup:
  ```yaml
        - name: Setup GitHub CLI
          uses: cli/cli-action@v2
          with:
            github-token: ${{ secrets.GITHUB_TOKEN }}
  ```
- [ ] Add version calculation step (from CONTINUOUS_DELIVERY.md):
  - [ ] Get latest tag
  - [ ] Get merged PRs since last tag
  - [ ] Read PR labels to determine bump type
  - [ ] Calculate new version
  - [ ] Output version and tag_name
- [ ] Add Cargo.toml version update step:
  ```yaml
        - name: Update Cargo.toml version
          run: |
            sed -i "s/^version = \".*\"/version = \"${{ steps.version.outputs.version }}\"/" Cargo.toml
            echo "Updated Cargo.toml version to ${{ steps.version.outputs.version }}"
      ```
- [ ] Verify version calculation logic matches VERSIONING.md strategy
- [ ] Test version calculation locally (if possible) or in test PR

### 6. Add Multi-Platform Build Job

- [ ] Add build-and-release job (depends on security and version):
  ```yaml
    build-and-release:
      needs: [security, version]
      runs-on: ${{ matrix.os }}
      strategy:
        matrix:
          include:
            - os: ubuntu-latest
              target: x86_64-unknown-linux-gnu
              artifact_name: move_maker-linux-x86_64
            - os: ubuntu-latest
              target: aarch64-unknown-linux-gnu
              artifact_name: move_maker-linux-aarch64
            - os: macos-latest
              target: x86_64-apple-darwin
              artifact_name: move_maker-macos-x86_64
            - os: macos-latest
              target: aarch64-apple-darwin
              artifact_name: move_maker-macos-aarch64
  ```
- [ ] Add permissions:
  ```yaml
      permissions:
        contents: write
  ```
- [ ] Add checkout step:
  ```yaml
      steps:
        - name: Checkout code
          uses: actions/checkout@v4
          with:
            fetch-depth: 0
  ```
- [ ] Add Cargo.toml version update step:
  ```yaml
        - name: Update Cargo.toml with calculated version
          run: |
            sed -i "s/^version = \".*\"/version = \"${{ needs.version.outputs.version }}\"/" Cargo.toml
            echo "Updated Cargo.toml version to ${{ needs.version.outputs.version }}"
      ```
- [ ] Add Rust installation with target:
  ```yaml
        - name: Install Rust
          uses: dtolnay/rust-toolchain@stable
          with:
            targets: ${{ matrix.target }}
      ```
- [ ] Add cargo-nextest installation:
  ```yaml
        - name: Install cargo-nextest
          uses: taiki-e/install-action@cargo-nextest
      ```
- [ ] Add test step:
  ```yaml
        - name: Run tests
          run: cargo nextest run
      ```
- [ ] Add cargo-auditable installation:
  ```yaml
        - name: Install cargo-auditable
          run: cargo install cargo-auditable
      ```
- [ ] Add release build step:
  ```yaml
        - name: Build release binary with embedded dependency info
          run: cargo auditable build --release --target ${{ matrix.target }}
      ```
- [ ] Add cargo-audit installation:
  ```yaml
        - name: Install cargo-audit for binary auditing
          run: cargo install cargo-audit
      ```
- [ ] Add binary audit step:
  ```yaml
        - name: Audit release binary
          run: cargo audit bin target/${{ matrix.target }}/release/move_maker
      ```
- [ ] Add binary stripping step (Linux/macOS):
  ```yaml
        - name: Strip binary (Linux/macOS)
          if: matrix.os != 'windows'
          run: strip target/${{ matrix.target }}/release/move_maker
      ```
- [ ] Add artifact upload step:
  ```yaml
        - name: Upload artifact
          uses: actions/upload-artifact@v4
          with:
            name: ${{ matrix.artifact_name }}
            path: target/${{ matrix.target }}/release/move_maker
            retention-days: 1
      ```
- [ ] Add checksum creation step:
  ```yaml
        - name: Create checksum
          shell: bash
          run: |
            cd target/${{ matrix.target }}/release
            shasum -a 256 move_maker > move_maker.sha256
            cat move_maker.sha256
      ```
- [ ] Add checksum upload step:
  ```yaml
        - name: Upload checksum
          uses: actions/upload-artifact@v4
          with:
            name: ${{ matrix.artifact_name }}.sha256
            path: target/${{ matrix.target }}/release/move_maker.sha256
            retention-days: 1
      ```
- [ ] Verify all build steps are correct
- [ ] Commit build job to workflow

### 7. Add Release Job

- [ ] Add release job (depends on security, version, and build-and-release):
  ```yaml
    release:
      needs: [security, version, build-and-release]
      runs-on: ubuntu-latest
      permissions:
        contents: write
  ```
- [ ] Add checkout step:
  ```yaml
      steps:
        - name: Checkout code
          uses: actions/checkout@v4
          with:
            fetch-depth: 0
  ```
- [ ] Add release notes generation step:
  ```yaml
        - name: Generate release notes
          id: release_notes
          run: |
            # Get commits since last tag, or all commits if no tags
            if git describe --tags --abbrev=0 2>/dev/null; then
              LAST_TAG=$(git describe --tags --abbrev=0)
              NOTES=$(git log ${LAST_TAG}..HEAD --pretty=format:"- %s (%h)" --no-merges)
            else
              NOTES=$(git log --pretty=format:"- %s (%h)" --no-merges -10)
            fi
            
            if [ -z "$NOTES" ]; then
              NOTES="- No significant changes"
            fi
            
            {
              echo "## Changes"
              echo ""
              echo "$NOTES"
              echo ""
              echo "## Installation"
              echo ""
              echo "Download the appropriate binary for your platform:"
              echo "- Linux (x86_64): \`move_maker-linux-x86_64\`"
              echo "- Linux (ARM64): \`move_maker-linux-aarch64\`"
              echo "- macOS (Intel): \`move_maker-macos-x86_64\`"
              echo "- macOS (Apple Silicon): \`move_maker-macos-aarch64\`"
            } > release_notes.md
            
            echo "notes<<EOF" >> $GITHUB_OUTPUT
            cat release_notes.md >> $GITHUB_OUTPUT
            echo "EOF" >> $GITHUB_OUTPUT
      ```
- [ ] Add artifact download step:
  ```yaml
        - name: Download all artifacts
          uses: actions/download-artifact@v4
          with:
            path: artifacts
      ```
- [ ] Add Cargo.toml version update step:
  ```yaml
        - name: Update Cargo.toml with calculated version
          run: |
            sed -i "s/^version = \".*\"/version = \"${{ needs.version.outputs.version }}\"/" Cargo.toml
            echo "Updated Cargo.toml version to ${{ needs.version.outputs.version }}"
      ```
- [ ] Add git commit and push step (optional, to update Cargo.toml in repo):
  ```yaml
        - name: Commit and push version update
          run: |
            git config user.name "github-actions[bot]"
            git config user.email "github-actions[bot]@users.noreply.github.com"
            git add Cargo.toml
            git commit -m "chore: bump version to ${{ needs.version.outputs.version }}" || true
            git push origin HEAD:main || true
      ```
- [ ] Add git tag creation step:
  ```yaml
        - name: Create git tag
          run: |
            git tag -a "${{ needs.version.outputs.tag_name }}" -m "Release ${{ needs.version.outputs.tag_name }}"
            git push origin "${{ needs.version.outputs.tag_name }}"
      ```
- [ ] Add GitHub release creation step:
  ```yaml
        - name: Create GitHub Release
          uses: softprops/action-gh-release@v2
          with:
            tag_name: ${{ needs.version.outputs.tag_name }}
            name: Release ${{ needs.version.outputs.tag_name }}
            body: ${{ steps.release_notes.outputs.notes }}
            files: |
              artifacts/move_maker-linux-x86_64
              artifacts/move_maker-linux-x86_64.sha256
              artifacts/move_maker-linux-aarch64
              artifacts/move_maker-linux-aarch64.sha256
              artifacts/move_maker-macos-x86_64
              artifacts/move_maker-macos-x86_64.sha256
              artifacts/move_maker-macos-aarch64
              artifacts/move_maker-macos-aarch64.sha256
            draft: false
            prerelease: false
          env:
            GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      ```
- [ ] Verify release job is complete
- [ ] Commit release job to workflow

### 8. Verify Workflow Syntax

- [ ] Validate YAML syntax: Use online YAML validator or GitHub Actions syntax check
- [ ] Review workflow for:
  - [ ] Correct job dependencies
  - [ ] Correct permissions
  - [ ] Correct artifact names
  - [ ] Correct file paths
  - [ ] Correct version calculation logic
- [ ] Fix any syntax errors
- [ ] Commit complete workflow file

### 9. Test Release Workflow (Dry Run)

- [ ] Create a test branch from `main`
- [ ] Make a small change (e.g., update README)
- [ ] Commit with Conventional Commits format: `chore: test release workflow`
- [ ] Push branch and create pull request
- [ ] Verify PR label workflow applies appropriate label
- [ ] Merge PR to `main` (or simulate merge)
- [ ] Verify release workflow triggers on push to `main`
- [ ] Monitor workflow execution in GitHub Actions
- [ ] Verify all jobs complete successfully:
  - [ ] Security job passes
  - [ ] Version job calculates version correctly
  - [ ] Build jobs complete for all platforms
  - [ ] Release job creates release
- [ ] Review created release:
  - [ ] Verify release tag is created
  - [ ] Verify release notes are generated
  - [ ] Verify binaries are attached
  - [ ] Verify checksums are attached
- [ ] Test downloading and verifying a binary
- [ ] Delete test release (if needed)

### 10. Handle Version Calculation Edge Cases

- [ ] Test version calculation with no previous tags (first release)
- [ ] Test version calculation with major version label
- [ ] Test version calculation with minor version label
- [ ] Test version calculation with no label (patch)
- [ ] Test version calculation with multiple PRs
- [ ] Test version calculation with conflicting labels (should take highest)
- [ ] Verify version is updated in Cargo.toml
- [ ] Verify version is used in release tag

### 11. Optimize Workflow (if needed)

- [ ] Review workflow execution time
- [ ] Consider caching dependencies (if applicable)
- [ ] Consider parallelizing independent jobs
- [ ] Review artifact retention settings
- [ ] Optimize build steps if needed

### 12. Add Binary Signing (Optional)

- [ ] Decide if binary signing is needed
- [ ] If yes:
  - [ ] Set up GPG key or code signing certificate
  - [ ] Add signing step to build job
  - [ ] Upload signed binaries
  - [ ] Document signing process
- [ ] If no, document decision

### 13. Update Documentation

- [ ] Update project README with release information:
  - [ ] How releases work
  - [ ] How to download binaries
  - [ ] How to verify checksums
  - [ ] Versioning strategy
- [ ] Document release process
- [ ] Document version calculation logic
- [ ] Add installation instructions for each platform
- [ ] Update CHANGELOG.md (if exists) or document release notes format

### 14. Verification

- [ ] PR workflow includes security checks
- [ ] PR workflow includes test runner (cargo-nextest) with JUnit XML output
- [ ] Test results are uploaded as artifacts in PR workflow
- [ ] Release workflow file exists and is correct
- [ ] Workflow triggers on pushes to `main`
- [ ] All jobs complete successfully
- [ ] Version is calculated correctly
- [ ] Binaries are built for all platforms
- [ ] Release is created with correct tag
- [ ] Release notes are generated
- [ ] Binaries and checksums are attached
- [ ] Cargo.toml version is updated
- [ ] Git tag is created
- [ ] Documentation is updated

## Success Criteria

- [ ] Security checks integrated into PR workflow (blocking)
- [ ] Test runner (cargo-nextest) integrated into PR workflow with JUnit XML output
- [ ] Test results uploaded as artifacts in PR workflow
- [ ] Security checks integrated into release workflow (blocking)
- [ ] Release workflow created (`.github/workflows/release.yaml`)
- [ ] Security checks run before builds (blocking)
- [ ] Version is calculated from PR labels
- [ ] Binaries are built for all target platforms
- [ ] Release is created automatically on push to `main`
- [ ] Release includes binaries and checksums
- [ ] Release notes are generated automatically
- [ ] Git tag is created with version
- [ ] Cargo.toml version is updated
- [ ] Workflow tested and working
- [ ] Documentation updated

## Release Platforms

- Linux x86_64 (`x86_64-unknown-linux-gnu`)
- Linux ARM64 (`aarch64-unknown-linux-gnu`)
- macOS Intel (`x86_64-apple-darwin`)
- macOS Apple Silicon (`aarch64-apple-darwin`)

## Version Calculation

Version is calculated from PR labels (from Phase 6):
- `version: major` or `breaking` → MAJOR bump
- `version: minor` or `feature` → MINOR bump
- No label → PATCH bump (by commit count)

See VERSIONING.md for detailed versioning strategy.

## Notes

- All releases are triggered automatically on pushes to `main`
- All security tools are **blocking** in CI/CD workflows
- Security checks must pass before builds or releases proceed
- Security checks run in both PR and release workflows
- Version is calculated from PR labels applied by PR label workflow
- Binaries are built with embedded dependency info (cargo-auditable)
- Release binaries are audited after build
- Checksums are generated for all binaries

## Troubleshooting

### Workflow Fails on Security Checks
- Verify all security tools are installed correctly
- Check security tool outputs for specific failures
- Fix security issues before retrying

### Version Calculation Fails
- Verify PR label workflow is working
- Check that PRs have appropriate labels
- Verify GitHub CLI has correct permissions
- Check version calculation script logic

### Build Fails on Specific Platform
- Check platform-specific build issues
- Verify Rust target is installed
- Check for platform-specific dependencies
- Review build logs for errors

### Release Creation Fails
- Verify GITHUB_TOKEN has correct permissions
- Check that tag doesn't already exist
- Verify release notes generation works
- Check artifact paths are correct

## References

- [softprops/action-gh-release](https://github.com/softprops/action-gh-release)
- [GitHub Actions: Creating Releases](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#release)
- [CONTINUOUS_DELIVERY.md](../plan/01_Quality/CONTINUOUS_DELIVERY.md) - Detailed CD documentation
- [VERSIONING.md](../plan/01_Quality/VERSIONING.md) - Versioning strategy documentation

