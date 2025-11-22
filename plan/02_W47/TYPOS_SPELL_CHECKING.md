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

Always install using Cargo:

```bash
cargo install typos-cli --locked
```

## Usage

```bash
# Check for typos (using config in .config/)
typos --config .config/typos.toml

# Fix typos automatically
typos --config .config/typos.toml --write-changes
typos --config .config/typos.toml -w

# Show diff of proposed changes without modifying files
typos --config .config/typos.toml --diff
```

**Note:** Commit messages are checked automatically via the `commit-msg` hook (see Pre-commit Integration section). There is no standalone command to check commit messages directly.

## Integration Notes
- **Must be used with pre-commit hooks** for checking commit messages
- **Must run before `git-sumi`** in pre-commit hooks
- Can check both source code and commit messages
- Configuration stored in `.config/typos.toml` (consistent with other project configs)
- Can be integrated with pre-commit framework

## Pre-commit Integration

### Configuration File: `.pre-commit-config.yaml`

Add typos to the pre-commit configuration, ensuring it runs before git-sumi:

```yaml
repos:
  # Spell checking (must run before git-sumi)
  - repo: https://github.com/crate-ci/typos
    rev: v1.39.2  # Use latest version
    hooks:
      - id: typos
        # Check source code (fail on typos, don't auto-fix in hooks)
        args: [--config, .config/typos.toml]
        stages: [pre-commit]
      - id: typos-commit
        # Check commit messages (fail on typos)
        args: [--config, .config/typos.toml]
        stages: [commit-msg]
```

**Note:** The hooks are configured to fail on typos rather than auto-fix them. This ensures typos are caught before commit. Users must manually fix typos or update the configuration to add new words.

### Manual Pre-commit Hook Setup

If using manual hooks, ensure typos runs before git-sumi:

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run typos first
typos --config .config/typos.toml
if [ $? -ne 0 ]; then
    echo "Spell check failed. Please fix typos and try again."
    exit 1
fi

# Then run git-sumi
# ... rest of pre-commit hook
```

## Configuration

### Configuration File Location

Configuration is stored in `.config/typos.toml` to maintain consistency with other project configuration files (e.g., `.config/deny.toml`, `.config/sumi.toml`, `.config/nextest.toml`). This keeps the project root clean and avoids modifying `Cargo.toml` unnecessarily, which is important for stable cache keys.

The `--config` flag must be used to specify the configuration file location in all typos commands and pre-commit hooks.

### Basic Configuration

Create `.config/typos.toml` to handle false positives:

```toml
[default.extend-words]
# Add project-specific words
terraform = "terraform"
hcl = "hcl"
moved = "moved"
maker = "maker"

[default.extend-identifiers]
# Allow specific identifiers
ResourceID = "ResourceID"
```

## Interactive Mode

**typos does not support interactive mode during commit.** When typos detects spelling errors:

1. The commit will **fail** if typos are found
2. The user must either:
   - Manually fix the typos in the code/commit message
   - Update the configuration file (`.config/typos.toml`) to add new words to the dictionary
3. After fixing or updating configuration, the user can retry the commit

For interactive spell checking before committing, run typos manually:

```bash
# Check for typos interactively
typos --config .config/typos.toml

# Auto-fix typos (use before committing)
typos --config .config/typos.toml --write-changes
```

## Pros
- Fast execution suitable for CI/CD
- Low false positive rate
- Automatic correction capability (when run manually)
- Supports commit message checking
- Well-maintained and actively developed
- Pre-commit hook support
- Fails fast on typos, preventing bad commits

## Cons
- Requires configuration for project-specific terms
- May need periodic updates to dictionary
- Additional dependency in pre-commit hooks

## Recommendation
Integrate typos into pre-commit hooks **before git-sumi** to catch spelling mistakes early. Configure `.config/typos.toml` to handle project-specific terminology and false positives, keeping it consistent with other project configuration files. The hooks should be configured to fail on typos, requiring users to fix spelling errors or update the configuration before committing.

## CI Integration

### Pre-commit Hook Order

Ensure typos runs **before git-sumi** in the pre-commit hook sequence:

1. typos (source code check) - `pre-commit` stage
2. typos-commit (commit message check) - `commit-msg` stage
3. git-sumi (checksum verification) - `commit-msg` stage

The order in `.pre-commit-config.yaml` determines execution order. Place typos hooks before git-sumi.

### GitHub Actions Integration

**Note:** Since pre-commit hooks are already run in the GitHub Actions workflows, typos will be automatically checked as part of the pre-commit hook execution. There is no need to add a separate typos step or use the typos GitHub Action.

If you need to run typos separately in CI (e.g., for reporting purposes), you can add:

```yaml
- name: Install typos
  run: cargo install typos-cli --locked

- name: Check spelling
  run: typos --config .config/typos.toml
```

However, this is typically unnecessary since the pre-commit hooks already perform this check.

## Implementation

This plan has been implemented following the detailed implementation plan:

- **Implementation Plan**: `work/02_W47/TYPOS_SPELL_CHECKING.md`

The implementation plan provides step-by-step instructions for integrating typos into the project, including configuration setup, pre-commit hook integration, testing, and verification.

## References
- [typos Documentation](https://github.com/crate-ci/typos)
- [typos GitHub Action](https://github.com/crate-ci/typos-action)
