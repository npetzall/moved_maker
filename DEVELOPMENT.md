# Development Guide

This document covers how to build, run, test, and develop this project.

## Installation

```bash
cargo build --release
```

The binary will be available at `target/release/move_maker`.

## Usage

```bash
move_maker --src <directory> --module-name <module_name>
```

### Arguments

- `--src <directory>`: Source directory containing Terraform files (`.tf` files in the directory, non-recursive)
- `--module-name <name>`: Name of the module to move resources into

### Example

Given a directory with `main.tf`:
```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345"
  instance_type = "t3.micro"
}
```

Running:
```bash
move_maker --src . --module-name compute
```

Will output:
```hcl
# From: main.tf
moved {
  from = aws_instance.web
  to   = module.compute.aws_instance.web
}
```

## Testing

This project uses [cargo-nextest](https://nexte.st/) for faster test execution and [pretty_assertions](https://docs.rs/pretty_assertions/) for enhanced test failure diagnostics.

### Running Tests

**Recommended: Use cargo-nextest** (faster, up to 3x faster than `cargo test`):
```bash
# Install cargo-nextest (if not already installed)
cargo install cargo-nextest

# Run all tests
cargo nextest run

# List all tests
cargo nextest list
```

**Alternative: Use standard cargo test**:
```bash
# Run all tests
cargo test

# Run only integration tests
cargo test --test integration_test
```

### Test Output

The project uses `pretty_assertions` for better test failure diagnostics. When tests fail, you'll see colored diff output that makes it easier to identify differences between expected and actual values.

### JUnit XML Output

For CI/CD workflows, JUnit XML output is configured via `.config/nextest.toml`. The output is generated in `target/nextest/default/test-results.xml` when running `cargo nextest run`.

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to enforce code quality standards before commits. The hooks ensure code formatting, run tests, validate commit messages, and perform security checks.

### Installation

**Preferred method (using uv):**
```bash
uv tool install pre-commit
```

**Alternative methods:**
```bash
# macOS (Homebrew)
brew install pre-commit

# Using pip
pip install pre-commit
```

### Setup

After installing pre-commit, install the hooks:
```bash
pre-commit install
```

This automatically installs both `pre-commit` and `commit-msg` hooks.

### Running Hooks Manually

Run all hooks on all files:
```bash
pre-commit run --all-files
```

Run a specific hook:
```bash
pre-commit run <hook-id> --all-files
# Example: pre-commit run cargo-fmt --all-files
```

### Configured Hooks

The following hooks are configured:

**Required:**
- `cargo-fmt`: Rust code formatting
- `cargo-test` (nextest): Run tests before commit
- `git-sumi`: Commit message validation (Conventional Commits)

**Recommended:**
- `cargo-clippy`: Rust linting and best practices
- `pre-commit-hooks`: General file checks (trailing whitespace, YAML/TOML/JSON validation, etc.)
- `cargo-check`: Fast compilation check
- `cargo-deny`: License compliance, vulnerability detection, banned dependencies
- `cargo-audit`: Vulnerability scanning using RustSec Advisory Database
- `ripsecrets`: Secret scanning to prevent accidental secret commits

### Commit Message Format

Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type** (required): `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert`

**Scope** (optional): The area of the codebase affected (e.g., `parser`, `processor`, `cli`)

**Subject** (required):
- Use imperative mood: "add" not "added" or "adds"
- First letter lowercase
- No period at the end
- Maximum 72 characters

**Examples:**
```
feat(parser): add support for data blocks
fix(processor): handle empty resource blocks correctly
docs: update README with installation instructions
test(cli): add integration tests for file discovery
chore: update dependencies
```

See `.config/sumi.toml` for complete configuration details.

### Updating Hooks

Update hook versions to their latest releases:
```bash
pre-commit autoupdate
```

Always review changes before committing:
```bash
# 1. Update hooks
pre-commit autoupdate

# 2. Review changes
git diff .pre-commit-config.yaml

# 3. Test updated hooks
pre-commit run --all-files

# 4. Commit updates
git add .pre-commit-config.yaml
git commit -m "chore: update pre-commit hooks"
```

### Bypassing Hooks (Not Recommended)

If you need to bypass hooks (e.g., for emergency fixes):
```bash
git commit --no-verify
```

**Warning**: Only use `--no-verify` in exceptional circumstances. It defeats the purpose of quality gates.

### Troubleshooting

**Formatting Hook Fails:**
```bash
# Auto-fix formatting
cargo fmt --all

# Then commit again
git add . && git commit -m "style: format code"
```

**Commit Message Validation Fails:**
- Check the format matches: `<type>(<scope>): <subject>`
- Ensure type is one of the allowed types (see `.config/sumi.toml`)
- Use imperative mood for the subject
- Ensure description starts with lowercase
- Ensure header doesn't end with a period
- Ensure header doesn't exceed 72 characters

**Pre-commit Not Running:**
```bash
# Reinstall hooks
pre-commit uninstall && pre-commit install

# Verify hooks are installed
ls -la .git/hooks/
```

## Code Coverage

This project uses [cargo-llvm-cov](https://github.com/taiki-e/cargo-llvm-cov) for code coverage tracking.

### Coverage Thresholds

- **Line coverage**: > 80% (enforced in CI)
- **Branch coverage**: > 70% (enforced in CI)
- **Function coverage**: > 85% (enforced in CI)

Current coverage: Line 91.52%, Function 91.23% ✅

### Generating Coverage Reports Locally

**Prerequisites:**
```bash
# Install llvm-tools-preview component
rustup component add llvm-tools-preview

# Install cargo-llvm-cov
cargo install cargo-llvm-cov
```

**Generate Coverage Report:**
```bash
# Generate coverage summary (quick check)
cargo llvm-cov nextest --all-features --summary-only

# Generate HTML report (detailed view)
cargo llvm-cov nextest --all-features --html
```

**View HTML Report:**
```bash
# macOS
open target/llvm-cov/html/index.html

# Linux
xdg-open target/llvm-cov/html/index.html
```

### Coverage Exclusions

The following are excluded from coverage metrics:
- Test code (`tests/` directory)
- Main entry point (`src/main.rs` - minimal logic)
- Error handling paths that are difficult to test

## Error Handling

This project uses [`anyhow`](https://docs.rs/anyhow/) for error handling throughout the codebase. All functions that can fail return `Result<T, anyhow::Error>` (or `anyhow::Result<T>` for short).

### Error Handling Patterns

**Function Signatures:**
- Functions that can fail return `Result<T>` (where `Result` is `anyhow::Result<T>`)
- Use `use anyhow::{Context, Result};` at the top of modules that need error handling

**Error Propagation:**
- Use the `?` operator to propagate errors up the call stack
- Add context at module boundaries and user-facing operations using `.context()` or `.with_context()`

**Error Context:**
- Use `.context()` for static error messages:
  ```rust
  parse_body(&content).context("Failed to parse HCL file")?
  ```
- Use `.with_context()` for dynamic messages that need formatting:
  ```rust
  fs::read_to_string(path)
      .with_context(|| format!("Failed to read file: {}", path.display()))?
  ```

**Main Function:**
- `main()` function calls a `run() -> Result<()>` function
- Errors are displayed with `{:#}` format for pretty-printed error chains:
  ```rust
  fn main() {
      if let Err(e) = run() {
          eprintln!("Error: {:#}", e);
          std::process::exit(1);
      }
  }
  ```

### Examples

**Reading Files:**
```rust
use anyhow::{Context, Result};

pub fn parse_terraform_file(path: &Path) -> Result<Body> {
    let content = fs::read_to_string(path)
        .with_context(|| format!("Failed to read file: {}", path.display()))?;

    parse_body(&content)
        .with_context(|| format!("Failed to parse HCL file: {}", path.display()))
}
```

**Adding Context at Module Boundaries:**
```rust
use anyhow::{Context, Result};

pub fn find_terraform_files(src: &Path) -> Result<Vec<PathBuf>> {
    let entries = fs::read_dir(src)
        .with_context(|| format!("Failed to read directory: {}", src.display()))?;
    // ... rest of function
}
```

**Error Handling in Tests:**
```rust
#[test]
fn test_parse_file() -> Result<()> {
    let content = parse_file(&path)?;
    assert_eq!(content, expected);
    Ok(())
}

#[test]
fn test_parse_invalid_file() {
    let result = parse_file(&invalid_path);
    assert!(result.is_err());
    let error_msg = result.unwrap_err().to_string();
    assert!(error_msg.contains("Failed to read file"));
}
```

### Best Practices

1. **Add Context at Module Boundaries**: Add context when crossing module boundaries (e.g., when calling external functions)
2. **Include Relevant Information**: Include file paths, line numbers, or other context that helps debug the issue
3. **Preserve Error Chains**: Use `{:#}` format to display full error chains for debugging
4. **User-Friendly Messages**: Ensure error messages are descriptive and helpful for end users
5. **Avoid Sensitive Information**: Don't expose sensitive information (passwords, tokens, etc.) in error messages
6. **Use `?` Operator**: Prefer `?` over `unwrap()` or `expect()` in production code
7. **Test Error Cases**: Write tests for error scenarios to ensure error messages are correct

### Error Display Formats

- `{:#}` - Pretty-printed error chains (use for user-facing output)
- `{:?}` - Debug format (use for debug logging)
- `{}` - Simple error message (loses error chain context)

### When to Use `unwrap()` or `expect()`

`unwrap()` and `expect()` are acceptable in:
- Test setup code where you control the environment (e.g., `TempDir::new().unwrap()`)
- Asserting expected errors in tests (e.g., `result.unwrap_err()`)
- Not acceptable when testing error handling paths or in production code

## Security Checks

For information about running security checks, see the [Security section in TOOLING.md](TOOLING.md#security).

To run all security checks locally:

```bash
# Update advisory database and run all checks
cargo audit update && cargo deny check --config .config/deny.toml && cargo audit --deny warnings && cargo geiger
```

## GitHub Configuration

This project uses GitHub branch protection, automated workflows, and version labeling to maintain code quality and enable continuous delivery.

### Branch Protection

The `main` branch is protected with the following rules:

- **Pull requests required**: All changes must go through pull requests
- **Linear history required**: Merge commits are disabled to maintain a clean, linear git history
- **Status checks required**: All CI/CD workflows must pass before merging (see [Troubleshooting](#troubleshooting) below)
- **Conversation resolution**: All PR comments and review discussions must be resolved before merging
- **No direct pushes**: Direct pushes to `main` are blocked

### Merge Strategy

The repository allows two merge methods that maintain linear history:

- **Rebase and merge**: Replays your commits on top of the base branch
- **Squash and merge**: Combines all commits into a single commit

**Merge commits are disabled** to maintain linear history, which is required for the versioning strategy.

Both rebase and squash merge maintain linear history, so you can choose either method based on your preference:
- Use **rebase and merge** if you want to preserve individual commit history
- Use **squash and merge** if you want to combine all commits into a single commit

### Pull Request Workflow

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes** and commit using [Conventional Commits](https://www.conventionalcommits.org/) format

3. **Push to your fork** and create a pull request

4. **Wait for status checks** to pass (tests, linting, security checks, etc.)

5. **Address review feedback** if requested

6. **Merge using rebase or squash merge** once approved and all checks pass

### Version Label System

Pull requests are automatically labeled based on commit messages using the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- **`version: major`**: Breaking changes (commits with `BREAKING CHANGE:` footer or `!` in type)
- **`version: minor`**: New features (commits with type `feat`)
- **`version: patch`**: Bug fixes and other changes (commits with type `fix`, `docs`, `chore`, etc.)

Labels are automatically applied by the PR label workflow when you push commits or update the PR. You can manually override labels if needed.

**Example commit messages and their labels:**
- `feat(parser): add support for data blocks` → `version: minor`
- `fix(processor): handle empty resource blocks` → `version: patch`
- `feat(api)!: change response format` → `version: major` (breaking change)

### Code Owners

The repository uses a `CODEOWNERS` file to define code ownership. When enabled in branch protection, PRs require review from code owners for files they own. See `.github/CODEOWNERS` for the current ownership configuration.

### Troubleshooting

**PR Cannot Be Merged - "Required status checks must pass":**
- Ensure all CI/CD workflows are passing (check the Actions tab)
- Wait for all workflows to complete
- Fix any failing tests or linting errors
- If workflows haven't been created yet, status checks won't appear (this is expected during initial setup)

**Labels Not Auto-Applied:**
- Labels are automatically applied by the PR label workflow
- Check the Actions tab to see if the workflow ran
- Ensure your commit messages follow Conventional Commits format
- You can manually add labels if needed

**Cannot Rebase or Squash Merge:**
- Ensure your PR branch is up to date with `main`
- Rebase your branch: `git checkout your-branch && git rebase main`
- Push the rebased branch: `git push --force-with-lease`
- Both rebase and squash merge maintain linear history, so either can be used

**Status Checks Not Appearing:**
- Status checks only appear after workflows have run at least once
- Create a test PR to trigger workflows
- Wait for workflows to complete
- If still not appearing, check that workflow files are correctly configured

For more detailed troubleshooting, see the [GitHub Configuration troubleshooting section](../work/01_Quality/06_GitHub_Configuration.md#troubleshooting).

## Project Structure

```
src/
  cli.rs           - CLI argument parsing and validation
  file_discovery.rs - Finding .tf files in directory
  parser.rs        - HCL file parsing
  processor.rs     - Block extraction and moved block generation
  output.rs        - Output body generation
  main.rs          - Main orchestration logic

tests/
  fixtures/        - Sample Terraform files for testing
  integration_test.rs - End-to-end integration tests
```
