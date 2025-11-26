"""Tests for parser module."""

import json
from pathlib import Path

import pytest

from coverage_summary.parser import (
    CoverageData,
    CoverageMetrics,
    FileCoverage,
    OverallCoverage,
    parse_coverage_json,
)


def test_parse_coverage_json_high_coverage(
    sample_coverage_json_high, temp_dir
):
    """Test parsing coverage JSON with high coverage."""
    json_file = temp_dir / "coverage.json"
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(sample_coverage_json_high, f)

    result = parse_coverage_json(json_file)

    assert isinstance(result, CoverageData)
    assert result.overall.line_coverage.percent == pytest.approx(95.39)
    assert result.overall.line_coverage.covered == 200
    assert result.overall.line_coverage.total == 215  # 200 + 5 + 10

    assert result.overall.branch_coverage.percent == pytest.approx(90.0)
    assert result.overall.branch_coverage.covered == 45
    assert result.overall.branch_coverage.total == 50  # 45 + 2 + 3

    assert result.overall.function_coverage.percent == pytest.approx(94.74)
    assert result.overall.function_coverage.covered == 18
    assert result.overall.function_coverage.total == 19  # 18 + 0 + 1

    assert len(result.files) == 2
    assert result.files[0].path == "src/main.rs"
    assert result.files[0].line_coverage.percent == pytest.approx(100.0)


def test_parse_coverage_json_low_coverage(sample_coverage_json_low, temp_dir):
    """Test parsing coverage JSON with low coverage."""
    json_file = temp_dir / "coverage.json"
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(sample_coverage_json_low, f)

    result = parse_coverage_json(json_file)

    assert result.overall.line_coverage.percent == pytest.approx(60.0)
    assert result.overall.line_coverage.covered == 60
    assert result.overall.line_coverage.total == 100  # 60 + 10 + 30

    assert len(result.files) == 1
    assert result.files[0].path == "src/main.rs"
    assert result.files[0].line_coverage.percent == pytest.approx(50.0)


def test_parse_coverage_json_no_branches(
    sample_coverage_json_no_branches, temp_dir
):
    """Test parsing coverage JSON with no branches."""
    json_file = temp_dir / "coverage.json"
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(sample_coverage_json_no_branches, f)

    result = parse_coverage_json(json_file)

    assert result.overall.branch_coverage.percent == pytest.approx(0.0)
    assert result.overall.branch_coverage.covered == 0
    assert result.overall.branch_coverage.total == 0

    assert len(result.files) == 0


def test_parse_coverage_json_empty(sample_coverage_json_empty, temp_dir):
    """Test parsing coverage JSON with empty coverage."""
    json_file = temp_dir / "coverage.json"
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(sample_coverage_json_empty, f)

    result = parse_coverage_json(json_file)

    assert result.overall.line_coverage.percent == pytest.approx(0.0)
    assert result.overall.line_coverage.total == 0
    assert len(result.files) == 0


def test_parse_coverage_json_file_not_found(temp_dir):
    """Test parsing non-existent JSON file."""
    json_file = temp_dir / "nonexistent.json"

    with pytest.raises(FileNotFoundError):
        parse_coverage_json(json_file)


def test_parse_coverage_json_invalid_json(temp_dir):
    """Test parsing invalid JSON file."""
    json_file = temp_dir / "invalid.json"
    json_file.write_text("invalid json content")

    with pytest.raises(json.JSONDecodeError):
        parse_coverage_json(json_file)


def test_parse_coverage_json_invalid_structure(temp_dir):
    """Test parsing JSON with invalid structure."""
    json_file = temp_dir / "invalid.json"
    with json_file.open("w", encoding="utf-8") as f:
        json.dump({"invalid": "structure"}, f)

    with pytest.raises(ValueError, match="expected non-empty array"):
        parse_coverage_json(json_file)


def test_parse_coverage_json_missing_totals(temp_dir):
    """Test parsing JSON with missing totals field."""
    json_file = temp_dir / "invalid.json"
    with json_file.open("w", encoding="utf-8") as f:
        json.dump([{"files": []}], f)

    with pytest.raises(ValueError, match="missing 'totals' field"):
        parse_coverage_json(json_file)


def test_parse_coverage_json_missing_optional_fields(
    sample_coverage_json_high, temp_dir
):
    """Test parsing JSON with missing optional fields."""
    # Remove files field
    data = sample_coverage_json_high.copy()
    data[0].pop("files", None)

    json_file = temp_dir / "coverage.json"
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    result = parse_coverage_json(json_file)

    assert result.overall.line_coverage.percent == pytest.approx(95.39)
    assert len(result.files) == 0
