# Implementation Plan: Cache build to complete before tag build (build-and-release)

**Status**: ✅ Complete

## Overview
Implement workflow coordination to ensure the `cache-build` workflow completes before the `release-build` workflow starts executing. This involves adding concurrency control to `cache-build`, adding a `workflow_run` trigger to `release-build`, and implementing tag detection logic to conditionally execute release builds only for tagged commits. The `release-build` workflow will no longer trigger on direct tag pushes.

## Checklist Summary

### Phase 1: Add Concurrency Control to Cache Build
- [x] 1/1 tasks completed

### Phase 2: Add Workflow Run Trigger and Tag Detection to Release Build
- [x] 1/1 tasks completed

### Phase 3: Verify Release Build Self-Sufficiency
- [x] 1/1 tasks completed

## Context
Reference to corresponding REQ_ document: `plan/25W48/REQ_CACHE_BUILD_BEFORE_TAG_BUILD.md`

**Current State**:
- `cache-build` workflow triggers on push to `main` branch
- `release-build` workflow triggers on tag push (`v*`)
- These workflows are completely independent with no coordination
- Both workflows can run simultaneously or in any order
- No mechanism exists to ensure cache build completes before tag build starts

**Problem Statement**:
Tag builds may start without a populated cache, leading to slower builds, redundant dependency downloads, and inefficient CI resource usage. There's also a potential race condition where tag builds may start before the cache is ready.

**Prerequisites**:
- REQ_COMBINE_COMMIT_AND_TAG_PUSH.md must be implemented first (enables single push that triggers cache-build via push to main)

## Goals
- Ensure cache build always completes before release build starts (when cache build runs)
- Implement concurrency control so only one cache build runs at a time, with subsequent pushes queued
- Only tagged commits trigger release builds (non-tagged commits to main skip release builds)
- Solution works automatically without manual intervention
- Release builds are resilient to cache build failures (fully self-contained)
- Release builds only trigger via workflow coordination (no direct tag push triggers)

## Non-Goals
- Modifying `release-version.yaml` (handled by REQ_COMBINE_COMMIT_AND_TAG_PUSH.md)
- Changing the fundamental structure of existing workflows
- Supporting direct tag push triggers (removed per user requirement)

## Design Decisions

**Important**: Document all key architectural and implementation decisions here. This section should explain the "why" behind major choices, not just the "what".

- **Use `workflow_run` trigger instead of job-level coordination**: The `release-build` workflow is triggered via `workflow_run` with `types: [completed]` when `cache-build` completes (regardless of success/failure status).
  - **Rationale**: `workflow_run` with `types: [completed]` provides a clean way to trigger one workflow after another completes. It fires on completion (success or failure), which is desired behavior. This approach allows `cache-build` to run on main push while `release-build` is triggered conditionally based on tag detection.
  - **Alternatives Considered**:
    - Job-level coordination: Making cache build a job in release workflow (rejected - cache build runs on main push, not tag push)
    - Status checks: Using GitHub status checks to gate tag builds (rejected - more complex, requires additional setup)
    - Manual workflow dispatch: Require manual triggering after cache build (rejected - too manual, breaks automation)
  - **Trade-offs**: `workflow_run` only triggers from default branch (`main`), which matches our use case. The workflow only handles `workflow_run` trigger (no direct tag push triggers).
  - **Skip scenario behavior**: When `release-version` workflow skips commit/tag creation (version unchanged), `cache-build` still runs (triggered by push to main), but `release-build` correctly detects no tag and skips all release jobs. This is expected and correct behavior.

- **Tag detection via git commands in workflow**: The `release-build` workflow checks if the commit has a version tag using `git tag --points-at HEAD | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+' | head -n 1` to match only semantic version tags (e.g., `v1.2.3`). Pre-release tags are not supported. Only the first matching tag is used if multiple tags point to the same commit.
  - **Rationale**: This approach is simple, reliable, and doesn't require external API calls. It works for the `workflow_run` trigger by checking the commit from the triggering workflow. The pattern matches only `v[MAJOR].[MINOR].[PATCH]` format tags. Using `head -n 1` ensures only the first match is used, preventing ambiguity if multiple version tags exist.
  - **Alternatives Considered**:
    - Using GitHub API to check tags (rejected - requires API calls, more complex, potential rate limiting)
    - Using `github.ref` context directly (rejected - doesn't work for `workflow_run` trigger which doesn't have tag context)
    - Erroring if multiple tags found (rejected - using first match is simpler and sufficient)
  - **Trade-offs**: Requires fetching tags in the workflow, but this is a fast operation with minimal impact on execution time. Checkout must use `fetch-depth: 0` to ensure tags are available.

