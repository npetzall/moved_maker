"""Commit message parser for Conventional Commits."""
from typing import Optional, Tuple

from github.Commit import Commit


def parse_commits(commits: list[Commit]) -> Tuple[Optional[str], Optional[str]]:
    """Parse commits to determine version bump type and semantic label.

    Analyzes commit messages for Conventional Commit patterns:
    - BREAKING CHANGE: or !: indicates major version bump
    - feat: prefix indicates minor version bump
    - Other commits default to patch version bump

    Args:
        commits: List of Commit objects from a PR

    Returns:
        Tuple of (version_label, alt_label) where:
        - version_label: "version: major", "version: minor", or None (patch)
        - alt_label: "breaking", "feature", or None
    """
    version_label: Optional[str] = None
    alt_label: Optional[str] = None

    for commit in commits:
        message = commit.commit.message if commit.commit else ""
        if not message:
            continue

        # Check for breaking change (highest priority)
        if "BREAKING CHANGE:" in message or "!:" in message:
            version_label = "version: major"
            alt_label = "breaking"
            # Breaking change is highest priority, so we can stop here
            break

        # Check for feature (only if we haven't found breaking change)
        if version_label is None and message.startswith("feat:"):
            version_label = "version: minor"
            alt_label = "feature"
            # Continue checking in case there's a breaking change later

    return (version_label, alt_label)
