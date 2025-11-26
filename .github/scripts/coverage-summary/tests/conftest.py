"""Pytest configuration and fixtures."""

import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_coverage_json_high():
    """Sample coverage JSON with high coverage."""
    return [
        {
            "totals": {
                "lines": {
                    "percent": 95.39,
                    "count": {"covered": 200, "partial": 5, "missed": 10},
                },
                "branches": {
                    "percent": 90.0,
                    "count": {"covered": 45, "partial": 2, "missed": 3},
                },
                "functions": {
                    "percent": 94.74,
                    "count": {"covered": 18, "partial": 0, "missed": 1},
                },
            },
            "files": [
                {
                    "filename": "src/main.rs",
                    "lines": {
                        "percent": 100.0,
                        "count": {"covered": 50, "partial": 0, "missed": 0},
                    },
                    "branches": {
                        "percent": 100.0,
                        "count": {"covered": 10, "partial": 0, "missed": 0},
                    },
                    "functions": {
                        "percent": 100.0,
                        "count": {"covered": 5, "partial": 0, "missed": 0},
                    },
                },
                {
                    "filename": "src/lib.rs",
                    "lines": {
                        "percent": 90.0,
                        "count": {"covered": 90, "partial": 5, "missed": 5},
                    },
                    "branches": {
                        "percent": 85.0,
                        "count": {"covered": 17, "partial": 2, "missed": 1},
                    },
                    "functions": {
                        "percent": 92.0,
                        "count": {"covered": 23, "partial": 0, "missed": 2},
                    },
                },
            ],
        }
    ]


@pytest.fixture
def sample_coverage_json_low():
    """Sample coverage JSON with low coverage."""
    return [
        {
            "totals": {
                "lines": {
                    "percent": 60.0,
                    "count": {"covered": 60, "partial": 10, "missed": 30},
                },
                "branches": {
                    "percent": 50.0,
                    "count": {"covered": 10, "partial": 5, "missed": 5},
                },
                "functions": {
                    "percent": 70.0,
                    "count": {"covered": 7, "partial": 0, "missed": 3},
                },
            },
            "files": [
                {
                    "filename": "src/main.rs",
                    "lines": {
                        "percent": 50.0,
                        "count": {"covered": 25, "partial": 5, "missed": 20},
                    },
                    "branches": {
                        "percent": 40.0,
                        "count": {"covered": 4, "partial": 2, "missed": 4},
                    },
                    "functions": {
                        "percent": 60.0,
                        "count": {"covered": 3, "partial": 0, "missed": 2},
                    },
                },
            ],
        }
    ]


@pytest.fixture
def sample_coverage_json_no_branches():
    """Sample coverage JSON with no branches (count = 0)."""
    return [
        {
            "totals": {
                "lines": {
                    "percent": 95.39,
                    "count": {"covered": 200, "partial": 5, "missed": 10},
                },
                "branches": {
                    "percent": 0.0,
                    "count": {"covered": 0, "partial": 0, "missed": 0},
                },
                "functions": {
                    "percent": 94.74,
                    "count": {"covered": 18, "partial": 0, "missed": 1},
                },
            },
            "files": [],
        }
    ]


@pytest.fixture
def sample_coverage_json_empty():
    """Sample coverage JSON with empty files."""
    return [
        {
            "totals": {
                "lines": {
                    "percent": 0.0,
                    "count": {"covered": 0, "partial": 0, "missed": 0},
                },
                "branches": {
                    "percent": 0.0,
                    "count": {"covered": 0, "partial": 0, "missed": 0},
                },
                "functions": {
                    "percent": 0.0,
                    "count": {"covered": 0, "partial": 0, "missed": 0},
                },
            },
            "files": [],
        }
    ]


@pytest.fixture
def sample_coverage_json_file(temp_dir, sample_coverage_json_high):
    """Create a temporary coverage JSON file."""
    json_file = temp_dir / "coverage.json"
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(sample_coverage_json_high, f)
    return json_file
