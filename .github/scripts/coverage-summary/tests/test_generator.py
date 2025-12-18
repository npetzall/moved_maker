"""Tests for generator module."""

from pathlib import Path

import pytest

from coverage_summary.generator import (
    generate_file_breakdown,
    generate_markdown_summary,
    generate_mermaid_chart,
    generate_overall_section,
    generate_regression_section,
    get_coverage_indicator,
    write_summary,
)
from coverage_summary.parser import (
    CoverageData,
    CoverageMetrics,
    FileCoverage,
    OverallCoverage,
)


def test_get_coverage_indicator():
    """Test coverage indicator generation."""
    # Above threshold
    assert get_coverage_indicator(85.0, 80.0, 100) == "✅"
    # Below threshold
    assert get_coverage_indicator(75.0, 80.0, 100) == "❌"
    # At threshold
    assert get_coverage_indicator(80.0, 80.0, 100) == "✅"
    # N/A (count = 0)
    assert get_coverage_indicator(0.0, 80.0, 0) == "⚠️"


def test_generate_overall_section():
    """Test overall coverage section generation."""
    overall = OverallCoverage(
        line_coverage=CoverageMetrics(percent=95.39, covered=200, total=215),
        branch_coverage=CoverageMetrics(percent=90.0, covered=45, total=50),
        function_coverage=CoverageMetrics(percent=94.74, covered=18, total=19),
    )

    lines = generate_overall_section(overall, 80.0, 70.0, 85.0)

    assert "## Overall Coverage" in lines
    assert "**Status**: ✅" in lines
    assert "| Metric | Coverage | Status | Threshold |" in lines
    assert "95.39%" in "\n".join(lines)
    assert "✅" in "\n".join(lines)


def test_generate_overall_section_below_threshold():
    """Test overall coverage section with below-threshold coverage."""
    overall = OverallCoverage(
        line_coverage=CoverageMetrics(percent=70.0, covered=70, total=100),
        branch_coverage=CoverageMetrics(percent=60.0, covered=30, total=50),
        function_coverage=CoverageMetrics(percent=80.0, covered=8, total=10),
    )

    lines = generate_overall_section(overall, 80.0, 70.0, 85.0)

    assert "**Status**: ❌" in lines
    assert "❌" in "\n".join(lines)


def test_generate_overall_section_na_branch_coverage():
    """Test overall coverage section with N/A branch coverage (total == 0)."""
    # This scenario: lines and functions pass, but branches are N/A
    # Overall status should be ✅ because N/A metrics are skipped
    overall = OverallCoverage(
        line_coverage=CoverageMetrics(percent=95.52, covered=1001, total=1048),
        branch_coverage=CoverageMetrics(percent=0.0, covered=0, total=0),  # N/A
        function_coverage=CoverageMetrics(percent=97.27, covered=107, total=110),
    )

    lines = generate_overall_section(overall, 80.0, 70.0, 85.0)

    assert "**Status**: ✅" in lines
    assert "N/A" in "\n".join(lines)  # Branch coverage should show N/A
    assert "⚠️" in "\n".join(lines)  # Branch indicator should be ⚠️


def test_generate_mermaid_chart():
    """Test Mermaid chart generation."""
    overall = OverallCoverage(
        line_coverage=CoverageMetrics(percent=95.39, covered=200, total=215),
        branch_coverage=CoverageMetrics(percent=90.0, covered=45, total=50),
        function_coverage=CoverageMetrics(percent=94.74, covered=18, total=19),
    )

    lines = generate_mermaid_chart(overall)

    assert "## Coverage Distribution" in lines
    assert "```mermaid" in lines
    assert 'pie title "Line Coverage"' in lines
    assert '"Covered" : 95.39' in "\n".join(lines)
    assert '"Uncovered" : 4.61' in "\n".join(lines)


def test_generate_mermaid_chart_no_coverage():
    """Test Mermaid chart generation with no coverage."""
    overall = OverallCoverage(
        line_coverage=CoverageMetrics(percent=0.0, covered=0, total=0),
        branch_coverage=CoverageMetrics(percent=0.0, covered=0, total=0),
        function_coverage=CoverageMetrics(percent=0.0, covered=0, total=0),
    )

    lines = generate_mermaid_chart(overall)

    # Should return empty list when total is 0
    assert len(lines) == 0


