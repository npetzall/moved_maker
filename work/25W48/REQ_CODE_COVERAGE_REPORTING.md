# Implementation Plan: Code Coverage Reporting in Workflow Summaries

**Status**: ✅ Complete

## Overview
Implement rich markdown code coverage reporting in GitHub Actions job step summaries for build, release, and PR workflows. Create a Python script to parse coverage JSON output from `cargo llvm-cov`, generate formatted markdown summaries with tables and Mermaid pie charts, and write them to `$GITHUB_STEP_SUMMARY`.

## Checklist Summary

### Phase 1: Coverage Summary Parser Script
- [x] 3/3 tasks completed

### Phase 2: Workflow Integration
- [x] 2/2 tasks completed

### Phase 3: Testing and Documentation
- [x] 3/3 tasks completed

**Overall Progress**: 8/8 tasks completed (100%)

## Context
Reference to corresponding REQ_ document: `plan/25W48/REQ_CODE_COVERAGE_REPORTING.md`

**Current State**: Code coverage results are only visible in the workflow log output or in generated coverage files. Developers must manually check coverage files or scroll through logs to find coverage information. Coverage JSON is generated but not summarized in the workflow run summary.

**Problem**: Without a visual summary, it's difficult to quickly assess code coverage status after a workflow run. Coverage regressions and low-coverage files are buried in log output or separate files, making it harder to maintain code quality standards.

## Goals
- Create a Python script to parse coverage JSON output from `cargo llvm-cov report --json`
- Generate rich markdown summaries with overall coverage percentage, file-by-file breakdown, and Mermaid pie charts
- Integrate coverage summary generation into all workflows that generate coverage (PR, release-build)
- Display coverage metrics (line, branch, function coverage) with visual indicators for thresholds
- Show file-by-file breakdown for changed files in PRs
- Compare coverage with baseline for regression detection (when baseline available)
- Include links to detailed coverage reports if available
- Handle edge cases (coverage generation fails, missing files, etc.)

## Non-Goals
- PR comments for coverage results (job step summaries are sufficient)
- External coverage services or tools
- Modifying coverage generation logic
- Changing coverage threshold checking behavior
- Baseline coverage storage/retrieval system (baseline comparison is optional enhancement)

## Design Decisions

- **Python script for parsing**: Use Python to parse coverage JSON and generate markdown summaries
  - **Rationale**: The project already uses Python scripts in `.github/scripts/` for workflow automation (e.g., `test-summary`, `release-notes`). Python has excellent JSON parsing capabilities and is well-suited for text generation and markdown formatting.
  - **Alternatives Considered**: Bash script with `jq` - rejected due to complexity of markdown generation and Mermaid chart creation. Rust binary - rejected as it would require compilation and add complexity.
  - **Trade-offs**: Requires Python runtime in workflows (already available via `actions/setup-python` or `uv`)

- **Use `uv` for package management**: Use `uv` to manage Python dependencies and virtual environments
  - **Rationale**: All existing Python scripts in `.github/scripts/` use `uv` for package management. This ensures consistency across the project and leverages `uv`'s fast dependency resolution.
  - **Alternatives Considered**: pip, poetry - rejected to maintain consistency with existing scripts.
  - **Trade-offs**: Requires `uv` installation in workflows (already available or easily added)

- **Use `pytest` for testing**: Use `pytest` as the testing framework
  - **Rationale**: All existing Python scripts in `.github/scripts/` use `pytest` for testing. It provides excellent test discovery, fixtures, and reporting capabilities.
  - **Alternatives Considered**: unittest, nose - rejected to maintain consistency with existing scripts.
  - **Trade-offs**: Adds pytest as a dev dependency, but provides better testing capabilities than standard library unittest

- **Parse JSON output from cargo llvm-cov**: Parse the JSON report that `cargo llvm-cov report --json` already generates
  - **Rationale**: The coverage workflow already generates JSON format (in `coverage.json`). No need to change coverage generation or add additional output formats. The JSON structure is well-defined and contains all necessary metrics.
  - **Alternatives Considered**: Parse LCOV format - rejected as JSON is more structured and easier to parse. HTML parsing - rejected as JSON is the source of truth.
  - **Trade-offs**: JSON parsing is straightforward and the format is already generated

