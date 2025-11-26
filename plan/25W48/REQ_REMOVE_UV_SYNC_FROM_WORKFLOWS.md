# REQ: Remove Redundant `uv sync` Commands from GitHub Actions Workflows

**Status**: ✅ Completed

## Overview
Remove explicit `uv sync` and `uv sync --extra dev` commands from GitHub Actions workflows since `uv run` automatically syncs dependencies before execution.

## Motivation
The `uv` tool's `run` command automatically locks and syncs project dependencies before executing commands, making explicit `uv sync` calls redundant. Removing these redundant commands will:
- Simplify workflow files
- Reduce workflow execution time (eliminating duplicate sync operations)
- Follow `uv` best practices
- Improve maintainability by reducing unnecessary steps

## Current Behavior

**Workflows with explicit `uv sync` commands:**

1. **`.github/workflows/pull_request.yaml`**:
   - Line 80: `uv sync --extra dev` before `test-summary` (test-ubuntu job)
   - Line 125: `uv sync --extra dev` before `test-summary` (test-macos job)
   - Line 206: `uv sync --extra dev` before `coverage-summary` (coverage job)

2. **`.github/workflows/release-build.yaml`**:
   - Line 148: `uv sync --extra dev` before `coverage-summary` (coverage job)
   - Line 198: `uv sync --extra dev` before `test-summary` (build-and-release job)

**Workflows without explicit sync (already correct):**
- `.github/workflows/pr-label.yml` - uses `uv run` directly
- `.github/workflows/release-version.yaml` - uses `uv run` directly
- `.github/workflows/release-build.yaml` - `release-notes` and `create-checksum` use `uv run` directly

**Script dependency analysis:**
- `test-summary`: No runtime dependencies (`dependencies = []`), dev deps only for testing
- `coverage-summary`: No runtime dependencies (`dependencies = []`), dev deps only for testing
- `pr-labels`: Runtime dependency `pygithub>=2.0.0` (auto-synced by `uv run`)
- `release-notes`: Runtime dependencies `pygithub>=2.0.0`, `packaging>=24.0` (auto-synced by `uv run`)
- `release-version`: Runtime dependencies `pygithub>=2.0.0`, `packaging>=24.0`, `tomlkit>=0.12.0` (auto-synced by `uv run`)
- `create-checksum`: No runtime dependencies (`dependencies = []`)

## Proposed Behavior

Remove all explicit `uv sync` and `uv sync --extra dev` commands from workflows. The `uv run` command will automatically:
- Detect and install the correct Python version (from `.python-version` files)
- Sync runtime dependencies (from `pyproject.toml` `dependencies`)
- Execute the script

**Changes required:**

1. **`.github/workflows/pull_request.yaml`**:
   - Remove `uv sync --extra dev` from test-summary steps (lines 80, 125)
   - Remove `uv sync --extra dev` from coverage-summary step (line 206)

2. **`.github/workflows/release-build.yaml`**:
   - Remove `uv sync --extra dev` from coverage-summary step (line 148)
   - Remove `uv sync --extra dev` from test-summary step (line 198)

**No changes needed:**
- Scripts that already use `uv run` directly (pr-labels, release-version, release-notes, create-checksum)

## Use Cases
- Workflow execution: Scripts continue to run correctly with automatic dependency syncing
- CI/CD efficiency: Reduced workflow execution time by eliminating redundant sync operations
- Maintenance: Simpler workflow files that follow `uv` best practices

## Implementation Considerations
- **Verification**: Test all affected workflows to ensure scripts run correctly after removing `uv sync`
- **Python version**: `uv run` will automatically detect Python 3.13 from `.python-version` files
- **Dependency resolution**: `uv run` handles dependency resolution automatically
- **Dev dependencies**: Scripts don't require dev dependencies at runtime (only for testing), so `--extra dev` is unnecessary

## Alternatives Considered
- **Keep `uv sync --extra dev` for consistency**: Rejected - adds unnecessary overhead and doesn't follow `uv` best practices
- **Use `uv run --extra dev` instead**: Rejected - scripts don't need dev dependencies at runtime, only for testing
- **Keep sync for scripts with runtime dependencies**: Rejected - `uv run` automatically syncs runtime dependencies

## Impact
- **Breaking Changes**: No - workflows will continue to function identically
- **Documentation**: No documentation updates required
- **Testing**:
  - Verify all affected workflows run successfully
  - Test PR workflow (test-ubuntu, test-macos, coverage jobs)
  - Test release-build workflow (coverage, build-and-release jobs)
- **Dependencies**: No new dependencies required

## References
- Related to: Python 3.13 upgrade work (REQ_PYTHON_3_13_UPGRADE.md)
- External references:
  - [uv documentation on sync](https://docs.astral.sh/uv/concepts/projects/sync/)
  - [uv run command](https://docs.astral.sh/uv/commands/run/)
