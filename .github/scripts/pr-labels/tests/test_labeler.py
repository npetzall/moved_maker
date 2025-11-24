"""Tests for labeler module."""
from unittest.mock import MagicMock

import pytest
from github import GithubException

from pr_labels.labeler import (
    add_label,
    apply_labels,
    ensure_label_exists,
    get_existing_labels,
    remove_label,
)


def test_ensure_label_exists_label_exists(mock_repo):
    """Test ensuring label exists when it already exists."""
    mock_label = MagicMock()
    mock_repo.get_label.return_value = mock_label

    ensure_label_exists(mock_repo, "version: major")
    mock_repo.get_label.assert_called_once_with("version: major")
    mock_repo.create_label.assert_not_called()


def test_ensure_label_exists_create_label(mock_repo):
    """Test creating label when it doesn't exist."""
    # First call raises 404, label is created
    mock_label = MagicMock()
    mock_repo.get_label.side_effect = GithubException(
        404, {"message": "Not Found"}, None
    )
    mock_repo.create_label.return_value = mock_label

    ensure_label_exists(mock_repo, "version: major")
    mock_repo.get_label.assert_called_once_with("version: major")
    mock_repo.create_label.assert_called_once_with(
        name="version: major",
        color="d73a4a",
        description="Major version bump",
    )


def test_ensure_label_exists_error(mock_repo):
    """Test error handling when label creation fails."""
    mock_repo.get_label.side_effect = GithubException(
        500, {"message": "Internal Server Error"}, None
    )

    with pytest.raises(GithubException):
        ensure_label_exists(mock_repo, "version: major")


def test_get_existing_labels(mock_pr):
    """Test getting existing labels from PR."""
    mock_label1 = MagicMock()
    mock_label1.name = "version: major"
    mock_label2 = MagicMock()
    mock_label2.name = "breaking"
    mock_pr.get_labels.return_value = [mock_label1, mock_label2]

    labels = get_existing_labels(mock_pr)
    assert len(labels) == 2
    assert labels[0].name == "version: major"
    assert labels[1].name == "breaking"


def test_get_existing_labels_error(mock_pr):
    """Test error handling when getting labels fails."""
    mock_pr.get_labels.side_effect = GithubException(
        500, {"message": "Internal Server Error"}, None
    )

    with pytest.raises(GithubException):
        get_existing_labels(mock_pr)


def test_remove_label_success(mock_pr):
    """Test removing label successfully."""
    remove_label(mock_pr, "version: major")
    mock_pr.remove_from_labels.assert_called_once_with("version: major")


def test_remove_label_not_found(mock_pr):
    """Test removing label that doesn't exist (404 should be ignored)."""
    mock_pr.remove_from_labels.side_effect = GithubException(
        404, {"message": "Not Found"}, None
    )

    # Should not raise
    remove_label(mock_pr, "version: major")


def test_remove_label_error(mock_pr):
    """Test error handling when removing label fails."""
    mock_pr.remove_from_labels.side_effect = GithubException(
        500, {"message": "Internal Server Error"}, None
    )

    with pytest.raises(GithubException):
        remove_label(mock_pr, "version: major")


def test_add_label_success(mock_pr):
    """Test adding label successfully."""
    add_label(mock_pr, "version: major")
    mock_pr.add_to_labels.assert_called_once_with("version: major")


def test_add_label_error(mock_pr):
    """Test error handling when adding label fails."""
    mock_pr.add_to_labels.side_effect = GithubException(
        500, {"message": "Internal Server Error"}, None
    )

    with pytest.raises(GithubException):
        add_label(mock_pr, "version: major")


def test_apply_labels_major_version(mock_pr, mock_repo, mock_breaking_commit):
    """Test applying labels for major version bump."""
    mock_pr.get_commits.return_value = [mock_breaking_commit]
    mock_pr.get_labels.return_value = []

    # Mock label existence check
    mock_label = MagicMock()
    mock_repo.get_label.return_value = mock_label

    apply_labels(mock_pr, mock_repo)

    # Verify labels were added
    assert mock_pr.add_to_labels.call_count == 2
    calls = [call[0][0] for call in mock_pr.add_to_labels.call_args_list]
    assert "version: major" in calls
    assert "breaking" in calls

    # Verify conflicting labels were removed
    assert mock_pr.remove_from_labels.call_count == 5


def test_apply_labels_minor_version(mock_pr, mock_repo, mock_feature_commit):
    """Test applying labels for minor version bump."""
    mock_pr.get_commits.return_value = [mock_feature_commit]
    mock_pr.get_labels.return_value = []

    # Mock label existence check
    mock_label = MagicMock()
    mock_repo.get_label.return_value = mock_label

    apply_labels(mock_pr, mock_repo)

    # Verify labels were added
    assert mock_pr.add_to_labels.call_count == 2
    calls = [call[0][0] for call in mock_pr.add_to_labels.call_args_list]
    assert "version: minor" in calls
    assert "feature" in calls


def test_apply_labels_patch_version(mock_pr, mock_repo, mock_patch_commit):
    """Test applying labels for patch version (no labels)."""
    mock_pr.get_commits.return_value = [mock_patch_commit]
    mock_pr.get_labels.return_value = []

    apply_labels(mock_pr, mock_repo)

    # Verify no labels were added
    mock_pr.add_to_labels.assert_not_called()

    # Verify conflicting labels were still removed
    assert mock_pr.remove_from_labels.call_count == 5


def test_apply_labels_creates_missing_labels(mock_pr, mock_repo, mock_feature_commit):
    """Test that missing labels are created before applying."""
    mock_pr.get_commits.return_value = [mock_feature_commit]
    mock_pr.get_labels.return_value = []

    # Both labels don't exist (404 errors)
    mock_repo.get_label.side_effect = GithubException(
        404, {"message": "Not Found"}, None
    )
    mock_label = MagicMock()
    mock_repo.create_label.return_value = mock_label

    apply_labels(mock_pr, mock_repo)

    # Verify labels were created (version: minor and feature)
    assert mock_repo.create_label.call_count == 2
    # Verify get_label was called for both labels
    assert mock_repo.get_label.call_count == 2


def test_apply_labels_removes_existing_labels(mock_pr, mock_repo, mock_feature_commit):
    """Test that existing conflicting labels are removed."""
    mock_pr.get_commits.return_value = [mock_feature_commit]
    mock_existing_label = MagicMock()
    mock_existing_label.name = "version: major"
    mock_pr.get_labels.return_value = [mock_existing_label]

    # Mock label existence check
    mock_label = MagicMock()
    mock_repo.get_label.return_value = mock_label

    apply_labels(mock_pr, mock_repo)

    # Verify all conflicting labels were attempted to be removed
    assert mock_pr.remove_from_labels.call_count == 5


def test_apply_labels_error_getting_commits(mock_pr, mock_repo):
    """Test error handling when getting commits fails."""
    mock_pr.get_commits.side_effect = GithubException(
        500, {"message": "Internal Server Error"}, None
    )

    with pytest.raises(GithubException):
        apply_labels(mock_pr, mock_repo)
