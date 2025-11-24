# Implementation Plan: Robust PR Labeling

**Status**: ✅ Completed

## Overview
Replace the bash-based PR labeling workflow with a Python-based solution using PyGithub. This will improve robustness by eliminating brittle bash parsing and removing dependency on the GitHub CLI (gh) tool that may change in runner images.

## Checklist Summary

### Phase 1: Project Setup
- [x] 3/3 tasks completed

### Phase 2: Core Implementation
- [x] 4/4 tasks completed

### Phase 3: Testing
- [x] 3/3 tasks completed

### Phase 4: Integration and Documentation
- [x] 3/3 tasks completed

## Context
**Related REQ Document**: `plan/25W48/REQ_ROBUST_PR_LABELING.md`

**Current State**: The PR labeling workflow (`.github/workflows/pr-label.yml`) uses bash scripts with the GitHub CLI (`gh`) to:
- Parse commit messages using `grep` to detect Conventional Commit patterns
- Apply version bump labels (`version: major`, `version: minor`, `version: patch`)
- Apply semantic labels (`breaking`, `feature`)

**Problem Statement**:
- Bash parsing is brittle and error-prone with multi-line or unusual commit messages
- GitHub CLI (`gh`) dependency on runner image may change unexpectedly, causing silent breakage
- No test coverage for the labeling logic

**Requirements**:
- Replace with Python project using `uv` and PyGithub
- Match existing structure of `.github/scripts/release-version` and `.github/scripts/release-notes`
- Implement comprehensive test coverage
- Ensure labels are created if they don't exist
- Handle all GitHub API errors gracefully

## Goals
- Replace bash-based PR labeling with robust Python implementation
- Eliminate dependency on GitHub CLI (`gh`) tool
- Improve commit message parsing reliability
- Add comprehensive test coverage
- Maintain backward compatibility with existing label names and behavior
- Follow existing project patterns for consistency

## Non-Goals
- Changing label names or semantic meaning
- Supporting additional Conventional Commit types beyond current scope
- Adding new features beyond what the current workflow provides
- Modifying other workflows or scripts

## Design Decisions

**Decision 1: Use PyGithub instead of GitHub CLI**
- **Rationale**: PyGithub provides a stable Python API that doesn't depend on runner image tooling. It handles pagination automatically and provides better error handling than shell commands.
- **Alternatives Considered**:
  - Continue using `gh` CLI with better error handling (rejected: still depends on runner image)
  - Use GitHub REST API directly with `requests` (rejected: PyGithub provides better abstraction and handles edge cases)
- **Trade-offs**: Requires Python runtime, but this is already established in the project for other scripts

**Decision 2: Create GitHubClient wrapper class**
- **Rationale**: Matches the pattern in `release-version/src/release_version/github_client.py` for consistency. Enables better testability through dependency injection and mocking.
- **Alternatives Considered**:
  - Use PyGithub directly in main module (rejected: less testable, inconsistent with existing patterns)
- **Trade-offs**: Slightly more code, but improves maintainability and testability

**Decision 3: Auto-create missing labels**
- **Rationale**: Ensures workflow doesn't fail if labels are accidentally deleted or missing. Provides better user experience.
- **Alternatives Considered**:
  - Fail if labels don't exist (rejected: brittle, requires manual intervention)
  - Skip labeling if labels don't exist (rejected: silent failures are worse)
- **Trade-offs**: Requires write permissions for labels, but this is already available in the workflow

**Decision 4: Remove all conflicting labels before applying new ones**
- **Rationale**: Ensures clean state - only one version label and appropriate semantic label at a time. Matches current behavior.
- **Alternatives Considered**:
  - Only remove labels that conflict (rejected: more complex logic, current approach is simpler)
- **Trade-offs**: None - this matches current behavior

## Implementation Steps

### Phase 1: Project Setup

**Objective**: Create the Python project structure matching existing patterns

