"""Version calculation logic."""
import subprocess
import sys
from typing import Optional, Tuple

from packaging import version as packaging_version
from packaging.version import InvalidVersion

from release_version.cargo import read_cargo_version


def get_latest_tag() -> Optional[str]:
    """Get the latest tag matching v* pattern.

    Returns:
        Tag name (e.g., "v1.0.0") or None if no tags exist
    """
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--match", "v*", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"Error getting latest tag: {e}", file=sys.stderr)
        return None


def get_tag_timestamp(tag: str) -> int:
    """Get Unix timestamp for a git tag.

    Args:
        tag: Git tag name

    Returns:
        Unix timestamp (seconds since epoch)

    Raises:
        ValueError: If tag doesn't exist or cannot be read
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", tag],
            capture_output=True,
            text=True,
            check=True,
        )
        return int(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error getting tag timestamp for {tag}: {e}", file=sys.stderr)
        raise ValueError(f"Tag {tag} not found or cannot be read") from e
    except ValueError as e:
        print(f"Error parsing tag timestamp: {e}", file=sys.stderr)
        raise


def get_commit_count(since_tag: str) -> int:
    """Get commit count since a tag.

    Args:
        since_tag: Git tag to count commits from

    Returns:
        Number of commits since the tag

    Raises:
        ValueError: If tag doesn't exist
    """
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", f"{since_tag}..HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return int(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit count: {e}", file=sys.stderr)
        raise ValueError(f"Tag {since_tag} not found") from e
    except ValueError as e:
        print(f"Error parsing commit count: {e}", file=sys.stderr)
        raise


def determine_bump_type(prs) -> str:
    """Determine version bump type from PR labels.

    Args:
        prs: List of PullRequest objects

    Returns:
        Bump type: "MAJOR", "MINOR", or "PATCH"
    """
    major_bump = False
    minor_bump = False

    for pr in prs:
        labels = [label.name for label in pr.labels]
        if any(label in labels for label in ["version: major", "breaking"]):
            major_bump = True
            print(f"PR #{pr.number} has major version label")
        elif any(label in labels for label in ["version: minor", "feature"]):
            minor_bump = True
            print(f"PR #{pr.number} has minor version label")

    if major_bump:
        return "MAJOR"
    elif minor_bump:
        return "MINOR"
    else:
        return "PATCH"


def calculate_version(
    base_version: str, bump_type: str, commit_count: int
) -> str:
    """Calculate new version based on bump type.

    Args:
        base_version: Base version string (e.g., "1.0.0")
        bump_type: Bump type: "MAJOR", "MINOR", or "PATCH"
        commit_count: Number of commits for patch bump

    Returns:
        New version string

    Raises:
        InvalidVersion: If base_version is not a valid version
    """
    try:
        parsed_version = packaging_version.parse(base_version)
        major, minor, patch = parsed_version.release[:3]

        if bump_type == "MAJOR":
            return f"{major + 1}.0.0"
        elif bump_type == "MINOR":
            return f"{major}.{minor + 1}.0"
        else:  # PATCH
            return f"{major}.{minor}.{patch + commit_count}"
    except (InvalidVersion, ValueError, IndexError) as e:
        print(f"Error calculating version: {e}", file=sys.stderr)
        raise InvalidVersion(f"Invalid base version: {base_version}") from e


def calculate_new_version(
    github_client, repo_path: str = "."
) -> Tuple[str, str]:
    """Calculate new version from PR labels and git tags.

    Args:
        github_client: GitHubClient instance
        repo_path: Path to repository root (for reading Cargo.toml)

    Returns:
        Tuple of (version, tag_name) where tag_name includes 'v' prefix

    Raises:
        ValueError: If version calculation fails
    """
    latest_tag = get_latest_tag()

    if not latest_tag:
        # First release - use version from Cargo.toml
        cargo_path = f"{repo_path}/Cargo.toml" if repo_path != "." else "Cargo.toml"
        version = read_cargo_version(cargo_path)
        print(
            f"No previous tag found (first release), using base version from Cargo.toml: {version}"
        )
        return (version, f"v{version}")

    # Extract version from tag (remove 'v' prefix)
    base_version = latest_tag.lstrip("v")

    # Get tag timestamp
    tag_timestamp = get_tag_timestamp(latest_tag)

    # Get merged PRs since tag
    prs = github_client.get_merged_prs_since(tag_timestamp)

    # Determine bump type
    bump_type = determine_bump_type(prs)

    # Get commit count for patch bump
    if bump_type == "PATCH":
        commit_count = get_commit_count(latest_tag)
    else:
        commit_count = 0

    # Calculate version
    new_version = calculate_version(base_version, bump_type, commit_count)

    print(f"Latest tag: {latest_tag}")
    print(f"Bump type: {bump_type}")
    print(f"Calculated version: {new_version}")

    return (new_version, f"v{new_version}")
