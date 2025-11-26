# REQ: Code Coverage Reporting in Workflow Summaries

**Status**: ✅ Complete

**Progress**: Implementation complete - Coverage summary script created, integrated into workflows, and tested.

## Overview
Add rich markdown code coverage reporting to GitHub Actions job step summaries for build, release, and PR workflows to provide clear visibility of code coverage metrics.

## Motivation
Code coverage information is currently only available in raw log output or separate coverage files, making it difficult to quickly assess coverage status and identify regressions. By utilizing GitHub Actions job step summaries, we can provide a clear, readable summary of coverage metrics that is immediately visible in the workflow run summary. This helps maintain code quality and makes it easier to identify coverage regressions.

## Current Behavior
Code coverage results are only visible in the workflow log output or in generated coverage files. Developers must manually check coverage files or scroll through logs to find coverage information.

## Proposed Behavior
After coverage generation in build, release, and PR workflows, generate a rich markdown summary that includes:
- Overall coverage percentage
- Coverage table with file-by-file breakdown for changed files
- Mermaid pie chart visualizing coverage distribution
- Coverage regressions compared to baseline (if available)
- Links to detailed coverage reports
- Visual indicators for coverage thresholds

The summary will be written to `$GITHUB_STEP_SUMMARY` and displayed in the workflow run summary page. Mermaid charts are natively supported in GitHub Actions job summaries, providing rich visualizations of coverage data.

## Use Cases
- Quickly assess code coverage after a workflow run without accessing separate files
- Identify which files have low coverage or coverage regressions
- Review coverage for changed files in PRs
- Track coverage trends over time in release workflows

## Implementation Considerations
- Parse coverage output from `cargo llvm-cov` (JSON format)
- Extract overall coverage percentage and file-level metrics
- Compare coverage with baseline for regression detection
- Format coverage data in markdown tables with file names, coverage percentages, and status indicators
- Generate Mermaid pie chart showing coverage distribution (covered vs uncovered code)
- Apply to all workflows: build, release, and PR
- Handle cases where coverage generation fails
- Include links to detailed coverage reports if available
- Highlight files with coverage below threshold

## Alternatives Considered
- **PR comments**: Rejected - job step summaries are sufficient since failed checks require review anyway
- **External coverage services**: Rejected - native GitHub Actions feature requires no additional dependencies
- **Log-only output**: Rejected - current approach is insufficient for quick status assessment

## Impact
- **Breaking Changes**: No
- **Documentation**: Update workflow documentation to describe the new coverage summary feature
- **Testing**: Test the summary generation with various coverage scenarios (high coverage, low coverage, regressions)
- **Dependencies**: No new dependencies required - uses native GitHub Actions `$GITHUB_STEP_SUMMARY` feature and existing `jq` for JSON parsing

## References
- [GitHub Actions: Workflow Commands](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions)
- [GitHub Actions: Step Summary](https://github.blog/2022-05-09-supercharging-github-actions-with-job-summaries/)
- [Mermaid Charts Documentation](https://mermaid.js.org/)
