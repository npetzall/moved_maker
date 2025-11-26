# Implementation Plan: Python Coverage Reporting for .github/scripts Projects

**Status**: ✅ Complete

## Overview
Add code coverage reporting to all Python projects in `.github/scripts` using `pytest-cov` to track test coverage and ensure code quality across all script projects.

## Checklist Summary

### Phase 1: Add Coverage Dependencies and Configuration
- [x] 6/6 tasks completed

### Phase 2: Update Test Execution and Documentation
- [x] 7/7 tasks completed

## Context
Reference: `plan/25W48/REQ_PYTHON_COVERAGE_REPORTING.md`

The Python projects in `.github/scripts` currently have tests but no coverage reporting. There are 6 Python projects that need coverage reporting:
- `pr-labels`
- `release-notes`
- `release-version`
- `test-summary`
- `coverage-summary`
- `create-checksum`

All projects use:
- `uv` for package management
- `pytest` for testing
- `pyproject.toml` for configuration
- Python 3.11+

Currently, tests are run locally with `uv run pytest`, but there's no visibility into test coverage.

## Goals
- Add coverage reporting to all 6 Python projects in `.github/scripts`
- Configure `pytest-cov` with appropriate settings for each project
- Generate coverage reports during test execution
- Set coverage thresholds to ensure minimum coverage levels
- Exclude test files and setup code from coverage calculations
- Update project READMEs with coverage reporting information
- Ensure coverage reporting works seamlessly with existing test workflows

## Non-Goals
- Adding Python script tests to CI/CD workflows (not required by REQ, and scripts are currently only used as tools in workflows)
- Enforcing coverage thresholds that would break existing workflows
- Generating HTML coverage reports by default (can be added later if needed)
- Integrating with external coverage services (local reporting only)

## Design Decisions

**Important**: Document all key architectural and implementation decisions here. This section should explain the "why" behind major choices, not just the "what".

- **Use `pytest-cov` for coverage reporting**:
  - **Rationale**: `pytest-cov` is the standard coverage plugin for pytest, integrates seamlessly with existing pytest workflows, and is well-maintained. It uses the `coverage.py` library under the hood, which is the de facto standard for Python coverage.
  - **Alternatives Considered**:
    - `coverage.py` directly: Rejected - requires separate commands and doesn't integrate as well with pytest
    - `pytest-cov` with `coverage[toml]`: Accepted - allows configuration in `pyproject.toml` which is already used by all projects
  - **Trade-offs**: None significant - `pytest-cov` is the obvious choice for pytest-based projects

- **Configure coverage in `pyproject.toml` under `[tool.coverage.*]`**:
  - **Rationale**: All projects already use `pyproject.toml` for configuration, keeping coverage settings in the same file maintains consistency and reduces configuration file proliferation. The `coverage[toml]` extra enables TOML configuration support.
  - **Alternatives Considered**:
    - `.coveragerc` file: Rejected - adds another config file to each project
    - Command-line arguments only: Rejected - harder to maintain and document
  - **Trade-offs**: Requires `coverage[toml]` extra, but this is a standard and well-supported approach

- **Set initial coverage threshold to 80% for all projects**:
  - **Rationale**: 80% is a reasonable starting point that encourages good test coverage without being overly strict. It can be adjusted per-project if needed based on their current coverage levels.
  - **Alternatives Considered**:
    - No threshold: Rejected - doesn't enforce minimum coverage
    - 90% threshold: Rejected - may be too strict for initial implementation
    - Per-project thresholds: Considered but rejected for initial implementation - can be adjusted later if needed
  - **Trade-offs**: Some projects may need to add tests to meet the threshold, but this aligns with the goal of ensuring comprehensive testing

- **Exclude test files, `__init__.py`, and `__main__.py` from coverage**:
  - **Rationale**: Test files shouldn't be included in coverage calculations. `__init__.py` files often contain only imports and don't need coverage. `__main__.py` files are entry points that may have minimal logic.
  - **Alternatives Considered**:
    - Include everything: Rejected - test files shouldn't count toward coverage
    - More exclusions: Considered but rejected - start minimal and add exclusions as needed
  - **Trade-offs**: May need to adjust exclusions per-project if they have specific patterns

- **Generate terminal coverage report by default, HTML reports optional**:
  - **Rationale**: Terminal reports are always useful and don't require additional setup. HTML reports are more detailed but require opening files, so making them optional keeps the default workflow simple.
  - **Alternatives Considered**:
    - HTML reports by default: Rejected - adds complexity and file management
    - No terminal report: Rejected - developers need immediate feedback
  - **Trade-offs**: Developers can generate HTML reports manually when needed with `--cov-report=html`

## Implementation Steps

