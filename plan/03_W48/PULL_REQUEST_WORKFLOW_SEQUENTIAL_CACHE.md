# Optimization: Pull Request Workflow - Sequential Job Execution for Cache Efficiency

## Description

The pull request workflow currently runs all jobs in parallel. When there's no cache from main yet, all jobs try to create the cache simultaneously, causing them all to work without cache. This makes the whole process slow when there is no cache, as each job takes time separately to build dependencies and install tools.

By making jobs execute sequentially, each job can use the cache populated by the previous step, significantly improving performance when starting without cache.

## Current State

**File**: `.github/workflows/pull_request.yaml`

All jobs run in parallel with no dependencies:
- `security` - runs independently
- `test` - runs independently (matrix: ubuntu-latest, macos-latest)
- `coverage` - runs independently
- `pre-commit` - runs independently

**Problem**: When there's no cache from main:
- All jobs start simultaneously
- Each job tries to create its own cache
- All jobs download dependencies and install tools in parallel
- No job benefits from cache created by other jobs
- Slow overall execution time

## Root Cause

Without job dependencies (`needs:`), GitHub Actions runs all jobs in parallel. When multiple jobs use the same `shared-key: "rust-cache"` but start at the same time without an existing cache:
1. All jobs attempt to restore cache simultaneously
2. None find a cache (no cache exists yet)
3. All jobs proceed to download dependencies and install tools
4. All jobs save their cache simultaneously
5. No job benefits from cache created by another job

## Expected State

Jobs should execute in a sequential order where:
1. `security` runs first and populates the cache
2. `test-ubuntu` runs after `security` and uses the cache
3. `test-macos` runs after `security` (can run in parallel with `test-ubuntu`)
4. `coverage` runs after `test-ubuntu` (doesn't wait for `test-macos`)
5. `pre-commit` runs after `test-ubuntu` (doesn't wait for `test-macos`)

**Benefits**:
- First job (`security`) builds cache once
- Subsequent jobs restore from cache and benefit immediately
- Faster overall execution when starting without cache
- Better cache utilization

## Solution

### 1. Split test job into separate ubuntu and macos jobs

Split the matrix-based `test` job into two separate jobs:
- `test-ubuntu` - runs on ubuntu-latest
- `test-macos` - runs on macos-latest

This allows `coverage` and `pre-commit` to depend only on `test-ubuntu` without waiting for `test-macos`.

### 2. Add job dependencies

Add `needs:` dependencies to create execution order:
- `test-ubuntu`: `needs: security`
- `test-macos`: `needs: security` (runs in parallel with `test-ubuntu`)
- `coverage`: `needs: test-ubuntu`
- `pre-commit`: `needs: test-ubuntu`

## Implementation

### Changes to `.github/workflows/pull_request.yaml`

#### 1. Replace `test` job with `test-ubuntu` and `test-macos`

**Before** (lines 48-82):
```yaml
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
    steps:
      # ... steps ...
      - name: Upload test results
        with:
          name: test-results-${{ matrix.os }}
```

**After**:
```yaml
  test-ubuntu:
    needs: security
    runs-on: ubuntu-latest
    steps:
      # ... same steps ...
      - name: Upload test results
        with:
          name: test-results-ubuntu-latest

  test-macos:
    needs: security
    runs-on: macos-latest
    steps:
      # ... same steps ...
      - name: Upload test results
        with:
          name: test-results-macos-latest
```

#### 2. Add dependency to `coverage` job

**Before** (line 84):
```yaml
  coverage:
    runs-on: ubuntu-latest
```

**After**:
```yaml
  coverage:
    needs: test-ubuntu
    runs-on: ubuntu-latest
```

#### 3. Add dependency to `pre-commit` job

**Before** (line 127):
```yaml
  pre-commit:
    runs-on: ubuntu-latest
```

**After**:
```yaml
  pre-commit:
    needs: test-ubuntu
    runs-on: ubuntu-latest
```

## Execution Flow

### Before (Parallel):
```
security ──┐
           ├──> All run simultaneously
test ──────┤
coverage ──┤
pre-commit┘
```

### After (Sequential with Parallel Where Appropriate):
```
security
  ├──> test-ubuntu ──┬──> coverage
  │                   └──> pre-commit
  └──> test-macos (runs in parallel, independent)
```

## Impact

- **Severity**: Medium (performance optimization)
- **Priority**: Medium (improves CI efficiency when cache is missing)

**Benefits**:
1. **Faster execution when no cache exists**:
   - First job builds cache once
   - Subsequent jobs restore from cache immediately
   - Reduces redundant dependency downloads and tool installations
2. **Better cache utilization**:
   - Jobs benefit from cache populated by previous jobs
   - Reduces cache storage usage (fewer duplicate cache entries)
3. **Optimized workflow timing**:
   - `coverage` and `pre-commit` don't wait for macos tests
   - Faster feedback for ubuntu-based checks
   - Macos tests can complete independently

**Trade-offs**:
- Slightly longer total workflow time (sequential execution)
- But significantly faster when starting without cache
- Better overall efficiency due to cache reuse

## Affected Files

- `.github/workflows/pull_request.yaml`
  - Split `test` job into `test-ubuntu` and `test-macos`
  - Add `needs: security` to both test jobs
  - Add `needs: test-ubuntu` to `coverage` job
  - Add `needs: test-ubuntu` to `pre-commit` job
  - Update artifact names to use fixed names instead of `${{ matrix.os }}`

## Considerations

- **Matrix strategy**: The original `test` job used a matrix strategy. Splitting into separate jobs maintains the same functionality while allowing more granular dependencies.
- **Cache sharing**: All jobs still use `shared-key: "rust-cache"`, so cache is shared across jobs on the same OS.
- **Parallel execution**: `test-ubuntu` and `test-macos` still run in parallel after `security` completes, which is optimal.
- **Workflow timing**: `coverage` and `pre-commit` can start as soon as `test-ubuntu` completes, without waiting for `test-macos`, which is beneficial since they only run on ubuntu anyway.
- **Artifact names**: Need to update artifact names from `test-results-${{ matrix.os }}` to fixed names like `test-results-ubuntu-latest` and `test-results-macos-latest`.

## Status

🔴 **OPEN** - Sequential job execution not yet implemented
