# Implementation Plan: GitHub Actions Rust Cache Shared Key

## Overview

Implement efficient Rust/Cargo cache configuration using `shared-key` to enable cache sharing across jobs and branches. Create a cache building workflow on main that pre-populates the cache with all dependencies and tools, allowing feature branches to restore from main's cache.

## Goals

- Enable cache sharing across jobs in the same workflow
- Allow feature branches to restore from main's dependency cache
- Reduce duplicate cache entries and storage usage
- Faster CI runs by avoiding redundant dependency downloads
- Pre-install all cargo tools in main's cache

## Target State

**Cache Building Workflow:**
- Runs on every push to `main`
- Installs all Rust components (clippy, rustfmt, llvm-tools-preview)
- Installs all cargo tools used across workflows
- Uses `shared-key: "rust-cache"` and `cache-targets: false`

**All Other Workflows:**
- Use `shared-key: "rust-cache"` consistently across all jobs
- Feature branches can restore from main's cache automatically
- Feature branches can use `cache-targets: true` for build artifacts
- Default branch uses `cache-targets: false` to keep cache size small

---

## Phase 1: Create Cache Building Workflow

### 1.1 Create cache-build.yaml workflow file

**File**: `.github/workflows/cache-build.yaml`

**Task**: Create a new workflow file that builds and populates the cache on every push to main

- [ ] Create `.github/workflows/cache-build.yaml`
- [ ] Add workflow name: `Cache Build`
- [ ] Configure trigger: `on.push.branches: [main]`
- [ ] Create `build-cache` job with matrix strategy for `ubuntu-latest` and `macos-latest`
- [ ] Add checkout step using `actions/checkout@93cb6efe18208431cddfb8368fd83d5badbf9bfd` (v5.0.1)
- [ ] Add Python setup step using `actions/setup-python@e797f83bcb11b83ae66e0230d6156d7c80228e7c` (v6.0.0) with Python 3.11
- [ ] Add Rust installation step using `dtolnay/rust-toolchain@0f44b27771c32bda9f458f75a1e241b09791b331` (master) with:
  - toolchain: 1.90.0
  - components: clippy rustfmt llvm-tools-preview
- [ ] Add rust-cache step using `Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1` (v2.8.1) with:
  - shared-key: "rust-cache"
  - cache-targets: false
- [ ] Add step to install security tools: `cargo install cargo-deny cargo-audit cargo-auditable`
- [ ] Add step to install cargo-geiger: `cargo install --locked cargo-geiger`
- [ ] Add step to install cargo-nextest: `cargo install cargo-nextest`
- [ ] Add step to install cargo-llvm-cov: `cargo install cargo-llvm-cov`
- [ ] Add step to install pre-commit: `pip install pre-commit`
- [ ] Add step to fetch dependencies: `cargo fetch`
- [ ] Verify YAML syntax is correct
- [ ] Verify all action versions match those used in other workflows

**Expected result:**
```yaml
name: Cache Build

on:
  push:
    branches:
      - main

jobs:
  build-cache:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
    steps:
      - name: Checkout code
        uses: actions/checkout@93cb6efe18208431cddfb8368fd83d5badbf9bfd  # v5.0.1

      - name: Setup Python
        uses: actions/setup-python@e797f83bcb11b83ae66e0230d6156d7c80228e7c  # v6.0.0
        with:
          python-version: '3.11'

      - name: Install Rust
        uses: dtolnay/rust-toolchain@0f44b27771c32bda9f458f75a1e241b09791b331  # master
        with:
          toolchain: 1.90.0
          components: clippy rustfmt llvm-tools-preview

      - uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
        with:
          shared-key: "rust-cache"
          cache-targets: false

      - name: Install security tools
        run: cargo install cargo-deny cargo-audit cargo-auditable

      - name: Install cargo-geiger
        run: cargo install --locked cargo-geiger

      - name: Install cargo-nextest
        run: cargo install cargo-nextest

      - name: Install cargo-llvm-cov
        run: cargo install cargo-llvm-cov

      - name: Install pre-commit
        run: pip install pre-commit

      - name: Fetch dependencies
        run: cargo fetch
```

---

## Phase 2: Update Pull Request Workflow

### 2.1 Update security job

**File**: `.github/workflows/pull_request.yaml`

**Location**: Line 19

**Task**: Add `shared-key: "rust-cache"` to the rust-cache step in the security job

- [ ] Open `.github/workflows/pull_request.yaml`
- [ ] Locate the rust-cache step in the `security` job (line 19)
- [ ] Add `with:` section if not present
- [ ] Add `shared-key: "rust-cache"` parameter
- [ ] Verify indentation matches other steps
- [ ] Verify the step now looks like:
  ```yaml
  - uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
    with:
      shared-key: "rust-cache"
  ```

### 2.2 Update test job

**File**: `.github/workflows/pull_request.yaml`

**Location**: Line 62

**Task**: Add `shared-key: "rust-cache"` and `cache-targets: true` to the rust-cache step in the test job

- [ ] Locate the rust-cache step in the `test` job (line 62)
- [ ] Update the `with:` section to include:
  - `shared-key: "rust-cache"`
  - `cache-targets: true`
  - Keep existing `cache-on-failure: false`
- [ ] Verify indentation matches other steps
- [ ] Verify the step now looks like:
  ```yaml
  - uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
    with:
      shared-key: "rust-cache"
      cache-targets: true
      cache-on-failure: false
  ```

### 2.3 Update coverage job

**File**: `.github/workflows/pull_request.yaml`

**Location**: Line 92

