# Add Small but Effective .cursorrules Files

## Overview

`.cursorrules` files are configuration files that provide context and instructions to Cursor AI when working in a specific directory. They help guide AI behavior, coding style, and project-specific conventions. This plan outlines how to add effective `.cursorrules` files to improve AI assistance throughout the project.

## How .cursorrules Files Work

### File Discovery and Hierarchy

Cursor searches for `.cursorrules` files starting from the current file's directory and walks up the directory tree to the repository root:

1. **Current directory**: Cursor first checks for `.cursorrules` in the directory containing the file being edited
2. **Parent directories**: If not found, Cursor searches each parent directory up to the root
3. **Repository root**: The root `.cursorrules` file serves as the base configuration
4. **Merging behavior**: When multiple `.cursorrules` files are found, they are typically merged, with more specific (nested) rules taking precedence over general (root) rules

### Best Practices

- **Root `.cursorrules`**: Contains project-wide conventions, language-specific guidelines, and general coding standards
- **Nested `.cursorrules`**: Contains directory-specific rules, domain-specific guidance, or specialized instructions for particular areas of the codebase
- **Keep rules concise**: Focus on actionable, specific guidance rather than verbose explanations
- **Update regularly**: Keep rules aligned with project evolution and team preferences

## Proposed .cursorrules Files

### 1. Root `.cursorrules` (Repository Root)

**Location**: `/Users/nilspetzall/repos/npetzall/moved_maker/.cursorrules`

**Purpose**: Establish project-wide conventions for Rust development, Terraform tooling, and general code quality.

**Content**:
```cursorrules
# Move Maker - Cursor Rules

## Project Context
This is a Rust CLI tool that parses Terraform files and generates `moved` blocks for refactoring resources and data sources into submodules.

## Rust Conventions
- Use `#![forbid(unsafe_code)]` - no unsafe code allowed
- Follow Rust naming conventions (snake_case for functions/variables, PascalCase for types)
- Prefer `Result<T>` over `Option<T>` for error handling
- Use `anyhow::Result` for error propagation in application code
- Use `panic!()` only for unrecoverable errors (e.g., invalid CLI arguments)
- Prefer iterator chains over explicit loops when idiomatic
- Use `#[derive(Debug)]` on all public types
- Document public APIs with doc comments (`///`)

## Code Style
- Use 4 spaces for indentation (Rust standard)
- Maximum line length: 100 characters
- Prefer early returns for error handling
- Use `cargo fmt` for formatting - always run before committing
- Use `cargo clippy` - address all warnings

## Testing
- Write unit tests in the same file using `#[cfg(test)]` modules
- Integration tests go in `tests/` directory
- Use `cargo nextest` for running tests
- Aim for high code coverage (tracked via coverage.json)

## Terraform/HCL Context
- This tool parses HCL (HashiCorp Configuration Language) files
- Uses `hcl-rs` crate via `hcl::edit` for parsing
- Focus on top-level `resource` and `data` blocks
- Generate `moved` blocks with correct Terraform address syntax

## File Organization
- Keep modules focused and single-purpose
- Use `mod` declarations in `main.rs` or `lib.rs`
- Group related functionality together
- Prefer composition over inheritance (Rust trait system)

## Error Messages
- Provide clear, actionable error messages
- Include context about what failed and why
- Use `eprintln!()` for warnings, `println!()` for output
```

### 2. Source Code `.cursorrules` (`src/`)

**Location**: `/Users/nilspetzall/repos/npetzall/moved_maker/src/.cursorrules`

**Purpose**: Provide specific guidance for Rust source code implementation.

**Content**:
```cursorrules
# Source Code Rules

## Module Structure
- Each file should contain a single logical module
- Use `pub` sparingly - only expose what's necessary
- Keep private implementation details private

## Error Handling
- Use `anyhow::Result` for functions that can fail
- Use `?` operator for error propagation
- Provide context with `.context()` when appropriate
- Log warnings with `eprintln!()` for non-fatal errors

## Type Safety
- Prefer strong types over stringly-typed code
- Use enums for state machines and variants
- Leverage Rust's type system to prevent invalid states

## Performance
- Prefer iterators over manual loops
- Use `Vec::with_capacity()` when size is known
- Avoid unnecessary allocations
- Use references (`&str`, `&Path`) instead of owned types when possible

## Testing
- Write tests alongside implementation
- Test edge cases and error conditions
- Use descriptive test names that explain what is being tested
```

### 3. Tests `.cursorrules` (`tests/`)

**Location**: `/Users/nilspetzall/repos/npetzall/moved_maker/tests/.cursorrules`

**Purpose**: Guide test writing conventions and best practices.

**Content**:
```cursorrules
# Test Rules

## Test Organization
- One integration test file per major feature area
- Use descriptive test function names: `test_<what>_<condition>_<expected_result>`
- Group related tests using modules or comments

## Test Fixtures
- Place test fixtures in `tests/fixtures/` directory
- Use descriptive fixture file names
- Keep fixtures minimal and focused

## Assertions
- Use `assert!`, `assert_eq!`, `assert_ne!` for simple checks
- Use `Result` return types for tests that can fail
- Provide clear failure messages in assertions

## Test Data
- Use realistic but minimal test data
- Avoid hardcoding paths - use `PathBuf` and relative paths
- Clean up any temporary files created during tests
```

### 4. GitHub Workflows `.cursorrules` (`.github/`)

**Location**: `/Users/nilspetzall/repos/npetzall/moved_maker/.github/.cursorrules`

**Purpose**: Guide GitHub Actions workflow development and maintenance.

**Content**:
```cursorrules
# GitHub Workflows Rules

