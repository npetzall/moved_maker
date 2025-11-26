"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_junit_all_pass():
    """Sample JUnit XML with all tests passing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="integration_test" tests="3" failures="0" errors="0" skipped="0" time="1.23">
    <testcase name="test_example_1" classname="integration_test" time="0.41"/>
    <testcase name="test_example_2" classname="integration_test" time="0.42"/>
    <testcase name="test_example_3" classname="integration_test" time="0.40"/>
  </testsuite>
</testsuites>
"""


@pytest.fixture
def sample_junit_some_fail():
    """Sample JUnit XML with some tests failing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="integration_test" tests="3" failures="1" errors="0" skipped="1" time="1.50">
    <testcase name="test_example_1" classname="integration_test" time="0.50">
      <failure message="Assertion failed" type="AssertionError">Expected true but got false</failure>
    </testcase>
    <testcase name="test_example_2" classname="integration_test" time="0.50"/>
    <testcase name="test_example_3" classname="integration_test" time="0.50">
      <skipped/>
    </testcase>
  </testsuite>
</testsuites>
"""


@pytest.fixture
def sample_junit_all_fail():
    """Sample JUnit XML with all tests failing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="integration_test" tests="2" failures="2" errors="0" skipped="0" time="0.80">
    <testcase name="test_example_1" classname="integration_test" time="0.40">
      <failure message="Test failed" type="RuntimeError">Something went wrong</failure>
    </testcase>
    <testcase name="test_example_2" classname="integration_test" time="0.40">
      <error message="Error occurred" type="ValueError">Invalid value</error>
    </testcase>
  </testsuite>
</testsuites>
"""


@pytest.fixture
def sample_junit_empty():
    """Sample JUnit XML with no tests."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="integration_test" tests="0" failures="0" errors="0" skipped="0" time="0.00">
  </testsuite>
</testsuites>
"""


@pytest.fixture
def sample_junit_malformed():
    """Malformed JUnit XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="integration_test"
"""
