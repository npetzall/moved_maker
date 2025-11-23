"""Entry point for pr-labels package."""
import argparse
import os
import re
import sys
from typing import List, Optional, Set, Tuple

from github import Auth, Github, GithubException


def parse_commit_message(message: str) -> Tuple[str, bool]:
    """
    Parse commit message to determine type and breaking status.
    
    Args:
        message: Full commit message
        
    Returns:
        Tuple of (commit_type, is_breaking)
    """
    # Split message into subject and body
    lines = message.split("\n", 1)
    subject = lines[0] if lines else ""
    body = lines[1] if len(lines) > 1 else ""
    
    # Parse subject: type(scope)!: subject or type: subject
    # The ! indicator before : indicates breaking change
    pattern = r"^(\w+)(?:\([^)]+\))?(!)?:\s*.+"
    match = re.match(pattern, subject)
    
    commit_type = "other"
    is_breaking = False
    
    if match:
        commit_type = match.group(1).lower()
        breaking_indicator = match.group(2)
        is_breaking = breaking_indicator == "!"
    
    # Check for BREAKING CHANGE in body/footer
    if not is_breaking and body:
        is_breaking = "BREAKING CHANGE:" in body or "BREAKING-CHANGE:" in body
    
    return commit_type, is_breaking


def determine_version_bump(commits: List) -> Tuple[str, str]:
    """
    Determine version bump and alternative label from commits.
    
    Args:
        commits: List of commit objects from PyGithub
        
    Returns:
        Tuple of (version_label, alt_label) where alt_label may be empty.
        Defaults to 'version: patch' if no feat or breaking changes found.
    """
    has_breaking = False
    has_feature = False
    
    for commit in commits:
        message = commit.commit.message
        commit_type, is_breaking = parse_commit_message(message)
        
        if is_breaking:
            has_breaking = True
            break  # Breaking change takes precedence
            
        if commit_type in ["feat", "feature"]:
            has_feature = True
    
    if has_breaking:
        return "version: major", "breaking"
    elif has_feature:
        return "version: minor", "feature"
    else:
        # Default to patch for any other commits (fix, docs, chore, etc.)
        return "version: patch", ""


def check_pr_title_body(pr) -> Tuple[str, str]:
    """
    Check PR title and body for version hints as supplemental signals.
    
    Args:
        pr: PullRequest object from PyGithub
        
    Returns:
        Tuple of (version_label, alt_label) or empty strings if no signals
    """
    title = pr.title or ""
    body = pr.body or ""
    
    # Check title for conventional commit format
    commit_type, is_breaking = parse_commit_message(title)
    
    # Check body for BREAKING CHANGE
    if not is_breaking and body:
        is_breaking = "BREAKING CHANGE:" in body or "BREAKING-CHANGE:" in body
    
    if is_breaking:
        return "version: major", "breaking"
    elif commit_type in ["feat", "feature"]:
        return "version: minor", "feature"
    
    return "", ""


def ensure_labels_exist(repo, dry_run: bool = False) -> None:
    """
    Ensure required labels exist in the repository.
    
    Args:
        repo: Repository object from PyGithub
        dry_run: If True, only log actions without making changes
    """
    required_labels = {
        "version: major": {
            "color": "d73a4a",
            "description": "Breaking changes - major version bump"
        },
        "version: minor": {
            "color": "0e8a16",
            "description": "New features - minor version bump"
        },
        "version: patch": {
            "color": "0366d6",
            "description": "Bug fixes and patches - patch version bump"
        },
        "breaking": {
            "color": "d73a4a",
            "description": "Breaking changes"
        },
        "feature": {
            "color": "0e8a16",
            "description": "New feature"
        },
    }
    
    try:
        existing_labels = {label.name: label for label in repo.get_labels()}
    except GithubException as e:
        print(f"Error fetching labels: {e}", file=sys.stderr)
        raise
    
    for label_name, label_info in required_labels.items():
        if label_name not in existing_labels:
            if dry_run:
                print(f"[DRY RUN] Would create label: {label_name}")
            else:
                try:
                    repo.create_label(
                        name=label_name,
                        color=label_info["color"],
                        description=label_info["description"]
                    )
                    print(f"✓ Created label: {label_name}")
                except GithubException as e:
                    print(f"Error creating label {label_name}: {e}", file=sys.stderr)
                    raise


def get_all_pr_commits(pr) -> List:
    """
    Fetch all commits in a PR with pagination.
    
    Args:
        pr: PullRequest object from PyGithub
        
    Returns:
        List of all commits in the PR
    """
    print(f"Fetching commits for PR #{pr.number}...")
    
    try:
        # PyGithub handles pagination automatically through PaginatedList
        commits = list(pr.get_commits())
        print(f"✓ Fetched {len(commits)} commit(s)")
    except GithubException as e:
        print(f"Error fetching commits: {e}", file=sys.stderr)
        raise
    
    return commits


