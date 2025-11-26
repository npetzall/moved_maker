"""Generator for markdown coverage summaries."""

from pathlib import Path
from typing import List, Optional

from coverage_summary.parser import (
    CoverageData,
    CoverageMetrics,
    FileCoverage,
    OverallCoverage,
)


def get_coverage_indicator(
    percent: float, threshold: float, count: int = 0
) -> str:
    """
    Get visual indicator for coverage based on threshold.

    Args:
        percent: Coverage percentage
        threshold: Coverage threshold
        count: Total count (0 means N/A)

    Returns:
        Visual indicator emoji (✅/⚠️/❌)
    """
    if count == 0:
        return "⚠️"  # N/A
    if percent >= threshold:
        return "✅"
    return "❌"


def generate_overall_section(
    overall: OverallCoverage,
    threshold_line: float,
    threshold_branch: float,
    threshold_function: float,
) -> List[str]:
    """
    Generate overall coverage section.

    Args:
        overall: Overall coverage metrics
        threshold_line: Line coverage threshold
        threshold_branch: Branch coverage threshold
        threshold_function: Function coverage threshold

    Returns:
        List of markdown lines for overall coverage section
    """
    lines: List[str] = []

    # Determine overall status
    line_indicator = get_coverage_indicator(
        overall.line_coverage.percent, threshold_line, overall.line_coverage.total
    )
    branch_indicator = get_coverage_indicator(
        overall.branch_coverage.percent,
        threshold_branch,
        overall.branch_coverage.total,
    )
    function_indicator = get_coverage_indicator(
        overall.function_coverage.percent,
        threshold_function,
        overall.function_coverage.total,
    )

    # Overall status
    if (
        overall.line_coverage.percent >= threshold_line
        and overall.branch_coverage.percent >= threshold_branch
        and overall.function_coverage.percent >= threshold_function
    ):
        overall_status = "✅"
    else:
        overall_status = "❌"

    lines.append("## Overall Coverage")
    lines.append("")
    lines.append(f"**Status**: {overall_status}")
    lines.append("")
    lines.append("| Metric | Coverage | Status | Threshold |")
    lines.append("|--------|----------|--------|-----------|")

    # Format coverage percentage
    def format_percent(metrics: CoverageMetrics) -> str:
        if metrics.total == 0:
            return "N/A"
        return f"{metrics.percent:.2f}% ({metrics.covered}/{metrics.total})"

    lines.append(
        f"| Lines | {format_percent(overall.line_coverage)} | "
        f"{line_indicator} | {threshold_line}% |"
    )
    lines.append(
        f"| Branches | {format_percent(overall.branch_coverage)} | "
        f"{branch_indicator} | {threshold_branch}% |"
    )
    lines.append(
        f"| Functions | {format_percent(overall.function_coverage)} | "
        f"{function_indicator} | {threshold_function}% |"
    )
    lines.append("")

    return lines


def generate_mermaid_chart(overall: OverallCoverage) -> List[str]:
    """
    Generate Mermaid pie chart for coverage distribution.

    Args:
        overall: Overall coverage metrics

    Returns:
        List of markdown lines for Mermaid chart
    """
    lines: List[str] = []

    if overall.line_coverage.total == 0:
        return lines

    lines.append("## Coverage Distribution")
    lines.append("")
    lines.append("```mermaid")
    lines.append('pie title "Line Coverage"')

    covered_percent = overall.line_coverage.percent
    uncovered_percent = 100.0 - covered_percent

    if covered_percent > 0:
        lines.append(f'    "Covered" : {covered_percent:.2f}')

    if uncovered_percent > 0:
        lines.append(f'    "Uncovered" : {uncovered_percent:.2f}')

    lines.append("```")
    lines.append("")

    return lines


