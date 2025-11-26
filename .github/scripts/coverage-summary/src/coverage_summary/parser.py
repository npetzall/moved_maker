"""Parser for coverage JSON output from cargo llvm-cov."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class CoverageMetrics:
    """Represents coverage metrics for lines, branches, or functions."""

    percent: float
    covered: int
    total: int


@dataclass
class FileCoverage:
    """Represents coverage metrics for a single file."""

    path: str
    line_coverage: CoverageMetrics
    branch_coverage: CoverageMetrics
    function_coverage: CoverageMetrics


@dataclass
class OverallCoverage:
    """Represents overall coverage metrics."""

    line_coverage: CoverageMetrics
    branch_coverage: CoverageMetrics
    function_coverage: CoverageMetrics


@dataclass
class CoverageData:
    """Represents parsed coverage data."""

    overall: OverallCoverage
    files: List[FileCoverage]


def parse_coverage_json(json_path: str | Path) -> CoverageData:
    """
    Parse coverage JSON file from cargo llvm-cov.

    Args:
        json_path: Path to coverage JSON file

    Returns:
        CoverageData object with parsed coverage metrics

    Raises:
        FileNotFoundError: If JSON file does not exist
        json.JSONDecodeError: If JSON is malformed
        ValueError: If JSON structure is invalid or missing required fields
    """
    json_path = Path(json_path)

    if not json_path.exists():
        raise FileNotFoundError(f"Coverage JSON file not found: {json_path}")

    try:
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Failed to parse JSON file {json_path}: {e}", e.doc, e.pos
        ) from e

    # Validate JSON structure
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError(
            f"Invalid JSON structure: expected non-empty array, got {type(data)}"
        )

    first_item = data[0]

    if "totals" not in first_item:
        raise ValueError("Invalid JSON structure: missing 'totals' field")

    totals = first_item["totals"]

    # Extract overall coverage metrics
    def extract_metrics(totals_key: str) -> CoverageMetrics:
        """Extract coverage metrics from totals object."""
        if totals_key not in totals:
            return CoverageMetrics(percent=0.0, covered=0, total=0)

        metric_data = totals[totals_key]
        percent = float(metric_data.get("percent", 0.0))
        count = metric_data.get("count", {})
        covered = int(count.get("covered", 0))
        total = int(count.get("partial", 0)) + int(count.get("missed", 0)) + covered

        return CoverageMetrics(percent=percent, covered=covered, total=total)

    overall = OverallCoverage(
        line_coverage=extract_metrics("lines"),
        branch_coverage=extract_metrics("branches"),
        function_coverage=extract_metrics("functions"),
    )

    # Extract file-level coverage
    files: List[FileCoverage] = []

    if "files" in first_item:
        for file_data in first_item["files"]:
            file_path = file_data.get("filename", "")

            # Extract file-level metrics
            def extract_file_metrics(file_key: str) -> CoverageMetrics:
                """Extract coverage metrics from file object."""
                if file_key not in file_data:
                    return CoverageMetrics(percent=0.0, covered=0, total=0)

                metric_data = file_data[file_key]
                percent = float(metric_data.get("percent", 0.0))
                count = metric_data.get("count", {})
                covered = int(count.get("covered", 0))
                total = (
                    int(count.get("partial", 0))
                    + int(count.get("missed", 0))
                    + covered
                )

                return CoverageMetrics(percent=percent, covered=covered, total=total)

            file_coverage = FileCoverage(
                path=file_path,
                line_coverage=extract_file_metrics("lines"),
                branch_coverage=extract_file_metrics("branches"),
                function_coverage=extract_file_metrics("functions"),
            )
            files.append(file_coverage)

    return CoverageData(overall=overall, files=files)
