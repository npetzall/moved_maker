"""Tests for parser module."""

import tempfile
from pathlib import Path

import pytest

from test_summary.parser import (
    TestCase,
    TestResults,
    TestSuite,
    parse_junit_xml,
)


def test_parse_junit_all_pass(sample_junit_all_pass, temp_dir):
    """Test parsing JUnit XML with all tests passing."""
    xml_file = temp_dir / "test-results.xml"
    xml_file.write_text(sample_junit_all_pass)

    results = parse_junit_xml(xml_file)

    assert len(results.suites) == 1
    assert results.total_tests == 3
    assert results.total_passed == 3
    assert results.total_failed == 0
    assert results.total_skipped == 0
    assert results.total_duration == pytest.approx(1.23)

    suite = results.suites[0]
    assert suite.name == "integration_test"
    assert suite.tests == 3
    assert suite.failures == 0
    assert suite.errors == 0
    assert suite.skipped == 0
    assert len(suite.test_cases) == 3

    for test_case in suite.test_cases:
        assert test_case.status == "passed"
        assert test_case.error_message is None


def test_parse_junit_some_fail(sample_junit_some_fail, temp_dir):
    """Test parsing JUnit XML with some tests failing."""
    xml_file = temp_dir / "test-results.xml"
    xml_file.write_text(sample_junit_some_fail)

    results = parse_junit_xml(xml_file)

    assert len(results.suites) == 1
    assert results.total_tests == 3
    assert results.total_passed == 1
    assert results.total_failed == 1
    assert results.total_skipped == 1

    suite = results.suites[0]
    assert len(suite.test_cases) == 3

    # Check failed test
    failed_test = next(tc for tc in suite.test_cases if tc.status == "failed")
    assert failed_test.name == "test_example_1"
    assert failed_test.error_message == "Expected true but got false"
    assert failed_test.error_type == "AssertionError"

    # Check passed test
    passed_test = next(tc for tc in suite.test_cases if tc.status == "passed")
    assert passed_test.name == "test_example_2"

    # Check skipped test
    skipped_test = next(tc for tc in suite.test_cases if tc.status == "skipped")
    assert skipped_test.name == "test_example_3"


def test_parse_junit_all_fail(sample_junit_all_fail, temp_dir):
    """Test parsing JUnit XML with all tests failing."""
    xml_file = temp_dir / "test-results.xml"
    xml_file.write_text(sample_junit_all_fail)

    results = parse_junit_xml(xml_file)

    assert len(results.suites) == 1
    assert results.total_tests == 2
    assert results.total_passed == 0
    assert results.total_failed == 2
    assert results.total_skipped == 0

    suite = results.suites[0]
    assert len(suite.test_cases) == 2

    for test_case in suite.test_cases:
        assert test_case.status == "failed"
        assert test_case.error_message is not None


def test_parse_junit_empty(sample_junit_empty, temp_dir):
    """Test parsing JUnit XML with no tests."""
    xml_file = temp_dir / "test-results.xml"
    xml_file.write_text(sample_junit_empty)

    results = parse_junit_xml(xml_file)

    assert len(results.suites) == 1
    assert results.total_tests == 0
    assert results.total_passed == 0
    assert results.total_failed == 0
    assert results.total_skipped == 0


def test_parse_junit_missing_file(temp_dir):
    """Test parsing non-existent file raises FileNotFoundError."""
    xml_file = temp_dir / "nonexistent.xml"

    with pytest.raises(FileNotFoundError):
        parse_junit_xml(xml_file)


def test_parse_junit_malformed(sample_junit_malformed, temp_dir):
    """Test parsing malformed XML raises ParseError."""
    xml_file = temp_dir / "test-results.xml"
    xml_file.write_text(sample_junit_malformed)

    with pytest.raises(Exception):  # ET.ParseError or similar
        parse_junit_xml(xml_file)


def test_parse_junit_testsuite_root(temp_dir):
    """Test parsing JUnit XML with testsuite as root element."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="unit_test" tests="2" failures="0" errors="0" skipped="0" time="0.50">
  <testcase name="test_one" classname="unit_test" time="0.25"/>
  <testcase name="test_two" classname="unit_test" time="0.25"/>
</testsuite>
"""
    xml_file = temp_dir / "test-results.xml"
    xml_file.write_text(xml_content)

    results = parse_junit_xml(xml_file)

    assert len(results.suites) == 1
    assert results.total_tests == 2
    assert results.total_passed == 2


def test_parse_junit_multiple_suites(temp_dir):
    """Test parsing JUnit XML with multiple test suites."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="suite1" tests="2" failures="0" errors="0" skipped="0" time="1.0">
    <testcase name="test1" classname="suite1" time="0.5"/>
    <testcase name="test2" classname="suite1" time="0.5"/>
  </testsuite>
  <testsuite name="suite2" tests="1" failures="1" errors="0" skipped="0" time="0.5">
    <testcase name="test3" classname="suite2" time="0.5">
      <failure message="Failed">Test failed</failure>
    </testcase>
  </testsuite>
</testsuites>
"""
    xml_file = temp_dir / "test-results.xml"
    xml_file.write_text(xml_content)

    results = parse_junit_xml(xml_file)

    assert len(results.suites) == 2
    assert results.total_tests == 3
    assert results.total_passed == 2
    assert results.total_failed == 1
