# Implementation Plan: Remove Redundant `uv sync` Commands from GitHub Actions Workflows

**Status**: ✅ Completed

## Overview
Remove explicit `uv sync --extra dev` commands from GitHub Actions workflows since `uv run` automatically syncs dependencies before execution. This simplifies workflows, reduces execution time, and follows `uv` best practices.

## Checklist Summary

### Phase 1: Remove `uv sync` from Pull Request Workflow
- [x] 3/3 tasks completed

### Phase 2: Remove `uv sync` from Release Build Workflow
- [x] 2/2 tasks completed

### Phase 3: Verification
- [x] 1/1 tasks completed

## Context
Reference to corresponding REQ document: `plan/25W48/REQ_REMOVE_UV_SYNC_FROM_WORKFLOWS.md`

The `uv` tool's `run` command automatically locks and syncs project dependencies before executing commands, making explicit `uv sync` calls redundant. Currently, several workflow steps include `uv sync --extra dev` before running Python scripts, which is unnecessary since:
- `uv run` automatically syncs runtime dependencies
- Scripts don't require dev dependencies at runtime (only for testing)
- The redundant sync operations add unnecessary overhead to workflow execution

## Goals
- Remove all explicit `uv sync --extra dev` commands from workflow files
- Ensure workflows continue to function correctly with automatic dependency syncing
- Simplify workflow files by following `uv` best practices
- Reduce workflow execution time by eliminating duplicate sync operations

## Non-Goals
- Modifying scripts that already use `uv run` directly (pr-labels, release-version, release-notes, create-checksum)
- Changing Python version requirements or dependency specifications
- Modifying script functionality or behavior

## Design Decisions

- **Remove `uv sync --extra dev` instead of keeping it**:
  - **Rationale**: `uv run` automatically syncs runtime dependencies, and scripts don't need dev dependencies at runtime. The explicit sync is redundant and adds unnecessary overhead.
  - **Alternatives Considered**:
    - Keep `uv sync --extra dev` for consistency: Rejected - adds unnecessary overhead and doesn't follow `uv` best practices
    - Use `uv run --extra dev` instead: Rejected - scripts don't need dev dependencies at runtime, only for testing
  - **Trade-offs**: None - this is a pure simplification that maintains functionality

- **Remove sync commands from all affected steps**:
  - **Rationale**: Consistency across all workflows and following `uv` best practices uniformly.
  - **Alternatives Considered**:
    - Keep sync for scripts with runtime dependencies: Rejected - `uv run` automatically syncs runtime dependencies
  - **Trade-offs**: None - all scripts benefit from automatic syncing

## Implementation Steps

### Phase 1: Remove `uv sync` from Pull Request Workflow

**Objective**: Remove redundant `uv sync --extra dev` commands from `.github/workflows/pull_request.yaml`

- [x] **Task 1**: Remove `uv sync --extra dev` from test-ubuntu job
  - [x] Remove line 82 (`uv sync --extra dev`) from test-ubuntu job's "Generate test summary" step
  - [x] Ensure `uv run python -m test_summary` command remains intact
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: None
  - **Testing**: Verify the step still executes correctly (workflow will be tested in Phase 3)
  - **Notes**: The `uv run` command on line 83 will automatically sync dependencies

- [x] **Task 2**: Remove `uv sync --extra dev` from test-macos job
  - [x] Remove line 129 (`uv sync --extra dev`) from test-macos job's "Generate test summary" step
  - [x] Ensure `uv run python -m test_summary` command remains intact
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: None
  - **Testing**: Verify the step still executes correctly (workflow will be tested in Phase 3)
  - **Notes**: The `uv run` command on line 130 will automatically sync dependencies

- [x] **Task 3**: Remove `uv sync --extra dev` from coverage job
  - [x] Remove line 212 (`uv sync --extra dev`) from coverage job's "Generate coverage summary" step
  - [x] Ensure `uv run python -m coverage_summary` commands remain intact
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: None
  - **Testing**: Verify the step still executes correctly (workflow will be tested in Phase 3)
  - **Notes**: The `uv run` commands on lines 214 and 218 will automatically sync dependencies

### Phase 2: Remove `uv sync` from Release Build Workflow

**Objective**: Remove redundant `uv sync --extra dev` commands from `.github/workflows/release-build.yaml`

