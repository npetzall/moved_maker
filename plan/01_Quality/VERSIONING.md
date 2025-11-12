# Versioning Strategy

## Overview
This document outlines versioning strategy proposals for the move_maker project.

**Selected Approach**: 
- **Option E (PR Labels auto-applied from Conventional Commits)** has been selected for version bump signaling. This approach automatically applies version labels to PRs based on Conventional Commits, with labels serving as the source of truth for version calculation.
- **Proposal 1 (Git-Based Auto-Versioning via GitHub Actions)** has been selected as the implementation. It natively supports Option E with the simplest implementation.

## Requirements

- **Automatic Releases**: Every push to the default branch (`main`) triggers a release
- **Semantic Versioning**: Version must follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)
- **Version Bump Signaling**: Must support signaling major or minor version updates (not just patch)
- **GitHub Compatibility**: Compatible with GitHub Releases and workflows
- **Build Integration**: Version must be used in build process and available via `--version` CLI argument
- **Automatic Calculation**: Version should be determinable automatically from git history
- **Linear Git History**: Must work with linear git history (no merge commits, linear commit chain)
- **PR-Based Workflow**: Must work with PR-based workflow (all changes merged via Pull Requests)

## Major/Minor Version Signaling Approaches

To support semantic versioning with major and minor bumps, we need a way to signal version increment type. Here are recommended approaches:

### Option A: Conventional Commits (Recommended)
Analyze commit messages since last tag to determine version bump:
- **Major**: Commits containing `BREAKING CHANGE:` or `!` after type (e.g., `feat!:`, `fix!:`)
- **Minor**: Commits with type `feat:` (new features)
- **Patch**: All other commits (default)

**Pros**: Industry standard, widely adopted, clear semantics
**Cons**: Requires commit message discipline

### Option B: Commit Message Markers
Look for explicit markers in commit messages:
- **Major**: `[major]`, `[MAJOR]`, `#major` in commit message
- **Minor**: `[minor]`, `[MINOR]`, `#minor` in commit message
- **Patch**: Default (no marker)

**Pros**: Simple, explicit, flexible
**Cons**: Less standard, requires manual marking

### Option C: PR Labels (GitHub-specific)
Use GitHub PR labels to signal version bump type:
- **Major**: PR labeled `version: major` or `breaking`
- **Minor**: PR labeled `version: minor` or `feature`
- **Patch**: Default (no label or `version: patch`)

**Pros**: Visual, can be enforced via branch protection
**Cons**: Only works with PRs, requires label management

### Option D: Configuration File
Maintain a `VERSION_CONFIG` file or section in `Cargo.toml`:
```toml
[package.metadata.version]
major = 0
minor = 1
# patch calculated from commits
```

**Pros**: Explicit control, versionable
**Cons**: Manual updates required, defeats automation

### Option E: Hybrid - PR Labels (Auto-applied from Conventional Commits) ✅ **SELECTED**

PR labels are the source of truth, automatically applied by a workflow that analyzes commit messages:
- **Automated Labeling**: A GitHub Actions workflow analyzes PR commit messages using Conventional Commits and automatically applies version labels
- **Labels as Source of Truth**: Version calculation workflow reads PR labels only (no commit analysis needed)
- **Major**: PR automatically labeled `version: major` or `breaking` if commits contain `BREAKING CHANGE:` or `!`
- **Minor**: PR automatically labeled `version: minor` or `feature` if commits contain `feat:`
- **Patch**: Default (no label applied, or `version: patch` label)
- **Manual Override**: Labels can be manually changed if needed (labels are source of truth)

**How it works**:
1. **Label Application Workflow** (runs on PR open/update):
   - Analyzes all commit messages in the PR using Conventional Commits rules
   - Automatically applies appropriate version label (`version: major`, `version: minor`, or leaves unlabeled for patch)
   - Can be manually overridden by adding/removing labels
2. **Version Calculation Workflow** (runs on merge to main):
   - Reads PR labels only (no commit analysis needed)
   - Uses label as the bump type for that PR
   - Takes the highest bump type found across all merged PRs since last tag

