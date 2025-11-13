# Continuous Delivery (CD)

## Overview
Automate the release process so that each push to the `main` branch creates a new GitHub release with compiled binaries for multiple platforms.

**Note**: This document is the source of truth for release workflows. The release workflow file is named `release.yaml` and runs on pushes to `main`. All pushes to `main` trigger a release.

## Release Strategy

**Versioning Strategy**: This project uses **Option E (PR Labels auto-applied from Conventional Commits)** with **Proposal 1 (Git-Based Auto-Versioning via GitHub Actions)**. See [VERSIONING.md](VERSIONING.md) for detailed versioning proposals and selection criteria.

**How it works**:
1. PR labels are automatically applied by `.github/workflows/pr-label.yml` based on Conventional Commits in PR commit messages
2. Version is calculated from PR labels when merging to `main`
3. Version is updated in `Cargo.toml` and used for the release tag
4. Each release creates a git tag for the next version calculation

## Release Automation Tools

### Option 1: softprops/action-gh-release (Recommended)

**Pros**:
- ✅ Well-maintained and widely used
- ✅ Supports multiple file uploads
- ✅ Automatic release notes generation
- ✅ Draft and prerelease support
- ✅ Cross-platform (Linux, Windows, macOS)

**Usage**:
```yaml
- uses: softprops/action-gh-release@v2
  with:
    tag_name: v${{ env.VERSION }}
    name: Release v${{ env.VERSION }}
    body: ${{ env.RELEASE_NOTES }}
    files: |
      target/release/move_maker
    draft: false
    prerelease: false
```

### Option 2: ncipollo/release-action

**Pros**:
- ✅ Good feature set
- ✅ Automatic changelog generation
- ✅ Artifact upload support

**Cons**:
- ⚠️ Less popular than softprops/action-gh-release

### Option 3: GitHub CLI (gh)

**Pros**:
- ✅ Official GitHub tool
- ✅ Maximum flexibility

**Cons**:
- ⚠️ More verbose setup
- ⚠️ Requires more manual scripting

**Recommendation**: Use **softprops/action-gh-release** for simplicity and reliability.

## Multi-Platform Builds

For a CLI tool, build binaries for:
- **Linux**: x86_64, aarch64 (ARM64)
- **macOS**: x86_64, aarch64 (Apple Silicon)
- **Windows**: x86_64 (optional, if needed)

**Tools for Cross-Compilation**:
- **cross**: Simplest option for cross-compilation
- **Native GitHub Actions runners**: Use matrix strategy with different OS runners
- **cargo build --target**: Direct Rust cross-compilation (requires toolchain setup)

**Recommendation**: Use GitHub Actions matrix strategy with native runners for best compatibility.

## Complete Release Workflow

**Workflow File**: `.github/workflows/release.yaml`

