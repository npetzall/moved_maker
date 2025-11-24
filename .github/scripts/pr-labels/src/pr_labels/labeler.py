"""PR label management logic."""
import sys
from typing import List, Optional

from github import GithubException
from github.Label import Label
from github.PullRequest import PullRequest
from github.Repository import Repository

from pr_labels.parser import parse_commits


# Label definitions
LABELS = {
    "version: major": {"color": "d73a4a", "description": "Major version bump"},
    "version: minor": {"color": "0075ca", "description": "Minor version bump"},
    "version: patch": {"color": "0e8a16", "description": "Patch version bump"},
    "breaking": {"color": "b60205", "description": "Breaking change"},
    "feature": {"color": "0e8a16", "description": "New feature"},
}

# Conflicting labels to remove
VERSION_LABELS = ["version: major", "version: minor", "version: patch"]
SEMANTIC_LABELS = ["breaking", "feature"]


def ensure_label_exists(repo: Repository, label_name: str) -> None:
    """Ensure a label exists in the repository, creating it if missing.

    Args:
        repo: Repository object
        label_name: Name of the label to ensure exists

    Raises:
        GithubException: If label cannot be created or accessed
    """
    try:
        repo.get_label(label_name)
    except GithubException as e:
        if e.status == 404:
            # Label doesn't exist, create it
            label_def = LABELS[label_name]
            try:
                repo.create_label(
                    name=label_name,
                    color=label_def["color"],
                    description=label_def["description"],
                )
                print(f"Created label: {label_name}")
            except GithubException as create_error:
                print(
                    f"Error creating label {label_name}: {create_error}",
                    file=sys.stderr,
                )
                raise
        else:
            print(f"Error checking label {label_name}: {e}", file=sys.stderr)
            raise


def get_existing_labels(pr: PullRequest) -> List[Label]:
    """Get existing labels on a pull request.

    Args:
        pr: PullRequest object

    Returns:
        List of Label objects

    Raises:
        GithubException: If labels cannot be retrieved
    """
    try:
        return list(pr.get_labels())
    except GithubException as e:
        print(f"Error getting PR labels: {e}", file=sys.stderr)
        raise


def remove_label(pr: PullRequest, label_name: str) -> None:
    """Remove a label from a pull request.

    Args:
        pr: PullRequest object
        label_name: Name of the label to remove

    Raises:
        GithubException: If label cannot be removed
    """
    try:
        pr.remove_from_labels(label_name)
    except GithubException as e:
        # Ignore 404 errors (label doesn't exist or already removed)
        if e.status != 404:
            print(f"Error removing label {label_name}: {e}", file=sys.stderr)
            raise


def add_label(pr: PullRequest, label_name: str) -> None:
    """Add a label to a pull request.

    Args:
        pr: PullRequest object
        label_name: Name of the label to add

    Raises:
        GithubException: If label cannot be added
    """
    try:
        pr.add_to_labels(label_name)
    except GithubException as e:
        print(f"Error adding label {label_name}: {e}", file=sys.stderr)
        raise


def apply_labels(pr: PullRequest, repo: Repository) -> None:
    """Apply version and semantic labels to a pull request based on commits.

    This function:
    1. Gets all commits from the PR
    2. Parses commits to determine version bump type
    3. Removes existing conflicting labels
    4. Ensures target labels exist (creates if missing)
    5. Applies correct version and semantic labels

    Args:
        pr: PullRequest object
        repo: Repository object

    Raises:
        GithubException: If any GitHub API operation fails
    """
    # Get all commits from PR
    try:
        commits = list(pr.get_commits())
    except GithubException as e:
        print(f"Error getting PR commits: {e}", file=sys.stderr)
        raise

    # Parse commits to determine version bump type
    version_label, alt_label = parse_commits(commits)

    # Remove existing conflicting labels
    all_conflicting_labels = VERSION_LABELS + SEMANTIC_LABELS
    for label_name in all_conflicting_labels:
        remove_label(pr, label_name)

    # Apply new labels if determined
    if version_label:
        # Ensure labels exist
        ensure_label_exists(repo, version_label)
        if alt_label:
            ensure_label_exists(repo, alt_label)

        # Add labels
        add_label(pr, version_label)
        if alt_label:
            add_label(pr, alt_label)

        labels_applied = f"{version_label}"
        if alt_label:
            labels_applied += f" and {alt_label}"
        print(f"Applied labels: {labels_applied}")
    else:
        print("No version label applied (patch bump)")
