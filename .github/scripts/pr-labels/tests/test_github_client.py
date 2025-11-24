"""Tests for GitHub client module."""
from unittest.mock import MagicMock, patch

import pytest
from github import GithubException

from pr_labels.github_client import GitHubClient


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


def test_get_pull_success(mock_repo):
    """Test getting pull request successfully."""
    mock_pr = MagicMock()
    mock_pr.number = 1
    mock_repo.get_pull.return_value = mock_pr

    client = GitHubClient("token", "owner/repo")
    client._repo = mock_repo

    pr = client.get_pull(1)
    assert pr == mock_pr
    mock_repo.get_pull.assert_called_once_with(1)


def test_get_pull_error(mock_repo):
    """Test getting pull request with error."""
    mock_repo.get_pull.side_effect = GithubException(
        404, {"message": "Not Found"}, None
    )

    client = GitHubClient("token", "owner/repo")
    client._repo = mock_repo

    with pytest.raises(GithubException):
        client.get_pull(1)