```yaml
name: Release

on:
  push:
    branches:
      - main

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
          fetch-depth: 0  # Needed for version calculation

      - name: Setup GitHub CLI
        uses: cli/cli-action@v2
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}

      - name: Calculate version from PR labels (Option E)
        id: version
        run: |
          # Fetch all tags (required for shallow clones)
          git fetch --tags --force

          # Get latest tag matching v* pattern
          LATEST_TAG=$(git describe --tags --match "v*" --abbrev=0 2>/dev/null || echo "")

          if [ -z "$LATEST_TAG" ]; then
            # No tag found, use base version from Cargo.toml
            BASE_VERSION=$(grep '^version = ' Cargo.toml | cut -d '"' -f 2)
            VERSION="$BASE_VERSION"
            echo "No previous tag found, using base version: $VERSION"
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

      - name: Update Cargo.toml version
        run: |
          sed -i "s/^version = \".*\"/version = \"${{ steps.version.outputs.version }}\"/" Cargo.toml
          echo "Updated Cargo.toml version to ${{ steps.version.outputs.version }}"

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

    permissions:
      contents: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Needed for release notes

      - name: Update Cargo.toml with calculated version
        run: |
          sed -i "s/^version = \".*\"/version = \"${{ needs.version.outputs.version }}\"/" Cargo.toml
          echo "Updated Cargo.toml version to ${{ needs.version.outputs.version }}"

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}

      - name: Install cargo-nextest
        uses: taiki-e/install-action@cargo-nextest

      - name: Install cargo-auditable
        run: cargo install cargo-auditable

      - name: Run tests
        run: cargo nextest run

      - name: Build release binary with embedded dependency info
        run: cargo auditable build --release --target ${{ matrix.target }}

      - name: Install cargo-audit for binary auditing
        run: cargo install cargo-audit

      - name: Audit release binary
        run: cargo audit bin target/${{ matrix.target }}/release/move_maker

      - name: Strip binary (Linux/macOS)
        if: matrix.os != 'windows'
        run: strip target/${{ matrix.target }}/release/move_maker

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact_name }}
          path: target/${{ matrix.target }}/release/move_maker
          retention-days: 1

      - name: Create checksum
        shell: bash
        run: |
          cd target/${{ matrix.target }}/release
          shasum -a 256 move_maker > move_maker.sha256
          cat move_maker.sha256

      - name: Upload checksum
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact_name }}.sha256
          path: target/${{ matrix.target }}/release/move_maker.sha256
          retention-days: 1

  release:
    needs: [security, version, build-and-release]
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

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

      - name: Download all artifacts
        uses: actions/download-artifact@v4
        with:
          path: artifacts

      - name: Update Cargo.toml with calculated version
        run: |
          sed -i "s/^version = \".*\"/version = \"${{ needs.version.outputs.version }}\"/" Cargo.toml
          echo "Updated Cargo.toml version to ${{ needs.version.outputs.version }}"

      - name: Commit and push version update
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add Cargo.toml
          git commit -m "chore: bump version to ${{ needs.version.outputs.version }}" || true
          git push origin HEAD:main || true

      - name: Create git tag
        run: |
          git tag -a "${{ needs.version.outputs.tag_name }}" -m "Release ${{ needs.version.outputs.tag_name }}"
          git push origin "${{ needs.version.outputs.tag_name }}"

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

## Version Management

**Selected Approach**: **Option E (PR Labels auto-applied from Conventional Commits)** + **Proposal 1 (Git-Based Auto-Versioning via GitHub Actions)**

See [VERSIONING.md](VERSIONING.md) for detailed versioning strategy and implementation approach.

### How Versioning Works

1. **PR Labeling** (`.github/workflows/pr-label.yml`):
   - Automatically analyzes PR commit messages using Conventional Commits
   - Applies `version: major` label if commits contain `BREAKING CHANGE:` or `!`
   - Applies `version: minor` label if commits contain `feat:`
   - Leaves unlabeled (patch) for all other commits
   - Labels can be manually overridden if needed

2. **Version Calculation** (in `release.yaml`):
   - Finds latest tag matching `v*` pattern
   - Gets all merged PRs since last tag
   - Reads PR labels (source of truth) to determine bump type:
     - `version: major` or `breaking` → MAJOR bump
     - `version: minor` or `feature` → MINOR bump
     - No label → PATCH bump (by commit count)
   - Takes highest bump type found across all PRs
   - Calculates new version and updates `Cargo.toml`
   - Creates git tag with new version

3. **Version Access**:
   - Version is available in `Cargo.toml` after calculation
   - Accessible via `env!("CARGO_PKG_VERSION")` in Rust code
   - Available via `--version` CLI argument

### Required Workflows

**`.github/workflows/pr-label.yml`** (must be created separately):
- Runs on PR open, update, and reopen
- Analyzes commit messages and applies version labels
- See [VERSIONING.md](VERSIONING.md) for complete workflow definition

**`.github/workflows/release.yaml`** (this workflow):
- Runs on pushes to `main`
- Calculates version from PR labels
- Updates `Cargo.toml` and creates release

## Release Notes Generation

**Options**:

1. **Commit-based** (shown in workflow above)
   - Extract commits since last tag
   - Format as bullet list
   - Simple and automatic

2. **CHANGELOG.md-based**
   - Maintain a `CHANGELOG.md` file
   - Extract relevant section for release
   - More control, requires maintenance

3. **GitHub's Automatic Release Notes**
   - Use GitHub API to generate notes
   - Categorizes by PR labels
   - Requires PR-based workflow

**Recommendation**: Start with commit-based notes, migrate to CHANGELOG.md as project grows.

## Security Considerations

1. **Binary Signing** (Optional but recommended)
   - Sign binaries with GPG or code signing certificates
   - Provides authenticity verification
   - More complex setup

2. **Checksums**
   - Generate SHA256 checksums (included in workflow)
   - Users can verify binary integrity
   - Simple and effective

3. **Permissions**
   - Use `GITHUB_TOKEN` (automatically provided)
   - Only grant `contents: write` permission
   - No additional secrets needed for basic releases

4. **Security Scanning** ✅ Integrated
   - **Security job runs before builds**: All security checks must pass before building
   - **cargo-deny**: Checks licenses, vulnerabilities, and banned dependencies (blocking)
   - **cargo-audit**: Scans for known vulnerabilities using RustSec Advisory Database (blocking)
   - **cargo-geiger**: Detects unsafe code usage (blocking)
   - **cargo-auditable**: Embeds dependency information in release binaries (blocking)
   - **Binary auditing**: Release binaries are audited after build to verify embedded dependency info (blocking)
   - All security tools are blocking - releases are blocked if any security check fails
   - See [SECURITY.md](SECURITY.md) for detailed security practices and tooling

## CD Best Practices

1. **Version Strategy**
   - Use semantic versioning
   - Tag every release
   - Keep version in sync with `Cargo.toml`

2. **Release Frequency**
   - Every push to main = new release (current plan)
   - Version strategy determined by [VERSIONING.md](VERSIONING.md) selection

3. **Artifact Management**
   - Upload binaries for all target platforms
   - Include checksums for verification
   - Keep artifacts reasonably sized

4. **Release Notes**
   - Always include release notes
   - Link to issues/PRs when relevant
   - Provide installation instructions

5. **Testing Before Release**
   - Run full test suite before building
   - Consider running on multiple platforms
   - Verify binaries work before uploading

## Alternative: Release on Version Bump Only

If you prefer to release only when version changes:

```yaml
name: Release