- **Mermaid pie charts for visualization**: Use Mermaid syntax for pie charts showing coverage distribution
  - **Rationale**: GitHub Actions job summaries natively support Mermaid charts. Pie charts provide immediate visual feedback on coverage distribution (covered vs uncovered code).
  - **Alternatives Considered**: ASCII art charts - rejected as less visually appealing. Bar charts - rejected as pie charts are more compact and better for showing proportions.
  - **Trade-offs**: Mermaid charts require proper syntax, but GitHub's native support makes them the best choice

- **Separate script in `.github/scripts/`**: Create a new Python package following the existing pattern
  - **Rationale**: Consistent with existing script structure (`test-summary`, `release-notes`). Allows for proper testing and maintainability.
  - **Alternatives Considered**: Inline bash script in workflows - rejected as it would be harder to test and maintain.
  - **Trade-offs**: Requires creating a new package structure, but provides better organization and testability

- **Summary generation after coverage check**: Generate summary as a separate step after coverage threshold check
  - **Rationale**: Allows summary generation even if threshold check fails. Can access coverage JSON file reliably. Summary provides additional context beyond threshold pass/fail.
  - **Alternatives Considered**: Generate during coverage generation - rejected as it would require modifying coverage output parsing and might miss edge cases.
  - **Trade-offs**: Adds an extra workflow step, but provides better reliability and error handling

- **File-by-file breakdown for changed files (PRs only)**: Show detailed coverage for files changed in PRs
  - **Rationale**: In PR workflows, developers care most about coverage of files they changed. Full file listing would be too verbose. In release workflows, overall metrics are more important.
  - **Alternatives Considered**: Always show all files - rejected as too verbose. Never show file breakdown - rejected as less useful for PR reviews.
  - **Trade-offs**: Requires detecting changed files in PR context, but provides more actionable information

- **Optional baseline comparison**: Support baseline comparison when baseline coverage data is available
  - **Rationale**: Regression detection is valuable but requires baseline storage/retrieval which is out of scope. Making it optional allows future enhancement without breaking current functionality.
  - **Alternatives Considered**: Always require baseline - rejected as it adds complexity and dependency. Never support baseline - rejected as it's a valuable feature mentioned in REQ.
  - **Trade-offs**: Baseline comparison is optional and may not be available initially, but the structure supports it

## Implementation Steps

### Phase 1: Coverage Summary Parser Script

**Objective**: Create a Python script that parses coverage JSON and generates markdown summaries with tables and Mermaid charts.

- [x] **Task 1**: Create Python package structure for coverage summary script
  - [x] Create directory structure: `.github/scripts/coverage-summary/`
  - [x] Create `pyproject.toml` with project metadata:
    - [x] Use `uv` for package management (follow existing script patterns)
    - [x] Set `requires-python = ">=3.11"`
    - [x] Use standard library only for dependencies (no external dependencies needed)
    - [x] Add `pytest>=8.0.0` to `[project.optional-dependencies]` dev section
    - [x] Configure `[build-system]` with `hatchling` (matching existing scripts)
    - [x] Add `[tool.pytest.ini_options]` section with testpaths, python_files, python_classes, python_functions
  - [x] Create `README.md` with usage instructions (include `uv sync --extra dev` and `uv run pytest` commands)
  - [x] Create `src/coverage_summary/__init__.py`
  - [x] Create `src/coverage_summary/__main__.py` for CLI entry point
  - **Files**: `.github/scripts/coverage-summary/pyproject.toml`, `.github/scripts/coverage-summary/README.md`, `.github/scripts/coverage-summary/src/coverage_summary/__init__.py`, `.github/scripts/coverage-summary/src/coverage_summary/__main__.py`
  - **Dependencies**: Python 3.11+ (standard library only - json, pathlib, sys, argparse). Dev dependencies: pytest>=8.0.0
  - **Testing**: Verify package structure follows existing script patterns. Run `uv sync --extra dev` to verify setup.
  - **Notes**: Follow the structure of existing scripts like `test-summary` and `release-notes`. Use `uv` for package management and `pytest` for testing.

