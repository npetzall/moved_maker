"""Entry point for version package."""
import os
import subprocess
import sys

import tomlkit

from version.cargo import update_cargo_version
from version.github_client import GitHubClient
from version.version import calculate_new_version, calculate_pr_version


def main() -> None:
    """Main execution logic."""
    # Get version mode from environment (default to "release" for backward compatibility)
    version_mode = os.environ.get("VERSION_MODE", "release").lower()
    print(f"Version mode: {version_mode}")

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
        print(f"GitHub client initialized for repository: {repo_name}")
    except Exception as e:
        print(f"Error initializing GitHub client: {e}", file=sys.stderr)
        sys.exit(1)

    # Get Cargo.toml path from environment or default
    cargo_toml_path = os.environ.get("CARGO_TOML_PATH", "Cargo.toml")
    repo_root = os.path.dirname(cargo_toml_path) or "."

    # Calculate version based on mode
    if version_mode == "pr":
        # PR mode: Get PR number and commit SHA
        pr_number_str = os.environ.get("PR_NUMBER")
        if not pr_number_str:
            print("Error: PR_NUMBER environment variable not set (required for PR mode)", file=sys.stderr)
            sys.exit(1)

        try:
            pr_number = int(pr_number_str)
        except ValueError:
            print(f"Error: Invalid PR_NUMBER: {pr_number_str} (must be an integer)", file=sys.stderr)
            sys.exit(1)

        commit_sha = os.environ.get("COMMIT_SHA")
        if not commit_sha:
            print("Error: COMMIT_SHA environment variable not set (required for PR mode)", file=sys.stderr)
            sys.exit(1)

        # Calculate PR version
        try:
            print("Calculating PR version...")
            version = calculate_pr_version(
                github_client, pr_number, commit_sha, repo_path=repo_root
            )
            tag_name = f"v{version}"  # For consistency, though not used in PR mode
        except Exception as e:
            print(f"Error calculating PR version: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Release mode: Use existing logic
        if version_mode != "release":
            print(f"Warning: Unknown VERSION_MODE '{version_mode}', defaulting to 'release'", file=sys.stderr)

        try:
            print("Calculating new version...")
            version, tag_name = calculate_new_version(github_client, repo_path=repo_root)
        except Exception as e:
            print(f"Error calculating version: {e}", file=sys.stderr)
            sys.exit(1)

    # Update Cargo.toml (use full path)
    try:
        print(f"Updating Cargo.toml with version {version}...")
        version_updated = update_cargo_version(cargo_toml_path, version)
        if version_updated:
            print(f"✓ Cargo.toml updated to version {version}")

            # Update Cargo.lock with the new version
            # Read package name from Cargo.toml
            try:
                with open(cargo_toml_path, "r", encoding="utf-8") as f:
                    cargo = tomlkit.parse(f.read())
                package_name = cargo.get("package", {}).get("name", "moved_maker")
            except Exception as e:
                print(f"Warning: Could not read package name from Cargo.toml: {e}", file=sys.stderr)
                print("Using default package name: moved_maker", file=sys.stderr)
                package_name = "moved_maker"

            try:
                print(f"Updating Cargo.lock with version {version}...")
                result = subprocess.run(
                    ["cargo", "update", "--package", package_name],
                    cwd=repo_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                print(f"✓ Cargo.lock updated to version {version}")
            except subprocess.CalledProcessError as e:
                print(f"Error updating Cargo.lock: {e}", file=sys.stderr)
                print(f"stdout: {e.stdout}", file=sys.stderr)
                print(f"stderr: {e.stderr}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"ℹ Cargo.toml already at version {version}, no update needed")
    except Exception as e:
        print(f"Error updating Cargo.toml: {e}", file=sys.stderr)
        sys.exit(1)

    # Output behavior differs by mode
    if version_mode == "pr":
        # PR mode: Always output version (even if unchanged)
        print(f"PR version calculated: {version}")
    else:
        # Release mode: Only output if version was updated
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