- **Concurrency control with `cancel-in-progress: false`**: The `cache-build` workflow uses concurrency control with `cancel-in-progress: false` to queue subsequent runs instead of canceling them.
  - **Rationale**: This ensures only one cache build runs at a time, with subsequent pushes queued. This prevents cache corruption from concurrent builds and ensures cache consistency. Queued cache builds will execute in order.
  - **Alternatives Considered**:
    - `cancel-in-progress: true` (rejected - would cancel in-progress builds, potentially leaving cache in inconsistent state)
    - No concurrency control (rejected - allows concurrent builds which can corrupt cache)
  - **Trade-offs**: Queued builds may wait longer, but this ensures cache integrity and proper workflow coordination.

- **Release build self-sufficiency**: The `release-build` workflow must include all dependency and tool installation steps to ensure it can complete successfully even if `cache-build` fails or the cache is unavailable.
  - **Rationale**: The `cache-build` workflow is an **optimization** to pre-populate caches and reduce release build time. The `release-build` workflow must remain **fully self-contained** and capable of installing all required dependencies and tools independently.
  - **Alternatives Considered**:
    - Making release build depend on cache build success (rejected - would break release builds if cache build fails, even though cache is just an optimization)
    - Removing dependency installation from release build (rejected - would break release builds if cache is unavailable)
  - **Trade-offs**: Release builds may be slower if cache is unavailable, but they remain reliable and functional.

- **Remove direct tag push trigger**: The `release-build` workflow no longer triggers on direct tag pushes, only via `workflow_run` when `cache-build` completes.
  - **Rationale**: Per user requirement, release builds should only trigger through workflow coordination, ensuring cache build always completes first. Direct tag pushes bypass the cache build process and are not supported.
  - **Alternatives Considered**:
    - Keep `push.tags` trigger as fallback (rejected - per user requirement to remove tag push trigger)
  - **Trade-offs**: Direct tag pushes will no longer trigger release builds. All releases must go through the main branch workflow coordination. This is a breaking change but ensures proper workflow coordination.

- **Use job-level permissions instead of workflow-level**: Individual jobs (`build-and-release` and `release`) already have `contents: write` permissions. No workflow-level permissions are needed.
  - **Rationale**: Job-level permissions are more granular and explicit. The existing permissions structure is sufficient and doesn't need to be changed.
  - **Alternatives Considered**:
    - Workflow-level permissions (rejected - redundant, job-level is more explicit)
  - **Trade-offs**: None - existing permissions structure is maintained.

## Implementation Steps

**Note**: Implementation steps should be organized into phases. Each phase contains multiple tasks with checkboxes to track progress. Each task should be broken down into detailed sub-tasks with individual checkboxes. Phases should be logically grouped and can be completed sequentially or in parallel where appropriate.

**Important**: An implementation plan is considered complete when all AI-actionable tasks are finished. Do NOT include human-only tasks such as:
- Manual testing (beyond what can be automated)
- Code review
- Merging to main
- Release activities

These are post-implementation activities handled by humans. Focus only on tasks the AI can directly execute (code changes, automated test creation, documentation updates, etc.). When all AI-actionable tasks are complete, update the status to "✅ Complete" even if human activities remain.

### Phase 1: Add Concurrency Control to Cache Build

**Objective**: Ensure only one cache build runs at a time, with subsequent pushes queued, preventing cache corruption and ensuring proper workflow coordination.

