# REQ: Pre-commit Caching in GitHub Actions

**Status**: 📋 Planned

## Overview
Add caching for pre-commit and its hook environments in GitHub Actions workflows to reduce CI execution time and bandwidth usage by 15-35 seconds per workflow run.

## Motivation
Currently, pre-commit is installed fresh on every workflow run, and hook environments are downloaded each time, adding 15-40+ seconds of overhead per CI execution. This wastes GitHub Actions minutes, increases bandwidth usage, and slows down the development feedback loop. While Rust/Cargo caching is already implemented via `rust-cache`, Python packages and pre-commit hook environments are not cached, creating an inconsistency in our caching strategy.

## Current Behavior

### Workflow Configuration
- **File**: `.github/workflows/pull_request.yaml`
- **Job**: `pre-commit` (lines 127-156)
- **Python Setup**: Uses `actions/setup-python@v6.0.0` without pip caching
- **Pre-commit Installation**: `pip install pre-commit` runs on every workflow execution (~5-10 seconds)
- **Hook Environments**: Pre-commit downloads hook environments to `~/.cache/pre-commit` on every run (~10-30+ seconds)
- **No Caching**: No caching mechanism in place for Python packages or pre-commit environments

### Performance Impact
- Pre-commit package is downloaded and installed on every run: ~5-10 seconds
- Hook environments are downloaded for each hook on every run: ~10-30+ seconds (varies by hook)
- Total overhead per workflow run: ~15-40+ seconds

### Related Context
- `rust-cache` action is used for Rust/Cargo caching but doesn't cache Python packages
- Comment in `cache-build.yaml` (line 48-50) notes that pre-commit is not cached because rust-cache doesn't handle Python packages

## Proposed Behavior

Implement two-level caching for pre-commit:

1. **Pip package caching**: Enable pip caching via `actions/setup-python` to cache the pre-commit Python package installation
2. **Pre-commit environment caching**: Cache hook environments downloaded by pre-commit using `actions/cache@v4`

### Expected Performance Improvements

**Without Caching**:
- Pre-commit installation: ~5-10 seconds
- Hook environment downloads: ~10-30+ seconds (varies by hook)
- Total overhead: ~15-40+ seconds per run

**With Caching**:
- Pre-commit installation: ~0-2 seconds (cache hit)
- Hook environment downloads: ~0-5 seconds (cache hit)
- Total overhead: ~0-7 seconds per run

**Estimated time savings**: 15-35 seconds per workflow run

## Use Cases
- Reduce CI execution time for pull request workflows
- Lower bandwidth usage by avoiding re-downloading packages and hook environments
- Improve developer experience with faster feedback on code changes
- Reduce GitHub Actions minutes consumption
- Maintain consistency with existing Rust/Cargo caching strategy

## Implementation Considerations

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

### Implementation Approach

**Recommended: Combined Approach (Option 3)**

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

This provides:
- Fast pre-commit package installation (via pip cache)
- Fast hook environment downloads (via pre-commit cache)
- Automatic cache invalidation when hooks change
- Minimal workflow changes

## Alternatives Considered

### Option 1: Use setup-python Built-in Caching Only
- **Approach**: Add `cache: 'pip'` to Python setup step
- **Why rejected**: While simple, this only caches the pre-commit package, not the hook environments which take longer to download

### Option 2: Cache Pre-commit Hook Environments Only
- **Approach**: Cache `~/.cache/pre-commit` directory using `actions/cache@v4`
- **Why rejected**: This misses the opportunity to also cache the pre-commit package installation, which adds 5-10 seconds per run

### Option 3: Combined Approach (Selected)
- **Approach**: Use both pip caching and pre-commit environment caching
- **Why selected**: Provides maximum efficiency by caching both the package installation and hook environments, reducing total overhead from 15-40+ seconds to 0-7 seconds

## Impact
- **Breaking Changes**: No - this is a performance optimization that doesn't change functionality
- **Documentation**: No documentation updates required - this is an internal CI/CD improvement
- **Testing**: Verify cache hits/misses in workflow runs, monitor cache effectiveness over time
- **Dependencies**: No new dependencies required - uses existing `actions/setup-python@v6.0.0` and `actions/cache@v4`

### Additional Considerations
- **Cache Storage**: Uses GitHub Actions cache storage (10 GB limit per repository)
- **Initial Cache Miss**: First run after changes will still be slow until cache is populated
- **Cache Key Management**: Cache keys are designed to automatically invalidate when hooks change

## References
- [GitHub Actions: Caching dependencies](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [actions/setup-python: Caching packages](https://github.com/actions/setup-python#caching-packages)
- [actions/cache: Documentation](https://github.com/actions/cache)
- [Pre-commit: Caching](https://pre-commit.com/#usage)
- Related: Rust/Cargo caching (existing via `rust-cache` action)
- Related: Comment in `cache-build.yaml` (line 48-50) noting pre-commit is not cached
