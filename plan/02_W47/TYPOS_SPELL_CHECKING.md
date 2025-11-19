# Spell Checking: typos

## Purpose
Add spell checking for source code and commit messages using typos to catch spelling mistakes before they reach the repository.

## Features
- Fast spell checking suitable for monorepos
- Low false positive rate
- Pre-commit hook integration
- Commit message checking
- Automatic correction capability

## Compatibility
- ✅ Apple Silicon (ARM): Compatible via `cargo install`
- ✅ Linux (GitHub Actions): Compatible

## Installation

```bash
cargo install typos-cli --locked
```

Or via Homebrew:
```bash
brew install typos-cli
```

## Usage

```bash
# Check for typos
typos

# Fix typos automatically
typos --write-changes
typos -w

# Check commit messages
typos --type-list
```

## Integration Notes
- Must run before `git-sumi` in pre-commit hooks
- Can check both source code and commit messages
- Supports configuration via `_typos.toml` for false positives
- Can be integrated with pre-commit framework

## Pre-commit Integration

### Configuration File: `.pre-commit-config.yaml`

Add typos to the pre-commit configuration, ensuring it runs before git-sumi:

```yaml
repos:
  - repo: https://github.com/crate-ci/typos
    rev: v1.39.2  # Use latest version
    hooks:
      - id: typos
        # Check source code
        args: [--write-changes]
      - id: typos-commit
        # Check commit messages
        stages: [commit-msg]
        args: [--format json]
```

### Manual Pre-commit Hook Setup

If using manual hooks, ensure typos runs before git-sumi:

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run typos first
typos --write-changes
if [ $? -ne 0 ]; then
    echo "Spell check failed. Please fix typos and try again."
    exit 1
fi

# Then run git-sumi
# ... rest of pre-commit hook
```

## Configuration

Create `_typos.toml` in the project root to handle false positives:

```toml
[default.extend-words]
# Add project-specific words
terraform = "terraform"
hcl = "hcl"

[default.extend-identifiers]
# Allow specific identifiers
ResourceID = "ResourceID"
```

## Pros
- Fast execution suitable for CI/CD
- Low false positive rate
- Automatic correction capability
- Supports commit message checking
- Well-maintained and actively developed
- Pre-commit hook support

## Cons
- Requires configuration for project-specific terms
- May need periodic updates to dictionary
- Additional dependency in pre-commit hooks

## Recommendation
Integrate typos into pre-commit hooks before git-sumi to catch spelling mistakes early. Configure `_typos.toml` to handle project-specific terminology and false positives.

## CI Integration

### Pre-commit Hook Order

Ensure typos runs before git-sumi in the pre-commit hook sequence:

1. typos (source code check)
2. typos-commit (commit message check)
3. git-sumi (checksum verification)

### GitHub Actions Integration

Add typos check to CI workflows:

```yaml
- name: Install typos
  run: cargo install typos-cli --locked

- name: Check spelling
  run: typos
```

## References
- [typos Documentation](https://github.com/crate-ci/typos)
- [typos GitHub Action](https://github.com/crate-ci/typos-action)
