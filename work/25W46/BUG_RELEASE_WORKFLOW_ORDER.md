# Implementation Plan: BUG_RELEASE_WORKFLOW_ORDER

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_RELEASE_WORKFLOW_ORDER.md`.

## Context

Related bug report: `plan/25W46/BUG_RELEASE_WORKFLOW_ORDER.md`

## Fix Required

Restructure the workflow so that:

1. `version` job calculates version and commits `Cargo.toml` update
2. `version` job creates and pushes the tag
3. `build-and-release` job checks out the tagged commit and builds from it
4. `release` job creates the GitHub release with artifacts

Alternatively, use a single job that:
1. Calculates version
2. Updates and commits `Cargo.toml`
3. Creates and pushes tag
4. Builds artifacts from the tagged commit
5. Creates GitHub release

## Investigation

### Continuous Delivery Model

Before evaluating approaches, it's important to establish the continuous delivery model this project follows:

**Core Principle: Version Every Push, Quality Gates Determine Release**

1. **Every push to `main` gets a version** - Each push event (which may contain multiple commits from a merged PR) receives a unique version number calculated from PR labels
2. **Versioning happens immediately** - The version is calculated, `Cargo.toml` is updated, committed, and tagged as soon as the push is received (after security checks)
3. **Quality gates determine releases** - Security checks, builds, and tests determine whether that versioned push becomes a published release
4. **Complete traceability** - Every push has a version tag, even if it never becomes a release

**Rationale:**
- **Complete Traceability**: Every push represents a potential release candidate; versioning all pushes maintains a complete audit trail
- **Separation of Concerns**: Versioning (traceability) is distinct from releasing (quality validation)
- **Alignment with CD Principles**: "Version Control Everything" means every change gets a version; "Build Quality In" means quality gates determine promotion to release
- **Practical Benefits**: Failed attempts are still versioned, making debugging and rollback easier; any versioned push can be rebuilt without re-versioning

This model means that **versioning and tagging should happen early in the workflow** (after security checks), and **quality gates determine whether a release is created**, not whether versioning occurs.

### Approach 1: Single Workflow with Sequential Jobs and Multiple Checkouts

**Structure:**
- Keep a single workflow triggered on push to `main`
- `security` job: Run security checks (blocking gate)
- `version` job: Calculate version, update `Cargo.toml`, commit to `main`, and push tag
- `build-and-release` job: Checkout the newly created tag, then build artifacts
- `release` job: Create GitHub release with artifacts (only if builds succeed)

**Implementation:**
```yaml
security:
  # Run security checks

version:
  needs: security
  # Calculate version
  # Update Cargo.toml
  # Commit and push to main
  # Create and push tag (every push gets versioned)

build-and-release:
  needs: version
  steps:
    - uses: actions/checkout@v4
      with:
        ref: ${{ needs.version.outputs.tag_name }}  # Checkout the tag
    # Build from tagged commit

release:
  needs: [version, build-and-release]
  # Create GitHub Release (only if all checks passed)
```

**Pros:**
- Simple workflow structure (single workflow file)
- All release logic in one place
- Easy to understand the flow
- Tag is available immediately for checkout
- Aligns with CD model: every push gets versioned, quality gates determine release

**Cons:**
- Requires `build-and-release` job to wait for tag push
- Potential race condition if tag push hasn't propagated
- All jobs must wait for version calculation

**Considerations:**
- May need a small delay or retry mechanism when checking out the tag
- Tag must be pushed before `build-and-release` can checkout
- Version is created even if security checks fail (for traceability), but build won't proceed

---

### Approach 2: Two Separate Workflows (Version on Push, Build on Tag)

**Structure:**
- **Workflow 1** (`release-version.yaml`): Triggered on push to `main`
  - `version` job: Calculate version, update `Cargo.toml`, commit to `main`, create and push tag
  - Tag push triggers Workflow 2
- **Workflow 2** (`release-build.yaml`): Triggered on tag push (`v*`)
  - `security` job: Run security checks (quality gate)
  - `build-and-release` job: Checkout the tag, build artifacts from tagged commit (matrix strategy)
  - `release` job: Create GitHub release with artifacts

**Implementation:**
```yaml
# release-version.yaml
on:
  push:
    branches: [main]
