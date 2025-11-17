"""Tests for formatter.py module."""

from unittest.mock import Mock

import pytest

from release_notes import formatter


@pytest.fixture
def mock_commit():
    """Create a mock commit."""
    commit = Mock()
    commit.sha = "abc123def456"
    commit.html_url = "https://github.com/owner/repo/commit/abc123def456"
    commit.commit = Mock()
    commit.commit.message = "feat: add new feature"
    commit.commit.author = Mock()
    commit.commit.author.name = "Test User"
    return commit


@pytest.fixture
def mock_breaking_commit():
    """Create a mock breaking change commit."""
    commit = Mock()
    commit.sha = "def456ghi789"
    commit.html_url = "https://github.com/owner/repo/commit/def456ghi789"
    commit.commit = Mock()
    commit.commit.message = "feat!: remove deprecated API"
    commit.commit.author = Mock()
    commit.commit.author.name = "Test User"
    return commit


class TestGroupByType:
    """Tests for group_by_type function."""

    def test_group_by_type(self, mock_commit):
        """Test grouping commits by type."""
        commits = [mock_commit]
        grouped = formatter.group_by_type(commits)
        assert "feat" in grouped
        assert len(grouped["feat"]) == 1

    def test_group_by_type_breaking(self, mock_breaking_commit):
        """Test grouping breaking changes separately."""
        commits = [mock_breaking_commit]
        grouped = formatter.group_by_type(commits)
        assert "breaking" in grouped
        assert len(grouped["breaking"]) == 1

    def test_group_by_type_multiple_types(self, mock_commit):
        """Test grouping multiple commit types."""
        fix_commit = Mock()
        fix_commit.commit = Mock()
        fix_commit.commit.message = "fix: fix bug"
        fix_commit.sha = "fix123"

        commits = [mock_commit, fix_commit]
        grouped = formatter.group_by_type(commits)
        assert "feat" in grouped
        assert "fix" in grouped
        assert len(grouped["feat"]) == 1
        assert len(grouped["fix"]) == 1


class TestFormatCommitEntry:
    """Tests for format_commit_entry function."""

    def test_format_commit_entry(self, mock_commit):
        """Test formatting commit entry."""
        result = formatter.format_commit_entry(mock_commit, "https://github.com/owner/repo")
        assert "add new feature" in result
        assert "abc123" in result
        assert "Test User" in result

    def test_format_commit_entry_no_repo_url(self, mock_commit):
        """Test formatting without repo URL."""
        result = formatter.format_commit_entry(mock_commit)
        assert "add new feature" in result
        assert "abc123" in result


class TestFormatSectionHeader:
    """Tests for format_section_header function."""

    def test_format_section_header(self):
        """Test formatting section header."""
        result = formatter.format_section_header("feat")
        assert "✨" in result
        assert "Features" in result

    def test_format_section_header_custom_emoji(self):
        """Test formatting with custom emoji."""
        result = formatter.format_section_header("feat", "🎉")
        assert "🎉" in result
        assert "Features" in result


class TestFormatBreakingChanges:
    """Tests for format_breaking_changes function."""

    def test_format_breaking_changes(self, mock_breaking_commit):
        """Test formatting breaking changes."""
        result = formatter.format_breaking_changes([mock_breaking_commit], "https://github.com/owner/repo")
        assert "💥" in result
        assert "Breaking Changes" in result
        assert "remove deprecated API" in result

    def test_format_breaking_changes_empty(self):
        """Test formatting empty breaking changes."""
        result = formatter.format_breaking_changes([])
        assert result == ""


class TestAddInstallationSection:
    """Tests for add_installation_section function."""

    def test_add_installation_section(self):
        """Test adding installation section."""
        result = formatter.add_installation_section("v1.2.0", "https://github.com/owner/repo")
        assert "📦 Installation" in result
        assert "v1.2.0" in result
        assert "move_maker-linux-x86_64" in result
        assert "move_maker-macos-aarch64" in result


class TestGenerateMarkdown:
    """Tests for generate_markdown function."""

    def test_generate_markdown_with_commits(self, mock_commit):
        """Test generating markdown with commits."""
        result = formatter.generate_markdown(
            [mock_commit],
            "v1.1.0",
            "v1.2.0",
            "https://github.com/owner/repo",
        )
        assert "Release v1.2.0" in result
        assert "What's New" in result
        assert "add new feature" in result
        assert "Installation" in result
        assert "Statistics" in result

    def test_generate_markdown_first_release(self, mock_commit):
        """Test generating markdown for first release."""
        result = formatter.generate_markdown(
            [mock_commit],
            None,
            "v1.0.0",
            "https://github.com/owner/repo",
        )
        assert "Release v1.0.0" in result
        assert "First release" in result

    def test_generate_markdown_no_commits(self):
        """Test generating markdown with no commits."""
        result = formatter.generate_markdown(
            [],
            "v1.1.0",
            "v1.2.0",
            "https://github.com/owner/repo",
        )
        assert "No application changes" in result
        assert "Application Commits" in result
        assert "Other Commits" in result

    def test_generate_markdown_with_breaking(self, mock_breaking_commit):
        """Test generating markdown with breaking changes."""
        result = formatter.generate_markdown(
            [mock_breaking_commit],
            "v1.1.0",
            "v1.2.0",
            "https://github.com/owner/repo",
        )
        assert "Breaking Changes" in result
        assert "remove deprecated API" in result

    def test_generate_markdown_no_installation(self, mock_commit):
        """Test generating markdown without installation section."""
        result = formatter.generate_markdown(
            [mock_commit],
            "v1.1.0",
            "v1.2.0",
            "https://github.com/owner/repo",
            installation_section=False,
        )
        assert "Installation" not in result
