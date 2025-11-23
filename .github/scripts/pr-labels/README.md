# PR Labels

A Python-based PR labeling utility for moved_maker that automatically applies semantic versioning labels based on Conventional Commits.

## Features

- Analyzes PR commits for Conventional Commit patterns
- Automatically applies version labels (major, minor, patch)
- Creates labels if they don't exist
- Supports dry-run mode for testing
- Removes conflicting version labels

## Usage

```bash
# From within the package directory
python -m pr_labels <PR_NUMBER>

# With dry-run mode
python -m pr_labels <PR_NUMBER> --dry-run

# Using environment variables
PR_NUM=123 python -m pr_labels
```

## Environment Variables

- `GITHUB_TOKEN`: GitHub API token (required)
- `GITHUB_REPOSITORY`: Repository in format owner/name (required)
- `PR_NUM` or `PR_NUMBER`: PR number (optional if provided as argument)

## Installation

```bash
pip install .
```