def test_generate_file_breakdown():
    """Test file breakdown generation."""
    files = [
        FileCoverage(
            path="src/main.rs",
            line_coverage=CoverageMetrics(percent=100.0, covered=50, total=50),
            branch_coverage=CoverageMetrics(percent=100.0, covered=10, total=10),
            function_coverage=CoverageMetrics(percent=100.0, covered=5, total=5),
        ),
        FileCoverage(
            path="src/lib.rs",
            line_coverage=CoverageMetrics(percent=80.0, covered=80, total=100),
            branch_coverage=CoverageMetrics(percent=75.0, covered=15, total=20),
            function_coverage=CoverageMetrics(percent=85.0, covered=17, total=20),
        ),
    ]

    lines = generate_file_breakdown(files)

    assert "## File Coverage Breakdown" in lines
    assert "| File | Line Coverage | Branch Coverage | Function Coverage | Status |" in lines
    assert "src/main.rs" in "\n".join(lines)
    assert "src/lib.rs" in "\n".join(lines)
    # Files should be sorted by coverage (lowest first)
    lib_index = "\n".join(lines).index("src/lib.rs")
    main_index = "\n".join(lines).index("src/main.rs")
    assert lib_index < main_index


def test_generate_file_breakdown_changed_files():
    """Test file breakdown with changed files filtering."""
    files = [
        FileCoverage(
            path="src/main.rs",
            line_coverage=CoverageMetrics(percent=100.0, covered=50, total=50),
            branch_coverage=CoverageMetrics(percent=100.0, covered=10, total=10),
            function_coverage=CoverageMetrics(percent=100.0, covered=5, total=5),
        ),
        FileCoverage(
            path="src/lib.rs",
            line_coverage=CoverageMetrics(percent=80.0, covered=80, total=100),
            branch_coverage=CoverageMetrics(percent=75.0, covered=15, total=20),
            function_coverage=CoverageMetrics(percent=85.0, covered=17, total=20),
        ),
        FileCoverage(
            path="src/other.rs",
            line_coverage=CoverageMetrics(percent=90.0, covered=90, total=100),
            branch_coverage=CoverageMetrics(percent=85.0, covered=17, total=20),
            function_coverage=CoverageMetrics(percent=90.0, covered=18, total=20),
        ),
    ]

    changed_files = ["src/main.rs", "src/lib.rs"]

    lines = generate_file_breakdown(files, changed_files=changed_files)

    assert "## Changed Files Coverage" in lines
    assert "src/main.rs" in "\n".join(lines)
    assert "src/lib.rs" in "\n".join(lines)
    assert "src/other.rs" not in "\n".join(lines)


def test_generate_file_breakdown_empty():
    """Test file breakdown with empty file list."""
    lines = generate_file_breakdown([])
    assert len(lines) == 0


def test_generate_file_breakdown_max_files():
    """Test file breakdown with max files limit."""
    files = [
        FileCoverage(
            path=f"src/file{i}.rs",
            line_coverage=CoverageMetrics(percent=float(100 - i), covered=100 - i, total=100),
            branch_coverage=CoverageMetrics(percent=90.0, covered=9, total=10),
            function_coverage=CoverageMetrics(percent=90.0, covered=9, total=10),
        )
        for i in range(60)
    ]

    lines = generate_file_breakdown(files, max_files=50)

    # Should show message about limiting
    assert "Showing top 50 files" in "\n".join(lines)
    assert "Total files: 60" in "\n".join(lines)


def test_generate_regression_section():
    """Test regression section generation."""
    current = CoverageData(
        overall=OverallCoverage(
            line_coverage=CoverageMetrics(percent=95.39, covered=200, total=215),
            branch_coverage=CoverageMetrics(percent=90.0, covered=45, total=50),
            function_coverage=CoverageMetrics(percent=94.74, covered=18, total=19),
        ),
        files=[],
    )

    baseline = CoverageData(
        overall=OverallCoverage(
            line_coverage=CoverageMetrics(percent=93.0, covered=186, total=200),
            branch_coverage=CoverageMetrics(percent=88.0, covered=44, total=50),
            function_coverage=CoverageMetrics(percent=92.0, covered=18, total=20),
        ),
        files=[],
    )

    lines = generate_regression_section(current, baseline)

    assert "## Coverage Changes" in lines
    assert "📈" in "\n".join(lines)  # Should show increase
    assert "+2.39%" in "\n".join(lines) or "2.39%" in "\n".join(lines)


