# REQ: Test Results Reporting in Workflow Summaries

**Status**: ✅ Completed

## Overview
Add rich markdown test results reporting to GitHub Actions job step summaries for build, release, and PR workflows to provide clear visibility of test execution status.

## Motivation
Currently, test results in GitHub Actions workflows are only visible in the raw log output, making it difficult to quickly assess test status. By utilizing GitHub Actions job step summaries, we can provide a clear, readable summary of test results that is immediately visible in the workflow run summary. This improves developer experience and makes it easier to identify test failures and their details.

## Current Behavior
Test results are only visible in the workflow log output. Developers must scroll through logs to find test execution details, pass/fail status, and duration information.

## Proposed Behavior
After test execution in build, release, and PR workflows, generate a rich markdown summary that includes:
- **Test results table**: A formatted markdown table showing test suite breakdown (unit tests, integration tests), pass/fail status, test counts, and duration for each suite
- **Pie chart**: A Mermaid pie chart visualizing the distribution of test results (passed, failed, skipped, etc.)
- Failed test details with error messages
- Links to test artifacts if available

The summary will be written to `$GITHUB_STEP_SUMMARY` and displayed in the workflow run summary page. Mermaid charts are natively supported in GitHub Actions job summaries.

## Use Cases
- Quickly assess test status after a workflow run without scrolling through logs
- Identify which test suites failed and why
- Review test execution duration to identify performance regressions
- Access test artifacts directly from the workflow summary

## Implementation Considerations
- Parse test output from `cargo nextest` (XML or JSON format)
- Extract test counts, pass/fail status, and duration from test output
- Generate a markdown table with test results (suite name, status, count, duration)
- Generate a Mermaid pie chart showing test result distribution (passed, failed, skipped, etc.)
- Format failed tests with details and error messages
- Apply to all workflows: build, release, and PR
- Handle cases where tests fail before completion
- Include links to test artifacts if available

## Alternatives Considered
- **PR comments**: Rejected - job step summaries are sufficient since failed checks require review anyway
- **External reporting tools**: Rejected - native GitHub Actions feature requires no additional dependencies
- **Log-only output**: Rejected - current approach is insufficient for quick status assessment

## Impact
- **Breaking Changes**: No
- **Documentation**: Update workflow documentation to describe the new test summary feature
- **Testing**: Test the summary generation with various test scenarios (all pass, some fail, all fail)
- **Dependencies**: No new dependencies required - uses native GitHub Actions `$GITHUB_STEP_SUMMARY` feature

## References
- [GitHub Actions: Workflow Commands](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions)
- [GitHub Actions: Step Summary](https://github.blog/2022-05-09-supercharging-github-actions-with-job-summaries/)
- [Mermaid Charts Documentation](https://mermaid.js.org/intro/)