- [x] **Task 1**: Add concurrency control to `cache-build.yaml`
  - [x] Add `concurrency` key at workflow level (after `on:` section, before `jobs:`)
  - [x] Use correct YAML syntax:
    ```yaml
    concurrency:
      group: cache-build
      cancel-in-progress: false
    ```
  - [x] Set `group: cache-build` to group all cache build runs together
  - [x] Set `cancel-in-progress: false` to queue subsequent runs instead of canceling them
  - [x] Verify the syntax matches GitHub Actions concurrency specification
  - **Files**: `.github/workflows/cache-build.yaml`
  - **Dependencies**: None
  - **Testing**: Verify workflow syntax is valid YAML and follows GitHub Actions concurrency specification
  - **Notes**: The concurrency group ensures only one cache build runs at a time. When multiple pushes to main occur, subsequent pushes will be queued and wait for the first cache build to complete before starting.

### Phase 2: Add Workflow Run Trigger and Tag Detection to Release Build

**Objective**: Add `workflow_run` trigger to `release-build` workflow that fires when `cache-build` completes, and implement tag detection logic to conditionally execute release builds only for tagged commits.

- [x] **Task 1**: Update `release-build.yaml` to add `workflow_run` trigger and tag detection
  - [x] Remove existing `push.tags` trigger from `on:` section
  - [x] Add `workflow_run` trigger to `on:` section that fires when `cache-build` workflow completes (regardless of success/failure)
    - [x] Set `workflows: ["Cache Build"]` to match the workflow name
    - [x] Set `types: [completed]` to trigger on completion (success or failure)
    - [x] Set `branches: [main]` to only trigger from main branch (workflow_run limitation)
  - [x] Create new `check-tag` job that:
    - [x] Checks out the commit using explicit `ref: ${{ github.event.workflow_run.head_sha }}` with `fetch-depth: 0` to ensure tags are available
    - [x] Fetches tags: `git fetch --tags --force` (let errors break the build - use `set -e` or fail on error)
    - [x] Checks if commit has a version tag using robust tag extraction (let errors break the build):
      - [x] Extract first matching tag: `TAG_NAME=$(git tag --points-at HEAD | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+' | head -n 1)`
      - [x] If tag found, set `has_tag=true` and `tag_name=$TAG_NAME`
      - [x] If no tag found, set `has_tag=false` and `tag_name=` (empty string)
      - [x] Matches only `v[MAJOR].[MINOR].[PATCH]` format, no pre-release tags
      - [x] Use `set -e` or ensure script fails on any error (no graceful error handling - errors should break the build)
    - [x] Sets output `has_tag` (string: "true" if tag found, "false" otherwise)
    - [x] Sets output `tag_name` (string: tag name if found, empty string otherwise)
  - [x] Update all existing jobs (`security`, `coverage`, `build-and-release`, `release`) to:
    - [x] Add `needs: check-tag` dependency
    - [x] Add conditional execution: `if: needs.check-tag.outputs.has_tag == 'true'`
    - [x] Update checkout steps to use explicit `ref: ${{ github.event.workflow_run.head_sha }}` instead of `github.ref`
    - [x] Update checkout steps to use `fetch-depth: 0` where needed (for jobs that need full history or tags)
  - [x] Update `security` job to install Rust components for self-sufficiency:
    - [x] Add `components: clippy rustfmt` to the Rust installation step in `security` job
    - [x] This ensures `security` job installs the same components as `cache-build` workflow for consistency and self-sufficiency
  - [x] Update `release` job to use `needs.check-tag.outputs.tag_name` instead of `github.ref_name` for all tag references:
    - [x] Replace `GITHUB_REF_NAME: ${{ github.ref_name }}` with `GITHUB_REF_NAME: ${{ needs.check-tag.outputs.tag_name }}` in release notes generation step
    - [x] Replace `gh release create "${{ github.ref_name }}"` with `gh release create "${{ needs.check-tag.outputs.tag_name }}"`
    - [x] Replace `--title "Release ${{ github.ref_name }}"` with `--title "Release ${{ needs.check-tag.outputs.tag_name }}"`
  - [x] Add workflow-level comments documenting the coordination mechanism and skip scenario:
    - [x] Add comment at top of workflow explaining `workflow_run` trigger fires when `cache-build` completes (success or failure)
    - [x] Add comment explaining tag detection: if no tag found, all release jobs are skipped
    - [x] Add comment explaining skip scenario: when `release-version` workflow skips commit/tag (version unchanged), `cache-build` still runs but `release-build` correctly skips all jobs
    - [x] Add comment explaining that direct tag pushes no longer trigger this workflow
    - [x] Add comment in `check-tag` job explaining tag detection logic and error handling (errors break the build)
  - **Files**: `.github/workflows/release-build.yaml`
  - **Dependencies**: Phase 1 (concurrency control should be in place)
  - **Testing**:
    - Verify workflow syntax is valid YAML
    - Verify tag detection logic correctly identifies version tags (v[MAJOR].[MINOR].[PATCH] pattern)
    - Verify tag detection uses first matching tag if multiple tags exist
    - Verify conditional execution works correctly (jobs skip when no tag found)
    - Verify `workflow_run` trigger works correctly
    - Verify all `github.ref_name` references are replaced with `needs.check-tag.outputs.tag_name`
  - **Notes**:
    - The `workflow_run` trigger with `types: [completed]` will fire when `cache-build` completes, ensuring cache build finishes before release build starts
    - Tag detection ensures only tagged commits trigger release builds
    - Tag detection extracts only the first matching tag using `head -n 1` to handle edge case of multiple tags
    - Direct tag pushes will no longer trigger release builds (breaking change)
    - All release jobs must depend on `check-tag` and conditionally run only if a tag is found
    - `github.ref` and `github.ref_name` are not available in `workflow_run` context, so tag name must come from `check-tag` job output
    - Skip scenario: When `release-version` workflow skips commit/tag (version unchanged), `cache-build` runs but `release-build` correctly skips all jobs (expected behavior)
    - Job-level permissions are maintained (no workflow-level permissions needed)
    - Checkout must explicitly use `ref: ${{ github.event.workflow_run.head_sha }}` to checkout the correct commit from the triggering workflow
    - Error handling: Tag detection script should use `set -e` or fail on error - errors should break the build rather than being handled gracefully