on:
  push:
    branches: [main]
    paths:
      - 'Cargo.toml'  # Only trigger on version changes

jobs:
  # ... same as above, but check if version changed
  - name: Check if version changed
    id: version_check
    run: |
      # Compare current version with last tag
      # Only proceed if different
```

## Integration with Pull Request Checks

The release workflow (`release.yaml`) runs independently on pushes to `main`. Pull request checks are handled by the `pull_request.yaml` workflow (see [IMPLEMENTATION.md](IMPLEMENTATION.md)).

**Workflow Organization**:
- **`.github/workflows/pr-label.yml`**: Runs on PR open/update, automatically applies version labels based on Conventional Commits
- **`.github/workflows/pull_request.yaml`**: Runs on pull requests, includes security, test, and coverage checks
- **`.github/workflows/release.yaml`**: Runs on pushes to `main`, includes security, build, version calculation, and release steps

All workflows run all security tools (cargo-deny, cargo-audit, cargo-geiger, cargo-auditable) as blocking checks.

**Version Labeling Flow**:
1. PR is opened/updated → `pr-label.yml` analyzes commits and applies version label
2. PR is merged to `main` → `release.yaml` reads PR labels and calculates version
3. Version is used for release tag and `Cargo.toml` update

## References

- [softprops/action-gh-release](https://github.com/softprops/action-gh-release)
- [ncipollo/release-action](https://github.com/ncipollo/create-release)
- [cargo-release Documentation](https://github.com/crate-ci/cargo-release)
- [GitHub Actions: Creating Releases](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#release)
