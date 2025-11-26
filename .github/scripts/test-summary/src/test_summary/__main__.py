"""Entry point for test-summary package."""

import argparse
import os
import sys
from pathlib import Path

from test_summary.formatter import generate_markdown_summary
from test_summary.parser import parse_junit_xml


def find_xml_files(xml_path: str) -> list[Path]:
    """
    Find JUnit XML files matching the given path pattern.

    Supports glob patterns and returns all matching files.

    Args:
        xml_path: Path pattern (may contain glob patterns)

    Returns:
        List of matching XML file paths
    """
    path = Path(xml_path)

    # If path contains glob patterns, use glob
    if "*" in str(path) or "**" in str(path):
        # Find the base directory for globbing
        parts = path.parts
        glob_index = next(
            (i for i, part in enumerate(parts) if "*" in part), len(parts)
        )
        base_dir = Path(*parts[:glob_index]) if glob_index > 0 else Path(".")
        pattern = str(Path(*parts[glob_index:]))

        if not base_dir.exists():
            return []

        xml_files = list(base_dir.glob(pattern))
        return sorted(xml_files)

    # Single file path
    if path.exists():
        return [path]

    return []


def main() -> int:
    """Main entry point for test-summary application."""
    parser = argparse.ArgumentParser(
        description="Parse JUnit XML test results and generate markdown summary"
    )
    parser.add_argument(
        "--xml-path",
        required=True,
        help="Path to JUnit XML file (supports glob patterns)",
    )
    parser.add_argument(
        "--artifact-name",
        help="Name of test artifact (optional, for linking)",
    )
    parser.add_argument(
        "--output",
        help="Path to output file (default: $GITHUB_STEP_SUMMARY or stdout)",
    )

    args = parser.parse_args()

    # Find XML files
    xml_files = find_xml_files(args.xml_path)

    if not xml_files:
        print(
            f"Error: No JUnit XML files found matching: {args.xml_path}",
            file=sys.stderr,
        )
        return 1

    # Parse all XML files and combine results
    all_suites = []
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    total_duration = 0.0

    for xml_file in xml_files:
        try:
            results = parse_junit_xml(xml_file)
            all_suites.extend(results.suites)
            total_tests += results.total_tests
            total_passed += results.total_passed
            total_failed += results.total_failed
            total_skipped += results.total_skipped
            total_duration += results.total_duration
        except FileNotFoundError as e:
            print(f"Warning: {e}", file=sys.stderr)
            continue
        except Exception as e:
            print(
                f"Error parsing {xml_file}: {e}",
                file=sys.stderr,
            )
            return 1

    if not all_suites and total_tests == 0:
        print(
            "Warning: No test results found in XML files",
            file=sys.stderr,
        )
        # Still generate a summary for empty results
        from test_summary.parser import TestResults, TestSuite

        combined_results = TestResults(
            suites=[],
            total_tests=0,
            total_passed=0,
            total_failed=0,
            total_skipped=0,
            total_duration=0.0,
        )
    else:
        from test_summary.parser import TestResults

        combined_results = TestResults(
            suites=all_suites,
            total_tests=total_tests,
            total_passed=total_passed,
            total_failed=total_failed,
            total_skipped=total_skipped,
            total_duration=total_duration,
        )

    # Generate markdown summary
    try:
        summary = generate_markdown_summary(combined_results, args.artifact_name)
    except Exception as e:
        print(f"Error generating summary: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1

    # Determine output destination
    output_path = None
    if args.output:
        output_path = Path(args.output)
    else:
        # Try GITHUB_STEP_SUMMARY environment variable
        github_step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if github_step_summary:
            output_path = Path(github_step_summary)

    # Write summary
    try:
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding="utf-8") as f:
                f.write(summary)
            print(f"✅ Test summary written to: {output_path}")
        else:
            # Write to stdout
            print(summary)
    except Exception as e:
        print(f"Error writing summary: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