- [x] **Task 1**: Remove `uv sync --extra dev` from coverage job
  - [x] Remove line 150 (`uv sync --extra dev`) from coverage job's "Generate coverage summary" step
  - [x] Ensure `uv run python -m coverage_summary` command remains intact
  - **Files**: `.github/workflows/release-build.yaml`
  - **Dependencies**: None
  - **Testing**: Verify the step still executes correctly (workflow will be tested in Phase 3)
  - **Notes**: The `uv run` command on line 151 will automatically sync dependencies

- [x] **Task 2**: Remove `uv sync --extra dev` from build-and-release job
  - [x] Remove line 202 (`uv sync --extra dev`) from build-and-release job's "Generate test summary" step
  - [x] Ensure `uv run python -m test_summary` command remains intact
  - **Files**: `.github/workflows/release-build.yaml`
  - **Dependencies**: None
  - **Testing**: Verify the step still executes correctly (workflow will be tested in Phase 3)
  - **Notes**: The `uv run` command on line 203 will automatically sync dependencies

### Phase 3: Verification

**Objective**: Verify all changes are correct and workflows will function properly

- [x] **Task 1**: Review and validate workflow changes
  - [x] Verify all `uv sync --extra dev` commands have been removed from specified locations
  - [x] Verify all `uv run` commands remain intact and properly formatted
  - [x] Check that no other workflow steps were accidentally modified
  - [x] Verify YAML syntax is correct (no indentation or formatting issues)
  - **Files**: `.github/workflows/pull_request.yaml`, `.github/workflows/release-build.yaml`
  - **Dependencies**: Completion of Phase 1 and Phase 2
  - **Testing**:
    - Run `yamllint` or similar YAML validator if available
    - Review diff to ensure only intended lines were removed
    - Verify workflow file structure is intact
  - **Notes**: Manual workflow testing will be done via GitHub Actions when changes are pushed

## Files to Modify/Create
- **Modified Files**:
  - `.github/workflows/pull_request.yaml` - Remove 3 instances of `uv sync --extra dev` commands
  - `.github/workflows/release-build.yaml` - Remove 2 instances of `uv sync --extra dev` commands

## Testing Strategy
- **Unit Tests**: Not applicable - this is a workflow configuration change
- **Integration Tests**: Not applicable - workflow changes are tested via GitHub Actions
- **Manual Testing**:
  - Create a test PR to trigger `pull_request.yaml` workflow and verify all jobs complete successfully
  - Trigger a release build workflow to verify `release-build.yaml` jobs complete successfully
  - Verify that test-summary and coverage-summary scripts execute correctly without explicit sync commands
  - Confirm that workflow execution time is reduced (informational verification)

## Breaking Changes
None - workflows will continue to function identically. The `uv run` command automatically handles dependency syncing, so removing explicit sync commands is a pure simplification.

## Migration Guide
Not applicable - no breaking changes.

## Documentation Updates
- [ ] No documentation updates required - this is an internal workflow optimization

## Success Criteria
- All explicit `uv sync --extra dev` commands removed from `.github/workflows/pull_request.yaml` (3 instances)
- All explicit `uv sync --extra dev` commands removed from `.github/workflows/release-build.yaml` (2 instances)
- All `uv run` commands remain intact and functional
- Workflow YAML syntax is valid
- Workflows execute successfully in GitHub Actions (verified via manual testing after implementation)

## Risks and Mitigations
- **Risk**: Scripts may fail if `uv run` doesn't properly sync dependencies
  - **Mitigation**: This is a low risk since `uv run` is the recommended approach and is already used successfully in other workflows (pr-labels, release-version, release-notes, create-checksum). Scripts have no runtime dependencies or minimal dependencies that `uv run` handles automatically.

- **Risk**: Workflow execution may fail due to YAML syntax errors
  - **Mitigation**: Careful review of changes and validation of YAML syntax. Only removing specific lines without modifying surrounding structure.

- **Risk**: Dev dependencies may be needed at runtime (unlikely but possible)
  - **Mitigation**: Script analysis shows no runtime dependencies on dev extras. Scripts like `test-summary` and `coverage-summary` have `dependencies = []` in their `pyproject.toml` files, confirming they don't need dev dependencies at runtime.

## References
- Related REQ_ document: `plan/25W48/REQ_REMOVE_UV_SYNC_FROM_WORKFLOWS.md`
- Related issues: None
- Related PRs: None
- Design documents: None
- External references:
  - [uv documentation on sync](https://docs.astral.sh/uv/concepts/projects/sync/)
  - [uv run command](https://docs.astral.sh/uv/commands/run/)