- [x] **Task 1**: Create project directory structure
  - [x] Create `.github/scripts/pr-labels/` directory
  - [x] Create `.github/scripts/pr-labels/src/pr_labels/` directory for source code
  - [x] Create `.github/scripts/pr-labels/tests/` directory for tests
  - [x] Create `__init__.py` files in appropriate locations
  - **Files**: New directories
  - **Dependencies**: None
  - **Testing**: Verify directory structure matches `release-version` pattern
  - **Notes**: Follow exact structure from `.github/scripts/release-version/`

- [x] **Task 2**: Create `pyproject.toml` configuration
  - [x] Create `pyproject.toml` with project metadata (name: "pr-labels", version: "0.1.0")
  - [x] Add `requires-python = ">=3.11"` to match existing scripts
  - [x] Add `pygithub>=2.0.0` as dependency
  - [x] Add `pytest>=8.0.0` and `pytest-datadir>=1.4.0` as dev dependencies
  - [x] Configure pytest in `[tool.pytest.ini_options]` section (testpaths, python_files, python_classes, python_functions)
  - [x] Configure build system with `hatchling`
  - **Files**: `.github/scripts/pr-labels/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Run `uv sync` to verify configuration
  - **Notes**: Match structure from `.github/scripts/release-version/pyproject.toml`

- [x] **Task 3**: Initialize uv project and generate lock file
  - [x] Run `uv sync` in `.github/scripts/pr-labels/` to create `uv.lock`
  - [x] Verify `uv.lock` file is created
  - [x] Verify all dependencies resolve correctly
  - **Files**: `.github/scripts/pr-labels/uv.lock`
  - **Dependencies**: Task 2 complete
  - **Testing**: Run `uv sync` and verify no errors
  - **Notes**: This ensures deterministic builds

### Phase 2: Core Implementation

**Objective**: Implement the PR labeling logic using PyGithub

- [x] **Task 1**: Create GitHubClient wrapper class
  - [x] Create `.github/scripts/pr-labels/src/pr_labels/github_client.py`
  - [x] Implement `GitHubClient` class with `__init__(token: str, repo_name: str)`
  - [x] Implement `get_repo()` method using `Github(auth=Auth.Token(token)).get_repo(repo_name)`
  - [x] Implement `get_pull(pr_number: int)` method using `repo.get_pull(pr_number)`
  - [x] Add error handling with `GithubException` for all methods
  - [x] Add docstrings following existing patterns
  - **Files**: `.github/scripts/pr-labels/src/pr_labels/github_client.py`
  - **Dependencies**: Phase 1 complete
  - **Testing**: Unit tests will be created in Phase 3
  - **Notes**: Match pattern from `release-version/src/release_version/github_client.py`

- [x] **Task 2**: Create commit parser module
  - [x] Create `.github/scripts/pr-labels/src/pr_labels/parser.py`
  - [x] Implement function to parse commit messages for Conventional Commit patterns
  - [x] Detect `BREAKING CHANGE:` or `!:` in commit messages (major version)
  - [x] Detect `feat:` prefix in commit messages (minor version)
  - [x] Return tuple of (version_label, alt_label) or (None, None) for patch
  - [x] Handle multi-line commit messages correctly
  - [x] Handle edge cases (empty messages, non-conventional commits)
  - [x] Add docstrings and type hints
  - **Files**: `.github/scripts/pr-labels/src/pr_labels/parser.py`
  - **Dependencies**: Phase 1 complete
  - **Testing**: Unit tests will be created in Phase 3
  - **Notes**: Logic should match current bash regex patterns: `(BREAKING CHANGE|!:)` and `^feat:`

- [x] **Task 3**: Create labeler module
  - [x] Create `.github/scripts/pr-labels/src/pr_labels/labeler.py`
  - [x] Implement function to get all commits from PR using `pr.get_commits()`
  - [x] Implement function to check if label exists using `repo.get_label(label_name)` with error handling
  - [x] Implement function to create label if missing using `repo.create_label(name, color, description)`
  - [x] Implement function to get existing PR labels using `pr.get_labels()`
  - [x] Implement function to remove conflicting labels using `pr.remove_from_labels(label_name)`
  - [x] Implement function to add labels using `pr.add_to_labels(label_name)`
  - [x] Implement main labeling logic that:
    - Gets all commits from PR
    - Parses commits to determine version bump type
    - Removes existing conflicting labels (version: major, version: minor, version: patch, breaking, feature)
    - Ensures target labels exist (creates if missing)
    - Applies correct version and semantic labels
  - [x] Add comprehensive error handling with `GithubException`
  - [x] Add docstrings and type hints
  - **Files**: `.github/scripts/pr-labels/src/pr_labels/labeler.py`
  - **Dependencies**: Tasks 1 and 2 complete
  - **Testing**: Unit tests will be created in Phase 3
  - **Notes**: Label colors and descriptions should match existing labels in repository

- [x] **Task 4**: Create main entry point
  - [x] Create `.github/scripts/pr-labels/src/pr_labels/__main__.py`
  - [x] Implement `main()` function that:
    - Reads `GITHUB_TOKEN` from environment (required)
    - Reads `GITHUB_REPOSITORY` from environment (required)
    - Reads `GITHUB_EVENT_PATH` or `PR_NUMBER` from environment to get PR number
    - Initializes `GitHubClient`
    - Calls labeler to apply labels
    - Handles errors and exits with appropriate codes
  - [x] Add `if __name__ == "__main__":` block
  - [x] Add error messages to stderr, info messages to stdout
  - [x] Add docstrings
  - **Files**: `.github/scripts/pr-labels/src/pr_labels/__main__.py`
  - **Dependencies**: Tasks 1, 2, 3 complete
  - **Testing**: Integration tests will be created in Phase 3
  - **Notes**: Match pattern from `release-version/src/release_version/__main__.py`

### Phase 3: Testing

**Objective**: Create comprehensive test coverage for all modules

- [x] **Task 1**: Create test infrastructure
  - [x] Create `.github/scripts/pr-labels/tests/__init__.py`
  - [x] Create `.github/scripts/pr-labels/tests/conftest.py` with pytest fixtures
  - [x] Add fixtures for mocked GitHub client, repository, PR, and commits
  - [x] Add fixtures for sample commit messages (breaking, feature, patch)
  - **Files**: `.github/scripts/pr-labels/tests/__init__.py`, `.github/scripts/pr-labels/tests/conftest.py`
  - **Dependencies**: Phase 2 complete
  - **Testing**: Run `uv run pytest` to verify fixtures work
  - **Notes**: Match pattern from `release-version/tests/conftest.py`

- [x] **Task 2**: Create unit tests
  - [x] Create `.github/scripts/pr-labels/tests/test_github_client.py`
    - [x] Test `GitHubClient.__init__()`
    - [x] Test `get_repo()` success case
    - [x] Test `get_repo()` error handling
    - [x] Test `get_pull()` success case
    - [x] Test `get_pull()` error handling
  - [x] Create `.github/scripts/pr-labels/tests/test_parser.py`
    - [x] Test parsing breaking change commits (`BREAKING CHANGE:`)
    - [x] Test parsing breaking change commits (`!:`)
    - [x] Test parsing feature commits (`feat:`)
    - [x] Test parsing patch commits (`fix:`, `chore:`, etc.)
    - [x] Test multi-line commit messages
    - [x] Test empty commit messages
    - [x] Test non-conventional commit messages
    - [x] Test multiple commits with different types (should return highest priority)
  - [x] Create `.github/scripts/pr-labels/tests/test_labeler.py`
    - [x] Test label existence check
    - [x] Test label creation when missing
    - [x] Test getting existing PR labels
    - [x] Test removing conflicting labels
    - [x] Test adding new labels
    - [x] Test full labeling flow for major version
    - [x] Test full labeling flow for minor version
    - [x] Test full labeling flow for patch version
    - [x] Test error handling for GitHub API failures
  - **Files**: `.github/scripts/pr-labels/tests/test_*.py`
  - **Dependencies**: Task 1 complete
  - **Testing**: Run `uv run pytest` and verify all tests pass
  - **Notes**: Use mocking extensively, match patterns from `release-version/tests/`

- [x] **Task 3**: Create integration test structure
  - [x] Create `.github/scripts/pr-labels/tests/test_integration.py` (can be minimal, focus on unit tests)
  - [x] Document how to run tests locally
  - [x] Verify test coverage is comprehensive
  - **Files**: `.github/scripts/pr-labels/tests/test_integration.py`
  - **Dependencies**: Task 2 complete
  - **Testing**: Run `uv run pytest --cov` to check coverage
  - **Notes**: Integration tests may require GitHub token, so focus on unit tests with mocks

### Phase 4: Integration and Documentation

**Objective**: Integrate Python script into workflow and update documentation

- [x] **Task 1**: Update GitHub workflow
  - [x] Read `.github/workflows/pr-label.yml`
  - [x] Replace bash script steps with Python script execution
  - [x] Add step to setup uv (matching pattern from other workflows)
  - [x] Add step to run Python script using `uv run`
  - [x] Remove `gh CLI availability` check step
  - [x] Keep same workflow triggers and permissions
  - [x] Ensure `GITHUB_TOKEN` and `GITHUB_REPOSITORY` are available to script
  - [x] Pass PR number to script (from `github.event.pull_request.number`)
  - **Files**: `.github/workflows/pr-label.yml`
  - **Dependencies**: Phase 2 and 3 complete
  - **Testing**: Create test PR to verify workflow runs successfully
  - **Notes**: Match pattern from workflows that use `release-version` or `release-notes` scripts

- [x] **Task 2**: Update Dependabot configuration
  - [x] Read `.github/dependabot.yml`
  - [x] Add new pip package ecosystem entry for `.github/scripts/pr-labels`
  - [x] Match configuration from existing `release-version` and `release-notes` entries
  - [x] Set schedule, labels, reviewers, and assignees
  - **Files**: `.github/dependabot.yml`
  - **Dependencies**: Phase 1 complete
  - **Testing**: Verify Dependabot configuration syntax
  - **Notes**: Follow exact pattern from existing pip entries

- [x] **Task 3**: Create README and update documentation
  - [x] Create `.github/scripts/pr-labels/README.md` with:
    - [x] Description of the script
    - [x] Installation instructions using `uv sync`
    - [x] Usage instructions
    - [x] Environment variables required
    - [x] Testing instructions
    - [x] Constraints and requirements
  - [x] Update main repository documentation if needed (DEVELOPMENT.md, etc.)
  - [x] Add note about commit message format requirement (include "fixes #9" when committing)
  - **Files**: `.github/scripts/pr-labels/README.md`, potentially `DEVELOPMENT.md`
  - **Dependencies**: All phases complete
  - **Testing**: Verify documentation is accurate
  - **Notes**: Match style from `.github/scripts/release-version/README.md` or `.github/scripts/release-notes/README.md`

## Files to Modify/Create
- **New Files**:
  - `.github/scripts/pr-labels/pyproject.toml` - Project configuration
  - `.github/scripts/pr-labels/uv.lock` - Dependency lock file
  - `.github/scripts/pr-labels/src/pr_labels/__init__.py` - Package init
  - `.github/scripts/pr-labels/src/pr_labels/__main__.py` - Main entry point
  - `.github/scripts/pr-labels/src/pr_labels/github_client.py` - GitHub API client wrapper
  - `.github/scripts/pr-labels/src/pr_labels/parser.py` - Commit message parser
  - `.github/scripts/pr-labels/src/pr_labels/labeler.py` - Label management logic
  - `.github/scripts/pr-labels/tests/__init__.py` - Test package init
  - `.github/scripts/pr-labels/tests/conftest.py` - Pytest fixtures
  - `.github/scripts/pr-labels/tests/test_github_client.py` - GitHub client tests
  - `.github/scripts/pr-labels/tests/test_parser.py` - Parser tests
  - `.github/scripts/pr-labels/tests/test_labeler.py` - Labeler tests
  - `.github/scripts/pr-labels/tests/test_integration.py` - Integration tests
  - `.github/scripts/pr-labels/README.md` - Documentation
- **Modified Files**:
  - `.github/workflows/pr-label.yml` - Replace bash script with Python script execution
  - `.github/dependabot.yml` - Add pip ecosystem entry for pr-labels

## Testing Strategy
- **Unit Tests**:
  - Test GitHubClient methods with mocked PyGithub objects
  - Test commit parser with various commit message formats
  - Test labeler logic with mocked PR and repository objects
  - Test error handling for all GitHub API operations
  - Achieve high code coverage (>90%)
- **Integration Tests**:
  - Test full workflow from PR number to label application (with mocks)
  - Test label creation when labels don't exist
  - Test label removal and re-application
- **Manual Testing**:
  - Create test PRs with different commit types to verify labels are applied correctly
  - Verify workflow runs successfully in GitHub Actions
  - Test edge cases (empty PRs, non-conventional commits, etc.)

## Breaking Changes
None - this is a replacement of existing functionality with the same behavior and label names.

## Migration Guide
N/A - No breaking changes. The workflow will continue to work the same way from a user perspective.

## Documentation Updates
- [x] Create `.github/scripts/pr-labels/README.md` with installation, usage, and testing instructions
- [x] Update `.github/workflows/pr-label.yml` comments if needed
- [x] Add doc comments to all public functions and classes
- [x] Document environment variables in README

## Success Criteria
- Python script successfully replaces bash-based labeling logic
- All existing label behaviors are preserved (major, minor, patch detection)
- Comprehensive test coverage (>90%) with all tests passing
- Workflow runs successfully in GitHub Actions without errors
- Labels are created automatically if they don't exist
- No dependency on GitHub CLI (`gh`) tool
- Code follows existing project patterns and conventions
- Dependabot is configured to update Python dependencies

## Risks and Mitigations
- **Risk**: PyGithub API changes or breaking changes in future versions
  - **Mitigation**: Pin `pygithub>=2.0.0` version, use Dependabot to track updates, comprehensive tests will catch API changes
- **Risk**: Python runtime not available in GitHub Actions (unlikely)
  - **Mitigation**: Other scripts already use Python/uv, so runtime is established. Verify in workflow setup step.
- **Risk**: Label creation requires additional permissions
  - **Mitigation**: Current workflow already has `pull-requests: write` which includes label management. Verify permissions are sufficient.
- **Risk**: Commit message parsing differences from bash version
  - **Mitigation**: Comprehensive test coverage with same test cases as current bash logic, side-by-side comparison testing

## References
- Related REQ document: `plan/25W48/REQ_ROBUST_PR_LABELING.md`
- Related issues: #9
- Related PRs: (to be created)
- Design documents: N/A
- External references:
  - [PyGithub Documentation](https://pygithub.readthedocs.io/)
  - [Conventional Commits Specification](https://www.conventionalcommits.org/)
  - Existing scripts: `.github/scripts/release-version/`, `.github/scripts/release-notes/`

## Implementation Notes
- **Important**: When committing the implementation, include "fixes #9" in the commit message as specified in the REQ document
- Follow existing code style and patterns from `release-version` and `release-notes` scripts
- Ensure all error messages are clear and actionable
- Use type hints throughout for better code clarity
- Consider adding logging instead of print statements for better observability (optional enhancement)