- [x] **Task 2**: Implement coverage JSON parser
  - [x] Create `src/coverage_summary/parser.py` module
  - [x] Implement function to load and parse JSON from file path
  - [x] Extract overall coverage metrics from `data[0].totals`:
    - [x] Line coverage percentage and count
    - [x] Branch coverage percentage and count
    - [x] Function coverage percentage and count
  - [x] Extract file-level coverage from `data[0].files`:
    - [x] File path
    - [x] Line coverage percentage
    - [x] Branch coverage percentage
    - [x] Function coverage percentage
    - [x] Line coverage count (covered/total)
    - [x] Branch coverage count (covered/total)
    - [x] Function coverage count (covered/total)
  - [x] Handle edge cases:
    - [x] Missing or invalid JSON file
    - [x] Empty coverage data
    - [x] Missing fields in JSON structure
  - [x] Add error handling with descriptive messages
  - **Files**: `.github/scripts/coverage-summary/src/coverage_summary/parser.py`
  - **Dependencies**: json (standard library)
  - **Testing**: Create unit tests with sample JSON data covering various scenarios (high coverage, low coverage, missing fields, invalid JSON)
  - **Notes**: Reference `.config/coverage-threshold-check.jq` to understand JSON structure. Use the same field paths for consistency.

- [x] **Task 3**: Implement markdown summary generator
  - [x] Create `src/coverage_summary/generator.py` module
  - [x] Implement function to generate overall coverage section:
    - [x] Overall coverage percentage with visual indicator (✅/⚠️/❌ based on thresholds)
    - [x] Line, branch, and function coverage metrics in a table
    - [x] Coverage thresholds (80% line, 70% branch, 85% function) as reference
  - [x] Implement function to generate Mermaid pie chart:
    - [x] Calculate covered vs uncovered percentages for lines
    - [x] Generate Mermaid pie chart syntax showing coverage distribution
    - [x] Use appropriate colors (green for covered, red for uncovered)
  - [x] Implement function to generate file-by-file breakdown table:
    - [x] Sort files by coverage percentage (lowest first for visibility)
    - [x] Include file path, line coverage %, branch coverage %, function coverage %
    - [x] Add visual indicators (✅/⚠️/❌) based on line coverage threshold (80%)
    - [x] Limit to changed files when `--changed-files` option is provided
  - [x] Implement function to generate regression section (optional):
    - [x] Compare current coverage with baseline when baseline file provided
    - [x] Show coverage changes (increase/decrease) with indicators
    - [x] Highlight regressions (coverage decreases)
  - [x] Implement function to write summary to `$GITHUB_STEP_SUMMARY`:
    - [x] Combine all sections into complete markdown
    - [x] Write to file path (default: `$GITHUB_STEP_SUMMARY` environment variable)
    - [x] Handle file write errors gracefully
  - [x] Add CLI argument parsing:
    - [x] `--json-path`: Path to coverage JSON file (required)
    - [x] `--summary-path`: Path to write summary (default: `$GITHUB_STEP_SUMMARY`)
    - [x] `--changed-files`: Path to file containing list of changed files (optional, one per line)
    - [x] `--baseline-json`: Path to baseline coverage JSON for comparison (optional)
    - [x] `--threshold-line`: Line coverage threshold (default: 80)
    - [x] `--threshold-branch`: Branch coverage threshold (default: 70)
    - [x] `--threshold-function`: Function coverage threshold (default: 85)
  - **Files**: `.github/scripts/coverage-summary/src/coverage_summary/generator.py`
  - **Dependencies**: json, pathlib, sys, argparse (standard library)
  - **Testing**: Create unit tests for each generation function with various coverage scenarios. Test markdown formatting and Mermaid syntax validity.
  - **Notes**: Follow markdown formatting best practices. Ensure Mermaid syntax is valid (test with GitHub's renderer if possible). Use emoji indicators consistently.

### Phase 2: Workflow Integration

**Objective**: Integrate coverage summary generation into PR and release-build workflows.

- [x] **Task 1**: Integrate into PR workflow
  - [x] Locate the `coverage` job in `.github/workflows/pull_request.yaml` (around line 138-180)
  - [x] Add step to detect changed files in PR:
    - [x] Use `git diff --name-only origin/${{ github.base_ref }}...HEAD` to get changed files
    - [x] Filter to only Rust source files (`.rs` files in `src/`)
    - [x] Write changed files list to a temporary file (one per line)
    - [x] Run this step after checkout but before coverage summary generation
  - [x] Add step to install `uv` (if not already present):
    - [x] Use `astral-sh/setup-uv@d7d33e16d4ecbbea0da49ecb6fcc16df877ddac8` action
    - [x] Place after checkout step
  - [x] Add step to generate coverage summary:
    - [x] Run after "Check coverage thresholds" step
    - [x] Use `if: always()` to run even if threshold check fails
    - [x] Change directory to `.github/scripts/coverage-summary`
    - [x] Run `uv sync --extra dev` to install dependencies
    - [x] Run `uv run python -m coverage_summary --json-path ../../../coverage.json --changed-files ../../../changed-files.txt`
    - [x] Handle errors gracefully (don't fail workflow if summary generation fails)
  - [x] Ensure coverage.json exists before summary generation (it's created in "Check coverage thresholds" step)
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: `uv` action, coverage summary script
  - **Testing**: Test workflow locally or in a test PR. Verify summary appears in workflow run summary. Test with various coverage scenarios.
  - **Notes**: Follow the pattern used in test-summary integration. Use `if: always()` to ensure summary is generated even if previous steps fail.

- [x] **Task 2**: Integrate into release-build workflow
  - [x] Locate the `coverage` job in `.github/workflows/release-build.yaml` (around line 92-137)
  - [x] Add step to install `uv` (if not already present):
    - [x] Use `astral-sh/setup-uv@d7d33e16d4ecbbea0da49ecb6fcc16df877ddac8` action
    - [x] Place after checkout step
  - [x] Add step to generate coverage summary:
    - [x] Run after "Check coverage thresholds" step
    - [x] Use `if: always()` to run even if threshold check fails
    - [x] Change directory to `.github/scripts/coverage-summary`
    - [x] Run `uv sync --extra dev` to install dependencies
    - [x] Run `uv run python -m coverage_summary --json-path ../../../coverage.json`
    - [x] Don't include `--changed-files` option (show all files or top N files with lowest coverage)
    - [x] Handle errors gracefully (don't fail workflow if summary generation fails)
  - [x] Ensure coverage.json exists before summary generation (it's created in "Check coverage thresholds" step)
  - **Files**: `.github/workflows/release-build.yaml`
  - **Dependencies**: `uv` action, coverage summary script
  - **Testing**: Test workflow in a release scenario. Verify summary appears in workflow run summary.
  - **Notes**: Release workflows don't need changed files filtering - overall metrics are more important. Consider showing top N files with lowest coverage instead of all files.

### Phase 3: Testing and Documentation

**Objective**: Create comprehensive tests and update documentation.

- [x] **Task 1**: Create unit tests for coverage parser
  - [x] Create `tests/test_parser.py`
  - [x] Test parsing valid JSON with all fields present
  - [x] Test parsing JSON with missing optional fields
  - [x] Test parsing invalid JSON (error handling)
  - [x] Test parsing empty coverage data
  - [x] Test extracting overall metrics (line, branch, function)
  - [x] Test extracting file-level metrics
  - [x] Test edge cases (zero coverage, 100% coverage, missing files)
  - [x] Use pytest fixtures for sample JSON data
  - **Files**: `.github/scripts/coverage-summary/tests/test_parser.py`
  - **Dependencies**: pytest, sample JSON files
  - **Testing**: Run `uv run pytest` to verify all tests pass
  - **Notes**: Create realistic sample JSON data based on actual `cargo llvm-cov` output structure.

- [x] **Task 2**: Create unit tests for markdown generator
  - [x] Create `tests/test_generator.py`
  - [x] Test overall coverage section generation
  - [x] Test Mermaid pie chart generation (verify syntax)
  - [x] Test file-by-file table generation
  - [x] Test changed files filtering
  - [x] Test regression comparison (when baseline provided)
  - [x] Test markdown formatting (headers, tables, code blocks)
  - [x] Test threshold indicators (✅/⚠️/❌) based on coverage values
  - [x] Test file write functionality
  - [x] Use pytest fixtures for coverage data
  - **Files**: `.github/scripts/coverage-summary/tests/test_generator.py`
  - **Dependencies**: pytest, sample coverage data
  - **Testing**: Run `uv run pytest` to verify all tests pass. Manually verify Mermaid syntax if possible.
  - **Notes**: Test with various coverage scenarios (high, low, mixed). Verify markdown is valid and readable.

- [x] **Task 3**: Update documentation and add integration tests
  - [x] Update `README.md` with:
    - [x] Usage examples for different scenarios (PR, release, with/without changed files)
    - [x] Command-line argument reference
    - [x] Example output screenshots or descriptions
    - [x] Troubleshooting section
  - [x] Add integration test workflow or manual testing instructions
  - [x] Document expected JSON structure from `cargo llvm-cov`
  - [x] Add comments in workflow files explaining coverage summary step
  - [x] Update main project README if workflow documentation exists
  - **Files**: `.github/scripts/coverage-summary/README.md`, workflow files, project README (if applicable)
  - **Dependencies**: None
  - **Testing**: Verify documentation is clear and complete. Test examples work as documented.
  - **Notes**: Follow documentation patterns from other scripts like `test-summary`. Include examples of actual usage in workflows.

## Files to Modify/Create
- **New Files**:
  - `.github/scripts/coverage-summary/pyproject.toml` - Python package configuration
  - `.github/scripts/coverage-summary/README.md` - Usage documentation
  - `.github/scripts/coverage-summary/src/coverage_summary/__init__.py` - Package init
  - `.github/scripts/coverage-summary/src/coverage_summary/__main__.py` - CLI entry point
  - `.github/scripts/coverage-summary/src/coverage_summary/parser.py` - JSON parser
  - `.github/scripts/coverage-summary/src/coverage_summary/generator.py` - Markdown generator
  - `.github/scripts/coverage-summary/tests/test_parser.py` - Parser unit tests
  - `.github/scripts/coverage-summary/tests/test_generator.py` - Generator unit tests
- **Modified Files**:
  - `.github/workflows/pull_request.yaml` - Add coverage summary generation step in coverage job
  - `.github/workflows/release-build.yaml` - Add coverage summary generation step in coverage job

## Testing Strategy
- **Unit Tests**: Test JSON parsing, markdown generation, Mermaid chart creation, file filtering, threshold indicators, error handling
- **Integration Tests**: Test full script execution with sample JSON files, verify markdown output format, test CLI arguments
- **Manual Testing**: Verify summary appears correctly in GitHub Actions workflow run summaries, test with real coverage data from workflow runs, verify Mermaid charts render correctly in GitHub UI

## Breaking Changes
- None

## Migration Guide
- N/A (no breaking changes)

## Documentation Updates
- [x] Update `.github/scripts/coverage-summary/README.md` with usage instructions
- [x] Add comments in workflow files explaining coverage summary step
- [x] Update main project README if workflow documentation exists (optional)

## Success Criteria
- Coverage summary appears in GitHub Actions job step summaries for PR and release workflows
- Summary includes overall coverage percentage with visual indicators
- Summary includes Mermaid pie chart showing coverage distribution
- Summary includes file-by-file breakdown for changed files in PRs
- Summary handles edge cases gracefully (missing files, invalid JSON, etc.)
- All unit tests pass
- Script follows existing project patterns (uv, pytest, package structure)
- Documentation is complete and clear

## Risks and Mitigations
- **Risk**: Mermaid chart syntax errors preventing summary display
  - **Mitigation**: Validate Mermaid syntax in unit tests, use simple pie chart format, test in GitHub UI
- **Risk**: Performance impact from parsing large coverage JSON files
  - **Mitigation**: Use efficient JSON parsing, limit file breakdown to changed files or top N files, profile if needed
- **Risk**: Changed files detection fails in PR workflows
  - **Mitigation**: Use robust git commands, handle errors gracefully, fall back to showing all files if detection fails
- **Risk**: Summary generation fails and breaks workflow
  - **Mitigation**: Use `if: always()` in workflow steps, handle errors gracefully in script, don't fail workflow on summary generation errors

## References
- Related REQ_ document: `plan/25W48/REQ_CODE_COVERAGE_REPORTING.md`
- Related implementation: `work/25W48/REQ_TEST_REPORTING.md` (similar pattern for test summaries)
- Coverage threshold check script: `.config/coverage-threshold-check.jq` (reference for JSON structure)
- GitHub Actions: Workflow Commands - https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions
- GitHub Actions: Step Summary - https://github.blog/2022-05-09-supercharging-github-actions-with-job-summaries/
- Mermaid Charts Documentation - https://mermaid.js.org/