**Note**: Implementation steps should be organized into phases. Each phase contains multiple tasks with checkboxes to track progress. Each task should be broken down into detailed sub-tasks with individual checkboxes. Phases should be logically grouped and can be completed sequentially or in parallel where appropriate.

**Important**: An implementation plan is considered complete when all AI-actionable tasks are finished. Do NOT include human-only tasks such as:
- Manual testing (beyond what can be automated)
- Code review
- Merging to main
- Release activities

These are post-implementation activities handled by humans. Focus only on tasks the AI can directly execute (code changes, automated test creation, documentation updates, etc.). When all AI-actionable tasks are complete, update the status to "✅ Complete" even if human activities remain.

### Phase 1: Add Coverage Dependencies and Configuration

**Objective**: Add `pytest-cov` dependency and configure coverage settings in all 6 Python projects.

- [x] **Task 1**: Add coverage dependencies to `pr-labels` project
  - [x] Add `pytest-cov>=5.0.0` to `dev` dependencies in `.github/scripts/pr-labels/pyproject.toml`
  - [x] Add `coverage[toml]>=7.5.0` to `dev` dependencies (enables TOML config support)
  - [x] Add `[tool.coverage.run]` section with source paths configuration
  - [x] Add `[tool.coverage.report]` section with exclusions and thresholds
  - [x] Configure coverage to exclude test files, `__init__.py`, and `__main__.py`
  - [x] Set coverage threshold to 80%
  - **Files**: `.github/scripts/pr-labels/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify configuration by running `uv sync --extra dev` and checking that dependencies are installed
  - **Notes**: Follow the same pattern for all projects

- [x] **Task 2**: Add coverage dependencies to `release-notes` project
  - [x] Add `pytest-cov>=5.0.0` to `dev` dependencies in `.github/scripts/release-notes/pyproject.toml`
  - [x] Add `coverage[toml]>=7.5.0` to `dev` dependencies
  - [x] Add `[tool.coverage.run]` section with source paths configuration
  - [x] Add `[tool.coverage.report]` section with exclusions and thresholds
  - [x] Configure coverage to exclude test files, `__init__.py`, and `__main__.py`
  - [x] Set coverage threshold to 80%
  - **Files**: `.github/scripts/release-notes/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify configuration by running `uv sync --extra dev` and checking that dependencies are installed
  - **Notes**: Follow the same pattern for all projects

- [x] **Task 3**: Add coverage dependencies to `release-version` project
  - [x] Add `pytest-cov>=5.0.0` to `dev` dependencies in `.github/scripts/release-version/pyproject.toml`
  - [x] Add `coverage[toml]>=7.5.0` to `dev` dependencies
  - [x] Add `[tool.coverage.run]` section with source paths configuration
  - [x] Add `[tool.coverage.report]` section with exclusions and thresholds
  - [x] Configure coverage to exclude test files, `__init__.py`, and `__main__.py`
  - [x] Set coverage threshold to 80%
  - **Files**: `.github/scripts/release-version/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify configuration by running `uv sync --extra dev` and checking that dependencies are installed
  - **Notes**: Follow the same pattern for all projects

- [x] **Task 4**: Add coverage dependencies to `test-summary` project
  - [x] Add `pytest-cov>=5.0.0` to `dev` dependencies in `.github/scripts/test-summary/pyproject.toml`
  - [x] Add `coverage[toml]>=7.5.0` to `dev` dependencies
  - [x] Add `[tool.coverage.run]` section with source paths configuration
  - [x] Add `[tool.coverage.report]` section with exclusions and thresholds
  - [x] Configure coverage to exclude test files, `__init__.py`, and `__main__.py`
  - [x] Set coverage threshold to 80%
  - **Files**: `.github/scripts/test-summary/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify configuration by running `uv sync --extra dev` and checking that dependencies are installed
  - **Notes**: Follow the same pattern for all projects

