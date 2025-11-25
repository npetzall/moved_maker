# Add Small but Effective .cursorrules Files

**Status**: ✅ Complete

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

**Purpose**: Direct file creation to appropriate directories and establish project-wide Rust conventions.

**Content**:
```cursorrules
# Move Maker - Cursor Rules

## Project Context
This is a Rust CLI tool that parses Terraform files and generates `moved` blocks for refactoring resources and data sources into submodules.

## Templates
When generating REQ_, BUG_, or implementation plan documents, always reference and use the templates found in `.cursor/templates/`:
- REQ_ documents: Read and follow `.cursor/templates/req_template.md` as a guide
- BUG_ documents: Read and follow `.cursor/templates/bug_template.md` as a guide
- Implementation plans: Read and follow `.cursor/templates/implementation_plan_template.md` as a guide
Templates define all document structure, sections, formatting, and status header placement - follow them exactly.

## Work Documents - Where to Create Files
- **REQ_ documents**: Create new documents in `plan/XX_Backlog/` (literal folder name, not a placeholder)
  - Use `REQ_` prefix for requests (features, enhancements, modifications)
  - Always use `.cursor/templates/req_template.md` as the template
  - See `plan/.cursorrules` for detailed structure, workflow, and templates
  - Note: `XX_Backlog` is primarily used by rules for new documents; year-week directories (e.g., `YYWW/`) are created manually by users
- **BUG_ documents**: Create new documents in `plan/XX_Backlog/` first (literal folder name, not a placeholder)
  - Use `BUG_` prefix for bug reports
  - Always use `.cursor/templates/bug_template.md` as the template
  - See `plan/.cursorrules` for detailed structure, workflow, and templates
  - Note: `XX_Backlog` is primarily used by rules for new documents; year-week directories (e.g., `YYWW/`) are created manually by users
- **Implementation plans**: When creating implementation plans for REQ_ or BUG_ documents (after review/refinement and when requested by user):
  - Place in a subfolder of `work/` with the same name as the folder where the REQ_ or BUG_ is located
  - Keep the same filename as the REQ_ or BUG_ document
  - Always use `.cursor/templates/implementation_plan_template.md` as the template
  - Example: `plan/YYWW/REQ_EXAMPLE.md` → `work/YYWW/REQ_EXAMPLE.md`
  - Example: `plan/XX_Backlog/BUG_SOMETHING.md` → `work/XX_Backlog/BUG_SOMETHING.md`
  - See `work/.cursorrules` for detailed structure and templates

## Rust Conventions (Project-Wide)
- Follow Rust naming conventions (snake_case for functions/variables, PascalCase for types)
- Prefer `Result<T>` over `Option<T>` for error handling
- Use `anyhow::Result` for error propagation in application code
- Use `panic!()` only for unrecoverable errors (e.g., invalid CLI arguments)
- Prefer iterator chains over explicit loops when idiomatic
- Use `#[derive(Debug)]` on all public types
- Document public APIs with doc comments (`///`)
- Use 4 spaces for indentation, max 100 characters per line
- Use `cargo fmt` for formatting, `cargo clippy` for linting
- Write unit tests with `#[cfg(test)]` modules, integration tests in `tests/`

## Directory-Specific Rules
Nested `.cursorrules` files provide detailed guidance when working in specific directories:
- `src/.cursorrules` - Source code implementation guidelines
- `tests/.cursorrules` - Test writing conventions
- `.github/workflows/.cursorrules` - GitHub Actions workflow guidance
- `.github/scripts/.cursorrules` - Python script development (uv, pytest)
- `examples/.cursorrules` - Terraform example file guidelines
- `plan/.cursorrules` - Planning document structure, workflow, and templates
- `work/.cursorrules` - Implementation plan structure, workflow, and templates
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

### 4. GitHub Workflows `.cursorrules` (`.github/workflows/`)

**Location**: `/Users/nilspetzall/repos/npetzall/moved_maker/.github/workflows/.cursorrules`

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

### 5. GitHub Scripts `.cursorrules` (`.github/scripts/`)

**Location**: `/Users/nilspetzall/repos/npetzall/moved_maker/.github/scripts/.cursorrules`

**Purpose**: Guide Python script development for GitHub Actions and automation.

