# Decision: Release Build - Remove Cross-compilation

## Description

When building `aarch64-unknown-linux-gnu` target on `ubuntu-latest` (which is an amd64 system), the build fails with a linker error:

```
def781bcbbdf5035.move_maker.f071bcf1fe204851-cgu.00.rcgu.o: error adding symbols: file in wrong format
collect2: error: ld returned 1 exit status
```

This occurs because we're attempting to cross-compile using `cargo` directly, which requires proper cross-compilation toolchain setup.

## Decision

**Remove cross-compilation entirely and build only native targets.**

### Rationale

1. **Cost**: macOS runner minutes are 10x more expensive than Linux runners
2. **Complexity**: Cross-compilation requires additional tooling (`cross`) and configuration
3. **Testing**: Cross-compiled binaries can't be tested natively without emulation (QEMU), which is slow
4. **Maintenance**: Native builds are simpler and more reliable

### Implementation

Simplify the build matrix to only include native targets:

**Before:**
- `x86_64-unknown-linux-gnu` on `ubuntu-latest` (native)
- `aarch64-unknown-linux-gnu` on `ubuntu-latest` (cross-compile) ❌
- `x86_64-apple-darwin` on `macos-latest` (Rosetta 2)
- `aarch64-apple-darwin` on `macos-latest` (native)

**After:**
- `x86_64-unknown-linux-gnu` on `ubuntu-latest` (native) ✅
- `aarch64-apple-darwin` on `macos-latest` (native) ✅

## Changes Required

**File**: `.github/workflows/release-build.yaml`

Update the matrix (lines 100-114) to:

```yaml
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        target: x86_64-unknown-linux-gnu
        artifact_name: move_maker-linux-x86_64
      - os: macos-latest
        target: aarch64-apple-darwin
        artifact_name: move_maker-macos-aarch64
```

## Impact

- **Builds**: Only native targets are built (Linux AMD64, macOS ARM64)
- **Cost**: Reduced macOS runner usage
- **Reliability**: No cross-compilation issues
- **Coverage**: ARM64 Linux and Intel macOS are no longer supported in releases

## Status

✅ **IMPLEMENTED** - Cross-compilation removed, only native targets built

**Implementation Date**: 2024-12-19

## Implementation

See detailed implementation plan: `work/02_W47/RELEASE_BUILD_CROSS_COMPILATION_LINKER_ERROR.md`

**Changes Made**:
- Updated `.github/workflows/release-build.yaml` matrix to remove cross-compilation targets
- Removed `aarch64-unknown-linux-gnu` (cross-compile on ubuntu-latest)
- Removed `x86_64-apple-darwin` (Rosetta 2 on macos-latest)
- Kept only native targets: `x86_64-unknown-linux-gnu` and `aarch64-apple-darwin`
