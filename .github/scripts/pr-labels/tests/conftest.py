"""Pytest configuration and fixtures."""
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_github_client():
    """Create a mock GitHub client."""
    client = MagicMock()
    return client


@pytest.fixture
def mock_repo():
    """Create a mock repository object."""
    repo = MagicMock()
    repo.full_name = "owner/repo"
    return repo


@pytest.fixture
def mock_pr():
    """Create a mock pull request object."""
    pr = MagicMock()
    pr.number = 1
    return pr


@pytest.fixture
def mock_commit():
    """Create a mock commit object."""
    commit = MagicMock()
    commit_obj = MagicMock()
    commit_obj.message = "feat: add new feature"
    commit.commit = commit_obj
    return commit


@pytest.fixture
def mock_breaking_commit():
    """Create a mock commit with breaking change."""
    commit = MagicMock()
    commit_obj = MagicMock()
    commit_obj.message = "feat!: breaking change\n\nBREAKING CHANGE: This is a breaking change"
    commit.commit = commit_obj
    return commit


@pytest.fixture
def mock_feature_commit():
    """Create a mock commit with feature prefix."""
    commit = MagicMock()
    commit_obj = MagicMock()
    commit_obj.message = "feat: add new feature"
    commit.commit = commit_obj
    return commit


@pytest.fixture
def mock_patch_commit():
    """Create a mock commit with patch prefix."""
    commit = MagicMock()
    commit_obj = MagicMock()
    commit_obj.message = "fix: fix a bug"
    commit.commit = commit_obj
    return commit


@pytest.fixture
def mock_empty_commit():
    """Create a mock commit with empty message."""
    commit = MagicMock()
    commit_obj = MagicMock()
    commit_obj.message = ""
    commit.commit = commit_obj
    return commit


@pytest.fixture
def mock_label():
    """Create a mock label object."""
    label = MagicMock()
    label.name = "version: major"
    return label
