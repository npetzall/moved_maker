# Bug: Release Build - Cross-compilation linker error for aarch64-unknown-linux-gnu

## Description

When building `aarch64-unknown-linux-gnu` target on `ubuntu-latest` (which is an amd64 system), the build fails with a linker error:

```
def781bcbbdf5035.move_maker.f071bcf1fe204851-cgu.00.rcgu.o: error adding symbols: file in wrong format
collect2: error: ld returned 1 exit status
```

This occurs because we're attempting to cross-compile using `cargo` directly, which may be using the wrong linker for the target architecture.

## Current State

**File**: `.github/workflows/release-build.yaml`

**Line 156**: The build step uses `cargo` directly:
```yaml
- name: Build release binary with embedded dependency info
  run: cargo auditable build --release --target ${{ matrix.target }}
```

When `matrix.target` is `aarch64-unknown-linux-gnu` and the runner is `ubuntu-latest` (amd64), this causes a linker mismatch.

## Root Cause

Cross-compilation from amd64 to aarch64 requires:
1. The correct cross-compilation toolchain
2. The correct linker for the target architecture
3. Properly configured environment

Using `cargo` directly may not handle the cross-compilation setup correctly, especially for the linker configuration.

## Expected State

Use `cross` tool for cross-compilation instead of `cargo` directly. The `cross` tool handles cross-compilation setup automatically, including:
- Installing the correct toolchain
- Configuring the correct linker
- Setting up the build environment

## Impact

- **Severity**: High (builds fail for aarch64-unknown-linux-gnu target)
- **Priority**: High (blocks releases for ARM64 Linux)

## Affected Files

- `.github/workflows/release-build.yaml`
  - Line 119-123: Rust installation with target
  - Line 155-156: Build step using `cargo auditable build`

## Solution

### Option 1: Use `cross` tool (Recommended)

1. Install `cross` before building:
   ```yaml
   - name: Install cross
     run: cargo install cross --locked
   ```

2. Replace `cargo auditable build` with `cross build`:
   ```yaml
   - name: Build release binary with embedded dependency info
     run: cross build --release --target ${{ matrix.target }}
   ```

   **Note**: This approach may require additional setup for `cargo-auditable` integration with `cross`.

### Option 2: Use `cross` with `cargo auditable` (If auditable is required)

If `cargo-auditable` must be used, we may need to:
1. Use `cross` for the build environment
2. Configure `cross` to use `cargo-auditable` as the build command
3. Or use `cross` with custom configuration

### Option 3: Use native runners (Alternative)

Use native ARM64 runners for aarch64 builds instead of cross-compilation:
- GitHub Actions now supports `ubuntu-latest` on ARM64 runners
- Use `runs-on: ubuntu-latest-arm64` for aarch64 builds

## Implementation Plan

### Phase 1: Install cross

Add cross installation step after Rust installation:

```yaml
- name: Install cross
  run: cargo install cross --locked
```

### Phase 2: Update build command

Replace the build step:

**Before:**
```yaml
- name: Build release binary with embedded dependency info
  run: cargo auditable build --release --target ${{ matrix.target }}
```

**After (if using cross directly):**
```yaml
- name: Build release binary
  run: cross build --release --target ${{ matrix.target }}
```

**After (if auditable is required):**
```yaml
- name: Build release binary with embedded dependency info
  run: cross build --release --target ${{ matrix.target }} --features auditable
```

Or investigate if `cargo-auditable` can work with `cross`.

### Phase 3: Update test command

If using `cross`, tests may also need to use `cross`:

**Before:**
```yaml
- name: Run tests
  run: cargo nextest run
```

**After:**
```yaml
- name: Run tests
  run: cross nextest run --target ${{ matrix.target }}
```

**Note**: Only apply cross-compilation for non-native targets. For native targets (e.g., x86_64-unknown-linux-gnu on ubuntu-latest), continue using `cargo` directly.

## Conditional Logic

Consider using conditional logic to only use `cross` for cross-compilation targets:

```yaml
- name: Build release binary with embedded dependency info
  run: |
    if [ "${{ matrix.target }}" != "x86_64-unknown-linux-gnu" ] && [ "${{ matrix.os }}" == "ubuntu-latest" ]; then
      cross build --release --target ${{ matrix.target }}
    else
      cargo auditable build --release --target ${{ matrix.target }}
    fi
```

## References

- [cross GitHub Repository](https://github.com/cross-rs/cross)
- [cross Documentation](https://github.com/cross-rs/cross#readme)
- [Rust Cross-compilation Guide](https://rust-lang.github.io/rustup/cross-compilation.html)

## Investigation Notes

- The error "file in wrong format" typically indicates an architecture mismatch
- `cross` is specifically designed to handle cross-compilation setup
- Alternative: Use native ARM64 runners if available
- Need to verify `cargo-auditable` compatibility with `cross`

## Status

🔴 **OPEN** - Build fails for aarch64-unknown-linux-gnu target
