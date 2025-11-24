# BUG: Release Build Workflow - Replace Shell-Based Checksum with Python Script

**Status**: ✅ Complete

## Description

The `release-build.yaml` workflow uses shell commands (`sha256sum` on Linux, `shasum` on macOS) to create checksums, which requires OS-specific conditional logic. This can be replaced with a Python script using `hashlib`, which is cross-platform, more maintainable, and Python is already available in GitHub Actions runners.

## Current State

**File**: `.github/workflows/release-build.yaml` (lines 147-156)

The current checksum creation step:
```yaml
- name: Create checksum
  shell: bash
  run: |
    cd target/${{ matrix.target }}/release
    if command -v sha256sum >/dev/null 2>&1; then
      sha256sum move_maker > move_maker.sha256
    else
      shasum -a 256 move_maker > move_maker.sha256
    fi
    cat move_maker.sha256
```

### Issues with Current Approach

1. **OS-specific logic**: Requires conditional check for `sha256sum` vs `shasum`
2. **Maintenance burden**: Different commands for different operating systems
3. **Error handling**: Limited error handling capabilities
4. **Consistency**: Output format may vary slightly between tools
5. **Portability**: Less portable across different environments

## Expected State

Replace the shell-based checksum creation with a Python script using `hashlib`:

```yaml
- name: Create checksum
  run: |
    python3 .github/scripts/create-checksum.py \
      target/${{ matrix.target }}/release/move_maker \
      target/${{ matrix.target }}/release/move_maker.sha256
```

## Impact

### Code Quality Impact
- **Severity**: Low-Medium
- **Priority**: Low-Medium

- **Better maintainability**: Single implementation instead of OS-specific conditionals
- **Better error handling**: Python provides better error handling and validation
- **Consistency**: Same output format across all platforms
- **Portability**: Works identically on all operating systems

### Developer Experience Impact
- **Severity**: Low
- **Priority**: Low

- **Easier to test**: Python script can be tested independently
- **Easier to extend**: Can add features like verification, multiple hash algorithms, etc.
- **Better documentation**: Python code is self-documenting


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_BUILD_CHECKSUM_PYTHON_SCRIPT.md` for the detailed implementation plan.
