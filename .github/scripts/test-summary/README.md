# Test Summary

A Python script to parse JUnit XML test results from `cargo nextest` and generate rich markdown summaries with tables and Mermaid pie charts for GitHub Actions job step summaries.

## Usage

### Setup

Install dependencies using `uv`:

```bash
cd .github/scripts/test-summary
uv sync --extra dev
```

### Running the Script

Run the script using `uv run`:

```bash
uv run python -m test_summary --xml-path target/nextest/**/test-results.xml --artifact-name test-results-ubuntu-latest
```

### Command-Line Arguments

- `--xml-path`: Path to JUnit XML file (required)
- `--artifact-name`: Name of test artifact (optional, for linking)
- `--output`: Path to output file (default: `$GITHUB_STEP_SUMMARY` or stdout)

### Example Output

The script generates a markdown summary with:
- Test results table showing suite breakdown, status, counts, and duration
- Mermaid pie chart visualizing test result distribution
- Failed test details with error messages (if any)
- Links to test artifacts (if artifact name provided)

### Testing

Run tests using pytest:

```bash
uv run pytest
```

For verbose output:

```bash
uv run pytest -v
```

## Integration

The script is integrated into GitHub Actions workflows:
- `pull_request.yaml`: Test summary for `test-ubuntu` and `test-macos` jobs
- `release-build.yaml`: Test summary for `build-and-release` job

The script writes to `$GITHUB_STEP_SUMMARY` which is automatically displayed in the workflow run summary page.
