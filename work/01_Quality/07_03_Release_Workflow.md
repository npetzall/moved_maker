# Phase 7.3: Release Workflow Implementation

## Overview
Automate the release process so that each push to the `main` branch creates a new GitHub release with compiled binaries for multiple platforms. The workflow calculates version from PR labels, builds binaries, and creates releases automatically.

## Goals
- Automate release creation on pushes to `main`
- Build binaries for multiple platforms (Linux x86_64/ARM64, macOS Intel/Apple Silicon)
- Calculate version from PR labels (labels created in Phase 6, applied by PR label workflow)
- Generate release notes automatically
- Include binary checksums for verification
- Integrate security checks into release process

## Prerequisites
- [ ] Phase 1 (Security) completed
- [ ] Phase 6 (GitHub Configuration) completed (version labels created in GitHub UI)
- [ ] Phase 7.2 (PR Label Workflow) completed (labels are being applied to PRs)
- [ ] GitHub repository access (admin or owner permissions)

## Workflow File
- **File**: `.github/workflows/release.yaml`
- **Trigger**: Push to `main` branch

## Required Permissions
- `contents: write` - To create releases, tags, and update Cargo.toml
- `pull-requests: read` - To read PR labels for version calculation

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

## Implementation Tasks

### 1. Create Release Workflow File

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

