"""Tests for git.py module."""

import subprocess
from unittest.mock import MagicMock, Mock, patch

import pytest
from packaging import version

from release_notes import git


@pytest.fixture
def mock_repo():
    """Create a mock repository with tags."""
    repo = MagicMock()

    # Create mock tags
    tag1 = Mock()
    tag1.name = "v1.0.0"
    tag1.commit.sha = "abc123"

    tag2 = Mock()
    tag2.name = "v1.1.0"
    tag2.commit.sha = "def456"

    tag3 = Mock()
    tag3.name = "v1.2.0"
    tag3.commit.sha = "ghi789"

    repo.get_tags.return_value = [tag1, tag2, tag3]
    return repo


@pytest.fixture
def mock_repo_with_commits():
    """Create a mock repository with commits."""
    repo = MagicMock()

    commit1 = Mock()
    commit1.sha = "commit1"
    commit1.commit.message = "feat: add feature"

    commit2 = Mock()
    commit2.sha = "commit2"
    commit2.commit.message = "fix: fix bug"

    repo.get_commits.return_value = [commit1, commit2]
    return repo


class TestGetTagsSorted:
    """Tests for get_tags_sorted function."""

    def test_get_tags_sorted(self, mock_repo):
        """Test that tags are sorted by version (descending)."""
        tags = git.get_tags_sorted(mock_repo)
        assert len(tags) == 3
        assert tags[0].name == "v1.2.0"
        assert tags[1].name == "v1.1.0"
        assert tags[2].name == "v1.0.0"

    def test_get_tags_sorted_without_v_prefix(self, mock_repo):
        """Test that tags without 'v' prefix are handled."""
        tag1 = Mock()
        tag1.name = "1.0.0"
        tag2 = Mock()
        tag2.name = "v1.1.0"
        mock_repo.get_tags.return_value = [tag1, tag2]

        tags = git.get_tags_sorted(mock_repo)
        assert len(tags) == 2
        assert tags[0].name == "v1.1.0"
        assert tags[1].name == "1.0.0"

    def test_get_tags_sorted_empty(self):
        """Test with no tags."""
        repo = MagicMock()
        repo.get_tags.return_value = []
        tags = git.get_tags_sorted(repo)
        assert tags == []

    def test_get_tags_sorted_filters_invalid_versions(self):
        """Test that invalid version tags are filtered out."""
        repo = MagicMock()
        tag1 = Mock()
        tag1.name = "v1.0.0"
        tag2 = Mock()
        tag2.name = "invalid-tag"
        tag3 = Mock()
        tag3.name = "v1.1.0"
        repo.get_tags.return_value = [tag1, tag2, tag3]

        tags = git.get_tags_sorted(repo)
        assert len(tags) == 2
        assert tags[0].name == "v1.1.0"
        assert tags[1].name == "v1.0.0"


class TestGetPreviousTag:
    """Tests for get_previous_tag function."""

    def test_get_previous_tag(self, mock_repo):
        """Test getting previous tag."""
        previous = git.get_previous_tag(mock_repo, "v1.2.0")
        assert previous is not None
        assert previous.name == "v1.1.0"

    def test_get_previous_tag_first_tag(self, mock_repo):
        """Test that first tag returns None."""
        previous = git.get_previous_tag(mock_repo, "v1.0.0")
        assert previous is None

    def test_get_previous_tag_not_found(self, mock_repo):
        """Test that non-existent tag returns None."""
        previous = git.get_previous_tag(mock_repo, "v2.0.0")
        assert previous is None

    def test_get_previous_tag_no_tags(self):
        """Test with no tags."""
        repo = MagicMock()
        repo.get_tags.return_value = []
        previous = git.get_previous_tag(repo, "v1.0.0")
        assert previous is None


class TestGetCommitsBetweenTags:
    """Tests for get_commits_between_tags function."""

    def test_get_commits_between_tags(self, mock_repo):
        """Test getting commits between tags."""
        # Create mock comparison
        comparison = MagicMock()
        commit1 = Mock()
        commit2 = Mock()
        comparison.commits = [commit1, commit2]
        mock_repo.compare.return_value = comparison

        previous_tag = Mock()
        previous_tag.commit.sha = "abc123"
        current_tag = Mock()
        current_tag.commit.sha = "ghi789"

        commits = git.get_commits_between_tags(mock_repo, previous_tag, current_tag)
        assert len(commits) == 2
        mock_repo.compare.assert_called_once_with("abc123", "ghi789")

    def test_get_commits_between_tags_no_previous(self, mock_repo):
        """Test with no previous tag."""
        current_tag = Mock()
        commits = git.get_commits_between_tags(mock_repo, None, current_tag)
        assert commits == []


