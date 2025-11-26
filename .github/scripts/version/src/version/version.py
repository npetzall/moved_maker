"""Version calculation logic."""
import subprocess
import sys
from typing import Optional, Tuple

from packaging import version as packaging_version
from packaging.version import InvalidVersion, Version

from version.cargo import read_cargo_version


def shorten_commit_sha(sha: str, length: int = 7) -> str:
    """Shorten commit SHA to specified length.

    Args:
        sha: Full commit SHA string
        length: Desired length of shortened SHA (default: 7)

    Returns:
        Shortened SHA string

    Raises:
        ValueError: If SHA format is invalid or length is invalid
    """
    if not sha:
        raise ValueError("Commit SHA cannot be empty")
    if length < 1:
        raise ValueError(f"Length must be at least 1, got {length}")
    if not sha.isalnum():
        raise ValueError(f"Invalid SHA format: {sha} (must be alphanumeric)")

    # Ensure we don't exceed the SHA length (40 characters for full SHA)
    actual_length = min(length, len(sha))
    return sha[:actual_length]


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


def get_commit_count(since_tag: Optional[str] = None) -> int:
    """Get commit count since a tag for application-related files only.

    Only counts commits that modify files in src/, Cargo.toml, or Cargo.lock.
    Commits that only modify other files (documentation, workflows, scripts, etc.)
    are excluded from the count.

    Args:
        since_tag: Git tag to count commits from. If None, counts all commits.

    Returns:
        Number of commits since the tag (or all commits if since_tag is None)
        that modify application code or dependencies

    Raises:
        ValueError: If tag doesn't exist (only when since_tag is provided)
    """
    try:
        if since_tag:
            print(f"Counting commits since tag {since_tag} that modify application code...")
            rev_range = f"{since_tag}..HEAD"
        else:
            print("Counting all commits that modify application code...")
            rev_range = "HEAD"

        result = subprocess.run(
            [
                "git",
                "rev-list",
                "--count",
                rev_range,
                "--",
                "src/",
                "Cargo.toml",
                "Cargo.lock",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        count = int(result.stdout.strip())
        print(f"Found {count} commit(s) modifying application code")
        return count
    except subprocess.CalledProcessError as e:
        if since_tag:
            print(f"Error getting commit count: {e}", file=sys.stderr)
            raise ValueError(f"Tag {since_tag} not found") from e
        else:
            print(f"Error getting commit count: {e}", file=sys.stderr)
            raise ValueError("Failed to count commits") from e
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
    print(f"Analyzing {len(prs)} PR(s) for version labels...")
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
        print("Determined bump type: MAJOR (breaking changes detected)")
        return "MAJOR"
    elif minor_bump:
        print("Determined bump type: MINOR (features detected)")
        return "MINOR"
    else:
        print("Determined bump type: PATCH (no major/minor labels found)")
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
        New version string (validated as semantic version)

    Raises:
        InvalidVersion: If base_version is not a valid version, or if calculated version is invalid (should not happen)
    """
    try:
        parsed_version = packaging_version.parse(base_version)
        major, minor, patch = parsed_version.release[:3]

        if bump_type == "MAJOR":
            new_version = f"{major + 1}.0.0"
        elif bump_type == "MINOR":
            new_version = f"{major}.{minor + 1}.0"
        else:  # PATCH
            new_version = f"{major}.{minor}.{patch + commit_count}"

        # Validate calculated version (defensive programming)
        try:
            Version(new_version)
        except InvalidVersion as e:
            raise InvalidVersion(
                f"Calculated invalid version: {new_version}. "
                "This should not happen - please report this bug."
            ) from e

        return new_version
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
        ValueError: If version calculation fails, or if tag version format is invalid
    """
    latest_tag = get_latest_tag()
    cargo_path = f"{repo_path}/Cargo.toml" if repo_path != "." else "Cargo.toml"

    # Determine base version and timestamp based on whether tag exists
    if not latest_tag:
        print("No tags found - this will be the first release")
        # First release - get base version from Cargo.toml
        print("Determining base version from Cargo.toml...")
        base_version = read_cargo_version(cargo_path)
        print(f"Base version from Cargo.toml: {base_version}")
        # Use timestamp 0 to get all PRs, and None for commit count (count all commits)
        tag_timestamp = 0
        tag_for_commit_count = None
    else:
        print(f"Found latest tag: {latest_tag}")
        # Extract version from tag (remove 'v' prefix)
        print(f"Extracting base version from tag: {latest_tag}")
        base_version = latest_tag.lstrip("v")
        print(f"Base version: {base_version}")

        # Validate tag version format immediately
        try:
            Version(base_version)  # Raises InvalidVersion if invalid
        except InvalidVersion as e:
            raise ValueError(
                f"Invalid version format in git tag '{latest_tag}': {base_version}. "
                "Expected semantic version (e.g., 1.0.0)"
            ) from e

        # Get tag timestamp
        tag_timestamp = get_tag_timestamp(latest_tag)
        tag_for_commit_count = latest_tag

    # Shared logic for both scenarios
    # Get merged PRs since tag (or all PRs if timestamp is 0)
    prs = github_client.get_merged_prs_since(tag_timestamp)

    # Determine bump type
    bump_type = determine_bump_type(prs)

    # Get commit count for patch bump
    if bump_type == "PATCH":
        commit_count = get_commit_count(tag_for_commit_count)
    else:
        commit_count = 0

    # Calculate version
    new_version = calculate_version(base_version, bump_type, commit_count)

    # Log comprehensive summary
    print("=" * 50)
    print("Version Calculation Summary:")
    print(f"  Base version: {base_version}")
    print(f"  Bump type: {bump_type}")
    if bump_type == "PATCH":
        print(f"  Commit count: {commit_count}")
    print(f"  Calculated version: {new_version}")
    print("=" * 50)

    return (new_version, f"v{new_version}")


def calculate_pr_version(
    github_client,
    pr_number: int,
    commit_sha: str,
    repo_path: str = ".",
) -> str:
    """Calculate PR version with pre-release identifier and build metadata.

    Uses the same logic as release version calculation (bump type from PR labels,
    commit count) but formats as semantic version with pre-release `pr[PR-NUMBER]`
    and build metadata `[SHORT-SHA]`.

    Args:
        github_client: GitHubClient instance
        pr_number: Pull request number
        commit_sha: Full commit SHA
        repo_path: Path to repository root (for reading Cargo.toml)

    Returns:
        PR version string in format: X.Y.Z-pr[NUMBER]+[SHORT-SHA] (e.g., "1.2.3-pr123+abc1234")

    Raises:
        ValueError: If version calculation fails, or if PR number or SHA is invalid
    """
    if pr_number < 1:
        raise ValueError(f"PR number must be positive, got {pr_number}")
    if not commit_sha:
        raise ValueError("Commit SHA cannot be empty")

    # Get base version using same logic as release
    latest_tag = get_latest_tag()
    cargo_path = f"{repo_path}/Cargo.toml" if repo_path != "." else "Cargo.toml"

    # Determine base version and timestamp based on whether tag exists
    if not latest_tag:
        print("No tags found - using Cargo.toml version as base")
        base_version = read_cargo_version(cargo_path)
        print(f"Base version from Cargo.toml: {base_version}")
        tag_timestamp = 0
        tag_for_commit_count = None
    else:
        print(f"Found latest tag: {latest_tag}")
        base_version = latest_tag.lstrip("v")
        print(f"Base version: {base_version}")

        # Validate tag version format
        try:
            Version(base_version)
        except InvalidVersion as e:
            raise ValueError(
                f"Invalid version format in git tag '{latest_tag}': {base_version}. "
                "Expected semantic version (e.g., 1.0.0)"
            ) from e

        tag_timestamp = get_tag_timestamp(latest_tag)
        tag_for_commit_count = latest_tag

    # Get merged PRs since tag (or all PRs if timestamp is 0)
    prs = github_client.get_merged_prs_since(tag_timestamp)

    # Determine bump type
    bump_type = determine_bump_type(prs)

    # Get commit count for patch bump
    if bump_type == "PATCH":
        commit_count = get_commit_count(tag_for_commit_count)
    else:
        commit_count = 0

    # Calculate base version (without pre-release/build metadata)
    base_new_version = calculate_version(base_version, bump_type, commit_count)

    # Shorten commit SHA for build metadata
    short_sha = shorten_commit_sha(commit_sha)

    # Format as semantic version with pre-release and build metadata
    pr_version = f"{base_new_version}-pr{pr_number}+{short_sha}"

    # Validate the full PR version format
    try:
        # Note: packaging.version.Version doesn't support build metadata in pre-release,
        # but we can validate the base version and format separately
        Version(base_new_version)
    except InvalidVersion as e:
        raise ValueError(f"Invalid calculated base version: {base_new_version}") from e

    # Log comprehensive summary
    print("=" * 50)
    print("PR Version Calculation Summary:")
    print(f"  Base version: {base_version}")
    print(f"  Bump type: {bump_type}")
    if bump_type == "PATCH":
        print(f"  Commit count: {commit_count}")
    print(f"  Calculated base version: {base_new_version}")
    print(f"  PR number: {pr_number}")
    print(f"  Commit SHA: {commit_sha} (shortened to {short_sha})")
    print(f"  PR version: {pr_version}")
    print("=" * 50)

    return pr_version