**Pros**: 
- ✅ Fully automated - labels applied automatically from commit messages
- ✅ Labels are source of truth (can be manually overridden if needed)
- ✅ Visual and clear - version bump type visible in PR UI
- ✅ Enforceable via branch protection (require labels for major/minor)
- ✅ No fallback logic needed - labels always present (auto-applied)
- ✅ Consistent - all PRs get labeled automatically

**Cons**: 
- ⚠️ Only works with PRs (direct commits to main won't have labels)
- ⚠️ Requires two workflows (label application + version calculation)
- ⚠️ Requires GitHub API/CLI access in workflows

**Implementation Example**:

**Workflow 1: Auto-label PRs based on Conventional Commits** (`.github/workflows/pr-label.yml`):
```yaml
name: Auto-label PR by Conventional Commits

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  label-pr:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup GitHub CLI
        uses: cli/cli-action@v2
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}

      - name: Analyze commits and apply label
        run: |
          PR_NUM=${{ github.event.pull_request.number }}
          
          # Get all commit messages in this PR
          COMMITS=$(gh pr view $PR_NUM --json commits --jq '.commits[].message' | tr '\n' '\n')
          
          # Determine version bump type from commits
          VERSION_LABEL=""
          if echo "$COMMITS" | grep -qE "(BREAKING CHANGE|!:)"; then
            VERSION_LABEL="version: major"
          elif echo "$COMMITS" | grep -qE "^feat:"; then
            VERSION_LABEL="version: minor"
          fi
          
          # Remove existing version labels
          gh pr edit $PR_NUM --remove-label "version: major" "version: minor" "version: patch" 2>/dev/null || true
          
          # Apply new label if determined
          if [ -n "$VERSION_LABEL" ]; then
            gh pr edit $PR_NUM --add-label "$VERSION_LABEL"
            echo "Applied label: $VERSION_LABEL"
          else
            echo "No version label applied (patch bump)"
          fi
```

**Workflow 2: Calculate version from PR labels** (used in release workflow):
```yaml
- name: Calculate version from PR labels
  id: version
  run: |
    # Get merged PRs since last tag
    LATEST_TAG=$(git describe --tags --match "v*" --abbrev=0 2>/dev/null || echo "")
    TAG_DATE=$(git log -1 --format=%ct ${LATEST_TAG:-HEAD~1000})
    
    PRS=$(gh pr list --state merged --base main --json number,labels,mergedAt --limit 100)
    
    MAJOR_BUMP=false
    MINOR_BUMP=false
    
    # Check labels on merged PRs (labels are source of truth)
    for PR_NUM in $(echo "$PRS" | jq -r '.[] | select(.mergedAt != null) | select((.mergedAt | fromdateiso8601) > '$TAG_DATE') | .number'); do
      LABELS=$(gh pr view $PR_NUM --json labels --jq '.labels[].name' | tr '\n' ' ')
      
      if echo "$LABELS" | grep -qE "(version: major|breaking)"; then
        MAJOR_BUMP=true
      elif echo "$LABELS" | grep -qE "(version: minor|feature)"; then
        MINOR_BUMP=true
      fi
    done
    
    # Calculate version based on highest bump type found
    if [ "$MAJOR_BUMP" = true ]; then
      # MAJOR bump logic
    elif [ "$MINOR_BUMP" = true ]; then
      # MINOR bump logic
    else
      # PATCH bump logic
    fi
```

**Selection**: **Option E (Hybrid)** has been **selected** for this project. Labels are automatically applied from Conventional Commits and serve as the source of truth for version bump determination.

---

## Proposal 1: Git-Based Auto-Versioning via GitHub Actions (shipkit-style) ✅ **SELECTED**

**Description**: Automatically calculate version based on latest tag and commit count using GitHub Actions workflow scripts, similar to [shipkit-auto-version](https://github.com/shipkit/shipkit-auto-version). Works best with linear history enforced in GitHub.

**Version Bump Signaling**: Supports **Option A (Conventional Commits)** or **Option E (Hybrid - PR Labels auto-applied from Conventional Commits)**. See "Major/Minor Version Signaling Approaches" section above.

**Implementation**:
- Base version spec in `Cargo.toml`: `version = "0.1.0"` (used as fallback)
- Find latest tag matching pattern (e.g., `v0.1.*` or `v*`)
- Analyze commits/PRs since that tag to determine version bump type
- Calculate version based on highest bump type found:
  - **Option A (Conventional Commits)**: Analyze commit messages
    - If any commit has `BREAKING CHANGE:` → increment MAJOR, reset MINOR and PATCH
    - Else if any commit has `feat:` → increment MINOR, reset PATCH
    - Else → increment PATCH by commit count
  - **Option E (Hybrid)**: Read PR labels only (labels are source of truth, auto-applied by separate workflow)
    - Separate workflow analyzes commit messages and applies labels automatically
    - If PR has `version: major` or `breaking` label → increment MAJOR
    - Else if PR has `version: minor` or `feature` label → increment MINOR
    - Else → increment PATCH by commit count (no label = patch)
- Each release creates a tag, next build uses that tag as base
- Version available via `env!("CARGO_PKG_VERSION")` after updating `Cargo.toml`

**How it works** (Option A - Conventional Commits):
1. Run `git describe --tags --match "v*"` to find latest tag
2. If tag found (e.g., `v0.1.5`), extract version and analyze commits since tag
3. Check commit messages for version bump signals:
   - `BREAKING CHANGE:` or `!` → MAJOR bump (e.g., `0.1.5` → `1.0.0`)
   - `feat:` → MINOR bump (e.g., `0.1.5` → `0.2.0`)
   - Otherwise → PATCH bump by commit count (e.g., `0.1.5` + 3 commits → `0.1.8`)
4. If no tag found, use base version from `Cargo.toml`
5. Update `Cargo.toml` with calculated version
6. When releasing, tag with calculated version
7. Version accessible via `env!("CARGO_PKG_VERSION")` in code

**How it works** (Option E - Hybrid):
1. **Separate workflow** (runs on PR open/update) analyzes commit messages and auto-applies version labels
2. **Version calculation workflow** (runs on merge to main):
   - Run `git describe --tags --match "v*"` to find latest tag
   - Get merged PRs since last tag using GitHub CLI
   - For each PR, read labels only (labels are source of truth, already auto-applied):
     - `version: major` or `breaking` → MAJOR bump
     - `version: minor` or `feature` → MINOR bump
     - No label → PATCH bump
   - Take highest bump type found across all PRs
3. Update `Cargo.toml` with calculated version
4. When releasing, tag with calculated version
5. Version accessible via `env!("CARGO_PKG_VERSION")` in code

**Pros**:
- ✅ Fully automatic - no manual version bumps needed
- ✅ Semantic versioning compatible with major/minor/patch support
- ✅ Works excellently with linear history (commit count is accurate)
- ✅ Each release is tagged, creating clear history
- ✅ Similar to shipkit-auto-version workflow (proven approach)
- ✅ Version reflects actual development activity
- ✅ No version conflicts (always increments)
- ✅ No build-time dependencies required
- ✅ Easy to debug and modify
- ✅ Works entirely in CI/CD environment
- ✅ Supports Conventional Commits for automatic version bump detection
- ✅ Version available in build and via `--version` CLI argument

**Cons**:
- ⚠️ Requires git history (works fine in CI/CD)
- ⚠️ Requires full git history fetch (`fetch-depth: 0`)
- ⚠️ Need to ensure tags follow pattern
- ⚠️ Requires linear history for accurate commit counting
- ⚠️ Shell script complexity in workflow
- ⚠️ Requires commit message discipline for Conventional Commits

**Workflow Implementation** (Option A - Conventional Commits):
```yaml
- name: Checkout code
  uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Fetch full history for accurate commit counting

- name: Calculate version from git (Conventional Commits)
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
      
      # Analyze commits since tag for version bump type
      COMMITS=$(git log ${LATEST_TAG}..HEAD --pretty=format:"%s")
      
      # Check for breaking changes (MAJOR bump)
      if echo "$COMMITS" | grep -qE "(BREAKING CHANGE|!:)"; then
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        BUMP_TYPE="MAJOR"
      # Check for features (MINOR bump)
      elif echo "$COMMITS" | grep -qE "^feat:"; then
        MINOR=$((MINOR + 1))
        PATCH=0
        BUMP_TYPE="MINOR"
      # Otherwise, PATCH bump by commit count
      else
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

- name: Update Cargo.toml version (required for build-time access)
  run: |
    sed -i "s/^version = \".*\"/version = \"${{ steps.version.outputs.version }}\"/" Cargo.toml
    echo "Updated Cargo.toml version to ${{ steps.version.outputs.version }}"
    
- name: Build and release
  # ... build steps using ${{ steps.version.outputs.version }} ...
  
- name: Create git tag
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git tag -a "v${{ steps.version.outputs.version }}" -m "Release v${{ steps.version.outputs.version }}"
    git push origin "v${{ steps.version.outputs.version }}"
```

**Workflow Implementation** (Option E - Hybrid: PR Labels auto-applied from Conventional Commits):

**Note**: This requires two workflows:
1. **Auto-label workflow** (see Option E implementation example above) - runs on PR open/update
2. **Version calculation workflow** (below) - runs on merge to main

```yaml
- name: Checkout code
  uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Fetch full history for accurate commit counting

- name: Setup GitHub CLI
  uses: cli/cli-action@v2
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}

- name: Calculate version from PR labels (labels are source of truth)
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

- name: Update Cargo.toml version (required for build-time access)
  run: |
    sed -i "s/^version = \".*\"/version = \"${{ steps.version.outputs.version }}\"/" Cargo.toml
    echo "Updated Cargo.toml version to ${{ steps.version.outputs.version }}"
    
- name: Build and release
  # ... build steps using ${{ steps.version.outputs.version }} ...
  
- name: Create git tag
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git tag -a "v${{ steps.version.outputs.version }}" -m "Release v${{ steps.version.outputs.version }}"
    git push origin "v${{ steps.version.outputs.version }}"
```

**With Linear History**:
- Linear history ensures accurate commit counting
- Commit messages determine version bump type (MAJOR/MINOR/PATCH)
- Tags mark release points
- Next build calculates version from last tag + commit analysis

**Example Flow**:
1. Initial: `v0.1.0` tagged
2. 3 patch commits → version `0.1.3` → tag `v0.1.3`
3. 1 feat commit → version `0.2.0` → tag `v0.2.0` (MINOR bump)
4. 2 patch commits → version `0.2.2` → tag `v0.2.2`
5. 1 BREAKING CHANGE commit → version `1.0.0` → tag `v1.0.0` (MAJOR bump)

**Version in Code**:
```rust
// After Cargo.toml is updated, version is available via:
const VERSION: &str = env!("CARGO_PKG_VERSION");

// In CLI argument parsing (using clap):
#[derive(Parser)]
#[command(version = env!("CARGO_PKG_VERSION"))]
struct Cli {
    // ...
}
```

**Recommendation**: Best option for simplicity and reliability. Works well with linear history, doesn't require build-time dependencies, and is easy to debug. This approach is most similar to shipkit-auto-version's workflow.

---

## Proposal 2: Git-Based Auto-Versioning via `git2version` Crate

**Description**: Automatically calculate version based on latest tag and commit analysis using the `git2version` Rust crate in a build script. Similar to [shipkit-auto-version](https://github.com/shipkit/shipkit-auto-version). Works best with linear history enforced in GitHub.

**Implementation**:
- Base version spec in `Cargo.toml`: `version = "0.1.0"` (used as fallback)
- Use `git2version` crate in `build.rs` to extract git information
- Analyze commit messages to determine version bump type (MAJOR/MINOR/PATCH)
- Calculate version based on highest bump type found
- Set version at build time via `cargo:rustc-env=CARGO_PKG_VERSION`

**How it works**:
1. Build script runs `git2version::get_version_info()` to get git metadata
2. Extracts latest tag version and commits since tag
3. Analyzes commit messages for Conventional Commits patterns
4. Calculates new version based on bump type:
   - BREAKING CHANGE → MAJOR bump
   - feat: → MINOR bump
   - Otherwise → PATCH bump by commit count
5. Sets `CARGO_PKG_VERSION` environment variable for use in code

**Pros**:
- ✅ Fully automatic - no manual version bumps needed
- ✅ Semantic versioning compatible with major/minor/patch support
- ✅ Works excellently with linear history (commit count is accurate)
- ✅ Version available at compile time in Rust code
- ✅ No CI/CD workflow changes needed
- ✅ Version embedded in binary
- ✅ Similar to shipkit-auto-version workflow (proven approach)
- ✅ Version reflects actual development activity
- ✅ Supports Conventional Commits for automatic version bump detection
- ✅ Version available via `--version` CLI argument via `env!("CARGO_PKG_VERSION")`

**Cons**:
- ⚠️ Requires git history (works fine in CI/CD)
- ⚠️ Requires build-time dependency (`git2version`)
- ⚠️ Need to ensure tags follow pattern
- ⚠️ Requires linear history for accurate commit counting
- ⚠️ Build script complexity (need to implement commit message analysis)
- ⚠️ Version only available at build time, not in workflow
- ⚠️ Requires commit message discipline for Conventional Commits

**Implementation**:

```toml
# Cargo.toml
[package]
version = "0.1.0"  # Fallback version

[build-dependencies]
git2version = "0.1"
```

```rust
// build.rs
use std::process::Command;

fn main() {
    if let Some(git_info) = git2version::get_version_info() {
        let mut major = git_info.major;
        let mut minor = git_info.minor;
        let mut patch = git_info.patch;
        
        // Analyze commits since tag for version bump type
        let commits = get_commit_messages_since_tag(&git_info.tag);
        
        // Check for breaking changes (MAJOR bump)
        if commits.iter().any(|msg| msg.contains("BREAKING CHANGE") || msg.matches("!:").count() > 0) {
            major += 1;
            minor = 0;
            patch = 0;
        }
        // Check for features (MINOR bump)
        else if commits.iter().any(|msg| msg.starts_with("feat:")) {
            minor += 1;
            patch = 0;
        }
        // Otherwise, PATCH bump by commit count
        else {
            patch += git_info.commits_since_tag;
        }
        
        let version = format!("{}.{}.{}", major, minor, patch);
        println!("cargo:rustc-env=CARGO_PKG_VERSION={}", version);
    }
}

fn get_commit_messages_since_tag(tag: &str) -> Vec<String> {
    // Implementation to get commit messages since tag
    // This would use git commands or git2 crate
    vec![] // Placeholder
}
```

**Usage in code**:
```rust
const VERSION: &str = env!("CARGO_PKG_VERSION");

// In CLI argument parsing (using clap):
#[derive(Parser)]
#[command(version = env!("CARGO_PKG_VERSION"))]
struct Cli {
    // ...
}
```

**With Linear History**:
- Linear history ensures accurate commit counting
- Commit messages determine version bump type (MAJOR/MINOR/PATCH)
- Tags mark release points
- Next build calculates version from last tag + commit analysis

**Example Flow**:
1. Initial: `v0.1.0` tagged
2. 3 patch commits → version `0.1.3` → tag `v0.1.3`
3. 1 feat commit → version `0.2.0` → tag `v0.2.0` (MINOR bump)
4. 2 patch commits → version `0.2.2` → tag `v0.2.2`
5. 1 BREAKING CHANGE commit → version `1.0.0` → tag `v1.0.0` (MAJOR bump)

**Recommendation**: Good option if you need version information available at compile time in your Rust code. Requires adding a build dependency and implementing commit message analysis logic. More complex than Proposal 1 but provides structured git information.

---

## Proposal 3: Git-Based Auto-Versioning via `vergen` Crate

**Description**: Automatically calculate version based on latest tag and commit analysis using the `vergen` Rust crate in a build script. Similar to [shipkit-auto-version](https://github.com/shipkit/shipkit-auto-version). Works best with linear history enforced in GitHub.

**Implementation**:
- Base version spec in `Cargo.toml`: `version = "0.1.0"` (used as fallback)
- Use `vergen` crate in `build.rs` to generate git-based version information
- Expose version information via environment variables at compile time
- Analyze commit messages to determine version bump type
- Calculate version from git describe output and commit analysis

**How it works**:
1. Build script runs `vergen` to generate git metadata
2. `vergen` uses `git describe` to get latest tag and commit count
3. Exposes version information via environment variables
4. Can be accessed in code via `env!()` macro or used in workflows

**Pros**:
- ✅ Fully automatic - no manual version bumps needed
- ✅ Semantic versioning compatible with major/minor/patch support
- ✅ Works excellently with linear history (commit count is accurate)
- ✅ Rich git information available (commit hash, date, etc.)
- ✅ Well-maintained crate with good documentation
- ✅ Version available at compile time in Rust code
- ✅ Similar to shipkit-auto-version workflow (proven approach)
- ✅ Version reflects actual development activity
- ✅ Supports Conventional Commits for automatic version bump detection
- ✅ Version available via `--version` CLI argument

**Cons**:
- ⚠️ Requires git history (works fine in CI/CD)
- ⚠️ Requires build-time dependency (`vergen`)
- ⚠️ Need to ensure tags follow pattern
- ⚠️ Requires linear history for accurate commit counting
- ⚠️ More complex setup than simple shell script
- ⚠️ Version calculation logic requires custom implementation
- ⚠️ Requires commit message discipline for Conventional Commits

**Implementation**:

```toml
# Cargo.toml
[build-dependencies]
vergen = { version = "8", features = ["git"] }
```

```rust
// build.rs
use vergen::EmitBuilder;

fn main() {
    EmitBuilder::builder()
        .git_commit_count()
        .git_describe(true, true, None)
        .emit()
        .unwrap();
}
```

**Usage in code**:
```rust
// Access git information via environment variables
const GIT_COMMIT_COUNT: &str = env!("VERGEN_GIT_COMMIT_COUNT");
const GIT_DESCRIBE: &str = env!("VERGEN_GIT_DESCRIBE");
```

**Note**: `vergen` provides git metadata but doesn't automatically calculate the version. You need to:
1. Parse `GIT_DESCRIBE` output (e.g., `v0.1.5-3-gabc123`) to extract base version and commit count
2. Analyze commit messages since tag to determine bump type (MAJOR/MINOR/PATCH)
3. Calculate final version based on bump type
4. Set `CARGO_PKG_VERSION` environment variable

**Example Implementation**:
```rust
// build.rs - simplified example
use vergen::EmitBuilder;
use std::process::Command;

fn main() {
    EmitBuilder::builder()
        .git_commit_count()
        .git_describe(true, true, None)
        .emit()
        .unwrap();
    
    // Parse GIT_DESCRIBE and analyze commits for version calculation
    // Implementation would analyze commit messages and calculate version
    // Then set: println!("cargo:rustc-env=CARGO_PKG_VERSION={}", version);
}
```

**With Linear History**:
- Linear history ensures accurate commit counting
- Commit messages determine version bump type (MAJOR/MINOR/PATCH)
- Tags mark release points
- Next build calculates version from last tag + commit analysis

**Example Flow**:
1. Initial: `v0.1.0` tagged
2. 3 patch commits → version `0.1.3` → tag `v0.1.3`
3. 1 feat commit → version `0.2.0` → tag `v0.2.0` (MINOR bump)
4. 2 patch commits → version `0.2.2` → tag `v0.2.2`
5. 1 BREAKING CHANGE commit → version `1.0.0` → tag `v1.0.0` (MAJOR bump)

**Recommendation**: Good option if you need rich git metadata (commit hash, date, etc.) in addition to version information. Requires implementing custom version calculation logic that parses git describe output and analyzes commit messages. Most complex option but provides maximum flexibility.

---

## Requirements Compliance Evaluation

| Requirement | Proposal 1 (GitHub Actions) | Proposal 2 (git2version) | Proposal 3 (vergen) |
|-------------|----------------------------|------------------------|---------------------|
| **Automatic Releases** | ✅ Yes - Triggers on push to main | ✅ Yes - Works with any build | ✅ Yes - Works with any build |
| **Semantic Versioning** | ✅ Yes - Full MAJOR.MINOR.PATCH support | ✅ Yes - Full MAJOR.MINOR.PATCH support | ✅ Yes - Full MAJOR.MINOR.PATCH support |
| **Version Bump Signaling** | ✅ Yes - Conventional Commits analysis | ✅ Yes - Requires custom implementation | ✅ Yes - Requires custom implementation |
| **GitHub Compatibility** | ✅ Yes - Native GitHub Actions workflow | ✅ Yes - Works in any CI/CD | ✅ Yes - Works in any CI/CD |
| **Build Integration** | ✅ Yes - Updates Cargo.toml, available via env!() | ✅ Yes - Sets CARGO_PKG_VERSION at build time | ✅ Yes - Can set CARGO_PKG_VERSION |
| **Automatic Calculation** | ✅ Yes - Fully automatic from git history | ✅ Yes - Fully automatic from git history | ✅ Yes - Fully automatic from git history |
| **Linear Git History** | ✅ Yes - Designed for linear history | ✅ Yes - Works with linear history | ✅ Yes - Works with linear history |
| **PR-Based Workflow** | ✅ Yes - Supports Option E (PR labels) or Option A (commits) | ✅ Yes - Works with any workflow | ✅ Yes - Works with any workflow |

## Comparison Table (with Option E Selected)

| Proposal | Requirements Met | Option E Support | Complexity | Implementation | Recommendation |
|----------|------------------|------------------|------------|----------------|----------------|
| **1. GitHub Actions** ✅ **SELECTED** | ✅ 8/8 | ✅ Native support | Medium | Two workflows (label + version) | ✅ **SELECTED** - Only practical choice |
| **2. git2version** | ⚠️ 8/8* | ❌ Complex custom work | Very High | Build script + GitHub API integration | ❌ Not recommended |
| **3. vergen** | ⚠️ 8/8* | ❌ Very complex custom work | Very High | Build script + GitHub API integration | ❌ Not recommended |

\* *Would meet requirements but Option E support adds significant complexity*

---

## Selection Criteria

Consider the following when selecting a versioning strategy:

1. **Release Frequency**: How often do you release?
2. **Version Meaning**: Do you need to communicate breaking changes?
3. **Automation**: Do you want fully automatic versioning?
4. **Standards**: Do you need to follow semantic versioning?
5. **Tooling**: Will this be used as a dependency?

---

## Recommendation

**For move_maker**: **Proposal 1 (Git-Based Auto-Versioning via GitHub Actions)** has been **selected** along with **Option E (PR Labels auto-applied from Conventional Commits)**. This combination provides native Option E support with the simplest implementation.

### ✅ Proposal 1: GitHub Actions ✅ **SELECTED** (with Option E)

**Requirements Compliance**: ✅ Meets all 8 requirements

**Strengths** (with Option E selected):
- ✅ **Automatic Releases**: Native GitHub Actions integration, triggers automatically on push to main
- ✅ **Semantic Versioning**: Full MAJOR.MINOR.PATCH support via Option E (PR labels)
- ✅ **Version Bump Signaling**: Option E provides automated label application from Conventional Commits
- ✅ **GitHub Compatibility**: Designed specifically for GitHub workflows, perfect for Option E
- ✅ **Build Integration**: Updates Cargo.toml, version available via `env!("CARGO_PKG_VERSION")` and `--version`
- ✅ **Automatic Calculation**: Fully automatic from PR labels, no manual intervention
- ✅ **Linear Git History**: Works perfectly with rebase-and-merge (linear history)
- ✅ **PR-Based Workflow**: Native support for Option E - labels auto-applied, version calculated from labels
- ✅ **Visual Control**: Version bump type visible in PR UI via labels
- ✅ **Works with Rebase Merge**: PR labels persist after rebase-and-merge, fully compatible

**Implementation Benefits**:
- No build-time dependencies required
- Easy to debug and modify (shell script in workflow)
- Version calculation happens before build, available throughout workflow
- Similar to proven shipkit-auto-version approach
- Each release automatically creates git tag

**Limitations** (with Option E):
- Requires two workflows (label application + version calculation)
- Requires commit message discipline (Conventional Commits for auto-labeling)
- Requires GitHub API/CLI access in workflows
- Shell script complexity in workflows
- Requires full git history fetch (`fetch-depth: 0`)

---

### ⚠️ Proposal 2: git2version Crate (Not Recommended with Option E)

**Requirements Compliance**: ⚠️ Partially meets requirements (Option E support would require significant custom work)

**Evaluation with Option E Selected**:
- ❌ **Option E Support**: Would require implementing PR label reading logic in build script (complex)
- ❌ **GitHub API Access**: Build scripts don't have easy access to GitHub API for reading PR labels
- ❌ **Workflow Integration**: Would need separate workflow to read PR labels and pass to build script
- ⚠️ **Complexity**: Much more complex than Proposal 1 for Option E support
- ✅ **Version in Code**: Version available at compile time (only benefit)

**Limitations**:
- ⚠️ Option E support requires custom GitHub API integration in build script
- ⚠️ Build-time dependency adds complexity
- ⚠️ Version only available at build time, not in workflow steps
- ⚠️ Would need separate workflow to fetch PR labels and pass to build
- ⚠️ More complex implementation than Proposal 1 for Option E

**When to Use**: Only if you absolutely need version at compile time AND are willing to implement complex Option E support. Not recommended with Option E selected.

---

### ⚠️ Proposal 3: vergen Crate (Not Recommended with Option E)

**Requirements Compliance**: ⚠️ Partially meets requirements (Option E support would require extensive custom work)

**Evaluation with Option E Selected**:
- ❌ **Option E Support**: Would require implementing PR label reading via GitHub API in build script (very complex)
- ❌ **GitHub API Access**: Build scripts don't have easy access to GitHub API for reading PR labels
- ❌ **Workflow Integration**: Would need separate workflow to read PR labels and pass to build script
- ⚠️ **Complexity**: Most complex option, especially for Option E support
- ✅ **Rich Metadata**: Rich git metadata available (only benefit if needed)

**Limitations**:
- ⚠️ Option E support requires extensive custom GitHub API integration
- ⚠️ Most complex option overall
- ⚠️ Build-time dependency
- ⚠️ Version calculation logic must be implemented from scratch
- ⚠️ Would need separate workflow to fetch PR labels and pass to build
- ⚠️ Not practical for Option E implementation

**When to Use**: Only if you need rich git metadata beyond version AND are willing to implement very complex Option E support. Not recommended with Option E selected.

---

## Final Recommendation (with Option E Selected)

**Choose Proposal 1 (GitHub Actions)** because:
1. ✅ **Native Option E Support**: Built-in support for PR labels via GitHub API
2. ✅ **Meets all requirements**: All 8 requirements met with Option E
3. ✅ **Simplest implementation**: Two straightforward workflows (label + version calculation)
4. ✅ **Native GitHub integration**: Perfect for GitHub-hosted projects with PR-based workflows
5. ✅ **No build-time dependencies**: Everything happens in workflows
6. ✅ **Easy to debug and maintain**: Shell scripts in workflows are easy to modify
7. ✅ **Version available throughout workflow**: Available in all workflow steps and in build
8. ✅ **Works with rebase-and-merge**: PR labels persist after rebase merge
9. ✅ **Visual control**: Version bump type visible in PR UI via labels
10. ✅ **Proven approach**: Similar to shipkit-auto-version

**Proposal 2 and 3 are NOT recommended** with Option E selected because:
- ❌ Would require complex GitHub API integration in build scripts
- ❌ Build scripts don't have easy access to PR labels
- ❌ Would need separate workflows to fetch and pass PR labels
- ❌ Much more complex than Proposal 1 for Option E support
- ❌ No clear advantage over Proposal 1 for Option E

**Conclusion**: With Option E and Proposal 1 both **selected**, this combination provides the optimal solution for automatic versioning with PR-based workflows.

---

## Next Steps

1. ✅ Review proposals - **COMPLETED**
2. ✅ Select versioning strategy - **COMPLETED** (Option E + Proposal 1 selected)
3. Update [CONTINUOUS_DELIVERY.md](CONTINUOUS_DELIVERY.md) with selected approach
4. Implement version extraction in release workflow (Option E + Proposal 1)
5. Document version bump process
6. Create auto-label workflow for PRs (Option E)
7. Create version calculation workflow (Proposal 1 with Option E)