jobs:
  version:
    # Calculate, commit, tag (every push gets versioned)

# release-build.yaml
on:
  push:
    tags:
      - 'v*'
jobs:
  security:
    # Run security checks
  build-and-release:
    needs: security
    # Checkout tag, build, test
  release:
    needs: build-and-release
    # Create GitHub Release (only if builds succeed)
```

**Pros:**
- Clear separation of concerns: versioning vs. building
- Build workflow automatically triggered by tag creation
- No race conditions (tag exists before build starts)
- Build workflow can be re-run by re-pushing the tag
- Follows GitHub Actions best practices (workflow per concern)
- Perfect alignment with CD model: version every push, quality gates determine release
- Security checks run before builds (quality gate in build workflow)
- If security fails, version exists but build won't proceed
- If build fails, version exists but no release is created

**Cons:**
- Two workflow files to maintain
- Requires coordination between workflows
- More complex to understand the full release process
- Tag push must succeed for build to trigger

**Considerations:**
- Need to ensure tag format matches trigger pattern
- Build workflow won't run if tag push fails
- Can add manual workflow_dispatch trigger for rebuilds
- Security checks are quality gates in the build workflow, not blocking versioning

---

### Approach 3: Single Workflow with Single Job (Monolithic)

**Structure:**
- One job that does everything sequentially:
  1. Run security checks
  2. Calculate version
  3. Update and commit `Cargo.toml`
  4. Push commit
  5. Create and push tag
  6. Checkout the tag
  7. Build artifacts
  8. Create GitHub release

**Pros:**
- Simplest structure (one job)
- No coordination needed between jobs
- Guaranteed sequential execution
- No race conditions
- Version is created for every push (aligns with CD model)

**Cons:**
- Very long-running job (builds all platforms sequentially)
- No parallelization of builds
- Harder to debug (all steps in one job)
- Security checks must run in same job
- If build fails, version is already committed (but this is acceptable per CD model)

**Considerations:**
- Cannot parallelize builds (matrix strategy requires multiple jobs, not steps within a job)
- Security checks should probably remain separate
- Not ideal for multiple platform builds (would require sequential builds for each platform)
- Aligns with CD model but sacrifices parallelization

---

### Approach 4: Single Workflow with Workflow Run Completion Trigger (INVALID)

**Structure:**
- **Workflow 1** (`release-version.yaml`): Triggered on push to `main`
  - Calculate, commit, tag (every push gets versioned)
- **Workflow 2** (`release-build.yaml`): Triggered when Workflow 1 completes successfully
  - Checkout the tag created by Workflow 1
  - Build and release

**Why This Approach is Invalid:**

The `workflow_run` trigger only fires when the triggering workflow completes **successfully**. This conflicts with the continuous delivery model requirement that **every push gets a version**, even if quality gates fail.

**Problems:**
1. **Incompatible with CD Model**: If security checks fail in Workflow 1, the workflow fails and Workflow 2 never triggers. This means:
   - Version may not be created if the workflow fails before tagging
   - Even if version is created, the build workflow won't trigger on failure
   - Violates "version every push" principle

2. **No Tag-Based Trigger**: Unlike Approach 2, this doesn't use tag push as a trigger, which means:
   - Cannot rebuild by re-pushing a tag
   - Less flexible for manual rebuilds
   - More complex dependency management

3. **Workflow Completion Dependency**: The build workflow depends on workflow completion status rather than the actual tag existence, creating unnecessary coupling.

**Valid Alternative:**
Use Approach 2 (Two Separate Workflows with tag-based trigger) instead, which properly implements the CD model and allows versioning even when some checks fail.

---

## Recommendation

**Recommended: Approach 2 (Two Separate Workflows - Version on Push, Build on Tag)**

This approach best implements the continuous delivery model where **every push gets a version, and quality gates determine releases**.

**Why This Approach:**

1. **Perfect CD Alignment**:
   - Every push to `main` triggers version calculation and tagging (complete traceability)
   - Quality gates (security and tests in build workflow) determine if a release is created
   - Version exists even if quality gates fail (for debugging and rollback)

2. **Correctness**:
   - Tag is created on the commit that contains the version update in `Cargo.toml`
   - Build workflow checks out the tagged commit, ensuring binaries are built from the correct versioned state
   - No version mismatch between tag, commit, and binaries

3. **Reliability**:
   - No race conditions (tag exists before build starts)
   - Build workflow can be re-triggered independently by re-pushing the tag
   - Clear failure points: version always created; security failure → build doesn't proceed; build failure → version exists but no release

4. **Flexibility**:
   - Can rebuild any versioned push without re-versioning
   - Build workflow can be manually triggered for specific tags
   - Clear separation allows independent maintenance of versioning vs. building logic

5. **Best Practices**:
   - Follows GitHub Actions pattern of workflow per concern
   - Tag-based triggers are standard and well-supported
   - Each workflow has a single, clear purpose

**Implementation Steps:**

1. **Create `release-version.yaml`:**
   - Trigger on push to `main`
   - `version` job:
     - Calculate version from PR labels
     - Update `Cargo.toml` with version
     - Commit and push version update to `main`
     - Create and push git tag (e.g., `v1.2.3`)
     - Tag push triggers the build workflow
   - No security job (versioning happens immediately)

2. **Create `release-build.yaml`:**
   - Trigger on tag push (`v*`)
   - `security` job: Run security checks (quality gate)
   - `build-and-release` job:
     - Depends on `security` job
     - Checkout the tag (ensures building from versioned commit)
     - Run tests (quality gate)
     - Build release artifacts using matrix strategy
     - Upload artifacts
   - `release` job:
     - Depends on `build-and-release` job
     - Download artifacts
     - Create GitHub Release with artifacts
     - Only succeeds if all previous steps passed

**Workflow Flow:**
```
Push to main
  ↓