**Content**:
```cursorrules
# GitHub Scripts Rules

## Python Package Management
- Use `uv` for Python package management and virtual environment handling
- Create `pyproject.toml` or `requirements.txt` for dependencies
- Use `uv sync` to install dependencies
- Use `uv run` to execute scripts within the virtual environment

## Testing
- Use `pytest` for all Python tests
- Write tests in `tests/` directory or alongside scripts with `test_` prefix
- Use descriptive test function names: `test_<what>_<condition>_<expected_result>`
- Run tests with `uv run pytest` or `pytest` if already in virtual environment
- Use pytest fixtures for test setup and teardown
- Aim for high test coverage

## Code Style
- Follow PEP 8 style guidelines
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use type hints for function parameters and return values
- Use `black` for code formatting (if configured)
- Use `ruff` or `flake8` for linting (if configured)

## Script Structure
- Use `#!/usr/bin/env python3` shebang for executable scripts
- Include docstrings for modules, classes, and functions
- Use `if __name__ == "__main__":` guard for script entry points
- Handle errors gracefully with try/except blocks
- Use logging instead of print statements for production scripts

## Dependencies
- Pin dependency versions in `pyproject.toml` or `requirements.txt`
- Document why each dependency is needed
- Keep dependencies minimal and focused
- Update dependencies regularly for security patches

## Dependabot Configuration
- When adding Python dependencies, ensure Dependabot is configured to monitor them
- Check `.github/dependabot.yml` for Python ecosystem entries
- If missing, add a Dependabot entry for Python:
  ```yaml
  - package-ecosystem: "pip"
    directory: "/.github/scripts"
    schedule:
      interval: "weekly"
  ```
- For `pyproject.toml`-based projects, use `package-ecosystem: "pip"` with the appropriate directory
```

### 6. Examples `.cursorrules` (`examples/`)

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

### 7. Plan Documents `.cursorrules` (`plan/`)

**Location**: `/Users/nilspetzall/repos/npetzall/moved_maker/plan/.cursorrules`

**Purpose**: Guide creation and maintenance of planning documents.

**Content**:
```cursorrules
# Planning Documents Rules

## Document Naming and Organization
- Use `REQ_` prefix for requests (features, enhancements, modifications)
- Use `BUG_` prefix for bug reports
- Newly create documents should be placed in `plan/XX_Backlog` (literal folder name, not a placeholder)
- Both REQ_ and BUG_ documents get implementation plans in `work/` folder
- No `done/` folders - use status headers instead
- See REQ_WORK_DOCUMENT_STRUCTURE.md for complete structure guidelines
- Note: `XX_Backlog` is primarily used by rules for new documents; year-week directories (e.g., `YYWW/`) are created manually by users

## Workflow
1. **Discovery** → Add to `plan/XX_Backlog/` with `REQ_` or `BUG_` prefix (literal folder name)
2. **Planning** → Manually move to `plan/YYWW/` (year-week directory, e.g., `24W48/`), review and improve (manual step done by user)
3. **Implementation** → After review/refinement, when requested by user, create matching file in `work/` folder with same folder name and same filename
   - Example: `plan/YYWW/REQ_EXAMPLE.md` → `work/YYWW/REQ_EXAMPLE.md`
   - Example: `plan/XX_Backlog/BUG_SOMETHING.md` → `work/XX_Backlog/BUG_SOMETHING.md`
4. **Completion** → Update status to "✅ Complete" in `plan/` document (leave in place)

## Template Usage
- Always read and use templates from `.cursor/templates/` before generating documents:
  - REQ_ documents → `.cursor/templates/req_template.md`
  - BUG_ documents → `.cursor/templates/bug_template.md`
  - Implementation plans → `.cursor/templates/implementation_plan_template.md`
- Templates define all document structure, sections, formatting, and status header placement
- Follow template structure exactly - do not add or remove sections
```

### 8. Work Documents `.cursorrules` (`work/`)

**Location**: `/Users/nilspetzall/repos/npetzall/moved_maker/work/.cursorrules`

**Purpose**: Guide creation and maintenance of implementation plans.

**Content**:
```cursorrules
# Implementation Plans Rules

## Document Naming and Organization
- Implementation plans MUST be placed in a subfolder of `work/` with the same name as the folder where the corresponding REQ_ or BUG_ is located
- Filenames MUST be identical to the corresponding document in `plan/` folder
- Organize by matching the folder structure from `plan/` (e.g., `plan/YYWW/` → `work/YYWW/`, `plan/XX_Backlog/` → `work/XX_Backlog/`)
- Both REQ_ and BUG_ documents have matching implementation plans in `work/` folder
- No `done/` folders - use status headers instead
- See REQ_WORK_DOCUMENT_STRUCTURE.md for complete structure guidelines
- Implementation plans are created after review/refinement and when requested by user

## Relationship to Plan Documents
- Each file in `work/` corresponds to a file in `plan/` with the same folder name and same filename
- Always reference the corresponding `plan/` document at the beginning
- Implementation plans should align with requirements/scope defined in `plan/` documents
- Update status in both `plan/` and `work/` documents as work progresses

