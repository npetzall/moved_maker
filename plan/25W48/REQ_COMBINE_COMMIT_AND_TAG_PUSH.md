# REQ: Combine commit push and tag push into single git push

**Status**: 📋 Planned

## Overview
Combine the separate `git push` commands for the commit and tag into a single push operation in the release-version workflow.

## Motivation
Currently, the release-version workflow performs two separate git push operations:
1. Push the commit to main branch
2. Push the tag separately

This is inefficient and can be simplified. Git supports pushing both commits and tags in a single push operation, which:
- Reduces the number of network operations
- Simplifies the workflow code
- Makes the intent clearer (both operations are atomic)
- Slightly improves workflow execution time

## Current Behavior
In `.github/workflows/release-version.yaml`, the workflow:
1. Commits version changes to Cargo.toml and Cargo.lock
2. Pushes the commit to main: `git push origin HEAD:main`
3. Creates an annotated tag
4. Pushes the tag separately: `git push origin "${{ steps.version.outputs.tag_name }}"`

These are two separate push operations that could be combined.

## Proposed Behavior
Combine the commit push and tag push into a single git push command:
```bash
git push origin HEAD:main "${{ steps.version.outputs.tag_name }}"
```

This pushes both the branch reference and the tag reference in one atomic operation.

## Use Cases
- When the release-version workflow runs and creates a new version commit and tag, both should be pushed together
- The workflow should be simpler and more efficient
- The push operation should be atomic (both commit and tag pushed together)

## Implementation Considerations
- The tag is created on the current HEAD (the commit being pushed), so they can be pushed together
- Git supports pushing multiple refs in a single push command
- Alternative: Could use `--follow-tags` flag, but explicitly listing the tag is clearer
- No risk of race conditions since both refs are pushed atomically
- Should verify the change works correctly in the workflow

## Alternatives Considered
- **Keep separate pushes**: Current approach (rejected - less efficient, more verbose)
- **Use --follow-tags**: `git push origin HEAD:main --follow-tags` (rejected - less explicit, pushes all reachable tags)
- **Single push with explicit tag**: `git push origin HEAD:main "${{ steps.version.outputs.tag_name }}"` (selected - clear and explicit)

## Impact
- **Breaking Changes**: No (behavior is identical, just more efficient)
- **Documentation**: No documentation changes needed
- **Testing**: Should verify the workflow still works correctly after the change
- **Dependencies**: No new dependencies required

## References
- Related issues: N/A
- Related PRs: N/A
- External references:
  - Git push documentation for pushing multiple refs
  - Current workflow: `.github/workflows/release-version.yaml` (lines 72-76)
