# Implementation Plan: Cache build step fails due to sparse checkout

**Status**: ✅ Complete

## Overview
Fix the cache build workflow by removing sparse checkout and using a normal checkout with `fetch-depth: 1` to ensure compatibility with rust-cache while maintaining optimization benefits.

## Checklist Summary

### Phase 1: Fix Workflow Configuration
- [x] 1/1 tasks completed

## Context
Reference: `plan/25W48/BUG_CACHE_BUILD_SPARSE_CHECKOUT.md`

The cache build workflow currently uses sparse checkout to optimize checkout time and bandwidth by only fetching `Cargo.toml` and `Cargo.lock`. However, this causes issues with the rust-cache action, preventing the cache from being built and populated. The solution is to use a normal checkout with `fetch-depth: 1` to avoid fetching full git history while still providing a complete checkout that rust-cache can work with.

## Goals
- Remove sparse checkout from cache-build workflow
- Add `fetch-depth: 1` to optimize checkout (avoid full git history)
- Ensure rust-cache action works correctly
- Maintain optimization benefits (reduced bandwidth/time) where possible

## Non-Goals
- Changing other aspects of the cache-build workflow
- Modifying other workflows
- Changing rust-cache configuration

## Design Decisions

- **Use normal checkout with fetch-depth: 1**: Replace sparse checkout with a normal checkout that only fetches the latest commit
  - **Rationale**: rust-cache requires a normal checkout to function properly. Using `fetch-depth: 1` still provides optimization by avoiding full git history while ensuring compatibility
  - **Alternatives Considered**:
    - Keep sparse checkout and fix rust-cache configuration (rejected - rust-cache likely needs full checkout structure)
    - Use full checkout with full history (rejected - unnecessary bandwidth/time cost)
  - **Trade-offs**: Slightly more bandwidth/time than sparse checkout, but still optimized compared to full history, and ensures rust-cache compatibility

## Implementation Steps

### Phase 1: Fix Workflow Configuration

**Objective**: Update the cache-build workflow to use normal checkout with fetch-depth: 1 instead of sparse checkout

- [x] **Task 1**: Update checkout step in cache-build workflow
  - [x] Remove `sparse-checkout` configuration from checkout step
  - [x] Add `fetch-depth: 1` to checkout step
  - [x] Update comments to reflect the change
  - **Files**: `.github/workflows/cache-build.yaml`
  - **Dependencies**: None
  - **Testing**: Verify workflow runs successfully on next push to main
  - **Notes**: This is a simple configuration change that should immediately fix the issue

## Files to Modify/Create
- **Modified Files**:
  - `.github/workflows/cache-build.yaml` - Remove sparse checkout, add fetch-depth: 1

## Testing Strategy
- **Unit Tests**: N/A (workflow configuration change)
- **Integration Tests**: N/A (workflow configuration change)
- **Manual Testing**: Verify the cache-build workflow runs successfully on next push to main branch

## Breaking Changes
- None

## Migration Guide
N/A (no breaking changes)

## Documentation Updates
- [x] Update workflow comments to reflect the change

## Success Criteria
- Cache build workflow runs successfully without errors
- rust-cache action completes successfully
- All cargo tools are installed and cached
- Workflow checkout is optimized (fetch-depth: 1) while maintaining rust-cache compatibility

## Risks and Mitigations
- **Risk**: Normal checkout may take slightly longer than sparse checkout
  - **Mitigation**: Using `fetch-depth: 1` minimizes this impact by avoiding full git history
- **Risk**: rust-cache may still have issues if there are other problems
  - **Mitigation**: This is the most likely fix based on the bug description. If issues persist, they would be separate problems

## References
- Related BUG_ document: `plan/25W48/BUG_CACHE_BUILD_SPARSE_CHECKOUT.md`
- Related issues: N/A
- Related PRs: N/A
- External references:
  - GitHub Actions checkout action documentation
  - rust-cache action documentation