## Workflow Structure
- Use descriptive workflow names
- Include clear job names and step descriptions
- Use matrix strategies for cross-platform builds
- Cache dependencies and build artifacts appropriately

## Best Practices
- Use `actions/checkout@v4` or later
- Pin action versions (avoid `@main` or `@master`)
- Use environment variables for secrets
- Add appropriate permissions (minimal required)
- Use `fail-fast: false` for matrix jobs when appropriate

## Rust-Specific
- Use `actions-rs/toolchain@v1` or `dtolnay/rust-toolchain` for Rust setup
- Cache `~/.cargo/registry` and `~/.cargo/git`
- Cache `target/` directory with appropriate keys
- Use `cargo nextest` for test execution
- Run `cargo deny check` and `cargo audit` for security

## Artifacts
- Name artifacts descriptively (include platform/architecture)
- Upload test results for visibility
- Use appropriate retention policies
```

### 5. Examples `.cursorrules` (`examples/`)

**Location**: `/Users/nilspetzall/repos/npetzall/moved_maker/examples/.cursorrules`

**Purpose**: Guide creation and maintenance of example Terraform configurations.

**Content**:
```cursorrules
# Example Terraform Files Rules

## Example Structure
- Each example should be self-contained and runnable
- Include realistic but minimal Terraform configurations
- Use clear, descriptive resource names
- Include comments explaining the example's purpose

## File Organization
- Follow standard Terraform file naming: `main.tf`, `variables.tf`, `outputs.tf`, `data.tf`, `locals.tf`
- Group related resources logically
- Use consistent formatting (run `terraform fmt`)

## Documentation
- Include a README.md in each example directory explaining:
  - What the example demonstrates
  - How to run it
  - Expected output
- Add comments in Terraform files for complex logic

## Testing Examples
- Examples should be valid Terraform syntax
- Avoid requiring real cloud credentials (use data sources or mock resources)
- Keep examples focused on demonstrating tool functionality
```

### 6. Plan Documents `.cursorrules` (`plan/`)

**Location**: `/Users/nilspetzall/repos/npetzall/moved_maker/plan/.cursorrules`

**Purpose**: Guide creation and maintenance of planning documents.

**Content**:
```cursorrules
# Planning Documents Rules

## Document Naming and Organization
- Use `REQ_` prefix for requests (features, enhancements, modifications)
- Use `BUG_` prefix for bug reports
- Organize documents by year-week format (e.g., `24W48/`)
- Each document in `plan/` should have a matching file in `work/` with the same filename
- See REQ_WORK_DOCUMENT_STRUCTURE.md for complete structure guidelines

## Document Structure
- Start with status header: `**Status**: 📋 Planned | 🟡 In Progress | ✅ Complete | ⏸️ Blocked`
- Start with context: current state, problem statement, or requirements
- Include clear task breakdowns
- Provide implementation details and examples
- Document benefits and considerations

## Markdown Formatting
- Use clear headings (## for main sections, ### for subsections)
- Use code blocks with language identifiers
- Include file paths and line numbers when referencing code
- Use lists for task items and considerations

## Content Guidelines
- Be specific and actionable
- Include references to GitHub issues when applicable
- Document file locations that need changes
- Provide examples of expected outcomes
- Note any breaking changes or migration steps
```

## Implementation Steps

1. **Create root `.cursorrules`**
   - Add comprehensive project-wide rules
   - Focus on Rust conventions, code style, and project context
   - Test that Cursor recognizes and applies the rules

2. **Create `src/.cursorrules`**
   - Add source code-specific guidance
   - Focus on module structure, error handling, and type safety
   - Ensure it complements (doesn't contradict) root rules

3. **Create `tests/.cursorrules`**
   - Add test-specific conventions
   - Guide test organization and fixture usage
   - Ensure consistency with testing practices

4. **Create `.github/.cursorrules`**
   - Add GitHub Actions workflow guidance
   - Include Rust-specific CI/CD best practices
   - Document artifact and caching strategies

5. **Create `examples/.cursorrules`**
   - Add Terraform example file guidelines
   - Ensure examples remain clear and maintainable
   - Guide documentation standards for examples

6. **Create `plan/.cursorrules`**
   - Add planning document structure guidelines
   - Ensure consistency across planning documents
   - Guide markdown formatting and content organization

7. **Verify and Test**
   - Test that Cursor recognizes rules in each directory
   - Verify rule hierarchy works correctly (nested rules take precedence)
   - Update rules based on actual usage and feedback

## Benefits

- **Consistent AI assistance**: Cursor will provide more contextually appropriate suggestions
- **Reduced context switching**: Rules provide project context automatically
- **Better code quality**: AI suggestions align with project conventions
- **Faster onboarding**: New contributors get consistent guidance
- **Maintainability**: Rules document project standards and preferences

## Maintenance

- Review and update rules quarterly or when project conventions change
- Remove rules that become outdated or are no longer relevant
- Add rules based on common patterns or issues encountered
- Keep rules concise and actionable - avoid verbose explanations
- Test rule changes to ensure they improve AI assistance

## Notes

- `.cursorrules` files are typically ignored by git (add to `.gitignore` if desired, though many projects commit them)
- Rules are suggestions, not enforced - developers can override when appropriate
- Start with minimal rules and expand based on actual needs
- Focus on rules that provide clear value rather than exhaustive documentation

## Related Documents

- [CURSOR_AI_TEMPLATES.md](CURSOR_AI_TEMPLATES.md) - Template specifications for AI-generated documents
- [REQ_WORK_DOCUMENT_STRUCTURE.md](REQ_WORK_DOCUMENT_STRUCTURE.md) - Work document structure and organization guidelines
