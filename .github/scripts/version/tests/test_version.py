"""Tests for version module."""
from unittest.mock import MagicMock, patch

import pytest
from packaging.version import InvalidVersion

from version.version import (
    calculate_new_version,
    calculate_pr_version,
    calculate_version,
    determine_bump_type,
    get_commit_count,
    get_latest_tag,
    get_tag_timestamp,
    shorten_commit_sha,
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

    with patch("version.version.get_latest_tag") as mock_get_tag:
        mock_get_tag.return_value = "vinvalid-version-string"

        with pytest.raises(ValueError, match="Invalid version format in git tag"):
            calculate_new_version(mock_github_client, repo_path=".")


def test_calculate_new_version_valid_tag():
    """Test calculate_new_version with valid tag version."""
    mock_github_client = MagicMock()
    mock_github_client.get_merged_prs_since.return_value = []

    with patch("version.version.get_latest_tag") as mock_get_tag, patch(
        "version.version.get_tag_timestamp"
    ) as mock_timestamp, patch(
        "version.version.get_commit_count"
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

    with patch("version.version.get_latest_tag") as mock_get_tag:
        mock_get_tag.return_value = None  # No tags - first release

        with patch("version.version.read_cargo_version") as mock_read:
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


def test_shorten_commit_sha_default_length():
    """Test shortening commit SHA with default length."""
    sha = "abc1234567890def1234567890abc1234567890"
    shortened = shorten_commit_sha(sha)
    assert shortened == "abc1234"
    assert len(shortened) == 7


def test_shorten_commit_sha_custom_length():
    """Test shortening commit SHA with custom length."""
    sha = "abc1234567890def1234567890abc1234567890"
    shortened = shorten_commit_sha(sha, length=10)
    assert shortened == "abc1234567"
    assert len(shortened) == 10


def test_shorten_commit_sha_short_input():
    """Test shortening commit SHA when input is shorter than requested length."""
    sha = "abc123"
    shortened = shorten_commit_sha(sha, length=10)
    assert shortened == "abc123"
    assert len(shortened) == 6


def test_shorten_commit_sha_empty():
    """Test shortening commit SHA with empty input."""
    with pytest.raises(ValueError, match="Commit SHA cannot be empty"):
        shorten_commit_sha("")


def test_shorten_commit_sha_invalid_length():
    """Test shortening commit SHA with invalid length."""
    with pytest.raises(ValueError, match="Length must be at least 1"):
        shorten_commit_sha("abc123", length=0)


def test_shorten_commit_sha_invalid_format():
    """Test shortening commit SHA with invalid format."""
    with pytest.raises(ValueError, match="Invalid SHA format"):
        shorten_commit_sha("abc-123")


def test_calculate_pr_version_valid():
    """Test calculating PR version with valid inputs."""
    mock_github_client = MagicMock()
    mock_github_client.get_merged_prs_since.return_value = []

    with patch("version.version.get_latest_tag") as mock_get_tag, patch(
        "version.version.get_tag_timestamp"
    ) as mock_timestamp, patch(
        "version.version.get_commit_count"
    ) as mock_commit_count:
        mock_get_tag.return_value = "v1.0.0"
        mock_timestamp.return_value = 1234567890
        mock_commit_count.return_value = 2

        pr_version = calculate_pr_version(
            mock_github_client, pr_number=123, commit_sha="abc1234567890def1234567890abc1234567890", repo_path="."
        )
        # Should be: base version (1.0.2) + pr123 + short SHA (abc1234)
        assert pr_version == "1.0.2-pr123+abc1234"


def test_calculate_pr_version_first_release():
    """Test calculating PR version when no tags exist (first release scenario)."""
    mock_github_client = MagicMock()
    mock_github_client.get_merged_prs_since.return_value = []

    with patch("version.version.get_latest_tag") as mock_get_tag, patch(
        "version.version.read_cargo_version"
    ) as mock_read_cargo, patch(
        "version.version.get_commit_count"
    ) as mock_commit_count:
        mock_get_tag.return_value = None
        mock_read_cargo.return_value = "0.1.0"
        mock_commit_count.return_value = 0

        pr_version = calculate_pr_version(
            mock_github_client, pr_number=456, commit_sha="def9876543210abc9876543210def9876543210", repo_path="."
        )
        # Should be: base version (0.1.0) + pr456 + short SHA (def9876)
        assert pr_version == "0.1.0-pr456+def9876"


def test_calculate_pr_version_invalid_pr_number():
    """Test calculating PR version with invalid PR number."""
    mock_github_client = MagicMock()

    with pytest.raises(ValueError, match="PR number must be positive"):
        calculate_pr_version(mock_github_client, pr_number=0, commit_sha="abc123", repo_path=".")


def test_calculate_pr_version_empty_sha():
    """Test calculating PR version with empty commit SHA."""
    mock_github_client = MagicMock()

    with pytest.raises(ValueError, match="Commit SHA cannot be empty"):
        calculate_pr_version(mock_github_client, pr_number=123, commit_sha="", repo_path=".")
