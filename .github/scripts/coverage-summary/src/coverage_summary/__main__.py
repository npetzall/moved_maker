"""Entry point for coverage-summary package."""

import argparse
import os
import sys
from pathlib import Path

from coverage_summary.generator import generate_markdown_summary, write_summary
from coverage_summary.parser import parse_coverage_json


def load_changed_files(changed_files_path: str | Path) -> list[str]:
    """
    Load list of changed files from file.

    Args:
        changed_files_path: Path to file containing changed files (one per line)

    Returns:
        List of changed file paths
    """
    path = Path(changed_files_path)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main() -> int:
    """Main entry point for coverage-summary application."""
    parser = argparse.ArgumentParser(
        description="Parse coverage JSON and generate markdown summary"
    )
    parser.add_argument(
        "--json-path",
        required=True,
        help="Path to coverage JSON file",
    )
    parser.add_argument(
        "--summary-path",
        help="Path to write summary (default: $GITHUB_STEP_SUMMARY)",
    )
    parser.add_argument(
        "--changed-files",
        help="Path to file containing list of changed files (one per line)",
    )
    parser.add_argument(
        "--baseline-json",
        help="Path to baseline coverage JSON for comparison",
    )
    parser.add_argument(
        "--threshold-line",
        type=float,
        default=80.0,
        help="Line coverage threshold (default: 80)",
    )
    parser.add_argument(
        "--threshold-branch",
        type=float,
        default=70.0,
        help="Branch coverage threshold (default: 70)",
    )
    parser.add_argument(
        "--threshold-function",
        type=float,
        default=85.0,
        help="Function coverage threshold (default: 85)",
    )

    args = parser.parse_args()

    # Parse coverage JSON
    try:
        coverage_data = parse_coverage_json(args.json_path)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error parsing coverage JSON: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1

    # Load changed files if provided
    changed_files = None
    if args.changed_files:
        try:
            changed_files = load_changed_files(args.changed_files)
        except Exception as e:
            print(f"Warning: Failed to load changed files: {e}", file=sys.stderr)
            # Continue without changed files filtering

    # Load baseline if provided
    baseline_data = None
    if args.baseline_json:
        try:
            baseline_data = parse_coverage_json(args.baseline_json)
        except Exception as e:
            print(
                f"Warning: Failed to load baseline coverage: {e}",
                file=sys.stderr,
            )
            # Continue without baseline comparison

    # Generate markdown summary
    try:
        summary = generate_markdown_summary(
            coverage_data,
            threshold_line=args.threshold_line,
            threshold_branch=args.threshold_branch,
            threshold_function=args.threshold_function,
            changed_files=changed_files,
            baseline_data=baseline_data,
        )
    except Exception as e:
        print(f"Error generating summary: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1

    # Write summary
    try:
        write_summary(summary, args.summary_path)
        output_path = args.summary_path or os.environ.get("GITHUB_STEP_SUMMARY")
        if output_path:
            print(f"✅ Coverage summary written to: {output_path}")
    except Exception as e:
        print(f"Error writing summary: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