### Phase 3: Verify Release Build Self-Sufficiency

**Objective**: Ensure `release-build` workflow includes all necessary dependency and tool installation steps to remain fully self-contained, even if `cache-build` fails or cache is unavailable.

- [x] **Task 1**: Verify and document release build self-sufficiency
  - [x] Review `release-build.yaml` to ensure all jobs include necessary dependency and tool installation steps
  - [x] Compare with `cache-build.yaml` to verify `release-build` installs same or superset of dependencies/tools
  - [x] Verify `security` job installs Rust with components: `clippy rustfmt` (should be added in Phase 2)
  - [x] Document any missing dependencies or tools that need to be added
  - [x] Verify all dependency/tool installation steps are in place to ensure release build is fully self-contained
  - [x] Verify each job can complete successfully even if cache is unavailable
  - **Files**: `.github/workflows/release-build.yaml`
  - **Dependencies**: Phase 2 (release-build structure should be updated)
  - **Testing**:
    - Verify all required dependencies and tools are installed in each job
    - Verify jobs can complete successfully without cache (theoretical check - actual testing requires manual verification)
  - **Notes**:
    - The `cache-build` workflow installs: Rust components (clippy, rustfmt, llvm-tools-preview), cargo-deny, cargo-audit, cargo-auditable, cargo-geiger, cargo-nextest, cargo-llvm-cov
    - The `release-build` workflow must install all of these (or superset) to remain self-contained
    - Specifically, `security` job should include `clippy rustfmt` components in Rust installation
    - Cache is purely an optimization - release builds must work without it

## Files to Modify/Create
- **Modified Files**:
  - `.github/workflows/cache-build.yaml` - Add concurrency control to ensure only one cache build runs at a time
  - `.github/workflows/release-build.yaml` - Remove `push.tags` trigger, add `workflow_run` trigger, tag detection job, and conditional execution for all release jobs

## Testing Strategy
- **Unit Tests**: N/A (workflow files are configuration, not code)
- **Integration Tests**:
  - Verify workflow YAML syntax is valid
  - Verify tag detection logic correctly identifies version tags (v* pattern)
  - Verify conditional execution works correctly (jobs skip when no tag found)
  - Verify `workflow_run` trigger works correctly
  - Verify concurrency control syntax is correct
- **Manual Testing**:
  - Test workflow coordination in actual GitHub Actions environment (requires manual verification)
  - Test that cache build completes before release build starts
  - Test that non-tagged commits to main trigger cache build but skip release build
  - Test that tagged commits trigger both cache build and release build in correct order
  - Test that release build works correctly even if cache build fails
  - Test that release build works correctly even if cache is unavailable
  - Verify that direct tag pushes do not trigger release builds