### 2. Add Security Job to Release Workflow

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
          run: cargo geiger --output-format Json > geiger-report.json
  ```
- [ ] Note: Binary build and audit steps are handled in the build-and-release job (Section 4). This security job only runs source-level security checks.
- [ ] Ensure build-and-release job depends on security job: `needs: [security]`
- [ ] Verify security job blocks release if checks fail
- [ ] Verify workflow syntax
- [ ] Document that security checks block releases
- [ ] Commit security job to workflow

### 3. Add Version Calculation Job

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
- [ ] Add version calculation step:
  ```yaml
        - name: Fetch all tags
          run: git fetch --tags --force

        - name: Calculate version from PR labels
          id: version
          run: |
            set -e  # Exit on error - abort workflow if version calculation fails

            # Get latest tag matching v* pattern
            LATEST_TAG=$(git describe --tags --match "v*" --abbrev=0 2>/dev/null || echo "")

            if [ -z "$LATEST_TAG" ]; then
              # No tag found (first release), use base version from Cargo.toml
              BASE_VERSION=$(grep '^version = ' Cargo.toml | cut -d '"' -f 2)
              if [ -z "$BASE_VERSION" ]; then
                echo "Error: No version found in Cargo.toml and no previous tags exist"
                exit 1
              fi
              VERSION="$BASE_VERSION"
              echo "No previous tag found (first release), using base version from Cargo.toml: $VERSION"
            else
              # Extract version from tag (remove 'v' prefix)
              BASE_VERSION="${LATEST_TAG#v}"

              # Parse version components
              IFS='.' read -r MAJOR MINOR PATCH <<< "$BASE_VERSION"

              # Get merged PRs since last tag
              TAG_DATE=$(git log -1 --format=%ct ${LATEST_TAG})
              PRS=$(gh pr list --state merged --base main --json number,labels,mergedAt --limit 100)

              MAJOR_BUMP=false
              MINOR_BUMP=false

              # Check labels on merged PRs (labels are source of truth, already auto-applied)
              for PR_NUM in $(echo "$PRS" | jq -r '.[] | select(.mergedAt != null) | select((.mergedAt | fromdateiso8601) > '$TAG_DATE') | .number'); do
                LABELS=$(gh pr view $PR_NUM --json labels --jq '.labels[].name' | tr '\n' ' ')

                if echo "$LABELS" | grep -qE "(version: major|breaking)"; then
                  MAJOR_BUMP=true
                  echo "PR #$PR_NUM has major version label"
                elif echo "$LABELS" | grep -qE "(version: minor|feature)"; then
                  MINOR_BUMP=true
                  echo "PR #$PR_NUM has minor version label"
                fi
                # No label = patch bump (handled below)
              done

              # Calculate version based on highest bump type found
              if [ "$MAJOR_BUMP" = true ]; then
                MAJOR=$((MAJOR + 1))
                MINOR=0
                PATCH=0
                BUMP_TYPE="MAJOR"
              elif [ "$MINOR_BUMP" = true ]; then
                MINOR=$((MINOR + 1))
                PATCH=0
                BUMP_TYPE="MINOR"
              else
                # PATCH bump by commit count
                COMMIT_COUNT=$(git rev-list --count ${LATEST_TAG}..HEAD)
                PATCH=$((PATCH + COMMIT_COUNT))
                BUMP_TYPE="PATCH"
              fi

              VERSION="${MAJOR}.${MINOR}.${PATCH}"

              echo "Latest tag: $LATEST_TAG"
              echo "Bump type: $BUMP_TYPE"
              echo "Calculated version: $VERSION"
            fi

            echo "version=$VERSION" >> $GITHUB_OUTPUT
            echo "tag_name=v$VERSION" >> $GITHUB_OUTPUT
          ```
  - [ ] Note: `jq` is pre-installed on GitHub Actions `ubuntu-latest` runners, so no installation step is needed
  - [ ] Note: The script uses `set -e` to abort the workflow if version calculation fails. If any step in the version calculation fails, the workflow will abort and no release will be created.
  - [ ] Note: **First release behavior**: When no tags exist, the workflow uses the version from `Cargo.toml` as-is. This creates the first release and tag, which subsequent releases will use as a reference point.
- [ ] Add Cargo.toml version update step:
  ```yaml
        - name: Update Cargo.toml version
          run: |
            sed -i "s/^version = \".*\"/version = \"${{ steps.version.outputs.version }}\"/" Cargo.toml
            echo "Updated Cargo.toml version to ${{ steps.version.outputs.version }}"
      ```
  - [ ] Note: The version job updates Cargo.toml first. The build-and-release and release jobs also update it to ensure consistency across all jobs, since each job checks out the code independently.
- [ ] Verify version calculation logic matches VERSIONING.md strategy
- [ ] Test version calculation locally (if possible) or in test PR

### 4. Add Multi-Platform Build Job

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
- [ ] Add Cargo.toml version update step (ensures consistency, even though version job already updated it):
  ```yaml
        - name: Update Cargo.toml with calculated version
          run: |
            sed -i "s/^version = \".*\"/version = \"${{ needs.version.outputs.version }}\"/" Cargo.toml
            echo "Updated Cargo.toml version to ${{ needs.version.outputs.version }}"
      ```
  - [ ] Note: This step ensures the version is correct in this job's checkout, even though the version job already updated it. Each job checks out code independently.
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
            if command -v sha256sum >/dev/null 2>&1; then
              sha256sum move_maker > move_maker.sha256
            else
              shasum -a 256 move_maker > move_maker.sha256
            fi
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

### 5. Add Release Job

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
            # Get commits since last tag, or complete history if no tags (first release)
            if git describe --tags --abbrev=0 2>/dev/null; then
              LAST_TAG=$(git describe --tags --abbrev=0)
              NOTES=$(git log ${LAST_TAG}..HEAD --pretty=format:"- %s (%h)" --no-merges)
            else
              # First release: read complete history
              NOTES=$(git log --pretty=format:"- %s (%h)" --no-merges)
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
      - [ ] Note: If no previous tag exists (first release), the release notes include the complete git history. Subsequent releases only include commits since the last tag.
- [ ] Add artifact download step:
  ```yaml
        - name: Download all artifacts
          uses: actions/download-artifact@v4
          with:
            path: artifacts
      ```
      - [ ] Note: Artifacts are downloaded to the `artifacts/` directory. The artifact names match the `artifact_name` values from the build matrix (e.g., `move_maker-linux-x86_64`, `move_maker-linux-x86_64.sha256`). The file paths in the release creation step must match these artifact names.
- [ ] Add Cargo.toml version update step (for consistency in release job):
  ```yaml
        - name: Update Cargo.toml with calculated version
          run: |
            sed -i "s/^version = \".*\"/version = \"${{ needs.version.outputs.version }}\"/" Cargo.toml
            echo "Updated Cargo.toml version to ${{ needs.version.outputs.version }}"
      ```
  - [ ] Note: This ensures the version is correct in the release job's checkout before creating the git tag and release.
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
      - [ ] Note: The `files` paths are relative to the workspace root. Since artifacts are downloaded to `artifacts/` directory (from the download-artifact step), the paths must be prefixed with `artifacts/`. The artifact names in the build matrix (`artifact_name`) determine the directory structure when artifacts are downloaded.
- [ ] Verify release job is complete
- [ ] Commit release job to workflow

### 6. Verify Workflow Syntax

- [ ] Validate YAML syntax: Use online YAML validator or GitHub Actions syntax check
- [ ] Review workflow for:
  - [ ] Correct job dependencies
  - [ ] Correct permissions
  - [ ] Correct artifact names
  - [ ] Correct file paths
  - [ ] Correct version calculation logic
- [ ] Fix any syntax errors
- [ ] Commit complete workflow file

### 7. Test Release Workflow (Dry Run)

**Note**: This section tests the actual release workflow. To avoid creating unnecessary releases during testing:

- **Option 1**: Use draft releases - modify the release workflow temporarily to set `draft: true` in the release creation step
- **Option 2**: Test with a separate branch - create a test branch and modify the workflow trigger to use that branch temporarily
- **Option 3**: Delete test releases immediately after verification
- **Option 4**: Use a test repository - test the workflow in a separate repository first

**Recommended**: Start with Option 1 (draft releases) for initial testing, then switch to production releases once verified.

- [ ] Create a test branch from `main`
- [ ] Make a small change (e.g., update README)
- [ ] Commit with Conventional Commits format: `chore: test release workflow`
- [ ] Push branch and create pull request
- [ ] Verify PR label workflow (from Phase 7.2) applies appropriate label
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

### 8. Handle Version Calculation Edge Cases

- [ ] Test version calculation with no previous tags (first release)
- [ ] Test version calculation with major version label
- [ ] Test version calculation with minor version label
- [ ] Test version calculation with no label (patch)
- [ ] Test version calculation with multiple PRs
- [ ] Test version calculation with conflicting labels (should take highest)
- [ ] Verify version is updated in Cargo.toml
- [ ] Verify version is used in release tag

### 9. Optimize Workflow (if needed)

- [ ] Review workflow execution time
- [ ] Consider caching dependencies (if applicable)
- [ ] Consider parallelizing independent jobs
- [ ] Review artifact retention settings
- [ ] Optimize build steps if needed

### 10. Add Binary Signing (Optional)

- [ ] Decide if binary signing is needed
- [ ] If yes:
  - [ ] Set up GPG key or code signing certificate
  - [ ] Add signing step to build job
  - [ ] Upload signed binaries
  - [ ] Document signing process
- [ ] If no, document decision

### 11. Update Documentation

- [ ] Update project README with release information:
  - [ ] How releases work
  - [ ] How to download binaries
  - [ ] How to verify checksums
  - [ ] Versioning strategy
- [ ] Document release process
- [ ] Document version calculation logic
- [ ] Add installation instructions for each platform
- [ ] Update CHANGELOG.md (if exists) or document release notes format

## Verification

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

- [x] Security checks integrated into release workflow (blocking)
- [x] Release workflow created (`.github/workflows/release.yaml`)
- [x] Security checks run before builds (blocking)
- [x] Version is calculated from PR labels
- [x] Binaries are built for all target platforms
- [x] Release is created automatically on push to `main`
- [x] Release includes binaries and checksums
- [x] Release notes are generated automatically
- [x] Git tag is created with version
- [x] Cargo.toml version is updated
- [ ] Workflow tested and working (needs testing)
- [ ] Documentation updated

## Notes

- All releases are triggered automatically on pushes to `main`
- **Direct commits to `main` are prohibited** (enforced by branch protection rules configured in Phase 6)
- All security tools are **blocking** in CI/CD workflows
- Security checks must pass before builds or releases proceed
- Security checks run in both PR and release workflows
- Version is calculated from PR labels applied by PR label workflow
- **First release**: Uses version from `Cargo.toml` when no tags exist, creating the first tag for subsequent releases
- **Version calculation failure**: If version calculation fails (script exits with error), the workflow aborts and no release is created
- Binaries are built with embedded dependency info (cargo-auditable)
- Release binaries are audited after build
- Checksums are generated for all binaries
- **Artifact paths**: Artifacts are downloaded to `artifacts/` directory, and file paths in release creation must match the artifact names from the build matrix

## Troubleshooting

### Workflow Fails on Security Checks
- Verify all security tools are installed correctly
- Check security tool outputs for specific failures
- Fix security issues before retrying

### Version Calculation Fails
- **Workflow behavior**: If version calculation fails (script exits with error), the workflow aborts and no release is created
- Verify PR label workflow is working (see Phase 7.2)
- Check that PRs have appropriate labels
- Verify GitHub CLI has correct permissions
- Check version calculation script logic
- Verify version labels exist in repository (created in Phase 6)
- For first release: Verify `Cargo.toml` has a valid version string (required when no tags exist)

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

- [Main Continuous Delivery Plan](./07_Continuous_Delivery.md) - Overview and architecture
- [Pull Request Workflow Plan](./07_01_Pull_Request_Workflow.md) - PR quality checks
- [PR Label Workflow Plan](./07_02_PR_Label_Workflow.md) - PR label workflow
- [softprops/action-gh-release](https://github.com/softprops/action-gh-release)
- [GitHub Actions: Creating Releases](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#release)
- [CONTINUOUS_DELIVERY.md](../plan/01_Quality/CONTINUOUS_DELIVERY.md) - Detailed CD documentation
- [VERSIONING.md](../plan/01_Quality/VERSIONING.md) - Versioning strategy documentation