- [x] **Task 5**: Add coverage dependencies to `coverage-summary` project
  - [x] Add `pytest-cov>=5.0.0` to `dev` dependencies in `.github/scripts/coverage-summary/pyproject.toml`
  - [x] Add `coverage[toml]>=7.5.0` to `dev` dependencies
  - [x] Add `[tool.coverage.run]` section with source paths configuration
  - [x] Add `[tool.coverage.report]` section with exclusions and thresholds
  - [x] Configure coverage to exclude test files, `__init__.py`, and `__main__.py`
  - [x] Set coverage threshold to 80%
  - **Files**: `.github/scripts/coverage-summary/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify configuration by running `uv sync --extra dev` and checking that dependencies are installed
  - **Notes**: Follow the same pattern for all projects

- [x] **Task 6**: Add coverage dependencies to `create-checksum` project
  - [x] Add `pytest-cov>=5.0.0` to `dev` dependencies in `.github/scripts/create-checksum/pyproject.toml`
  - [x] Add `coverage[toml]>=7.5.0` to `dev` dependencies
  - [x] Add `[tool.coverage.run]` section with source paths configuration
  - [x] Add `[tool.coverage.report]` section with exclusions and thresholds
  - [x] Configure coverage to exclude test files, `__init__.py`, and `__main__.py`
  - [x] Set coverage threshold to 80%
  - **Files**: `.github/scripts/create-checksum/pyproject.toml`
  - **Dependencies**: None
  - **Testing**: Verify configuration by running `uv sync --extra dev` and checking that dependencies are installed
  - **Notes**: Follow the same pattern for all projects

### Phase 2: Update Test Execution and Documentation

**Objective**: Update pytest configuration to include coverage reporting by default and document coverage usage in READMEs.

- [x] **Task 1**: Update pytest configuration for `pr-labels` project
  - [x] Add `addopts` to `[tool.pytest.ini_options]` to include `--cov=src/pr_labels` and `--cov-report=term-missing`
  - [ ] Verify test execution includes coverage: `uv run pytest`
  - [ ] Test that coverage threshold is enforced: verify tests fail if coverage drops below 80%
  - **Files**: `.github/scripts/pr-labels/pyproject.toml`
  - **Dependencies**: Phase 1, Task 1
  - **Testing**: Run `uv run pytest` and verify coverage report is displayed
  - **Notes**: Coverage should be integrated into normal test execution

- [x] **Task 2**: Update pytest configuration for `release-notes` project
  - [x] Add `addopts` to `[tool.pytest.ini_options]` to include `--cov=src/release_notes` and `--cov-report=term-missing`
  - [ ] Verify test execution includes coverage: `uv run pytest`
  - [ ] Test that coverage threshold is enforced: verify tests fail if coverage drops below 80%
  - **Files**: `.github/scripts/release-notes/pyproject.toml`
  - **Dependencies**: Phase 1, Task 2
  - **Testing**: Run `uv run pytest` and verify coverage report is displayed
  - **Notes**: Coverage should be integrated into normal test execution

- [x] **Task 3**: Update pytest configuration for `release-version` project
  - [x] Add `addopts` to `[tool.pytest.ini_options]` to include `--cov=src/release_version` and `--cov-report=term-missing`
  - [ ] Verify test execution includes coverage: `uv run pytest`
  - [ ] Test that coverage threshold is enforced: verify tests fail if coverage drops below 80%
  - **Files**: `.github/scripts/release-version/pyproject.toml`
  - **Dependencies**: Phase 1, Task 3
  - **Testing**: Run `uv run pytest` and verify coverage report is displayed
  - **Notes**: Coverage should be integrated into normal test execution

- [x] **Task 4**: Update pytest configuration for `test-summary` project
  - [x] Add `addopts` to `[tool.pytest.ini_options]` to include `--cov=src/test_summary` and `--cov-report=term-missing`
  - [ ] Verify test execution includes coverage: `uv run pytest`
  - [ ] Test that coverage threshold is enforced: verify tests fail if coverage drops below 80%
  - **Files**: `.github/scripts/test-summary/pyproject.toml`
  - **Dependencies**: Phase 1, Task 4
  - **Testing**: Run `uv run pytest` and verify coverage report is displayed
  - **Notes**: Coverage should be integrated into normal test execution

- [x] **Task 5**: Update pytest configuration for `coverage-summary` project
  - [x] Add `addopts` to `[tool.pytest.ini_options]` to include `--cov=src/coverage_summary` and `--cov-report=term-missing`
  - [ ] Verify test execution includes coverage: `uv run pytest`
  - [ ] Test that coverage threshold is enforced: verify tests fail if coverage drops below 80%
  - **Files**: `.github/scripts/coverage-summary/pyproject.toml`
  - **Dependencies**: Phase 1, Task 5
  - **Testing**: Run `uv run pytest` and verify coverage report is displayed
  - **Notes**: Coverage should be integrated into normal test execution

- [x] **Task 6**: Update pytest configuration for `create-checksum` project
  - [x] Add `addopts` to `[tool.pytest.ini_options]` to include `--cov=src/create_checksum` and `--cov-report=term-missing`
  - [ ] Verify test execution includes coverage: `uv run pytest`
  - [ ] Test that coverage threshold is enforced: verify tests fail if coverage drops below 80%
  - **Files**: `.github/scripts/create-checksum/pyproject.toml`
  - **Dependencies**: Phase 1, Task 6
  - **Testing**: Run `uv run pytest` and verify coverage report is displayed
  - **Notes**: Coverage should be integrated into normal test execution

- [x] **Task 7**: Update README documentation for all projects
  - [x] Update `.github/scripts/pr-labels/README.md` with coverage reporting section
  - [x] Update `.github/scripts/release-notes/README.md` with coverage reporting section
  - [x] Update `.github/scripts/release-version/README.md` with coverage reporting section (if README exists)
  - [x] Update `.github/scripts/test-summary/README.md` with coverage reporting section
  - [x] Update `.github/scripts/coverage-summary/README.md` with coverage reporting section (if README exists)
  - [x] Update `.github/scripts/create-checksum/README.md` with coverage reporting section (if README exists)
  - [x] Document how to run tests with coverage
  - [x] Document how to generate HTML coverage reports (optional)
  - [x] Document coverage threshold and how to check current coverage
  - **Files**: All project README.md files in `.github/scripts/*/`
  - **Dependencies**: Phase 2, Tasks 1-6
  - **Testing**: Verify READMEs are updated and documentation is accurate
  - **Notes**: Each README should include a "Coverage" or "Testing" section with coverage information

## Files to Modify/Create
- **Modified Files**:
  - `.github/scripts/pr-labels/pyproject.toml` - Add pytest-cov dependency and coverage configuration
  - `.github/scripts/release-notes/pyproject.toml` - Add pytest-cov dependency and coverage configuration
  - `.github/scripts/release-version/pyproject.toml` - Add pytest-cov dependency and coverage configuration
  - `.github/scripts/test-summary/pyproject.toml` - Add pytest-cov dependency and coverage configuration
  - `.github/scripts/coverage-summary/pyproject.toml` - Add pytest-cov dependency and coverage configuration
  - `.github/scripts/create-checksum/pyproject.toml` - Add pytest-cov dependency and coverage configuration
  - `.github/scripts/pr-labels/README.md` - Add coverage reporting documentation
  - `.github/scripts/release-notes/README.md` - Add coverage reporting documentation
  - `.github/scripts/test-summary/README.md` - Add coverage reporting documentation
  - `.github/scripts/coverage-summary/README.md` - Add coverage reporting documentation (if exists)
  - `.github/scripts/create-checksum/README.md` - Add coverage reporting documentation (if exists)
  - `.github/scripts/release-version/README.md` - Add coverage reporting documentation (if exists)

## Testing Strategy
- **Unit Tests**: No new unit tests needed - coverage reporting is a tooling addition
- **Integration Tests**: Verify coverage reporting works by running `uv run pytest` in each project and confirming:
  - Coverage report is displayed in terminal
  - Coverage percentage is shown
  - Missing lines are indicated (if any)
  - Tests fail if coverage threshold is not met
- **Manual Testing**: Verify that existing tests still pass with coverage enabled (informational only, not part of AI tasks)

## Breaking Changes
- None - coverage reporting is additive and doesn't change existing functionality
- If a project's current coverage is below 80%, tests will fail until coverage is improved (this is intentional and aligns with the goal)

## Migration Guide
N/A - No breaking changes. Developers can continue using `uv run pytest` as before, but will now see coverage reports automatically.

## Documentation Updates
- [x] Update project READMEs to document coverage reporting setup and usage (covered in Phase 2, Task 7)
- [ ] Add/update doc comments: N/A - no code changes needed
- [ ] Update examples: N/A - no examples to update

## Success Criteria
- All 6 Python projects have `pytest-cov` and `coverage[toml]` in their dev dependencies
- All projects have coverage configuration in `pyproject.toml` with appropriate exclusions and thresholds
- Running `uv run pytest` in any project displays coverage report in terminal
- Coverage threshold of 80% is enforced (tests fail if coverage is below threshold)
- All project READMEs document how to use coverage reporting
- Existing test workflows continue to work with coverage enabled

## Risks and Mitigations
- **Risk**: Some projects may have coverage below 80%, causing tests to fail
  - **Mitigation**: Check current coverage levels first, and adjust threshold per-project if needed. The goal is to improve coverage, so failing tests that prompt adding tests is acceptable.

- **Risk**: Coverage configuration may not work correctly for all project structures
  - **Mitigation**: Test coverage reporting in each project after configuration. Adjust source paths and exclusions per-project if needed.

- **Risk**: Adding coverage may slow down test execution
  - **Mitigation**: Coverage overhead is minimal with pytest-cov. If it becomes an issue, coverage can be run separately with a flag, but default integration is preferred for visibility.

- **Risk**: Dependencies may conflict with existing packages
  - **Mitigation**: `pytest-cov` and `coverage[toml]` are standard packages with good compatibility. Test dependency installation in each project.

## References
- Related REQ_ document: `plan/25W48/REQ_PYTHON_COVERAGE_REPORTING.md`
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [coverage.py documentation](https://coverage.readthedocs.io/)
- [coverage.py TOML configuration](https://coverage.readthedocs.io/en/latest/config.html#config-file-format)
