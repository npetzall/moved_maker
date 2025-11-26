# REQ: Cache build to complete before tag build (build-and-release)

**Status**: ✅ Complete

## Overview
The cache build workflow should complete before the tag build (build-and-release) workflow runs, ensuring the cache is populated and available for the release build process.

## Motivation
Currently, the `cache-build` workflow runs on push to `main` and the `release-build` workflow runs on tag push (`v*`). These workflows are independent and there's no guarantee that the cache build completes before the tag build starts. This can lead to:
- Tag builds starting without a populated cache
- Slower tag builds as they need to download dependencies and install tools
- Inefficient use of CI resources when both workflows run simultaneously
- Potential race conditions where tag builds may start before cache is ready

By ensuring cache build completes before tag build, we can:
- Guarantee cache availability for tag builds
- Improve tag build performance
- Reduce redundant dependency downloads and tool installations
- Ensure consistent and efficient CI execution

## Current Behavior
- `cache-build` workflow triggers on push to `main` branch
- `release-build` workflow triggers on tag push (`v*`)
- These workflows are completely independent with no coordination
- Both workflows can run simultaneously or in any order
- No mechanism exists to ensure cache build completes before tag build starts

## Proposed Behavior
Implement a mechanism to ensure the `cache-build` workflow completes before the `release-build` workflow starts executing. The solution uses:

1. **Combined commit and tag push** (see REQ_COMBINE_COMMIT_AND_TAG_PUSH): When `release-version.yaml` pushes both the commit and tag together in a single push operation, the `cache-build` workflow is triggered via the push to `main`.

2. **Concurrency control**: The `cache-build` workflow uses concurrency control to ensure that only one instance runs at a time. When multiple pushes to `main` occur, subsequent pushes will be queued and wait for the first cache build to complete before starting.

3. **Workflow run trigger**: The `release-build` workflow is triggered via `workflow_run` with `types: [completed]` when `cache-build` completes (regardless of success/failure status). The workflow no longer triggers on direct tag pushes.

4. **Tag detection**: The `release-build` workflow checks if the commit from the triggering workflow has a version tag (`v*`). If a tag is found, it proceeds with the release build. If no tag is found, it skips the build.

**Important**: The `cache-build` workflow is an **optimization** to pre-populate caches and reduce release build time. The `release-build` workflow must remain **fully self-contained** and capable of installing all required dependencies and tools independently. If `cache-build` fails or the cache is unavailable, `release-build` will still execute successfully by installing any missing dependencies during its own execution.

This approach ensures:
- Cache build always completes before release build starts (when cache build runs)
- Only one cache build runs at a time, with subsequent pushes queued
- Only tagged commits trigger release builds
- Non-tagged commits to main don't trigger unnecessary release builds
- The solution works automatically without manual intervention
- Release builds are resilient to cache build failures
- Release builds only trigger via workflow coordination (no direct tag push triggers)

## Use Cases
- When a commit and tag are pushed together (from `release-version.yaml`), the cache build runs first, then release build is triggered
- When multiple pushes to `main` occur in quick succession, the first cache build runs immediately and subsequent pushes are queued
- Cache build populates the cache with all dependencies and tools before release builds start
- Release builds benefit from the pre-populated cache, reducing build time
- Non-tagged commits to main trigger cache build but skip release build (no unnecessary builds)
- The solution handles cases where cache build completes successfully or fails (`workflow_run` with `types: [completed]` triggers on completion)
- Direct tag pushes (without going through main branch) do not trigger release builds

## Solution

### Implementation Approach

1. **Update `release-version.yaml`** (see REQ_COMBINE_COMMIT_AND_TAG_PUSH):
   - Combine commit and tag push into single operation: `git push origin HEAD:main "${{ steps.version.outputs.tag_name }}"`
   - This ensures both commit and tag are pushed together, triggering `cache-build` via push to `main`

2. **Update `release-build.yaml`**:
   - Remove existing `push.tags` trigger
   - Add `workflow_run` trigger with `types: [completed]` that fires when `cache-build` completes (regardless of success/failure)
   - Use job-level permissions: Individual jobs (`build-and-release` and `release`) already have `contents: write` permissions. No workflow-level permissions are needed.
   - Add a `check-tag` job that:
     - Checks out the commit using `ref: ${{ github.event.workflow_run.head_sha }}` with `fetch-depth: 0` to include tags
     - Fetches tags: `git fetch --tags --force`
     - Checks if commit has a version tag: `git tag --points-at HEAD | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+'` (matches only `v[MAJOR].[MINOR].[PATCH]` format, no pre-release tags)
     - Sets outputs: `has_tag` (string: "true" or "false") and `tag_name` (string)
   - Make all release jobs depend on `check-tag` and conditionally run only if `has_tag == 'true'`
   - Update all checkout steps to use `github.event.workflow_run.head_sha` instead of `github.ref`
   - Update `release` job to use `needs.check-tag.outputs.tag_name` instead of `github.ref_name` for tag references
   - Ensure all release jobs include all necessary dependency and tool installation steps (same or superset of what `cache-build` installs, including Rust components: clippy, rustfmt, llvm-tools-preview)