def test_generate_regression_section_decrease():
    """Test regression section with coverage decrease."""
    current = CoverageData(
        overall=OverallCoverage(
            line_coverage=CoverageMetrics(percent=90.0, covered=180, total=200),
            branch_coverage=CoverageMetrics(percent=85.0, covered=42, total=50),
            function_coverage=CoverageMetrics(percent=88.0, covered=17, total=20),
        ),
        files=[],
    )

    baseline = CoverageData(
        overall=OverallCoverage(
            line_coverage=CoverageMetrics(percent=95.0, covered=190, total=200),
            branch_coverage=CoverageMetrics(percent=90.0, covered=45, total=50),
            function_coverage=CoverageMetrics(percent=92.0, covered=18, total=20),
        ),
        files=[],
    )

    lines = generate_regression_section(current, baseline)

    assert "📉" in "\n".join(lines)  # Should show decrease
    assert "-5.00%" in "\n".join(lines) or "5.00%" in "\n".join(lines)


def test_generate_markdown_summary():
    """Test complete markdown summary generation."""
    coverage_data = CoverageData(
        overall=OverallCoverage(
            line_coverage=CoverageMetrics(percent=95.39, covered=200, total=215),
            branch_coverage=CoverageMetrics(percent=90.0, covered=45, total=50),
            function_coverage=CoverageMetrics(percent=94.74, covered=18, total=19),
        ),
        files=[
            FileCoverage(
                path="src/main.rs",
                line_coverage=CoverageMetrics(percent=100.0, covered=50, total=50),
                branch_coverage=CoverageMetrics(percent=100.0, covered=10, total=10),
                function_coverage=CoverageMetrics(percent=100.0, covered=5, total=5),
            ),
        ],
    )

    summary = generate_markdown_summary(coverage_data)

    assert "# Code Coverage Summary" in summary
    assert "## Overall Coverage" in summary
    assert "## Coverage Distribution" in summary
    assert "## File Coverage Breakdown" in summary
    assert "src/main.rs" in summary


def test_generate_markdown_summary_with_baseline():
    """Test markdown summary with baseline comparison."""
    current = CoverageData(
        overall=OverallCoverage(
            line_coverage=CoverageMetrics(percent=95.39, covered=200, total=215),
            branch_coverage=CoverageMetrics(percent=90.0, covered=45, total=50),
            function_coverage=CoverageMetrics(percent=94.74, covered=18, total=19),
        ),
        files=[],
    )

    baseline = CoverageData(
        overall=OverallCoverage(
            line_coverage=CoverageMetrics(percent=93.0, covered=186, total=200),
            branch_coverage=CoverageMetrics(percent=88.0, covered=44, total=50),
            function_coverage=CoverageMetrics(percent=92.0, covered=18, total=20),
        ),
        files=[],
    )

    summary = generate_markdown_summary(current, baseline_data=baseline)

    assert "## Coverage Changes" in summary


def test_write_summary(temp_dir):
    """Test writing summary to file."""
    summary = "# Test Summary\n\nThis is a test summary."

    output_path = temp_dir / "summary.md"
    write_summary(summary, output_path)

    assert output_path.exists()
    assert output_path.read_text() == summary


def test_write_summary_default_env(monkeypatch, temp_dir):
    """Test writing summary using GITHUB_STEP_SUMMARY env var."""
    summary = "# Test Summary\n\nThis is a test summary."

    output_path = temp_dir / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(output_path))

    write_summary(summary)

    assert output_path.exists()
    assert output_path.read_text() == summary


def test_write_summary_no_output():
    """Test writing summary to stdout when no output path."""
    summary = "# Test Summary\n\nThis is a test summary."

    # Should not raise an error, just print to stdout
    # (we can't easily test stdout in pytest without mocking)
    try:
        write_summary(summary)
    except Exception:
        pytest.fail("write_summary should handle missing output path gracefully")
