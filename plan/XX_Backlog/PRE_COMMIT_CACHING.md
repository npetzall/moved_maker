# Pre-commit Caching in GitHub Actions

## Purpose
Add caching for pre-commit and its hook environments in GitHub Actions workflows to reduce CI execution time and bandwidth usage. Currently, pre-commit is installed fresh on every workflow run, and hook environments are downloaded each time.

## Current State

### Workflow Configuration
- **File**: `.github/workflows/pull_request.yaml`
- **Job**: `pre-commit` (lines 127-156)
- **Python Setup**: Uses `actions/setup-python@v6.0.0` without pip caching
- **Pre-commit Installation**: `pip install pre-commit` runs on every workflow execution
- **Hook Environments**: Pre-commit downloads hook environments to `~/.cache/pre-commit` on every run

### Current Performance Impact
- Pre-commit package is downloaded and installed on every run (~5-10 seconds)
- Hook environments are downloaded for each hook on every run (varies by hook, can be 10-30+ seconds)
- No caching mechanism in place for Python packages or pre-commit environments

### Related Context
- `rust-cache` action is used for Rust/Cargo caching but doesn't cache Python packages
- Comment in `cache-build.yaml` (line 48-50) notes that pre-commit is not cached because rust-cache doesn't handle Python packages

## Proposed Solution

Implement two-level caching for pre-commit:
1. **Pip package caching**: Cache the pre-commit Python package installation
2. **Pre-commit environment caching**: Cache hook environments downloaded by pre-commit

## Implementation

### Option 1: Use setup-python Built-in Caching (Recommended)

`actions/setup-python@v4+` supports built-in pip caching. This is the simplest approach:

```yaml
- name: Setup Python
  uses: actions/setup-python@e797f83bcb11b83ae66e0230d6156d7c80228e7c  # v6.0.0
  with:
    python-version: '3.11'
    cache: 'pip'  # Add this line to enable pip caching
```

**Benefits**:
- Single line change
- Automatically caches all pip packages
- No additional cache management needed
- Works seamlessly with existing setup

### Option 2: Cache Pre-commit Hook Environments

Pre-commit stores hook environments in `~/.cache/pre-commit`. Cache this directory:

```yaml
- name: Cache pre-commit environments
  uses: actions/cache@v4
  with:
    path: ~/.cache/pre-commit
    key: pre-commit-${{ runner.os }}-${{ hashFiles('.pre-commit-config.yaml') }}
    restore-keys: |
      pre-commit-${{ runner.os }}-
```

**Benefits**:
- Caches downloaded hook environments (ripsecrets, typos, git-sumi, etc.)
- Significantly reduces hook download time
- Cache key based on `.pre-commit-config.yaml` hash ensures cache invalidation when hooks change

### Option 3: Combined Approach (Most Efficient)

Use both pip caching and pre-commit environment caching:

```yaml
- name: Setup Python
  uses: actions/setup-python@e797f83bcb11b83ae66e0230d6156d7c80228e7c  # v6.0.0
  with:
    python-version: '3.11'
    cache: 'pip'  # Cache pip packages including pre-commit

- name: Cache pre-commit environments
  uses: actions/cache@v4
  with:
    path: ~/.cache/pre-commit
    key: pre-commit-${{ runner.os }}-${{ hashFiles('.pre-commit-config.yaml') }}
    restore-keys: |
      pre-commit-${{ runner.os }}-
```

## Expected Performance Improvements

### Without Caching
- Pre-commit installation: ~5-10 seconds
- Hook environment downloads: ~10-30+ seconds (varies by hook)
- Total overhead: ~15-40+ seconds per run

### With Caching
- Pre-commit installation: ~0-2 seconds (cache hit)
- Hook environment downloads: ~0-5 seconds (cache hit)
- Total overhead: ~0-7 seconds per run

**Estimated time savings**: 15-35 seconds per workflow run

## Implementation Details

### Files to Modify

1. **`.github/workflows/pull_request.yaml`**
   - Update `pre-commit` job (lines 127-156)
   - Add `cache: 'pip'` to Python setup step
   - Add pre-commit environment cache step

### Cache Key Strategy

**Pip Cache** (via setup-python):
- Automatically managed by `actions/setup-python`
- Key based on Python version and `requirements.txt` or `setup.py` if present
- Falls back to pip's dependency resolution

**Pre-commit Environment Cache**:
- Primary key: `pre-commit-${{ runner.os }}-${{ hashFiles('.pre-commit-config.yaml') }}`
  - OS-specific (different environments for different OS)
  - Hash of `.pre-commit-config.yaml` ensures cache invalidation when hooks change
- Restore key: `pre-commit-${{ runner.os }}-`
  - Allows partial cache hits across different hook configurations
  - Useful when hooks are added/removed but some remain the same

### Cache Invalidation

Caches will be invalidated when:
- `.pre-commit-config.yaml` changes (for hook environment cache)
- Python version changes (for pip cache)
- Pre-commit package version changes (for pip cache, if pinned)
- Cache expires (GitHub Actions cache retention policy)

## Pros

- **Faster CI runs**: Reduces pre-commit setup time by 15-35 seconds per run
- **Lower bandwidth usage**: Avoids re-downloading packages and hook environments
- **Consistent with existing caching strategy**: Complements Rust caching approach
- **Simple implementation**: Minimal changes required
- **Automatic cache management**: setup-python handles pip cache automatically
- **Cost effective**: Reduces GitHub Actions minutes usage

## Cons

- **Additional cache storage**: Uses GitHub Actions cache storage (10 GB limit)
- **Cache invalidation complexity**: Need to ensure caches invalidate when hooks change
- **Initial cache miss**: First run after changes will still be slow
- **Cache key management**: Need to ensure cache keys are appropriate

## Recommendation

Implement **Option 3 (Combined Approach)** for maximum efficiency:

1. Add `cache: 'pip'` to the Python setup step in `pull_request.yaml`
2. Add a pre-commit environment cache step using `actions/cache@v4`
3. Use cache key based on OS and `.pre-commit-config.yaml` hash

This provides:
- Fast pre-commit package installation (via pip cache)
- Fast hook environment downloads (via pre-commit cache)
- Automatic cache invalidation when hooks change
- Minimal workflow changes

## Implementation Priority

**Low-Medium**: Performance optimization that improves CI efficiency but doesn't affect functionality. Can be implemented alongside other workflow improvements.

## Related Features

- Rust/Cargo caching (existing via `rust-cache` action)
- GitHub Actions workflow optimization
- CI/CD performance improvements

## References

- [GitHub Actions: Caching dependencies](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [actions/setup-python: Caching packages](https://github.com/actions/setup-python#caching-packages)
- [actions/cache: Documentation](https://github.com/actions/cache)
- [Pre-commit: Caching](https://pre-commit.com/#usage)
