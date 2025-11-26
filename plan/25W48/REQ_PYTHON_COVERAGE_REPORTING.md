# REQ: Python Coverage Reporting for .github/scripts Projects

**Status**: ✅ Complete

## Overview
Add code coverage reporting to all Python projects in `.github/scripts` to track test coverage and ensure code quality across all script projects.

## Motivation
The Python projects in `.github/scripts` (pr-labels, release-notes, release-version, test-summary) currently lack coverage reporting, making it difficult to assess test coverage and identify untested code. Adding coverage reporting will help maintain code quality and ensure comprehensive testing across all script projects.

## Current Behavior
Python projects in `.github/scripts` have tests but no coverage reporting. There's no visibility into which code is covered by tests and which areas need additional test coverage.

## Proposed Behavior
Add coverage reporting to all Python projects in `.github/scripts`:
- Configure `pytest-cov` or similar coverage tool in each project's `pyproject.toml`
- Generate coverage reports during test execution
- Set up coverage thresholds or goals for each project
- Include coverage information in test output
- Optionally generate HTML coverage reports for detailed analysis

Each project should have:
- Coverage configuration in `pyproject.toml` under `[tool.coverage.*]`
- Coverage reporting integrated into test execution
- Coverage reports generated in CI/CD workflows (if applicable)

## Use Cases
- Identify untested code in Python script projects
- Track coverage trends over time
- Ensure new code includes adequate test coverage
- Review coverage reports to guide test writing efforts
- Set and enforce coverage thresholds

## Implementation Considerations
- Add `pytest-cov` to dev dependencies in each project's `pyproject.toml`
- Configure coverage settings (exclusions, report formats, thresholds)
- Update test execution commands to include coverage reporting
- Consider coverage thresholds appropriate for each project
- Ensure coverage reports don't break existing test workflows
- Handle coverage for projects with different structures (pr-labels, release-notes, release-version, test-summary)
- Exclude test files and setup code from coverage calculations

## Alternatives Considered
- **No coverage reporting**: Rejected - coverage visibility is important for maintaining code quality
- **External coverage services only**: Rejected - local coverage reporting is needed for development workflow
- **Coverage for only some projects**: Rejected - all Python projects should have consistent coverage reporting

## Impact
- **Breaking Changes**: No
- **Documentation**: Update project READMEs to document coverage reporting setup and usage
- **Testing**: Verify coverage reporting works correctly for all projects
- **Dependencies**: Add `pytest-cov` (or similar) to dev dependencies of affected projects

## References
- Related projects: pr-labels, release-notes, release-version, test-summary
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
