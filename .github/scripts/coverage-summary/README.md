# Coverage Summary

A Python script to parse coverage JSON output from `cargo llvm-cov` and generate rich markdown summaries with tables and Mermaid pie charts for GitHub Actions job step summaries.

## Usage

### Setup

Install dependencies using `uv`:

```bash
cd .github/scripts/coverage-summary
uv sync --extra dev
```

### Running the Script

Run the script using `uv run`:

```bash
uv run python -m coverage_summary --json-path coverage.json
```

For PR workflows with changed files:

```bash
uv run python -m coverage_summary \
  --json-path coverage.json \
  --changed-files changed-files.txt
```

### Command-Line Arguments

- `--json-path`: Path to coverage JSON file (required)
- `--summary-path`: Path to write summary (default: `$GITHUB_STEP_SUMMARY`)
- `--changed-files`: Path to file containing list of changed files (optional, one per line)
- `--baseline-json`: Path to baseline coverage JSON for comparison (optional)
- `--threshold-line`: Line coverage threshold (default: 80)
- `--threshold-branch`: Branch coverage threshold (default: 70)
- `--threshold-function`: Function coverage threshold (default: 85)

### Example Output

The script generates a markdown summary with:
- Overall coverage percentage with visual indicators (✅/⚠️/❌)
- Coverage metrics table (line, branch, function coverage)
- Mermaid pie chart visualizing coverage distribution
- File-by-file breakdown for changed files (in PR workflows)
- Coverage regression comparison (when baseline provided)

### Testing

Run tests using pytest:

```bash
uv run pytest
```

For verbose output:

```bash
uv run pytest -v
```

### Coverage

Code coverage reporting is integrated into the test suite using `pytest-cov`. Coverage reports are automatically generated when running tests:

```bash
uv run pytest
```

The coverage report shows:
- Overall coverage percentage
- Missing line indicators for uncovered code
- Coverage threshold enforcement (80% minimum)

To generate an HTML coverage report:

```bash
uv run pytest --cov-report=html
```

The HTML report will be generated in `htmlcov/` directory. Open `htmlcov/index.html` in a browser to view detailed coverage information.

**Coverage Configuration:**
- **Threshold**: 80% minimum coverage (tests will fail if coverage is below this threshold)
- **Exclusions**: Test files, `__init__.py`, and `__main__.py` are excluded from coverage calculations
- **Source**: Coverage is measured for code in `src/coverage_summary/`

## Integration

The script is integrated into GitHub Actions workflows:
- `pull_request.yaml`: Coverage summary for `coverage` job
- `release-build.yaml`: Coverage summary for `coverage` job

The script writes to `$GITHUB_STEP_SUMMARY` which is automatically displayed in the workflow run summary page.

## Expected JSON Structure

The script expects coverage JSON from `cargo llvm-cov report --json` with the following structure:

```json
[
  {
    "totals": {
      "lines": {
        "percent": 95.39,
        "count": {"covered": 200, "partial": 5, "missed": 10}
      },
      "branches": {
        "percent": 90.0,
        "count": {"covered": 45, "partial": 2, "missed": 3}
      },
      "functions": {
        "percent": 94.74,
        "count": {"covered": 18, "partial": 0, "missed": 1}
      }
    },
    "files": [
      {
        "filename": "src/main.rs",
        "lines": {...},
        "branches": {...},
        "functions": {...}
      }
    ]
  }
]
```

## Troubleshooting

- **No summary generated**: Check that `coverage.json` exists and is valid JSON
- **Missing files in breakdown**: Ensure changed files list contains paths matching coverage file paths
- **Mermaid chart not rendering**: Verify Mermaid syntax is valid (should be automatically generated correctly)
- **Coverage percentages are 0**: Verify coverage JSON was generated correctly from `cargo llvm-cov report --json`