## Breaking Changes
Yes - removing `push.tags` trigger means direct tag pushes will no longer trigger release builds. All releases must go through the main branch workflow coordination.

## Migration Guide
- Direct tag pushes will no longer trigger release builds
- All releases must be created via `release-version.yaml` which pushes both commit and tag to main branch
- This ensures proper workflow coordination and cache availability

## Documentation Updates
- [ ] Update workflow documentation if any exists (if applicable)

## Success Criteria
- Cache build workflow includes concurrency control with `cancel-in-progress: false` (using correct YAML syntax)
- Release build workflow includes `workflow_run` trigger with `types: [completed]` that fires when cache-build completes
- Release build workflow no longer includes `push.tags` trigger
- Release build workflow includes tag detection job that correctly identifies version tags (v[MAJOR].[MINOR].[PATCH] format)
- Tag detection uses `head -n 1` to extract only the first matching tag if multiple tags exist
- All release jobs conditionally execute only when a tag is found
- All checkout steps use `github.event.workflow_run.head_sha` instead of `github.ref`
- `release` job uses `needs.check-tag.outputs.tag_name` instead of `github.ref_name` for all tag references (GITHUB_REF_NAME env var, gh release create command, and release title)
- Release build workflow remains fully self-contained with all necessary dependency/tool installation steps (including clippy, rustfmt, llvm-tools-preview)
- Workflow includes comments documenting the coordination mechanism and skip scenario behavior
- Workflow YAML syntax is valid and follows GitHub Actions best practices
- Solution only uses `workflow_run` trigger (no direct tag push triggers)
- Direct tag pushes do not trigger release builds
- Job-level permissions are maintained (no workflow-level permissions added)

## Risks and Mitigations
- **Risk**: `workflow_run` trigger may not fire correctly if workflow names don't match exactly
  - **Mitigation**: Use exact workflow name "Cache Build" (case-sensitive) in `workflow_run` trigger
- **Risk**: Tag detection may fail if tags aren't fetched correctly
  - **Mitigation**: Use `fetch-depth: 0` in checkout step and `git fetch --tags --force` to ensure tags are available
- **Risk**: Direct tag pushes will no longer trigger release builds (breaking change)
  - **Mitigation**: Document this breaking change clearly. All releases must go through main branch workflow coordination.
- **Risk**: Concurrency control may cause builds to wait longer than expected
  - **Mitigation**: This is expected behavior - queued builds ensure cache consistency. Document this behavior.
- **Risk**: Release build may fail if cache is unavailable and dependencies aren't installed
  - **Mitigation**: Ensure all release jobs include all necessary dependency/tool installation steps (Phase 3)
- **Risk**: Conditional execution may skip builds incorrectly
  - **Mitigation**: Test tag detection logic thoroughly and verify it correctly identifies version tags (v[MAJOR].[MINOR].[PATCH] format). Use `head -n 1` to ensure only first matching tag is used if multiple tags exist.
- **Risk**: Multiple tags pointing to same commit may cause ambiguity
  - **Mitigation**: Tag detection uses `head -n 1` to extract only the first matching tag, preventing ambiguity. This is sufficient for normal use cases where only one version tag should exist per commit.
- **Risk**: `github.ref` and `github.ref_name` are not available in `workflow_run` context
  - **Mitigation**: Use `github.event.workflow_run.head_sha` for checkout and `needs.check-tag.outputs.tag_name` for tag name references

## References
- Related REQ_ document: `plan/25W48/REQ_CACHE_BUILD_BEFORE_TAG_BUILD.md`
- Related requirements:
  - `plan/25W48/REQ_COMBINE_COMMIT_AND_TAG_PUSH.md` (prerequisite - enables single push that triggers cache-build)
- External references:
  - GitHub Actions `workflow_run` trigger documentation
  - GitHub Actions workflow dependencies and coordination patterns
  - GitHub Actions concurrency control documentation
  - Current workflows:
    - `.github/workflows/cache-build.yaml` (triggers on push to main)
    - `.github/workflows/release-build.yaml` (currently triggers on tag push)
    - `.github/workflows/release-version.yaml` (creates version commit and tag)
