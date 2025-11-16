"""Tests for GitHub client module."""
from unittest.mock import MagicMock, patch

import pytest
from github import GithubException

from release_version.github_client import GitHubClient


def test_github_client_init():
    """Test GitHub client initialization."""
    client = GitHubClient("token", "owner/repo")
    assert client.repo_name == "owner/repo"
    assert client._repo is None


def test_get_repo_success():
    """Test getting repository successfully."""
    mock_repo = MagicMock()
    mock_repo.full_name = "owner/repo"

    with patch("github.Github") as mock_github:
        mock_github_instance = MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        client = GitHubClient("token", "owner/repo")
        client.github = mock_github_instance

        repo = client.get_repo()
        assert repo == mock_repo
        assert client._repo == mock_repo


def test_get_repo_error():
    """Test getting repository with error."""
    with patch("github.Github") as mock_github:
        mock_github_instance = MagicMock()
        mock_github_instance.get_repo.side_effect = GithubException(
            404, {"message": "Not Found"}, None
        )
        mock_github.return_value = mock_github_instance

        client = GitHubClient("token", "owner/repo")
        client.github = mock_github_instance

        with pytest.raises(GithubException):
            client.get_repo()


def test_get_merged_prs_since():
    """Test getting merged PRs since timestamp."""
    # Create mock PRs
    pr1 = MagicMock()
    pr1.merged_at = MagicMock()
    pr1.merged_at.timestamp.return_value = 2000
    pr1.updated_at = MagicMock()
    pr1.updated_at.timestamp.return_value = 2000

    pr2 = MagicMock()
    pr2.merged_at = MagicMock()
    pr2.merged_at.timestamp.return_value = 1500  # Before since_timestamp
    pr2.updated_at = MagicMock()
    pr2.updated_at.timestamp.return_value = 1500

    pr3 = MagicMock()
    pr3.merged_at = None  # Not merged
    pr3.updated_at = MagicMock()
    pr3.updated_at.timestamp.return_value = 1800

    mock_repo = MagicMock()
    mock_repo.get_pulls.return_value = [pr1, pr2, pr3]

    client = GitHubClient("token", "owner/repo")
    client._repo = mock_repo

    prs = client.get_merged_prs_since(1600)

    # Should only return pr1 (merged after timestamp)
    assert len(prs) == 1
    assert prs[0] == pr1


def test_get_merged_prs_since_api_error():
    """Test getting merged PRs with API error."""
    mock_repo = MagicMock()
    mock_repo.get_pulls.side_effect = GithubException(
        500, {"message": "Internal Server Error"}, None
    )

    client = GitHubClient("token", "owner/repo")
    client._repo = mock_repo

    with pytest.raises(GithubException):
        client.get_merged_prs_since(1000)
