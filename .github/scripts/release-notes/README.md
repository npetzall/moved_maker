# Release Notes

Python script for generating release notes from GitHub releases and commits.

## Testing

Run tests using pytest:

```bash
cd .github/scripts/release-notes
uv run pytest -v
```

## Coverage

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

### Coverage Configuration

- **Threshold**: 80% minimum coverage (tests will fail if coverage is below this threshold)
- **Exclusions**: Test files, `__init__.py`, and `__main__.py` are excluded from coverage calculations
- **Source**: Coverage is measured for code in `src/release_notes/`