Calculate version → Update Cargo.toml → Commit → Tag → Push tag
  ↓
Tag push triggers build workflow
  ↓
Security checks (quality gate)
  ↓
Checkout tag → Tests → Build artifacts (matrix)
  ↓
Create GitHub Release (only if all passed)
```

**Alternative Recommendation: Approach 1 (Single Workflow with Multiple Checkouts)**

If maintaining a single workflow file is preferred, Approach 1 can also implement the CD model:

- `security` job: Run security checks
- `version` job: Calculate version, update `Cargo.toml`, commit to `main`, create and push tag
- `build-and-release` job: Checkout the tag using `ref: ${{ needs.version.outputs.tag_name }}`, then build
- `release` job: Create GitHub Release

**Trade-offs:**
- ✅ Single workflow file (simpler file structure)
- ✅ All logic in one place
- ⚠️ Requires careful handling of tag checkout (may need retry/delay)
- ⚠️ Less flexible for rebuilding (must re-run entire workflow)

Both approaches correctly implement the "version every push, quality gates determine release" model and solve the original bug by ensuring builds happen from the tagged commit that contains the version update.

## Detailed Implementation Plan

### Prerequisites

**GitHub App Configuration:**

Before implementing this fix, a GitHub App must be configured to allow the workflow to push commits and tags to the repository:

1. **Create a GitHub App:**
   - Create a new GitHub App in organization or user settings (Settings → Developer settings → GitHub Apps → New GitHub App)
   - Configure the app with the following permissions:
     - Repository permissions:
       - Contents: Read and write
       - Metadata: Read-only (automatically granted)
   - Set the app to be installed only on this repository (or organization if needed)
   - Generate a private key for the app
   - Note the App ID

2. **Install the GitHub App:**
   - Install the GitHub App on the repository (or organization)
   - Grant the app access to the repository

3. **Store GitHub App Credentials:**
   - Store the App ID as a GitHub variable named `APP_ID`
   - Store the private key (in PEM format) as a GitHub secret named `APP_PRIVATE_KEY`

4. **Branch Protection Rules:**
   - The repository may have branch protection rules on `main` that prevent direct pushes
   - The GitHub App will be exempt from these rules (configured in branch protection settings)
   - This allows the workflow to push version updates and tags to `main`

### Phase 1: Implementation Steps

#### Step 1: Configure GitHub App and Secrets

**Prerequisites:**
- [x] Create GitHub App with Contents read/write permissions
- [x] Install GitHub App on the repository (or organization)
- [x] Generate and download private key for the GitHub App
- [x] Store App ID as GitHub variable `APP_ID`
- [x] Store private key (PEM format) as GitHub secret `APP_PRIVATE_KEY`
- [x] Configure branch protection rules to exempt GitHub App (if rules exist)

**Verification:**
- [x] Verify GitHub App has Contents read/write permissions
- [x] Verify variable `APP_ID` is accessible in repository variables
- [x] Verify secret `APP_PRIVATE_KEY` is accessible in repository secrets
- [x] Verify GitHub App is installed on the repository
- [-] Test that GitHub App can push to `main` (if testing environment available)

#### Step 2: Create `release-version.yaml` Workflow

**File:** `.github/workflows/release-version.yaml`

1. **Create new workflow file**
   - [x] Create `.github/workflows/release-version.yaml`
   - [x] Set trigger to `push` on `main` branch

2. **Add `version` job**
   - [x] Generate GitHub App token:
     ```yaml
     - name: Generate GitHub App token
       id: app-token
       uses: actions/create-github-app-token@v2
       with:
         app-id: ${{ vars.APP_ID }}
         private-key: ${{ secrets.APP_PRIVATE_KEY }}
     ```
   - [x] Configure checkout with GitHub App token:
     ```yaml
     - name: Checkout code
       uses: actions/checkout@v4
       with:
         fetch-depth: 0
         token: ${{ steps.app-token.outputs.token }}
     ```
   - [x] Configure git user for commits:
     ```yaml
     - name: Configure git
       run: |
         git config user.name "github-actions[bot]"
         git config user.email "github-actions[bot]@users.noreply.github.com"
     ```
   - [x] Keep version calculation logic (from existing `version` job)
   - [x] Add step to update `Cargo.toml`:
     ```yaml
     - name: Update Cargo.toml version
       run: |
         sed -i "s/^version = \".*\"/version = \"${{ steps.version.outputs.version }}\"/" Cargo.toml
         echo "Updated Cargo.toml version to ${{ steps.version.outputs.version }}"
     ```
   - [x] Add step to commit and push version update:
     ```yaml
     - name: Commit and push version update
       run: |
         git add Cargo.toml
         git commit -m "chore: bump version to ${{ steps.version.outputs.version }}"
         git push origin HEAD:main
     ```
   - [x] Add step to create and push tag:
     ```yaml
     - name: Create and push git tag
       run: |
         git tag -a "${{ steps.version.outputs.tag_name }}" -m "Release ${{ steps.version.outputs.tag_name }}"
         git push origin "${{ steps.version.outputs.tag_name }}"
     ```
   - [x] Ensure job outputs version and tag_name for potential future use

**Verification:**
- [x] Workflow file syntax is valid
- [x] All steps reference correct outputs
- [x] GitHub App token is generated and used for checkout
- [x] Git operations use GitHub App token authentication
- [x] No security job exists (versioning happens immediately)
- [x] No build or release jobs exist

#### Step 3: Create `release-build.yaml` Workflow

**File:** `.github/workflows/release-build.yaml`

1. **Create new workflow file**
   - [x] Create `.github/workflows/release-build.yaml`
   - [x] Set trigger to tag push: `tags: ['v*']`

2. **Add `security` job**
   - [x] Copy `security` job from existing `release.yaml`
   - [x] Verify all security checks are included (cargo-deny, cargo-audit, cargo-geiger)
   - [x] This job runs as a quality gate before builds

3. **Add `build-and-release` job**
   - [x] Copy `build-and-release` job from existing `release.yaml`
   - [x] Add dependency on `security` job: `needs: security`
   - [x] Modify checkout to use the tag:
     ```yaml
     - name: Checkout code
       uses: actions/checkout@v4
       with:
         ref: ${{ github.ref }}  # This will be the tag ref
         fetch-depth: 0
     ```
   - [x] Verify matrix strategy is configured for all platforms
   - [x] Keep all build steps (Rust installation, tests, builds, artifact uploads)
   - [x] Ensure tests run before builds (quality gate)

4. **Add `release` job**
   - [x] Copy `release` job from existing `release.yaml`
   - [x] Add dependency: `needs: build-and-release`
   - [x] Keep release notes generation logic
   - [x] Keep artifact download logic
   - [x] Keep GitHub Release creation logic
   - [x] Verify release only creates if all builds succeed

**Verification:**
- [x] Workflow file syntax is valid
- [x] Tag trigger pattern matches version tag format
- [x] Checkout uses tag reference correctly
- [x] All build platforms are included in matrix

#### Step 4: Remove Original `release.yaml`

- [x] Delete `.github/workflows/release.yaml` (replaced by two new workflows)
- [x] File is preserved in git history, so no backup is needed

**Verification:**
- [x] No duplicate workflows exist
- [x] Only new workflows are active

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - [ ] Disable new workflows (`release-version.yaml` and `release-build.yaml`)
   - [ ] Restore original `release.yaml` workflow
   - [ ] Verify original workflow works
   - [ ] Investigate issues in new workflows

2. **Partial Rollback**
   - [ ] If version workflow fails: Disable `release-version.yaml`, restore version job in `release.yaml`
   - [ ] If build workflow fails: Disable `release-build.yaml`, restore build jobs in `release.yaml`
   - [ ] Investigate specific workflow issues

3. **GitHub App Issues**
   - [ ] If GitHub App authentication fails:
     - Verify `APP_ID` variable is correctly set in repository variables
     - Verify `APP_PRIVATE_KEY` secret is correctly set in repository secrets
     - Verify GitHub App has Contents read/write permissions
     - Verify GitHub App is installed on the repository
     - Verify branch protection rules exempt GitHub App
     - Check private key format (must be PEM format)
     - Verify App ID matches the installed app
   - [ ] Alternative: Use `GITHUB_TOKEN` with appropriate permissions (may require branch protection rule changes)

### Implementation Order

1. **Configure GitHub App and secrets** (Step 1)
   - Must be done first as workflows depend on it
   - Test GitHub App access before proceeding

2. **Create `release-version.yaml`** (Step 2)
   - This workflow triggers first in the process
   - Test with a small change to verify version calculation and tagging

3. **Create `release-build.yaml`** (Step 3)
   - This workflow is triggered by tag push from version workflow
   - Test after version workflow is verified

4. **Remove original `release.yaml`** (Step 4)
   - Only after both new workflows are tested and working

### Risk Assessment

- **Risk Level:** Medium
- **Impact if Failed:**
  - Release process may be disrupted
  - Version updates may not be committed
  - Tags may not be created
  - Builds may not trigger
  - Releases may not be created
- **Mitigation:**
  - GitHub App configuration can be tested independently
  - Workflows can be tested incrementally
  - Original workflow can be restored quickly
  - Branch protection rules can be adjusted if needed
  - GitHub App exemption can be configured in branch protection
- **Testing:**
  - Can test version workflow with small changes
  - Can test build workflow by manually pushing a tag
  - Can verify GitHub App access before full implementation
- **Dependencies:**
  - GitHub App must be created and installed on repository
  - GitHub App must have Contents read/write permissions
  - `APP_ID` variable must be set in repository variables
  - `APP_PRIVATE_KEY` secret must be set in repository secrets
  - Branch protection rules must exempt GitHub App (if rules exist)
  - Tag format must match trigger pattern (`v*`)
- **Permissions:**
  - GitHub App needs Contents read/write permissions
  - Workflow needs `contents: write` permission for releases
  - Workflow needs `pull-requests: read` for version calculation

### Expected Outcomes

After successful implementation:

- **Correct Build/Version Alignment**: Builds happen from tagged commit that contains version update
- **Complete Traceability**: Every push gets a version tag, even if release fails
- **Quality Gates**: Security and test checks determine if release is created
- **Flexibility**: Build workflow can be re-triggered independently
- **Separation of Concerns**: Versioning and building are in separate workflows
- **GitHub App Authentication**: Secure authentication for git operations with fine-grained permissions
- **Branch Protection Compliance**: GitHub App exempt from protection rules allows automated commits

## References

- Best practices for release workflows: ensure artifacts are built from the tagged commit
- GitHub Apps: https://docs.github.com/en/apps/creating-github-apps/creating-github-apps/about-apps
- GitHub Actions: Authenticating with GitHub Apps: https://docs.github.com/en/actions/security-guides/automatic-token-authentication#using-the-github_token-in-a-workflow
- GitHub Actions: Workflow triggers: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows
