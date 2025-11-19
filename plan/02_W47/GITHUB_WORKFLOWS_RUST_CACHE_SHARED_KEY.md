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
- Rust version
- OS
- `Cargo.lock` hash
- Target (if `cache-targets: true`)

Without a `shared-key`, each job creates its own cache entry even when they could share the same dependencies and build artifacts. This is inefficient because:
1. Multiple jobs in the same workflow use the same Rust version and `Cargo.lock`
2. They could share dependency caches (`~/.cargo/registry`, `~/.cargo/git`)
3. They could share build artifacts for the same target

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

Add `shared-key` parameter to all `rust-cache` actions. The shared key should be:
- Consistent across jobs in the same workflow run
- Unique per workflow/ref to avoid conflicts
- Based on something that changes when dependencies change

### Recommended Shared Key Strategy

**Option 1: Per workflow run (Recommended)**
```yaml
shared-key: "rust-cache-${{ github.workflow }}-${{ github.run_id }}"
```

**Option 2: Per ref (branch/tag)**
```yaml
shared-key: "rust-cache-${{ github.ref }}"
```

**Option 3: Per ref and workflow**
```yaml
shared-key: "rust-cache-${{ github.workflow }}-${{ github.ref }}"
```

**Recommendation**: Use Option 2 (`github.ref`) as it:
- Shares cache across workflow runs on the same branch/tag
- Automatically invalidates when switching branches
- Simple and predictable

## Implementation Plan

### Phase 1: Update `.github/workflows/pull_request.yaml`

#### Update `security` job (line 19):
```yaml
- uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
  with:
    shared-key: "rust-cache-${{ github.ref }}"
```

#### Update `test` job (line 62):
```yaml
- uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
  with:
    shared-key: "rust-cache-${{ github.ref }}"
    cache-on-failure: false
```

#### Update `coverage` job (line 92):
```yaml
- uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
  with:
    shared-key: "rust-cache-${{ github.ref }}"
    cache-on-failure: false
```

#### Update `pre-commit` job (line 138):
```yaml
- uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
  with:
    shared-key: "rust-cache-${{ github.ref }}"
```

### Phase 2: Update `.github/workflows/release-build.yaml`

#### Update `security` job (line 22):
```yaml
- uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
  with:
    shared-key: "rust-cache-${{ github.ref }}"
```

#### Update `coverage` job (line 64):
```yaml
- uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
  with:
    shared-key: "rust-cache-${{ github.ref }}"
    cache-on-failure: false
```

#### Update `build-and-release` job (line 125):
```yaml
- uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
  with:
    shared-key: "rust-cache-${{ github.ref }}"
    cache-targets: true
    cache-on-failure: false
```

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
    shared-key: "rust-cache-${{ github.ref }}"
    cache-on-failure: false
```

## How Shared Keys Work

According to the `rust-cache` documentation, the `shared-key` parameter:
- Creates a base cache key that is shared across all jobs using the same `shared-key`
- Jobs can restore and save to the same cache entry
- The final cache key is: `{shared-key}-{rust-version}-{os}-{cargo-lock-hash}-{target?}`
- This allows sharing dependency caches while maintaining target-specific build artifact caches

## Benefits

1. **Faster CI runs**: Jobs later in the workflow benefit from cache populated by earlier jobs
2. **Reduced cache storage**: Dependencies are cached once per ref instead of once per job
3. **Better cache hit rates**: More likely to have cache hits when dependencies haven't changed
4. **Lower CI costs**: Faster builds = fewer CI minutes consumed

## Considerations

- **Cache invalidation**: Using `github.ref` means cache is shared across runs on the same branch/tag
- **Cache conflicts**: Multiple jobs writing to the same cache is safe (GitHub Actions handles this)
- **Cache size**: Shared cache may grow larger, but overall storage usage should decrease
- **Workflow dependencies**: Jobs that depend on each other (via `needs:`) will naturally benefit from shared cache

## References

- [rust-cache GitHub Repository](https://github.com/Swatinem/rust-cache)
- [rust-cache shared-key documentation](https://github.com/Swatinem/rust-cache#shared-key)

## Status

🔴 **OPEN** - Cache configuration is inefficient, should use shared keys
