"""GitHub API client wrapper."""
import sys
from typing import Optional

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

    def get_pull(self, pr_number: int) -> PullRequest:
        """Get pull request object.

        Args:
            pr_number: Pull request number

        Returns:
            PullRequest object

        Raises:
            GithubException: If pull request cannot be accessed
        """
        try:
            repo = self.get_repo()
            return repo.get_pull(pr_number)
        except GithubException as e:
            print(f"Error accessing pull request #{pr_number}: {e}", file=sys.stderr)
            raise