def apply_labels(pr, version_label: str, alt_label: str, dry_run: bool = False) -> None:
    """
    Apply version and alternative labels to PR, removing old ones.
    
    Args:
        pr: PullRequest object from PyGithub
        version_label: Primary version label (e.g., "version: major")
        alt_label: Alternative label (e.g., "breaking", "feature", or empty)
        dry_run: If True, only log actions without making changes
    """
    # Labels to remove (all version and alt labels)
    labels_to_remove = {
        "version: major", "version: minor", "version: patch",
        "breaking", "feature"
    }
    
    # Get current labels
    try:
        current_labels = {label.name for label in pr.labels}
    except GithubException as e:
        print(f"Error fetching PR labels: {e}", file=sys.stderr)
        raise
    
    # Remove old version/alt labels
    for label_name in labels_to_remove:
        if label_name in current_labels:
            if dry_run:
                print(f"[DRY RUN] Would remove label: {label_name}")
            else:
                try:
                    pr.remove_from_labels(label_name)
                    print(f"✓ Removed label: {label_name}")
                except GithubException as e:
                    # Ignore if label doesn't exist
                    if e.status != 404:
                        print(f"Error removing label {label_name}: {e}", file=sys.stderr)
    
    # Add new labels
    labels_to_add = [version_label]
    if alt_label:
        labels_to_add.append(alt_label)
    
    for label_name in labels_to_add:
        if dry_run:
            print(f"[DRY RUN] Would add label: {label_name}")
        else:
            try:
                pr.add_to_labels(label_name)
                print(f"✓ Added label: {label_name}")
            except GithubException as e:
                print(f"Error adding label {label_name}: {e}", file=sys.stderr)
                raise


def main() -> int:
    """Main entry point for pr-labels application."""
    parser = argparse.ArgumentParser(
        description="Label PRs based on Conventional Commits"
    )
    parser.add_argument(
        "pr_number",
        type=int,
        nargs="?",
        help="Pull request number (or use PR_NUMBER env var)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions without making changes"
    )
    
    args = parser.parse_args()
    
    # Get PR number from argument or environment
    pr_number = args.pr_number or os.environ.get("PR_NUMBER")
    if not pr_number:
        print("Error: PR number required (as argument or PR_NUMBER env var)", file=sys.stderr)
        return 1
    
    try:
        pr_number = int(pr_number)
    except ValueError:
        print(f"Error: Invalid PR number: {pr_number}", file=sys.stderr)
        return 1
    
    # Get GitHub token and repository from environment
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable is required", file=sys.stderr)
        return 1
    
    github_repository = os.environ.get("GITHUB_REPOSITORY")
    if not github_repository:
        print("Error: GITHUB_REPOSITORY environment variable is required", file=sys.stderr)
        return 1
    
    if args.dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No changes will be made to the repository")
        print("=" * 60)
    
    print(f"Processing PR #{pr_number} in {github_repository}...")
    
    try:
        # Initialize GitHub client
        github = Github(auth=Auth.Token(github_token))
        repo = github.get_repo(github_repository)
        
        # Ensure labels exist
        print("\nEnsuring labels exist...")
        ensure_labels_exist(repo, dry_run=args.dry_run)
        
        # Get pull request
        print(f"\nFetching PR #{pr_number}...")
        pr = repo.get_pull(pr_number)
        print(f"✓ Found PR: {pr.title}")
        
        # Get all commits in PR
        print("\nAnalyzing commits...")
        commits = get_all_pr_commits(pr)
        
        if not commits:
            print("Warning: No commits found in PR", file=sys.stderr)
            return 1
        
        # Determine version bump from commits
        version_label, alt_label = determine_version_bump(commits)
        label_str = f"{version_label}, {alt_label}" if alt_label else version_label
        print(f"\nDetermined from commits: {label_str}")
        
        # Check PR title/body as supplemental signal
        pr_version, pr_alt = check_pr_title_body(pr)
        if pr_version and pr_version != version_label:
            pr_label_str = f"{pr_version}, {pr_alt}" if pr_alt else pr_version
            print(f"PR title/body suggests: {pr_label_str}")
            # PR title/body takes precedence if it suggests a higher bump
            if pr_version == "version: major":
                version_label, alt_label = pr_version, pr_alt
                print("Using PR title/body signal (major bump)")
            elif pr_version == "version: minor" and version_label == "version: patch":
                version_label, alt_label = pr_version, pr_alt
                print("Using PR title/body signal (minor bump)")
        
        # Apply labels
        print(f"\nApplying labels...")
        apply_labels(pr, version_label, alt_label, dry_run=args.dry_run)
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully labeled PR #{pr_number}")
        print(f"   Version label: {version_label}")
        if alt_label:
            print(f"   Alternative label: {alt_label}")
        print("=" * 60)
        
        return 0
        
    except GithubException as e:
        print(f"\nError accessing GitHub API: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
