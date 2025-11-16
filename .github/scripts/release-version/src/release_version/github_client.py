"""GitHub API client wrapper."""
import sys
from typing import List, Optional

from github import Auth, Github, GithubException
from github.PullRequest import PullRequest
from github.Repository import Repository


class GitHubClient:
    """Wrapper for GitHub API client."""

    def __init__(self, token: str, repo_name: str):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token
            repo_name: Repository name in format "owner/repo"
        """
        self.github = Github(auth=Auth.Token(token))
        self.repo_name = repo_name
        self._repo: Optional[Repository] = None

    def get_repo(self) -> Repository:
        """Get repository object.

        Returns:
            Repository object

        Raises:
            GithubException: If repository cannot be accessed
        """
        if self._repo is None:
            try:
                self._repo = self.github.get_repo(self.repo_name)
            except GithubException as e:
                print(f"Error accessing repository {self.repo_name}: {e}", file=sys.stderr)
                raise
        return self._repo

    def get_merged_prs_since(self, since_timestamp: int) -> List[PullRequest]:
        """Get all merged PRs since the given timestamp.

        Args:
            since_timestamp: Unix timestamp to filter PRs

        Returns:
            List of merged PullRequest objects

        Raises:
            GithubException: If API call fails
        """
        try:
            repo = self.get_repo()
            prs = []

            # Get all closed PRs sorted by update time (newest first)
            # PyGithub handles pagination automatically
            for pr in repo.get_pulls(
                state="closed", base="main", sort="updated", direction="desc"
            ):
                # Stop if we've gone past the tag date (PRs are sorted by updated_at)
                if pr.updated_at and pr.updated_at.timestamp() < since_timestamp:
                    break

                # Only include merged PRs after the tag date
                if pr.merged_at and pr.merged_at.timestamp() > since_timestamp:
                    prs.append(pr)

            return prs
        except GithubException as e:
            print(f"Error getting merged PRs: {e}", file=sys.stderr)
            raise
