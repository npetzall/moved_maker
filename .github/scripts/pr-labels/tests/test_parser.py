"""Tests for commit parser module."""
from unittest.mock import MagicMock

from pr_labels.parser import parse_commits


def test_parse_breaking_change_commit(mock_breaking_commit):
    """Test parsing breaking change commit with BREAKING CHANGE:."""
    commits = [mock_breaking_commit]
    version_label, alt_label = parse_commits(commits)
    assert version_label == "version: major"
    assert alt_label == "breaking"


def test_parse_breaking_change_with_bang():
    """Test parsing breaking change commit with !:."""
    commit = MagicMock()
    commit_obj = MagicMock()
    commit_obj.message = "feat!: breaking change"
    commit.commit = commit_obj
    commits = [commit]

    version_label, alt_label = parse_commits(commits)
    assert version_label == "version: major"
    assert alt_label == "breaking"


def test_parse_feature_commit(mock_feature_commit):
    """Test parsing feature commit."""
    commits = [mock_feature_commit]
    version_label, alt_label = parse_commits(commits)
    assert version_label == "version: minor"
    assert alt_label == "feature"


def test_parse_patch_commit(mock_patch_commit):
    """Test parsing patch commit."""
    commits = [mock_patch_commit]
    version_label, alt_label = parse_commits(commits)
    assert version_label is None
    assert alt_label is None


def test_parse_empty_commit(mock_empty_commit):
    """Test parsing empty commit message."""
    commits = [mock_empty_commit]
    version_label, alt_label = parse_commits(commits)
    assert version_label is None
    assert alt_label is None


def test_parse_non_conventional_commit():
    """Test parsing non-conventional commit message."""
    commit = MagicMock()
    commit_obj = MagicMock()
    commit_obj.message = "Just a regular commit message"
    commit.commit = commit_obj
    commits = [commit]

    version_label, alt_label = parse_commits(commits)
    assert version_label is None
    assert alt_label is None


def test_parse_multiline_commit():
    """Test parsing multi-line commit message."""
    commit = MagicMock()
    commit_obj = MagicMock()
    commit_obj.message = "feat: add feature\n\nThis is a longer description\nwith multiple lines"
    commit.commit = commit_obj
    commits = [commit]

    version_label, alt_label = parse_commits(commits)
    assert version_label == "version: minor"
    assert alt_label == "feature"


def test_parse_multiple_commits_breaking_takes_priority(mock_feature_commit, mock_breaking_commit):
    """Test that breaking change takes priority over feature."""
    commits = [mock_feature_commit, mock_breaking_commit]
    version_label, alt_label = parse_commits(commits)
    assert version_label == "version: major"
    assert alt_label == "breaking"


def test_parse_multiple_commits_feature(mock_patch_commit, mock_feature_commit):
    """Test that feature is detected when mixed with patch commits."""
    commits = [mock_patch_commit, mock_feature_commit]
    version_label, alt_label = parse_commits(commits)
    assert version_label == "version: minor"
    assert alt_label == "feature"


def test_parse_multiple_commits_patch_only(mock_patch_commit):
    """Test that patch is default when only patch commits."""
    commit2 = MagicMock()
    commit_obj2 = MagicMock()
    commit_obj2.message = "chore: update dependencies"
    commit2.commit = commit_obj2
    commits = [mock_patch_commit, commit2]

    version_label, alt_label = parse_commits(commits)
    assert version_label is None
    assert alt_label is None


def test_parse_commit_with_none_commit():
    """Test parsing commit with None commit object."""
    commit = MagicMock()
    commit.commit = None
    commits = [commit]

    version_label, alt_label = parse_commits(commits)
    assert version_label is None
    assert alt_label is None
