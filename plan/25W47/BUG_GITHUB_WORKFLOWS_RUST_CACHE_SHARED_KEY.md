# Bug: GitHub Actions workflows - Inefficient Rust cache configuration

## Description

The Rust/Cargo cache configuration in GitHub Actions workflows is inefficient because each job uses separate cache keys, preventing cache sharing across jobs. This leads to:
- Duplicate cache entries
- Increased cache storage usage
- Slower CI runs when jobs could benefit from shared cache
- Higher cache eviction risk

## Current State

**Files**:
- `.github/workflows/pull_request.yaml`
- `.github/workflows/release-build.yaml`

All jobs use `Swatinem/rust-cache@v2` without a `shared-key` parameter:

```yaml
- uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
  with:
    cache-targets: true  # (only in build-and-release job)
    cache-on-failure: false  # (in some jobs)
```

## Root Cause

The `rust-cache` action generates cache keys based on:
- `shared-key` (if provided, otherwise uses a job-specific key)
- Rust version
- OS
- `Cargo.lock` hash

**Note**: `cache-targets` does NOT affect the cache key - it only controls which paths are cached (dependencies vs dependencies + targets).

Without a `shared-key`, each job creates its own cache entry even when they could share the same dependencies. This is inefficient because:
1. Multiple jobs in the same workflow use the same Rust version and `Cargo.lock`
2. They could share dependency caches (`~/.cargo/registry`, `~/.cargo/git`, installed cargo tools)
3. Without `shared-key`, each job generates a unique cache key, preventing cache sharing
4. This leads to duplicate dependency downloads and tool installations across jobs

## Expected State

Use `shared-key` parameter to enable cache sharing across jobs:

```yaml
- uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
  with:
    shared-key: "rust-cache-${{ github.ref }}"
    cache-targets: true  # (where applicable)
    cache-on-failure: false  # (where applicable)
```

## Impact

- **Severity**: Medium (performance and efficiency issue)
- **Priority**: Medium (improves CI efficiency and reduces cache usage)

**Without shared keys:**
- Each job creates separate cache entries
- Dependencies are cached multiple times (once per job)
- Build artifacts are not shared between jobs
- Increased cache storage usage (approaching 10 GB limit faster)
- Slower CI runs (jobs can't benefit from cache populated by other jobs)

**With shared keys:**
- Jobs share dependency caches
- Build artifacts can be shared for the same target
- Reduced cache storage usage
- Faster CI runs (jobs benefit from cache populated by earlier jobs)

## Affected Files

### New File: `.github/workflows/cache-build.yaml`

- New workflow that runs on push to main
- Installs all Rust components and cargo tools
- Populates cache for feature branches to restore from

### `.github/workflows/pull_request.yaml`

- `security` job (line 19)
- `test` job (line 62)
- `coverage` job (line 92)
- `pre-commit` job (line 138)

### `.github/workflows/release-build.yaml`

- `security` job (line 22)
- `coverage` job (line 64)
- `build-and-release` job (line 125)

## Solution

Implement a cache building workflow on the default branch (main) and use a consistent `shared-key` across all workflows to enable cache sharing.

### Cache Strategy

**Key Insight**: GitHub Actions caches are scoped per branch, but caches from the default branch (main) are accessible to other branches. This allows:
- Default branch creates a cache with `shared-key: "rust-cache"` (scoped to main)
- Feature branches can restore from main's cache using the same `shared-key: "rust-cache"`
- Feature branches save their own cache (scoped to their branch) using the same shared-key

**Cache Building Workflow**:
- Runs on `push` to `main` branch
- Installs all Rust components (clippy, rustfmt, llvm-tools-preview)
- Installs all cargo tools used across workflows
- Uses `shared-key: "rust-cache"` and `cache-targets: false` (dependencies only)
- Populates cache that feature branches can restore from

**All Other Workflows**:
- Use `shared-key: "rust-cache"` consistently across all jobs
- Feature branches restore from main's cache automatically
- Feature branches can use `cache-targets: true` for build artifacts
- Default branch uses `cache-targets: false` to keep cache size small

## Implementation Plan

See `work/25W47/GITHUB_WORKFLOWS_RUST_CACHE_SHARED_KEY.md` for the detailed implementation plan with step-by-step tasks.

## Example Fix

### Before (test job):
```yaml
- uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
  with:
    cache-on-failure: false
```

### After (test job):
```yaml
- uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
  with:
    shared-key: "rust-cache"
    cache-targets: true
    cache-on-failure: false
```

## How Shared Keys Work

According to the `rust-cache` documentation, the `shared-key` parameter:
- Creates a base cache key that is shared across all jobs using the same `shared-key`
- Jobs can restore and save to the same cache entry
- The final cache key is: `{shared-key}-{rust-version}-{os}-{cargo-lock-hash}`
- Note: `cache-targets` does NOT affect the cache key, only what paths are cached

**GitHub Actions Cache Scoping**:
- Caches are scoped per branch
- Caches from the default branch (main) are accessible to other branches
- When a feature branch uses the same `shared-key` as main, it can restore main's cache
- When a feature branch saves a cache, it's scoped to that branch (doesn't overwrite main's cache)

## Benefits

1. **Faster CI runs**:
   - Jobs later in the workflow benefit from cache populated by earlier jobs
   - Feature branches start with main's dependency cache, avoiding re-downloads
2. **Reduced cache storage**:
   - Dependencies are cached once per branch instead of once per job
   - Default branch cache is smaller (no targets)
3. **Better cache hit rates**:
   - More likely to have cache hits when dependencies haven't changed
   - Feature branches benefit from main's pre-populated cache
4. **Lower CI costs**:
   - Faster builds = fewer CI minutes consumed
   - Less time spent downloading dependencies
5. **Pre-installed tools**:
   - All cargo tools are pre-installed in main's cache
   - Feature branches don't need to install tools from scratch

## Considerations

- **Cache scoping**: Caches are scoped per branch, but main's cache is accessible to feature branches
- **Cache conflicts**: Multiple jobs writing to the same cache is safe (GitHub Actions handles this)
- **Cache size**:
  - Default branch cache is smaller (cache-targets: false)
  - Feature branches can cache targets for faster iteration
- **Workflow dependencies**: Jobs that depend on each other (via `needs:`) will naturally benefit from shared cache
- **Cache building workflow**: Runs on every push to main, ensuring cache is always up-to-date
- **Tag builds**: Tag builds won't benefit from main's cache (tags don't have access to branch caches), but this is expected for release builds

## References

- [rust-cache GitHub Repository](https://github.com/Swatinem/rust-cache)
- [rust-cache shared-key documentation](https://github.com/Swatinem/rust-cache#shared-key)

## Status

🔴 **OPEN** - Cache configuration is inefficient, should use shared keys
