"""Entry point for release-version package."""
import os
import sys

from release_version.cargo import update_cargo_version
from release_version.github_client import GitHubClient
from release_version.version import calculate_new_version


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

    # Initialize GitHub client
    try:
        github_client = GitHubClient(token, repo_name)
    except Exception as e:
        print(f"Error initializing GitHub client: {e}", file=sys.stderr)
        sys.exit(1)

    # Get Cargo.toml path from environment or default
    cargo_toml_path = os.environ.get("CARGO_TOML_PATH", "Cargo.toml")
    repo_root = os.path.dirname(cargo_toml_path) or "."

    # Calculate new version (pass repo_root for reading current version)
    try:
        version, tag_name = calculate_new_version(github_client, repo_path=repo_root)
    except Exception as e:
        print(f"Error calculating version: {e}", file=sys.stderr)
        sys.exit(1)

    # Update Cargo.toml (use full path)
    try:
        version_updated = update_cargo_version(cargo_toml_path, version)
    except Exception as e:
        print(f"Error updating Cargo.toml: {e}", file=sys.stderr)
        sys.exit(1)

    # Only output to GITHUB_OUTPUT/console if version was updated
    if not version_updated:
        print("Version unchanged, skipping output")
        sys.exit(0)

    # Output to GITHUB_OUTPUT
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        try:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(f"version={version}\n")
                f.write(f"tag_name={tag_name}\n")
        except Exception as e:
            print(f"Error writing to GITHUB_OUTPUT: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Fallback to stdout
        print(f"version={version}")
        print(f"tag_name={tag_name}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
