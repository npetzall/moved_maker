"""Formatter for generating markdown test summaries."""

from test_summary.parser import TestResults


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string (e.g., "1.23s", "45.67s")
    """
    return f"{seconds:.2f}s"


def get_status_emoji(passed: int, failed: int, skipped: int) -> str:
    """
    Get status emoji based on test results.

    Args:
        passed: Number of passed tests
        failed: Number of failed tests
        skipped: Number of skipped tests

    Returns:
        Status emoji (✅ for all pass, ❌ for failures, ⚠️ for skipped only)
    """
    if failed > 0:
        return "❌"
    if skipped > 0 and passed > 0:
        return "⚠️"
    return "✅"


def generate_markdown_summary(
    results: TestResults, artifact_name: str | None = None
) -> str:
    """
    Generate markdown summary from test results.

    Args:
        results: Parsed test results
        artifact_name: Optional artifact name for linking

    Returns:
        Markdown formatted summary string
    """
    lines: list[str] = []

    # Title
    lines.append("# Test Results Summary")
    lines.append("")

    # Overall status
    status_emoji = get_status_emoji(
        results.total_passed, results.total_failed, results.total_skipped
    )
    lines.append(f"**Status**: {status_emoji} ")
    if results.total_failed > 0:
        lines.append(
            f"{results.total_passed} passed, {results.total_failed} failed, "
            f"{results.total_skipped} skipped"
        )
    else:
        lines.append(
            f"{results.total_passed} passed, {results.total_skipped} skipped"
        )
    lines.append("")

    # Test results table
    if results.suites:
        lines.append("## Test Suites")
        lines.append("")
        lines.append("| Suite | Status | Tests | Passed | Failed | Skipped | Duration |")
        lines.append("|-------|--------|-------|--------|--------|---------|----------|")

        for suite in results.suites:
            suite_status = get_status_emoji(
                suite.tests - suite.failures - suite.errors - suite.skipped,
                suite.failures + suite.errors,
                suite.skipped,
            )
            passed_count = suite.tests - suite.failures - suite.errors - suite.skipped
            failed_count = suite.failures + suite.errors

            lines.append(
                f"| {suite.name} | {suite_status} | {suite.tests} | "
                f"{passed_count} | {failed_count} | {suite.skipped} | "
                f"{format_duration(suite.duration)} |"
            )

        lines.append("")
        lines.append(
            f"**Total**: {results.total_tests} tests in {len(results.suites)} suite(s) "
            f"({format_duration(results.total_duration)})"
        )
        lines.append("")

    # Mermaid pie chart
    if results.total_tests > 0:
        lines.append("## Test Results Distribution")
        lines.append("")
        lines.append("```mermaid")
        lines.append('pie title "Test Results"')
        if results.total_passed > 0:
            lines.append(f'    "Passed" : {results.total_passed}')
        if results.total_failed > 0:
            lines.append(f'    "Failed" : {results.total_failed}')
        if results.total_skipped > 0:
            lines.append(f'    "Skipped" : {results.total_skipped}')
        lines.append("```")
        lines.append("")

    # Failed test details
    failed_tests = []
    for suite in results.suites:
        for test_case in suite.test_cases:
            if test_case.status == "failed":
                failed_tests.append((suite.name, test_case))

    if failed_tests:
        lines.append("## Failed Tests")
        lines.append("")

        for suite_name, test_case in failed_tests:
            lines.append(f"### {suite_name}::{test_case.name}")
            lines.append("")
            if test_case.error_type:
                lines.append(f"**Error Type**: `{test_case.error_type}`")
                lines.append("")
            if test_case.error_message:
                # Truncate long error messages
                error_msg = test_case.error_message
                if len(error_msg) > 500:
                    error_msg = error_msg[:500] + "... (truncated)"
                lines.append("**Error Message**:")
                lines.append("")
                lines.append("```")
                lines.append(error_msg)
                lines.append("```")
                lines.append("")
            if test_case.stack_trace and test_case.stack_trace != test_case.error_message:
                # Only show stack trace if different from error message
                stack_trace = test_case.stack_trace
                if len(stack_trace) > 1000:
                    stack_trace = stack_trace[:1000] + "... (truncated)"
                lines.append("**Stack Trace**:")
                lines.append("")
                lines.append("```")
                lines.append(stack_trace)
                lines.append("```")
                lines.append("")

    # Artifact link
    if artifact_name:
        lines.append("## Test Artifacts")
        lines.append("")
        lines.append(
            f"Test results are available as artifacts: `{artifact_name}`"
        )
        lines.append("")

    return "\n".join(lines)
