"""Tests for formatter module."""

import pytest

from test_summary.formatter import (
    format_duration,
    generate_markdown_summary,
    get_status_emoji,
)
from test_summary.parser import TestCase, TestResults, TestSuite


def test_format_duration():
    """Test duration formatting."""
    assert format_duration(1.23) == "1.23s"
    assert format_duration(45.67) == "45.67s"
    assert format_duration(0.01) == "0.01s"


def test_get_status_emoji():
    """Test status emoji selection."""
    assert get_status_emoji(5, 0, 0) == "✅"
    assert get_status_emoji(5, 1, 0) == "❌"
    assert get_status_emoji(5, 0, 1) == "⚠️"
    assert get_status_emoji(0, 0, 5) == "⚠️"


def test_generate_markdown_all_pass():
    """Test markdown generation with all tests passing."""
    suite = TestSuite(
        name="integration_test",
        tests=3,
        failures=0,
        errors=0,
        skipped=0,
        duration=1.23,
        test_cases=[
            TestCase("test1", "integration_test", "passed", 0.41),
            TestCase("test2", "integration_test", "passed", 0.42),
            TestCase("test3", "integration_test", "passed", 0.40),
        ],
    )

    results = TestResults(
        suites=[suite],
        total_tests=3,
        total_passed=3,
        total_failed=0,
        total_skipped=0,
        total_duration=1.23,
    )

    summary = generate_markdown_summary(results)

    assert "# Test Results Summary" in summary
    assert "✅" in summary
    assert "3 passed" in summary
    assert "integration_test" in summary
    assert "```mermaid" in summary
    assert '"Passed" : 3' in summary
    assert "Failed Tests" not in summary


def test_generate_markdown_with_failures():
    """Test markdown generation with test failures."""
    suite = TestSuite(
        name="integration_test",
        tests=2,
        failures=1,
        errors=0,
        skipped=0,
        duration=0.80,
        test_cases=[
            TestCase("test1", "integration_test", "passed", 0.40),
            TestCase(
                "test2",
                "integration_test",
                "failed",
                0.40,
                error_message="Test failed",
                error_type="AssertionError",
            ),
        ],
    )

    results = TestResults(
        suites=[suite],
        total_tests=2,
        total_passed=1,
        total_failed=1,
        total_skipped=0,
        total_duration=0.80,
    )

    summary = generate_markdown_summary(results)

    assert "❌" in summary
    assert "1 passed, 1 failed" in summary
    assert "## Failed Tests" in summary
    assert "test2" in summary
    assert "Test failed" in summary
    assert "AssertionError" in summary
    assert '"Failed" : 1' in summary


def test_generate_markdown_with_skipped():
    """Test markdown generation with skipped tests."""
    suite = TestSuite(
        name="integration_test",
        tests=3,
        failures=0,
        errors=0,
        skipped=1,
        duration=1.50,
        test_cases=[
            TestCase("test1", "integration_test", "passed", 0.50),
            TestCase("test2", "integration_test", "passed", 0.50),
            TestCase("test3", "integration_test", "skipped", 0.50),
        ],
    )

    results = TestResults(
        suites=[suite],
        total_tests=3,
        total_passed=2,
        total_failed=0,
        total_skipped=1,
        total_duration=1.50,
    )

    summary = generate_markdown_summary(results)

    assert "✅" in summary
    assert "2 passed, 1 skipped" in summary
    assert '"Skipped" : 1' in summary


def test_generate_markdown_with_artifact():
    """Test markdown generation with artifact name."""
    suite = TestSuite(
        name="integration_test",
        tests=1,
        failures=0,
        errors=0,
        skipped=0,
        duration=0.50,
        test_cases=[TestCase("test1", "integration_test", "passed", 0.50)],
    )

    results = TestResults(
        suites=[suite],
        total_tests=1,
        total_passed=1,
        total_failed=0,
        total_skipped=0,
        total_duration=0.50,
    )

    summary = generate_markdown_summary(results, artifact_name="test-results-ubuntu")

    assert "## Test Artifacts" in summary
    assert "test-results-ubuntu" in summary


def test_generate_markdown_empty():
    """Test markdown generation with empty results."""
    results = TestResults(
        suites=[],
        total_tests=0,
        total_passed=0,
        total_failed=0,
        total_skipped=0,
        total_duration=0.0,
    )

    summary = generate_markdown_summary(results)

    assert "# Test Results Summary" in summary
    assert "0 tests" in summary or "Total" in summary


def test_generate_markdown_multiple_suites():
    """Test markdown generation with multiple test suites."""
    suite1 = TestSuite(
        name="suite1",
        tests=2,
        failures=0,
        errors=0,
        skipped=0,
        duration=1.0,
        test_cases=[
            TestCase("test1", "suite1", "passed", 0.5),
            TestCase("test2", "suite1", "passed", 0.5),
        ],
    )

    suite2 = TestSuite(
        name="suite2",
        tests=1,
        failures=1,
        errors=0,
        skipped=0,
        duration=0.5,
        test_cases=[
            TestCase(
                "test3",
                "suite2",
                "failed",
                0.5,
                error_message="Failed",
                error_type="RuntimeError",
            ),
        ],
    )

    results = TestResults(
        suites=[suite1, suite2],
        total_tests=3,
        total_passed=2,
        total_failed=1,
        total_skipped=0,
        total_duration=1.5,
    )

    summary = generate_markdown_summary(results)

    assert "suite1" in summary
    assert "suite2" in summary
    assert "3 tests in 2 suite(s)" in summary
