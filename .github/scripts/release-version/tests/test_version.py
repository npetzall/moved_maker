"""Tests for version module."""
from unittest.mock import MagicMock, patch

import pytest
from packaging.version import InvalidVersion

from release_version.version import (
    calculate_new_version,
    calculate_version,
    determine_bump_type,
    get_commit_count,
    get_latest_tag,
    get_tag_timestamp,
)


def test_get_latest_tag_with_tags():
    """Test getting latest tag when tags exist."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "v1.0.0\n"

        tag = get_latest_tag()
        assert tag == "v1.0.0"
        mock_run.assert_called_once()


def test_get_latest_tag_no_tags():
    """Test getting latest tag when no tags exist."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""

        tag = get_latest_tag()
        assert tag is None


def test_get_tag_timestamp_valid():
    """Test getting timestamp for valid tag."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "1234567890\n"

        timestamp = get_tag_timestamp("v1.0.0")
        assert timestamp == 1234567890


def test_get_tag_timestamp_invalid():
    """Test getting timestamp for invalid tag."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("Tag not found")

        with pytest.raises(Exception):
            get_tag_timestamp("invalid-tag")


def test_get_commit_count():
    """Test getting commit count with path filtering."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "5\n"

        count = get_commit_count("v1.0.0")
        assert count == 5

        # Verify path filtering is included in the command
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "--" in call_args
        assert "src/" in call_args
        assert "Cargo.toml" in call_args
        assert "Cargo.lock" in call_args


def test_determine_bump_type_major():
    """Test determining major bump type."""
    pr1 = MagicMock()
    pr1.number = 1
    label1 = MagicMock()
    label1.name = "version: major"
    pr1.labels = [label1]

    prs = [pr1]
    bump_type = determine_bump_type(prs)
    assert bump_type == "MAJOR"


def test_determine_bump_type_minor():
    """Test determining minor bump type."""
    pr1 = MagicMock()
    pr1.number = 1
    label1 = MagicMock()
    label1.name = "version: minor"
    pr1.labels = [label1]

    prs = [pr1]
    bump_type = determine_bump_type(prs)
    assert bump_type == "MINOR"


def test_determine_bump_type_patch():
    """Test determining patch bump type (no labels)."""
    pr1 = MagicMock()
    pr1.number = 1
    pr1.labels = []

    prs = [pr1]
    bump_type = determine_bump_type(prs)
    assert bump_type == "PATCH"


def test_determine_bump_type_multiple_prs_highest_priority():
    """Test that major takes priority over minor."""
    pr1 = MagicMock()
    pr1.number = 1
    label1 = MagicMock()
    label1.name = "version: minor"
    pr1.labels = [label1]

    pr2 = MagicMock()
    pr2.number = 2
    label2 = MagicMock()
    label2.name = "version: major"
    pr2.labels = [label2]

    prs = [pr1, pr2]
    bump_type = determine_bump_type(prs)
    assert bump_type == "MAJOR"


def test_calculate_version_major():
    """Test calculating major version bump."""
    new_version = calculate_version("1.0.0", "MAJOR", 0)
    assert new_version == "2.0.0"


def test_calculate_version_minor():
    """Test calculating minor version bump."""
    new_version = calculate_version("1.0.0", "MINOR", 0)
    assert new_version == "1.1.0"


def test_calculate_version_patch():
    """Test calculating patch version bump."""
    new_version = calculate_version("1.0.0", "PATCH", 3)
    assert new_version == "1.0.3"


def test_calculate_version_invalid_base():
    """Test calculating version with invalid base version."""
    with pytest.raises(InvalidVersion):
        calculate_version("invalid", "PATCH", 1)


def test_calculate_new_version_invalid_tag():
    """Test calculate_new_version with invalid tag version format."""
    mock_github_client = MagicMock()

    with patch("release_version.version.get_latest_tag") as mock_get_tag:
        mock_get_tag.return_value = "vinvalid-version-string"

        with pytest.raises(ValueError, match="Invalid version format in git tag"):
            calculate_new_version(mock_github_client, repo_path=".")


def test_calculate_new_version_valid_tag():
    """Test calculate_new_version with valid tag version."""
    mock_github_client = MagicMock()
    mock_github_client.get_merged_prs_since.return_value = []

    with patch("release_version.version.get_latest_tag") as mock_get_tag, patch(
        "release_version.version.get_tag_timestamp"
    ) as mock_timestamp, patch(
        "release_version.version.get_commit_count"
    ) as mock_commit_count:
        mock_get_tag.return_value = "v1.0.0"
        mock_timestamp.return_value = 1234567890
        mock_commit_count.return_value = 2

        version, tag_name = calculate_new_version(mock_github_client, repo_path=".")
        assert version == "1.0.2"  # PATCH bump with 2 commits
        assert tag_name == "v1.0.2"


def test_calculate_new_version_first_release_invalid_cargo_version():
    """Test calculate_new_version first release with invalid Cargo.toml version."""
    mock_github_client = MagicMock()

    with patch("release_version.version.get_latest_tag") as mock_get_tag:
        mock_get_tag.return_value = None  # No tags - first release

        with patch("release_version.version.read_cargo_version") as mock_read:
            mock_read.side_effect = ValueError(
                "Invalid version format in Cargo.toml: invalid-version. Expected semantic version (e.g., 1.0.0)"
            )

            with pytest.raises(ValueError, match="Invalid version format in Cargo.toml"):
                calculate_new_version(mock_github_client, repo_path=".")


def test_calculate_version_validates_output():
    """Test that calculate_version validates the output (defensive programming)."""
    # This test verifies that the defensive validation is in place
    # In practice, calculated versions should always be valid, but we test the mechanism
    # by ensuring valid versions pass through correctly
    new_version = calculate_version("1.0.0", "MAJOR", 0)
    assert new_version == "2.0.0"
    # If validation fails, an exception would be raised above
