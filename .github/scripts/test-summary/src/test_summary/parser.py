"""Parser for JUnit XML test results."""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class TestCase:
    """Represents a single test case."""

    name: str
    classname: str
    status: str  # "passed", "failed", "skipped"
    duration: float
    error_message: str | None = None
    error_type: str | None = None
    stack_trace: str | None = None


@dataclass
class TestSuite:
    """Represents a test suite."""

    name: str
    tests: int
    failures: int
    errors: int
    skipped: int
    duration: float
    test_cases: List[TestCase]


@dataclass
class TestResults:
    """Represents parsed test results."""

    suites: List[TestSuite]
    total_tests: int
    total_passed: int
    total_failed: int
    total_skipped: int
    total_duration: float


def parse_junit_xml(xml_path: str | Path) -> TestResults:
    """
    Parse JUnit XML file and extract test results.

    Args:
        xml_path: Path to JUnit XML file

    Returns:
        TestResults object with parsed test data

    Raises:
        FileNotFoundError: If XML file does not exist
        ET.ParseError: If XML is malformed
        ValueError: If XML structure is invalid
    """
    xml_path = Path(xml_path)

    if not xml_path.exists():
        raise FileNotFoundError(f"Test results file not found: {xml_path}")

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ET.ParseError(f"Failed to parse XML file {xml_path}: {e}") from e

    suites: List[TestSuite] = []
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    total_duration = 0.0

    # Handle both <testsuites> and <testsuite> root elements
    if root.tag == "testsuites":
        suite_elements = root.findall("testsuite")
        # Also check if root has attributes (aggregate testsuites)
        if not suite_elements and root.attrib:
            # Root is an aggregate testsuites element
            suite_elements = [root]
    elif root.tag == "testsuite":
        suite_elements = [root]
    else:
        raise ValueError(f"Unexpected root element: {root.tag}")

    for suite_elem in suite_elements:
        suite_name = suite_elem.get("name", "Unknown Suite")
        suite_tests = int(suite_elem.get("tests", 0))
        suite_failures = int(suite_elem.get("failures", 0))
        suite_errors = int(suite_elem.get("errors", 0))
        suite_skipped = int(suite_elem.get("skipped", 0))
        suite_duration = float(suite_elem.get("time", 0.0))

        test_cases: List[TestCase] = []

        for testcase_elem in suite_elem.findall("testcase"):
            test_name = testcase_elem.get("name", "Unknown Test")
            test_classname = testcase_elem.get("classname", "")
            test_duration = float(testcase_elem.get("time", 0.0))

            # Determine test status
            status = "passed"
            error_message = None
            error_type = None
            stack_trace = None

            # Check for failure
            failure_elem = testcase_elem.find("failure")
            if failure_elem is not None:
                status = "failed"
                error_message = failure_elem.text or failure_elem.get("message", "")
                error_type = failure_elem.get("type", "")
                stack_trace = failure_elem.text

            # Check for error
            error_elem = testcase_elem.find("error")
            if error_elem is not None:
                status = "failed"  # Errors are treated as failures
                error_message = error_elem.text or error_elem.get("message", "")
                error_type = error_elem.get("type", "")
                stack_trace = error_elem.text

            # Check for skipped
            skipped_elem = testcase_elem.find("skipped")
            if skipped_elem is not None:
                status = "skipped"

            test_case = TestCase(
                name=test_name,
                classname=test_classname,
                status=status,
                duration=test_duration,
                error_message=error_message,
                error_type=error_type,
                stack_trace=stack_trace,
            )
            test_cases.append(test_case)

        suite = TestSuite(
            name=suite_name,
            tests=suite_tests,
            failures=suite_failures,
            errors=suite_errors,
            skipped=suite_skipped,
            duration=suite_duration,
            test_cases=test_cases,
        )
        suites.append(suite)

        total_tests += suite_tests
        total_failed += suite_failures + suite_errors
        total_skipped += suite_skipped
        total_duration += suite_duration

    # Calculate passed tests
    total_passed = total_tests - total_failed - total_skipped

    return TestResults(
        suites=suites,
        total_tests=total_tests,
        total_passed=total_passed,
        total_failed=total_failed,
        total_skipped=total_skipped,
        total_duration=total_duration,
    )