def generate_file_breakdown(
    files: List[FileCoverage],
    changed_files: Optional[List[str]] = None,
    threshold_line: float = 80.0,
    max_files: int = 50,
) -> List[str]:
    """
    Generate file-by-file breakdown table.

    Args:
        files: List of file coverage data
        changed_files: Optional list of changed file paths to filter
        threshold_line: Line coverage threshold for indicators
        max_files: Maximum number of files to show

    Returns:
        List of markdown lines for file breakdown section
    """
    lines: List[str] = []

    # Filter files if changed_files provided
    if changed_files:
        changed_set = set(changed_files)
        # Normalize paths for comparison (handle relative paths)
        filtered_files = [
            f
            for f in files
            if any(
                f.path.endswith(changed) or changed.endswith(f.path)
                for changed in changed_set
            )
        ]
        if not filtered_files:
            # No matching files found, return empty
            return lines
        files_to_show = filtered_files
        section_title = "## Changed Files Coverage"
    else:
        files_to_show = files
        section_title = "## File Coverage Breakdown"

    if not files_to_show:
        return lines

    lines.append(section_title)
    lines.append("")

    # Sort by line coverage (lowest first for visibility)
    sorted_files = sorted(
        files_to_show, key=lambda f: f.line_coverage.percent
    )[:max_files]

    lines.append(
        "| File | Line Coverage | Branch Coverage | Function Coverage | Status |"
    )
    lines.append("|------|---------------|-----------------|-------------------|--------|")

    for file_cov in sorted_files:
        line_indicator = get_coverage_indicator(
            file_cov.line_coverage.percent,
            threshold_line,
            file_cov.line_coverage.total,
        )

        def format_file_percent(metrics: CoverageMetrics) -> str:
            if metrics.total == 0:
                return "N/A"
            return f"{metrics.percent:.2f}%"

        # Truncate long file paths for readability
        file_path = file_cov.path
        if len(file_path) > 60:
            file_path = "..." + file_path[-57:]

        lines.append(
            f"| `{file_path}` | {format_file_percent(file_cov.line_coverage)} | "
            f"{format_file_percent(file_cov.branch_coverage)} | "
            f"{format_file_percent(file_cov.function_coverage)} | "
            f"{line_indicator} |"
        )

    if len(files_to_show) > max_files:
        lines.append("")
        lines.append(
            f"*Showing top {max_files} files with lowest coverage. "
            f"Total files: {len(files_to_show)}*"
        )

    lines.append("")

    return lines


def generate_regression_section(
    current: CoverageData, baseline: CoverageData
) -> List[str]:
    """
    Generate regression comparison section.

    Args:
        current: Current coverage data
        baseline: Baseline coverage data

    Returns:
        List of markdown lines for regression section
    """
    lines: List[str] = []

    lines.append("## Coverage Changes")
    lines.append("")

    def compare_metrics(
        current_metrics: CoverageMetrics, baseline_metrics: CoverageMetrics, name: str
    ) -> List[str]:
        """Compare current and baseline metrics."""
        diff = current_metrics.percent - baseline_metrics.percent
        if diff > 0:
            indicator = "📈"
            change = f"+{diff:.2f}%"
        elif diff < 0:
            indicator = "📉"
            change = f"{diff:.2f}%"
        else:
            indicator = "➡️"
            change = "0.00%"

        return [
            f"- **{name}**: {current_metrics.percent:.2f}% "
            f"({change} from baseline {baseline_metrics.percent:.2f}%) {indicator}"
        ]

    lines.extend(
        compare_metrics(
            current.overall.line_coverage,
            baseline.overall.line_coverage,
            "Line Coverage",
        )
    )
    lines.extend(
        compare_metrics(
            current.overall.branch_coverage,
            baseline.overall.branch_coverage,
            "Branch Coverage",
        )
    )
    lines.extend(
        compare_metrics(
            current.overall.function_coverage,
            baseline.overall.function_coverage,
            "Function Coverage",
        )
    )

    lines.append("")

    return lines


def generate_markdown_summary(
    coverage_data: CoverageData,
    threshold_line: float = 80.0,
    threshold_branch: float = 70.0,
    threshold_function: float = 85.0,
    changed_files: Optional[List[str]] = None,
    baseline_data: Optional[CoverageData] = None,
) -> str:
    """
    Generate complete markdown summary from coverage data.

    Args:
        coverage_data: Parsed coverage data
        threshold_line: Line coverage threshold
        threshold_branch: Branch coverage threshold
        threshold_function: Function coverage threshold
        changed_files: Optional list of changed file paths
        baseline_data: Optional baseline coverage data for comparison

    Returns:
        Complete markdown formatted summary string
    """
    lines: List[str] = []

    # Title
    lines.append("# Code Coverage Summary")
    lines.append("")

    # Overall coverage section
    lines.extend(
        generate_overall_section(
            coverage_data.overall,
            threshold_line,
            threshold_branch,
            threshold_function,
        )
    )

    # Mermaid chart
    lines.extend(generate_mermaid_chart(coverage_data.overall))

    # Regression section (if baseline provided)
    if baseline_data:
        lines.extend(generate_regression_section(coverage_data, baseline_data))

    # File breakdown
    file_breakdown = generate_file_breakdown(
        coverage_data.files, changed_files, threshold_line
    )
    if file_breakdown:
        lines.extend(file_breakdown)

    return "\n".join(lines)


def write_summary(
    summary: str, output_path: Optional[str | Path] = None
) -> None:
    """
    Write summary to file.

    Args:
        summary: Markdown summary string
        output_path: Optional output file path (default: $GITHUB_STEP_SUMMARY)

    Raises:
        IOError: If file write fails
    """
    import os

    if output_path:
        path = Path(output_path)
    else:
        # Try GITHUB_STEP_SUMMARY environment variable
        github_step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if github_step_summary:
            path = Path(github_step_summary)
        else:
            # Fallback to stdout (will be handled by caller)
            print(summary)
            return

    # Create parent directories if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write summary
    with path.open("w", encoding="utf-8") as f:
        f.write(summary)
