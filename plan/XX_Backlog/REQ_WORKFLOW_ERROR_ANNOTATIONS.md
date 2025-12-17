# REQ: Workflow Error Annotations

**Status**: 📋 Planned

## Overview
Add GitHub Actions annotations for all errors that can occur in workflows to make them clearly visible in the workflow run summary, providing inline error messages, warnings, and notices directly in the workflow UI.

## Motivation
Currently, when workflows fail, developers must scroll through logs to find errors, which is time-consuming and error-prone. GitHub Actions annotations provide inline error messages with file and line number references directly in the workflow UI, making it much easier to identify and fix issues quickly. This improves developer experience and reduces debugging time.

## Current Behavior
Workflow errors are only visible in the workflow logs. Developers must:
- Scroll through potentially long log outputs
- Manually search for error messages
- Navigate to files and line numbers manually
- Parse tool output formats to understand issues

Errors from different tools (cargo build, cargo test, clippy, etc.) appear in their native formats without structured visibility in the workflow UI.

## Proposed Behavior
Add GitHub Actions annotations for all major workflow steps that can produce errors or warnings:

- **Build errors** (cargo build): Parse build output and create error annotations with file/line references
- **Test failures** (cargo nextest): Create error annotations for failed tests
- **Linting issues** (clippy, rustfmt): Create warning annotations for clippy warnings and error annotations for formatting failures
- **Coverage warnings**: Create warning annotations when coverage falls below threshold
- **Security vulnerabilities** (cargo audit): Create error annotations for discovered vulnerabilities

Annotations will appear in the "Annotations" tab of workflow runs with:
- Inline error messages in workflow UI
- File and line number references for quick navigation
- Appropriate annotation types (error, warning, notice)
- Clear visibility of issues in run summary

## Use Cases
- Developer sees build error annotation with file and line number, clicks to navigate directly to the issue
- Test failure annotation shows which test failed and why, without scrolling through logs
- Clippy warning annotation appears inline, making it easy to see all linting issues at a glance
- Coverage warning annotation alerts when code coverage drops below threshold
- Security scan annotation highlights vulnerabilities that need immediate attention

## Implementation Considerations
- **Error Parsing**: Different tools output errors in different formats, may need custom parsers for each tool
  - `cargo clippy`: Can use `--message-format=json` for structured output
  - `cargo test`: Parse test output or use nextest JSON format
  - `cargo fmt`: Simple pass/fail, add annotation on failure
  - `cargo audit`: Parse JSON output for vulnerabilities
- **Annotation Limits**: GitHub Actions may have limits on number of annotations; consider batching or summarizing for large outputs
- **Tool Output Formats**: Need to handle different error formats from different tools
- **Focus on Actionable Errors**: Prioritize actionable errors rather than all warnings to avoid annotation overload
- **Native Feature**: Uses GitHub Actions native workflow commands, no additional dependencies required

## Alternatives Considered
- **Log-only approach**: Keep current behavior of errors only in logs - rejected because it's time-consuming and error-prone
- **Third-party annotation tools**: Use external tools or actions - rejected because GitHub Actions native annotations are sufficient and don't require additional dependencies
- **Summary-only annotations**: Only create one annotation per workflow step - rejected because file/line-specific annotations provide much better developer experience

## Impact
- **Breaking Changes**: No - this is an additive feature that enhances workflow output without changing existing behavior
- **Documentation**: Update workflow documentation to explain annotation feature and how to interpret annotations in workflow runs
- **Testing**: Test annotation creation for each tool type (build, test, lint, coverage, security) to ensure proper parsing and formatting
- **Dependencies**: No new dependencies required - uses native GitHub Actions workflow commands

## References
- [GitHub Actions: Workflow Commands](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions)
- [GitHub Actions: Setting an error message](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-error-message)
