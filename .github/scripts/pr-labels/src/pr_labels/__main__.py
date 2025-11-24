"""Entry point for pr-labels package."""
import json
import os
import sys

from pr_labels.github_client import GitHubClient
from pr_labels.labeler import apply_labels


def main() -> None:
    """Main execution logic."""
    # Get GitHub token from environment (GITHUB_TOKEN is automatically available in GitHub Actions)
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Get repository name from environment
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    if not repo_name:
        print("Error: GITHUB_REPOSITORY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Get PR number from environment or GitHub event
    pr_number: int | None = None

    # Try PR_NUMBER environment variable first (for testing)
    pr_number_str = os.environ.get("PR_NUMBER")
    if pr_number_str:
        try:
            pr_number = int(pr_number_str)
        except ValueError:
            print(f"Error: PR_NUMBER must be an integer, got: {pr_number_str}", file=sys.stderr)
            sys.exit(1)

    # If not set, try to read from GitHub event
    if pr_number is None:
        event_path = os.environ.get("GITHUB_EVENT_PATH")
        if event_path:
            try:
                with open(event_path, "r", encoding="utf-8") as f:
                    event_data = json.load(f)
                    pr_number = event_data.get("pull_request", {}).get("number")
                    if pr_number is None:
                        print("Error: Could not find PR number in GitHub event", file=sys.stderr)
                        sys.exit(1)
            except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                print(f"Error reading GitHub event: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("Error: PR_NUMBER or GITHUB_EVENT_PATH must be set", file=sys.stderr)
            sys.exit(1)

    # Initialize GitHub client
    try:
        github_client = GitHubClient(token, repo_name)
        print(f"GitHub client initialized for repository: {repo_name}")
    except Exception as e:
        print(f"Error initializing GitHub client: {e}", file=sys.stderr)
        sys.exit(1)

    # Get PR and repository
    try:
        pr = github_client.get_pull(pr_number)
        repo = github_client.get_repo()
    except Exception as e:
        print(f"Error accessing PR or repository: {e}", file=sys.stderr)
        sys.exit(1)

    # Apply labels
    try:
        apply_labels(pr, repo)
    except Exception as e:
        print(f"Error applying labels: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