**Task**: Add `shared-key: "rust-cache"` and `cache-targets: true` to the rust-cache step in the coverage job

- [ ] Locate the rust-cache step in the `coverage` job (line 92)
- [ ] Update the `with:` section to include:
  - `shared-key: "rust-cache"`
  - `cache-targets: true`
  - Keep existing `cache-on-failure: false`
- [ ] Verify indentation matches other steps
- [ ] Verify the step now looks like:
  ```yaml
  - uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
    with:
      shared-key: "rust-cache"
      cache-targets: true
      cache-on-failure: false
  ```

### 2.4 Update pre-commit job

**File**: `.github/workflows/pull_request.yaml`

**Location**: Line 138

**Task**: Add `shared-key: "rust-cache"` and `cache-targets: true` to the rust-cache step in the pre-commit job

- [ ] Locate the rust-cache step in the `pre-commit` job (line 138)
- [ ] Add `with:` section with:
  - `shared-key: "rust-cache"`
  - `cache-targets: true`
- [ ] Verify indentation matches other steps
- [ ] Verify the step now looks like:
  ```yaml
  - uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
    with:
      shared-key: "rust-cache"
      cache-targets: true
  ```

---

## Phase 3: Update Release Build Workflow

### 3.1 Update security job

**File**: `.github/workflows/release-build.yaml`

**Location**: Line 22

**Task**: Add `shared-key: "rust-cache"` to the rust-cache step in the security job

- [ ] Open `.github/workflows/release-build.yaml`
- [ ] Locate the rust-cache step in the `security` job (line 22)
- [ ] Add `with:` section if not present
- [ ] Add `shared-key: "rust-cache"` parameter
- [ ] Verify indentation matches other steps
- [ ] Verify the step now looks like:
  ```yaml
  - uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
    with:
      shared-key: "rust-cache"
  ```

### 3.2 Update coverage job

**File**: `.github/workflows/release-build.yaml`

**Location**: Line 64

**Task**: Add `shared-key: "rust-cache"` and `cache-targets: true` to the rust-cache step in the coverage job

- [ ] Locate the rust-cache step in the `coverage` job (line 64)
- [ ] Update the `with:` section to include:
  - `shared-key: "rust-cache"`
  - `cache-targets: true`
  - Keep existing `cache-on-failure: false`
- [ ] Verify indentation matches other steps
- [ ] Verify the step now looks like:
  ```yaml
  - uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
    with:
      shared-key: "rust-cache"
      cache-targets: true
      cache-on-failure: false
  ```

### 3.3 Update build-and-release job

**File**: `.github/workflows/release-build.yaml`

**Location**: Line 125

**Task**: Add `shared-key: "rust-cache"` to the rust-cache step in the build-and-release job

- [ ] Locate the rust-cache step in the `build-and-release` job (line 125)
- [ ] Update the `with:` section to include:
  - `shared-key: "rust-cache"`
  - Keep existing `cache-targets: true`
  - Keep existing `cache-on-failure: false`
- [ ] Verify indentation matches other steps
- [ ] Verify the step now looks like:
  ```yaml
  - uses: Swatinem/rust-cache@f13886b937689c021905a6b90929199931d60db1  # v2.8.1
    with:
      shared-key: "rust-cache"
      cache-targets: true
      cache-on-failure: false
  ```

---

## Phase 4: Verification

### 4.1 Verify cache building workflow

- [ ] Push changes to main branch
- [ ] Verify the cache-build workflow runs successfully
- [ ] Check that cache is created for both ubuntu-latest and macos-latest
- [ ] Verify cache contains dependencies and installed tools
- [ ] Check cache size is reasonable (should be smaller without targets)

### 4.2 Verify pull request workflow

- [ ] Create a test pull request from a feature branch
- [ ] Verify all jobs in pull_request.yaml run successfully
- [ ] Check that jobs restore cache from main (look for cache hit messages)
- [ ] Verify jobs complete faster than before (due to cache hits)
- [ ] Verify test, coverage, and pre-commit jobs cache targets (cache-targets: true)
- [ ] Verify security job does not cache targets (no cache-targets specified, defaults to false)

### 4.3 Verify release build workflow

- [ ] Create a test tag (or use existing tag workflow)
- [ ] Verify all jobs in release-build.yaml run successfully
- [ ] Note: Tag builds won't restore from main's cache (expected behavior)
- [ ] Verify jobs still work correctly with shared-key configuration

### 4.4 Monitor cache usage

- [ ] Check GitHub Actions cache usage in repository settings
- [ ] Verify cache entries are being created with "rust-cache" in the key
- [ ] Verify cache entries are scoped correctly (main vs feature branches)
- [ ] Monitor cache size to ensure it stays within GitHub's 10 GB limit

---

## Notes

**Cache Key Structure:**
- Format: `{shared-key}-{rust-version}-{os}-{cargo-lock-hash}`
- `cache-targets` does NOT affect the cache key, only what paths are cached

**GitHub Actions Cache Scoping:**
- Caches are scoped per branch
- Caches from the default branch (main) are accessible to other branches
- When a feature branch uses the same `shared-key` as main, it can restore main's cache
- When a feature branch saves a cache, it's scoped to that branch (doesn't overwrite main's cache)

**Benefits:**
- Feature branches start with main's dependency cache, avoiding re-downloads
- All cargo tools are pre-installed in main's cache
- Jobs in the same workflow share cache, reducing duplicate downloads
- Default branch cache is smaller (cache-targets: false)
- Feature branches can cache targets for faster iteration (cache-targets: true)