## Template Usage
- Always read and use `.cursor/templates/implementation_plan_template.md` before generating documents
- Template defines all document structure, sections, formatting, and status header placement
- Follow template structure exactly - do not add or remove sections
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

4. **Create `.github/workflows/.cursorrules`**
   - Add GitHub Actions workflow guidance
   - Include Rust-specific CI/CD best practices
   - Document artifact and caching strategies

5. **Create `.github/scripts/.cursorrules`**
   - Add Python script development guidance
   - Document `uv` package management usage
   - Include `pytest` testing conventions
   - Guide Python code style and structure

6. **Create `examples/.cursorrules`**
   - Add Terraform example file guidelines
   - Ensure examples remain clear and maintainable
   - Guide documentation standards for examples

7. **Create `plan/.cursorrules`**
   - Add planning document naming and organization guidelines
   - Include year-week format organization (e.g., `YYWW/` format like `24W48/`)
   - Document workflow: Discovery → Planning → Implementation → Completion
   - Emphasize identical filenames between `plan/` and `work/` folders
   - Include template usage instructions (templates define all structure and formatting)
   - Document that both REQ_ and BUG_ get implementation plans
   - Clarify that `XX_Backlog` is a literal folder name (primarily for rules), year-week directories are created manually

8. **Create `work/.cursorrules`**
   - Add implementation plan naming and organization guidelines
   - Include year-week format organization (e.g., `YYWW/` format like `24W48/`)
   - Emphasize identical filenames requirement with `plan/` folder
   - Document relationship to `plan/` documents
   - Include template usage instructions (templates define all structure and formatting)
   - Clarify that implementation plans are created after review/refinement and when requested by user

9. **Verify Template Usage and Workflow**
   - Verify that templates exist in `.cursor/templates/` directory:
     - `req_template.md`
     - `bug_template.md`
     - `implementation_plan_template.md`
   - Test that Cursor AI can access and read templates from `.cursor/templates/`
   - Generate a sample REQ_ document in `plan/YYWW/` (or `plan/XX_Backlog/`) and verify it follows `req_template.md` structure exactly
   - Generate a sample BUG_ document in `plan/YYWW/` (or `plan/XX_Backlog/`) and verify it follows `bug_template.md` structure exactly
   - Generate matching implementation plans in `work/YYWW/` (or `work/XX_Backlog/`) with identical filenames
   - Verify that generated documents match template structure (sections, formatting, status header placement)
   - Verify that implementation plans reference corresponding `plan/` documents
   - Verify that both REQ_ and BUG_ documents have matching files in `work/` folder

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

## Template and Workflow Verification Checklist

When verifying template usage and workflow compliance, ensure:

- [ ] Templates exist in `.cursor/templates/` directory
- [ ] Root `.cursorrules` includes template reference section and work document structure
- [ ] `plan/.cursorrules` includes template usage instructions and workflow steps
- [ ] Cursor AI can successfully read templates when generating documents
- [ ] Generated REQ_ documents match `req_template.md` structure exactly (all sections, formatting, status header)
- [ ] Generated BUG_ documents match `bug_template.md` structure exactly (all sections, formatting, status header)
- [ ] Generated implementation plans match `implementation_plan_template.md` structure exactly (all sections, formatting, status header)
- [ ] Implementation plans reference corresponding `plan/` documents
- [ ] Documents use year-week format (e.g., `YYWW/` format like `24W48/`, not sequential numbering)
- [ ] Both REQ_ and BUG_ documents have matching files in `work/` folder
- [ ] Filenames are identical between `plan/` and `work/` folders
- [ ] No `done/` folders exist (status tracking is used instead)

## Notes

- `.cursorrules` files are typically ignored by git (add to `.gitignore` if desired, though many projects commit them)
- Rules are suggestions, not enforced - developers can override when appropriate
- Start with minimal rules and expand based on actual needs
- Focus on rules that provide clear value rather than exhaustive documentation
- Templates in `.cursor/templates/` should be committed to version control
- Always verify template usage after creating or updating `.cursorrules` files
- Work document structure follows year-week format for chronological organization
- Files stay in their week directory - no movement needed after initial organization
- Status tracking via headers replaces the need for `done/` folders

## Related Documents

- [CURSOR_AI_TEMPLATES.md](CURSOR_AI_TEMPLATES.md) - Template specifications for AI-generated documents
- [REQ_WORK_DOCUMENT_STRUCTURE.md](REQ_WORK_DOCUMENT_STRUCTURE.md) - Work document structure and organization guidelines
