# BUG: GitHub Actions workflows missing Rust/Cargo caching

**Status**: ✅ Complete

## Description

No Rust/Cargo caching is implemented in any workflow, leading to slower CI runs, unnecessary network traffic, higher CI costs, and slower feedback loops.

## Current State

✅ **FIXED** - Rust/Cargo caching is now implemented in all workflows using `Swatinem/rust-cache@v2`.

Previously, no Rust/Cargo caching was implemented in any workflow, which caused:
- Slower CI runs
- Unnecessary network traffic
- Higher CI costs
- Slower feedback loops

## Expected State

Add caching after Rust installation using `Swatinem/rust-cache@v2`:

```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    components: clippy rustfmt

- uses: Swatinem/rust-cache@v2
```

**Reference:** https://github.com/Swatinem/rust-cache

## Impact

### Performance Impact
- **Severity**: Medium
- **Priority**: Medium

Without caching:
- CI runs are significantly slower
- Dependencies are downloaded and compiled on every run
- Increased CI minutes consumption

## Steps to Fix

Add caching step after Rust installation in all jobs that build/test:

```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    components: clippy rustfmt

- uses: Swatinem/rust-cache@v2
```

**Note:** The cache action should be placed after Rust installation but before any cargo commands.

## Affected Files

- `.github/workflows/pull_request.yaml`
  - `security` job (after line 17)
  - `test` job (after line 48)
  - `coverage` job (after line 76)
  - `pre-commit` job (after line 144)

- `.github/workflows/release.yaml`
  - `security` job (after line 18)
  - `build-and-release` job (after line 170)

## Example Fix

### Before (test job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    components: clippy rustfmt

- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

### After (test job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    components: clippy rustfmt

- uses: Swatinem/rust-cache@v2

- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

### Before (security job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0

- name: Install security tools
  run: cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable
```

### After (security job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0

- uses: Swatinem/rust-cache@v2

- name: Install security tools
  run: cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable
```

### Before (build-and-release job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    targets: ${{ matrix.target }}

- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

### After (build-and-release job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    targets: ${{ matrix.target }}

- uses: Swatinem/rust-cache@v2

- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

## References

- [rust-cache GitHub Action](https://github.com/Swatinem/rust-cache)

## Investigation

### rust-cache Action Overview

The `Swatinem/rust-cache@v2` action provides intelligent caching for Rust projects with sensible defaults. It automatically:
- Caches `~/.cargo/registry` (downloaded crates)
- Caches `~/.cargo/git` (git dependencies)
- Caches `target` directory (build artifacts)
- Generates cache keys based on Rust version, OS, and `Cargo.lock` hash

### Configuration Options

The action supports several optional parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prefix-key` | string | `""` | Custom prefix for cache keys (useful for separating caches by job type) |
| `cache-targets` | boolean | `false` | Cache target directories (useful for cross-compilation) |
| `cache-on-failure` | boolean | `true` | Save cache even if workflow fails |
| `cache-all-crates` | boolean | `false` | Cache all crates in workspace |
| `cache-workspace-crates` | boolean | `false` | Cache workspace crates |
| `save-if` | string | `"true"` | Condition for saving cache (e.g., `"${{ job.status == 'success' }}"`) |
| `lookup-only` | boolean | `false` | Only restore cache, don't save |
| `cache-provider` | string | `"github"` | Cache provider (`github`, `s3`, `gcs`, `azure`) |
| `cache-bin` | boolean | `true` | Cache Cargo binaries |

### Recommended Configuration

#### Basic Configuration (Most Jobs)

For most jobs (test, security, coverage, pre-commit), the default configuration is sufficient:

```yaml
- uses: Swatinem/rust-cache@v2
```

**Rationale:**
- Defaults handle dependency caching effectively
- Cache keys automatically include Rust version and `Cargo.lock` hash
- No need to cache on failure for most jobs (prevents caching broken builds)

#### Optimized Configuration (Test/Coverage Jobs)

For test and coverage jobs, consider disabling cache-on-failure to avoid caching broken builds:

```yaml
- uses: Swatinem/rust-cache@v2
  with:
    cache-on-failure: false
```

**Rationale:**
- Prevents caching artifacts from failed test runs
- Keeps cache clean and ensures only successful builds are cached

#### Cross-Compilation Configuration (Build-and-Release Job)

For the `build-and-release` job that uses multiple targets, enable `cache-targets`:

```yaml
- uses: Swatinem/rust-cache@v2
  with:
    cache-targets: true
    cache-on-failure: false
```

**Rationale:**
- `cache-targets: true` caches target-specific build artifacts for each cross-compilation target
- Significantly speeds up builds when switching between targets
- `cache-on-failure: false` prevents caching failed release builds

#### Optional: Job-Specific Cache Prefixes

If you want to separate caches by job type (useful for debugging or different cache strategies):

```yaml
# For security job
- uses: Swatinem/rust-cache@v2
  with:
    prefix-key: "security-"

# For test job
- uses: Swatinem/rust-cache@v2
  with:
    prefix-key: "test-"
```

**Note:** This is generally not necessary as the action already handles cache key uniqueness well.

### Cache Size Considerations

- GitHub Actions cache limit: **10 GB per repository**
- Caches are evicted after **7 days** of no access
- The action automatically manages cache size by using content-addressable keys
- Multiple targets in `build-and-release` will create separate cache entries per target

### Performance Expectations

With proper caching:
- **First run**: No cache hit, normal build time
- **Subsequent runs** (same dependencies): 50-80% faster builds
- **Dependency changes**: Partial cache hit, faster than no cache
- **Cross-compilation**: Significant speedup when switching between targets (with `cache-targets: true`)

### Implementation Recommendation

**Recommended approach:** Start with basic configuration for all jobs, then optimize based on observed performance:

1. **Phase 1**: Add basic `Swatinem/rust-cache@v2` to all jobs
2. **Phase 2**: Monitor cache hit rates and build times
3. **Phase 3**: Add `cache-targets: true` to `build-and-release` if cross-compilation is slow
4. **Phase 4**: Consider `cache-on-failure: false` for test/coverage jobs if needed

### Additional Resources

- [rust-cache GitHub Repository](https://github.com/Swatinem/rust-cache)
- [GitHub Actions Cache Documentation](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [Rust CI Best Practices](https://github.com/actions-rs/meta/blob/master/recipes/quickstart.md)

### Cargo Install Caching

**Important:** The `rust-cache` action caches `~/.cargo/bin` by default (controlled by `cache-bin: true`), which means binaries installed via `cargo install` are automatically cached. This includes:
- `cargo-nextest` (installed in test, coverage, pre-commit, and build-and-release jobs)
- `cargo-deny`, `cargo-audit`, `cargo-geiger`, `cargo-auditable` (installed in security jobs)
- `cargo-llvm-cov` (installed in coverage job)

This significantly speeds up subsequent CI runs as these tools don't need to be recompiled.


## Related Implementation Plan

See `work/25W46/BUG_GITHUB_WORKFLOWS_RUST_CACHING.md` for the detailed implementation plan.