3. **Update `cache-build.yaml`**:
   - Add concurrency control using the `concurrency` key with a group identifier
   - Set `cancel-in-progress: false` to queue subsequent runs instead of canceling them
   - Example:
     ```yaml
     concurrency:
       group: cache-build
       cancel-in-progress: false
     ```
   - This ensures only one cache build runs at a time, with subsequent pushes queued
   - The `workflow_run` trigger in `release-build` will automatically fire when cache-build completes

### Key Implementation Details

- **Concurrency control**: Use GitHub Actions `concurrency` feature to ensure only one cache build runs at a time, with `cancel-in-progress: false` to queue subsequent runs
- **Workflow run context**: Use `github.event.workflow_run.head_sha` to get the commit SHA from the triggering workflow. The checkout step must explicitly use `ref: ${{ github.event.workflow_run.head_sha }}` to checkout the correct commit. Note that `github.ref` and `github.ref_name` are not available in `workflow_run` context, so tag name must be obtained from the `check-tag` job output.
- **Tag detection**: Fetch tags and check if commit has a tag matching version pattern (`v[MAJOR].[MINOR].[PATCH]`, e.g., `v1.2.3`)
- **Conditional execution**: All release jobs use `if: needs.check-tag.outputs.has_tag == 'true'` to skip when no tag is found
- **Single trigger**: `release-build` only triggers via `workflow_run` with `types: [completed]` when `cache-build` completes (no direct tag push triggers)
- **Workflow run limitation**: `workflow_run` only triggers from default branch (`main`), which matches our use case

## Implementation Considerations
- `workflow_run` trigger with `types: [completed]` fires on completion (success or failure), which is desired behavior
- Concurrency control with `cancel-in-progress: false` ensures subsequent cache builds are queued rather than canceled, preventing cache corruption from concurrent builds
- Tag detection requires fetching tags in the workflow
- Solution only uses `workflow_run` trigger (no direct tag push triggers)
- Must ensure tag detection logic correctly identifies version tags
- Consider impact on workflow execution time (minimal - tag check is fast)
- Queued cache builds will execute in order, ensuring cache consistency
- **Cache optimization**: If the cache already exists before `cache-build` runs, the build will be quick since installs will be instant (cache hits). This means `cache-build` serves as both a cache population step and a cache validation step.
- **Release build self-sufficiency**: The `release-build` workflow must include all dependency and tool installation steps to ensure it can complete successfully even if `cache-build` fails or the cache is unavailable. The cache is purely an optimization to speed up these installations.
- **Breaking change**: Removing `push.tags` trigger means direct tag pushes will no longer trigger release builds. All releases must go through the main branch workflow coordination.

## Alternatives Considered
- **No coordination**: Current state - workflows run independently (rejected because it doesn't solve the problem)
- **Manual workflow dispatch**: Require manual triggering after cache build (rejected - too manual, breaks automation)
- **Status checks**: Use GitHub status checks to gate tag builds (rejected - more complex, requires additional setup)
- **Workflow run trigger**: Use `workflow_run` with `types: [completed]` to trigger release build after cache build (✅ **SELECTED** - works well with tag detection)
- **Job-level coordination**: Make cache build a job in release workflow (rejected - cache build runs on main push, not tag push)
- **Keep tag push trigger as fallback**: Keep `push.tags` trigger for edge cases (rejected - user requirement to remove tag push trigger)

## Impact
- **Breaking Changes**: Yes - removing `push.tags` trigger means direct tag pushes will no longer trigger release builds. All releases must go through the main branch workflow coordination.
- **Documentation**: May need to document workflow dependencies and execution order
- **Testing**: Need to test workflow coordination and ensure it works in various scenarios (cache build running, complete, failed, etc.)
- **Dependencies**: May require changes to workflow structure or use of additional GitHub Actions features

## References
- Related issues: N/A
- Related PRs: N/A
- Related requirements:
  - REQ_COMBINE_COMMIT_AND_TAG_PUSH.md (prerequisite - enables single push that triggers cache-build)
- External references:
  - GitHub Actions `workflow_run` trigger documentation
  - GitHub Actions workflow dependencies and coordination patterns
  - Current workflows:
    - `.github/workflows/cache-build.yaml` (triggers on push to main)
    - `.github/workflows/release-build.yaml` (currently triggers on tag push)
    - `.github/workflows/release-version.yaml` (creates version commit and tag)
