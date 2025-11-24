# BUG: Cache build step fails due to sparse checkout

**Status**: 📋 Planned

## Overview
The cache build workflow fails because it uses sparse checkout, which causes issues with the rust-cache action. The workflow should use a normal checkout without history (fetch-depth: 1) instead.

## Environment
- **OS**: All (GitHub Actions runners)
- **Rust Version**: 1.90.0
- **Tool Version**: N/A (GitHub Actions workflow issue)
- **Terraform Version**: N/A

## Steps to Reproduce
1. Push a commit to the `main` branch
2. The `cache-build` workflow triggers automatically
3. The workflow fails during the cache build step

## Expected Behavior
The cache build workflow should successfully:
- Checkout the repository with a normal checkout (no sparse checkout)
- Use `fetch-depth: 1` to avoid fetching full git history (optimization)
- Successfully run rust-cache and install all cargo tools
- Populate the cache for other workflows to use

## Actual Behavior
The workflow fails when using sparse checkout, preventing the cache from being built and populated.

## Error Messages / Output
```
[Error details from workflow runs - to be filled in when available]
```

## Minimal Reproduction Case
The issue is in `.github/workflows/cache-build.yaml` at lines 15-23:

```yaml
- name: Checkout code
  uses: actions/checkout@93cb6efe18208431cddfb8368fd83d5badbf9bfd  # v5.0.1
  with:
    # Sparse checkout: Only fetch Cargo.toml and Cargo.lock
    # Optimization: Reduces checkout time and bandwidth since we only need
    # these files for cargo fetch and tool installation
    sparse-checkout: |
      Cargo.toml
      Cargo.lock
```

## Additional Context
- The sparse checkout was added as an optimization to reduce checkout time and bandwidth
- However, sparse checkout appears to be incompatible with or causes issues for the rust-cache action
- The solution is to use a normal checkout with `fetch-depth: 1` to avoid fetching full git history while still providing a complete checkout
- This maintains the optimization goal (reducing bandwidth/time) while ensuring compatibility with rust-cache
- Frequency: Always (whenever the cache-build workflow runs)

## Related Issues
- Related issues: N/A
- Related PRs: N/A
