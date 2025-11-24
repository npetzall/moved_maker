# BUG: Dependabot configuration is missing github-actions ecosystem

**Status**: ✅ Complete

## Description

The `.github/dependabot.yml` configuration file only includes the `cargo` package ecosystem for dependency updates. It is missing the `github-actions` ecosystem, which means Dependabot will not automatically create pull requests to update GitHub Actions used in workflows when new versions are released.

## Current State

The current `.github/dependabot.yml` configuration only includes:

```yaml
version: 2
updates:
  - package-ecosystem: "cargo"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
    reviewers:
      - npetzall
    assignees:
      - npetzall
```

**Missing:** A configuration entry for the `github-actions` ecosystem.

## Expected State

The `.github/dependabot.yml` should include both `cargo` and `github-actions` ecosystems:

```yaml
version: 2
updates:
  - package-ecosystem: "cargo"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
    reviewers:
      - npetzall
    assignees:
      - npetzall
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
    reviewers:
      - npetzall
    assignees:
      - npetzall
```

## Impact

### Security Impact
- **Severity**: Medium
- **Priority**: Medium

### Why This Matters

1. **Security Updates**: GitHub Actions can have security vulnerabilities, and Dependabot helps keep them updated automatically
2. **Feature Updates**: New versions of actions may include bug fixes and new features
3. **Best Practice**: Including `github-actions` ecosystem is a recommended practice for repositories using GitHub Actions
4. **Automation**: Without this configuration, action updates must be done manually, which can be forgotten or delayed

### Current Workflow Actions

The repository uses several GitHub Actions across multiple workflow files:
- `actions/checkout` (used in multiple workflows)
- `dtolnay/rust-toolchain` (used in multiple workflows)
- `Swatinem/rust-cache` (used in multiple workflows)
- `actions/upload-artifact` (used in multiple workflows)
- `actions/download-artifact` (used in release-build.yaml)
- `actions/setup-python` (used in pull_request.yaml)
- `actions/create-github-app-token` (used in release-version.yaml)

Without Dependabot monitoring these actions, updates must be tracked and applied manually.


## Related Implementation Plan

See `work/25W46/BUG_DEPENDABOT_MISSING_GITHUB_ACTIONS.md` for the detailed implementation plan.
