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
                    "count": 215,  # Integer: 200 + 5 + 10
                    "covered": 200,
                },
                "branches": {
                    "percent": 90.0,
                    "count": 50,  # Integer: 45 + 2 + 3
                    "covered": 45,
                    "notcovered": 5,  # 2 + 3
                },
                "functions": {
                    "percent": 94.74,
                    "count": 19,  # Integer: 18 + 0 + 1
                    "covered": 18,
                },
            },
            "files": [
                {
                    "filename": "src/main.rs",
                    "summary": {
                        "lines": {
                            "percent": 100.0,
                            "count": 50,
                            "covered": 50,
                        },
                        "branches": {
                            "percent": 100.0,
                            "count": 10,
                            "covered": 10,
                            "notcovered": 0,
                        },
                        "functions": {
                            "percent": 100.0,
                            "count": 5,
                            "covered": 5,
                        },
                    },
                },
                {
                    "filename": "src/lib.rs",
                    "summary": {
                        "lines": {
                            "percent": 90.0,
                            "count": 100,  # 90 + 5 + 5
                            "covered": 90,
                        },
                        "branches": {
                            "percent": 85.0,
                            "count": 20,  # 17 + 2 + 1
                            "covered": 17,
                            "notcovered": 3,  # 2 + 1
                        },
                        "functions": {
                            "percent": 92.0,
                            "count": 25,  # 23 + 0 + 2
                            "covered": 23,
                        },
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
                    "count": 100,  # 60 + 10 + 30
                    "covered": 60,
                },
                "branches": {
                    "percent": 50.0,
                    "count": 20,  # 10 + 5 + 5
                    "covered": 10,
                    "notcovered": 10,  # 5 + 5
                },
                "functions": {
                    "percent": 70.0,
                    "count": 10,  # 7 + 0 + 3
                    "covered": 7,
                },
            },
            "files": [
                {
                    "filename": "src/main.rs",
                    "summary": {
                        "lines": {
                            "percent": 50.0,
                            "count": 50,  # 25 + 5 + 20
                            "covered": 25,
                        },
                        "branches": {
                            "percent": 40.0,
                            "count": 10,  # 4 + 2 + 4
                            "covered": 4,
                            "notcovered": 6,  # 2 + 4
                        },
                        "functions": {
                            "percent": 60.0,
                            "count": 5,  # 3 + 0 + 2
                            "covered": 3,
                        },
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
                    "count": 215,  # 200 + 5 + 10
                    "covered": 200,
                },
                "branches": {
                    "percent": 0.0,
                    "count": 0,
                    "covered": 0,
                    "notcovered": 0,
                },
                "functions": {
                    "percent": 94.74,
                    "count": 19,  # 18 + 0 + 1
                    "covered": 18,
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
                    "count": 0,
                    "covered": 0,
                },
                "branches": {
                    "percent": 0.0,
                    "count": 0,
                    "covered": 0,
                    "notcovered": 0,
                },
                "functions": {
                    "percent": 0.0,
                    "count": 0,
                    "covered": 0,
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
