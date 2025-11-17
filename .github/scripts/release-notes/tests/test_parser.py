"""Tests for parser.py module."""

from unittest.mock import Mock

import pytest

from release_notes import parser


class TestParseCommitMessage:
    """Tests for parse_commit_message function."""

    def test_parse_conventional_commit_with_scope(self):
        """Test parsing conventional commit with scope."""
        message = "feat(parser): add new parsing function"
        parsed = parser.parse_commit_message(message)
        assert parsed.type == "feat"
        assert parsed.scope == "parser"
        assert parsed.subject == "add new parsing function"
        assert parsed.is_breaking is False

    def test_parse_conventional_commit_without_scope(self):
        """Test parsing conventional commit without scope."""
        message = "fix: resolve memory leak"
        parsed = parser.parse_commit_message(message)
        assert parsed.type == "fix"
        assert parsed.scope is None
        assert parsed.subject == "resolve memory leak"
        assert parsed.is_breaking is False

    def test_parse_conventional_commit_with_body(self):
        """Test parsing conventional commit with body."""
        message = "feat: add feature\n\nThis is a detailed description."
        parsed = parser.parse_commit_message(message)
        assert parsed.type == "feat"
        assert parsed.subject == "add feature"
        assert parsed.body == "\nThis is a detailed description."

    def test_parse_breaking_change_with_exclamation(self):
        """Test parsing breaking change with ! indicator."""
        message = "feat!: remove deprecated API"
        parsed = parser.parse_commit_message(message)
        assert parsed.type == "feat"
        assert parsed.is_breaking is True

    def test_parse_breaking_change_in_footer(self):
        """Test parsing breaking change in footer."""
        message = "feat: add new API\n\nBREAKING CHANGE: Old API removed"
        parsed = parser.parse_commit_message(message)
        assert parsed.is_breaking is True

    def test_parse_non_conventional_commit(self):
        """Test parsing non-conventional commit."""
        message = "Just a regular commit message"
        parsed = parser.parse_commit_message(message)
        assert parsed.type == "other"
        assert parsed.subject == "Just a regular commit message"
        assert parsed.is_breaking is False


class TestCategorizeCommit:
    """Tests for categorize_commit function."""

    def test_categorize_feat(self):
        """Test categorizing feature commit."""
        commit = Mock()
        commit.commit.message = "feat: add new feature"
        category = parser.categorize_commit(commit)
        assert category == "feat"

    def test_categorize_fix(self):
        """Test categorizing fix commit."""
        commit = Mock()
        commit.commit.message = "fix: fix bug"
        category = parser.categorize_commit(commit)
        assert category == "fix"

    def test_categorize_docs(self):
        """Test categorizing docs commit."""
        commit = Mock()
        commit.commit.message = "docs: update README"
        category = parser.categorize_commit(commit)
        assert category == "docs"

    def test_categorize_other(self):
        """Test categorizing unknown type."""
        commit = Mock()
        commit.commit.message = "unknown: some change"
        category = parser.categorize_commit(commit)
        assert category == "other"


class TestIsBreakingChange:
    """Tests for is_breaking_change function."""

    def test_is_breaking_change_with_exclamation(self):
        """Test detecting breaking change with !."""
        commit = Mock()
        commit.commit.message = "feat!: remove API"
        assert parser.is_breaking_change(commit) is True

    def test_is_breaking_change_in_footer(self):
        """Test detecting breaking change in footer."""
        commit = Mock()
        commit.commit.message = "feat: add API\n\nBREAKING CHANGE: Old removed"
        assert parser.is_breaking_change(commit) is True

    def test_is_not_breaking_change(self):
        """Test non-breaking change."""
        commit = Mock()
        commit.commit.message = "feat: add feature"
        assert parser.is_breaking_change(commit) is False


class TestExtractScopeAndSubject:
    """Tests for extract_scope_and_subject function."""

    def test_extract_scope_and_subject_with_scope(self):
        """Test extracting scope and subject."""
        message = "feat(parser): add function"
        scope, subject = parser.extract_scope_and_subject(message)
        assert scope == "parser"
        assert subject == "add function"

    def test_extract_scope_and_subject_without_scope(self):
        """Test extracting without scope."""
        message = "fix: fix bug"
        scope, subject = parser.extract_scope_and_subject(message)
        assert scope is None
        assert subject == "fix bug"
