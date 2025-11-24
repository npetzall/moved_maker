"""Entry point for release-notes application."""

import os
import sys
from pathlib import Path

from github import Auth, Github, GithubException

from release_notes import formatter, git, parser


def find_workspace_root(start_path: Path) -> Path | None:
    """
    Recursively traverse up the directory tree to find the workspace root.

    Looks for Cargo.toml as a marker file indicating the workspace root.
    Stops at filesystem root if not found.

    Args:
        start_path: Starting directory path to begin search from

    Returns:
        Path to workspace root directory if found, None otherwise
    """
    start_path = start_path.resolve()

    # Check if Cargo.toml exists in current directory
    cargo_toml = start_path / "Cargo.toml"
    if cargo_toml.exists():
        return start_path

    # Base case: reached filesystem root
    parent = start_path.parent
    if parent == start_path:  # At root directory (e.g., / on Unix, C:\ on Windows)
        return None

    # Recursive case: traverse up one level
    return find_workspace_root(parent)


def get_workspace_root() -> Path:
    """
    Get the workspace root directory.

    Priority:
    1. GITHUB_WORKSPACE environment variable (automatically set by GitHub Actions)
    2. Recursively find workspace root by traversing up from script location looking for Cargo.toml

    Returns:
        Path to workspace root directory

    Raises:
        RuntimeError: If workspace root cannot be determined
    """
    # First, try GITHUB_WORKSPACE (automatically set by GitHub Actions)
    workspace_env = os.environ.get("GITHUB_WORKSPACE")
    if workspace_env:
        workspace_path = Path(workspace_env)
        if workspace_path.exists() and workspace_path.is_dir():
            return workspace_path.resolve()
        print(
            f"Warning: GITHUB_WORKSPACE points to non-existent directory: {workspace_env}",
            file=sys.stderr
        )

    # Fallback: Recursively find workspace root from script location
    script_file = Path(__file__).resolve()
    workspace_root = find_workspace_root(script_file.parent)

    if workspace_root is None:
        raise RuntimeError(
            f"Could not determine workspace root. "
            f"Traversed up from {script_file} but could not find Cargo.toml. "
            f"Set GITHUB_WORKSPACE environment variable or ensure Cargo.toml exists in workspace root."
        )

    return workspace_root


def main() -> int:
    """Main entry point for release-notes application."""
    # Parse environment variables
    github_token = os.environ.get("GITHUB_TOKEN")
    github_repository = os.environ.get("GITHUB_REPOSITORY")
    github_ref_name = os.environ.get("GITHUB_REF_NAME")

    if not github_token:
        print("Error: GITHUB_TOKEN environment variable is required", file=sys.stderr)
        return 1

    if not github_repository:
        print("Error: GITHUB_REPOSITORY environment variable is required", file=sys.stderr)
        return 1

    if not github_ref_name:
        print("Error: GITHUB_REF_NAME environment variable is required", file=sys.stderr)
        return 1

    try:
        # Initialize GitHub client
        github = Github(auth=Auth.Token(github_token))
        repo = github.get_repo(github_repository)
    except GithubException as e:
        print(f"Error accessing repository {github_repository}: {e}", file=sys.stderr)
        return 1

    # Get current tag
    current_tag_name = github_ref_name

    try:
        # Get sorted tags
        tags = git.get_tags_sorted(repo)

        # Find current tag object
        current_tag = None
        for tag in tags:
            if tag.name == current_tag_name:
                current_tag = tag
                break

        if current_tag is None:
            print(f"Error: Tag {current_tag_name} not found in repository", file=sys.stderr)
            return 1

        # Get previous tag
        previous_tag = git.get_previous_tag(repo, current_tag_name)

        # Get commits
        if previous_tag:
            commits = git.get_commits_between_tags(repo, previous_tag, current_tag)
            previous_tag_name = previous_tag.name
        else:
            # First release: get all commits
            commits = git.get_all_commits(repo)
            previous_tag_name = None

        # Split commits into application and other
        application_commits, other_commits = git.split_commits_by_path(
            commits,
            previous_tag_name,
            current_tag_name,
            application_paths=["src/", "Cargo.toml", "Cargo.lock"],
        )

        # Generate repository URL
        repo_url = f"https://github.com/{github_repository}"

        # Generate Markdown release notes
        release_notes = formatter.generate_markdown(
            commits,  # All commits for statistics
            previous_tag_name,
            current_tag_name,
            repo_url,
            installation_section=True,
            application_commits=application_commits,
            other_commits=other_commits,
        )

        # Write to GITHUB_OUTPUT
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            output_file = Path(github_output)
            with output_file.open("a") as f:
                f.write("notes<<EOF\n")
                f.write(release_notes)
                f.write("\nEOF\n")

        # Write to release_notes.md file at workspace root
        try:
            workspace_root = get_workspace_root()
            output_file = workspace_root / "release_notes.md"
            with output_file.open("w") as f:
                f.write(release_notes)
            print(f"   Release notes written to: {output_file}")
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        print(f"✅ Release notes generated successfully for {current_tag_name}")
        print(f"   Total commits: {len(commits)}")
        print(f"   Application commits: {len(application_commits)}")
        print(f"   Other commits: {len(other_commits)}")
        if previous_tag_name:
            print(f"   Changes since: {previous_tag_name}")

        return 0

    except Exception as e:
        print(f"Error generating release notes: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
