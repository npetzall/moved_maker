# PR Labels

Python script for automatically labeling pull requests based on Conventional Commit patterns.

## Description

This script analyzes all commits in a pull request and applies version bump labels (`version: major`, `version: minor`, `version: patch`) and semantic labels (`breaking`, `feature`) based on Conventional Commit patterns.

## Installation

Install dependencies using `uv`:

```bash
cd .github/scripts/pr-labels
uv sync --extra dev
```

## Usage

The script is designed to run in GitHub Actions workflows. It requires the following environment variables:

- `GITHUB_TOKEN`: GitHub personal access token or app token (automatically available in GitHub Actions)
- `GITHUB_REPOSITORY`: Repository name in format "owner/repo" (automatically available in GitHub Actions)
- `GITHUB_EVENT_PATH` or `PR_NUMBER`: Either the path to the GitHub event JSON file (automatically available in GitHub Actions) or the PR number as an environment variable

### Running Locally

To run the script locally for testing:

```bash
cd .github/scripts/pr-labels
export GITHUB_TOKEN="your_token_here"
export GITHUB_REPOSITORY="owner/repo"
export PR_NUMBER=123
uv run python -m pr_labels
```

## Commit Message Format

The script detects Conventional Commit patterns:

- **Major version** (`version: major` + `breaking`): Commits containing `BREAKING CHANGE:` or `!:`
- **Minor version** (`version: minor` + `feature`): Commits starting with `feat:`
- **Patch version** (no label): All other commits (default)

The script analyzes all commits in a PR and applies the highest priority label (breaking > feature > patch).

## Label Management

The script automatically:
- Removes existing conflicting labels before applying new ones
- Creates missing labels if they don't exist in the repository
- Handles GitHub API errors gracefully

## Testing

Run tests using pytest:

```bash
cd .github/scripts/pr-labels
uv run pytest -v
```

For test coverage:

```bash
uv run pytest --cov
```

## Constraints and Requirements

- Python 3.11 or higher
- Requires `pull-requests: write` permission in GitHub Actions
- Labels are created automatically if missing (requires repository write access)
- The script uses PyGithub for GitHub API interactions

## Dependencies

- `pygithub>=2.0.0`: GitHub API client library

## Development Dependencies

- `pytest>=8.0.0`: Testing framework
- `pytest-datadir>=1.4.0`: Test data directory support
