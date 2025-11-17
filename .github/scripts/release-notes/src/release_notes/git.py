"""Git operations using PyGitHub."""

import subprocess
from typing import Optional

from github import Repository
from packaging import version


def get_tags_sorted(repo: Repository) -> list:
    """
    Get tags sorted by semantic version (descending: newest first).

    Args:
        repo: GitHub repository object

    Returns:
        List of tags sorted by semantic version (newest first)

    Raises:
        ValueError: If a tag cannot be parsed as a semantic version
    """
    tags = list(repo.get_tags())
    # Sort by semantic version
    try:
        tags.sort(
            key=lambda t: version.parse(t.name.lstrip("v")),
            reverse=True,
        )
    except version.InvalidVersion as e:
        # Filter out invalid version tags and log warning
        valid_tags = []
        for tag in tags:
            try:
                version.parse(tag.name.lstrip("v"))
                valid_tags.append(tag)
            except version.InvalidVersion:
                # Skip invalid version tags
                continue
        tags = valid_tags
        tags.sort(
            key=lambda t: version.parse(t.name.lstrip("v")),
            reverse=True,
        )
    return tags


def get_previous_tag(repo: Repository, current_tag_name: str) -> Optional[object]:
    """
    Get the previous tag before the current tag.

    Args:
        repo: GitHub repository object
        current_tag_name: Name of the current tag (e.g., "v1.2.0")

    Returns:
        Previous tag object, or None if this is the first tag
    """
    tags = get_tags_sorted(repo)
    if not tags:
        return None

    # Find current tag in sorted list
    current_index = None
    for i, tag in enumerate(tags):
        if tag.name == current_tag_name:
            current_index = i
            break

    if current_index is None:
        # Current tag not found, return None
        return None

    # Get next tag in sorted list (which is the previous version)
    if current_index + 1 < len(tags):
        return tags[current_index + 1]

    # This is the first tag (oldest)
    return None


def get_commits_between_tags(
    repo: Repository, previous_tag: object, current_tag: object
) -> list:
    """
    Get commits between two tags.

    Args:
        repo: GitHub repository object
        previous_tag: Previous tag object
        current_tag: Current tag object

    Returns:
        List of commit objects between the two tags
    """
    if previous_tag is None:
        return []

    # Use compare API to get commits between two SHAs
    comparison = repo.compare(
        previous_tag.commit.sha,
        current_tag.commit.sha,
    )
    return list(comparison.commits)


def get_all_commits(repo: Repository) -> list:
    """
    Get all commits from the repository (for first release).

    Args:
        repo: GitHub repository object

    Returns:
        List of all commit objects
    """
    commits = []
    for commit in repo.get_commits():
        commits.append(commit)
    return commits


def get_commit_shas_by_path(
    previous_tag: Optional[str], current_tag: str, paths: list[str]
) -> set[str]:
    """
    Get commit SHAs that modify specified paths using git CLI.

    Args:
        previous_tag: Previous tag name (None for first release)
        current_tag: Current tag name
        paths: List of paths to filter by (e.g., ["src/", "Cargo.toml", "Cargo.lock"])

    Returns:
        Set of commit SHAs that modify the specified paths
    """
    try:
        if previous_tag:
            range_spec = f"{previous_tag}..{current_tag}"
        else:
            range_spec = current_tag

        result = subprocess.run(
            [
                "git",
                "rev-list",
                range_spec,
                "--",
                *paths,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
    except subprocess.CalledProcessError:
        # If tag doesn't exist or no commits, return empty set
        return set()


def split_commits_by_path(
    commits: list,
    previous_tag: Optional[str],
    current_tag: str,
    application_paths: list[str] = ["src/", "Cargo.toml", "Cargo.lock"],
) -> tuple[list, list]:
    """
    Split commits into application and other based on modified paths.

    Args:
        commits: List of commit objects
        previous_tag: Previous tag name (None for first release)
        current_tag: Current tag name
        application_paths: Paths that define "application" commits

    Returns:
        Tuple of (application_commits, other_commits)
    """
    # Get SHAs of commits that modify application paths
    application_shas = get_commit_shas_by_path(previous_tag, current_tag, application_paths)

    application_commits = []
    other_commits = []

    for commit in commits:
        commit_sha = commit.sha if hasattr(commit, "sha") else str(commit)
        if commit_sha in application_shas:
            application_commits.append(commit)
        else:
            other_commits.append(commit)

    return application_commits, other_commits
