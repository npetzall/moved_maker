"""Entry point for release-notes application."""

import os
import sys
from pathlib import Path

from github import Auth, Github, GithubException

from release_notes import formatter, git, parser


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

        # Write to release_notes.md file
        output_file = Path("release_notes.md")
        with output_file.open("w") as f:
            f.write(release_notes)

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