class TestGetAllCommits:
    """Tests for get_all_commits function."""

    def test_get_all_commits(self, mock_repo_with_commits):
        """Test getting all commits."""
        commits = git.get_all_commits(mock_repo_with_commits)
        assert len(commits) == 2
        assert commits[0].sha == "commit1"
        assert commits[1].sha == "commit2"

    def test_get_all_commits_empty(self):
        """Test with no commits."""
        repo = MagicMock()
        repo.get_commits.return_value = []
        commits = git.get_all_commits(repo)
        assert commits == []


class TestGetCommitShasByPath:
    """Tests for get_commit_shas_by_path function."""

    def test_get_commit_shas_by_path_with_previous_tag(self):
        """Test getting commit SHAs filtered by path with previous tag."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "abc123\ndef456\n"

            shas = git.get_commit_shas_by_path("v1.0.0", "v1.1.0", ["src/", "Cargo.toml"])
            assert shas == {"abc123", "def456"}
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "v1.0.0..v1.1.0" in call_args
            assert "src/" in call_args
            assert "Cargo.toml" in call_args

    def test_get_commit_shas_by_path_first_release(self):
        """Test getting commit SHAs for first release."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "abc123\n"

            shas = git.get_commit_shas_by_path(None, "v1.0.0", ["src/"])
            assert shas == {"abc123"}
            call_args = mock_run.call_args[0][0]
            assert "v1.0.0" in call_args

    def test_get_commit_shas_by_path_empty(self):
        """Test with no matching commits."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""

            shas = git.get_commit_shas_by_path("v1.0.0", "v1.1.0", ["src/"])
            assert shas == set()

    def test_get_commit_shas_by_path_error(self):
        """Test handling of git command errors."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "git")

            shas = git.get_commit_shas_by_path("v1.0.0", "v1.1.0", ["src/"])
            assert shas == set()


class TestSplitCommitsByPath:
    """Tests for split_commits_by_path function."""

    def test_split_commits_by_path(self, mock_repo):
        """Test splitting commits into application and other."""
        commit1 = Mock()
        commit1.sha = "abc123"
        commit2 = Mock()
        commit2.sha = "def456"
        commit3 = Mock()
        commit3.sha = "ghi789"

        commits = [commit1, commit2, commit3]

        with patch("release_notes.git.get_commit_shas_by_path") as mock_get_shas:
            mock_get_shas.return_value = {"abc123", "def456"}

            app_commits, other_commits = git.split_commits_by_path(
                commits, "v1.0.0", "v1.1.0"
            )

            assert len(app_commits) == 2
            assert len(other_commits) == 1
            assert commit1 in app_commits
            assert commit2 in app_commits
            assert commit3 in other_commits

    def test_split_commits_by_path_all_application(self, mock_repo):
        """Test when all commits are application commits."""
        commit1 = Mock()
        commit1.sha = "abc123"
        commit2 = Mock()
        commit2.sha = "def456"

        commits = [commit1, commit2]

        with patch("release_notes.git.get_commit_shas_by_path") as mock_get_shas:
            mock_get_shas.return_value = {"abc123", "def456"}

            app_commits, other_commits = git.split_commits_by_path(
                commits, "v1.0.0", "v1.1.0"
            )

            assert len(app_commits) == 2
            assert len(other_commits) == 0

    def test_split_commits_by_path_all_other(self, mock_repo):
        """Test when all commits are other commits."""
        commit1 = Mock()
        commit1.sha = "abc123"
        commit2 = Mock()
        commit2.sha = "def456"

        commits = [commit1, commit2]

        with patch("release_notes.git.get_commit_shas_by_path") as mock_get_shas:
            mock_get_shas.return_value = set()

            app_commits, other_commits = git.split_commits_by_path(
                commits, "v1.0.0", "v1.1.0"
            )

            assert len(app_commits) == 0
            assert len(other_commits) == 2
