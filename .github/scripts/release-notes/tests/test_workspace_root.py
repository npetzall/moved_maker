"""Tests for workspace root detection functions."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from release_notes import __main__


class TestFindWorkspaceRoot:
    """Tests for find_workspace_root() function."""

    def test_finds_workspace_root_when_cargo_toml_exists(self, tmp_path):
        """Test that function finds workspace root when Cargo.toml exists."""
        # Create workspace structure
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        (workspace_root / "Cargo.toml").write_text("[package]")

        # Create nested directory structure
        nested_dir = workspace_root / "subdir" / "nested" / "deep"
        nested_dir.mkdir(parents=True)

        # Should find workspace root from nested directory
        result = __main__.find_workspace_root(nested_dir)
        assert result is not None
        assert result == workspace_root.resolve()

    def test_returns_none_when_cargo_toml_not_found(self, tmp_path):
        """Test that function returns None when Cargo.toml not found."""
        # Create directory structure without Cargo.toml
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        nested_dir = test_dir / "subdir" / "nested"
        nested_dir.mkdir(parents=True)

        # Should return None when traversing up to filesystem root
        result = __main__.find_workspace_root(nested_dir)
        assert result is None

    def test_handles_symlinks(self, tmp_path):
        """Test that function handles symlinks correctly."""
        # Create workspace structure
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        (workspace_root / "Cargo.toml").write_text("[package]")

        # Create symlink
        symlink_dir = tmp_path / "symlink_dir"
        symlink_dir.symlink_to(workspace_root)

        # Should resolve symlink and find workspace root
        result = __main__.find_workspace_root(symlink_dir)
        assert result is not None
        assert result == workspace_root.resolve()

    def test_stops_at_filesystem_root(self, tmp_path):
        """Test that function stops at filesystem root."""
        # Create directory structure without Cargo.toml
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Should return None when reaching filesystem root
        result = __main__.find_workspace_root(test_dir)
        assert result is None


class TestGetWorkspaceRoot:
    """Tests for get_workspace_root() function."""

    def test_uses_github_workspace_when_set_and_valid(self, tmp_path):
        """Test that function uses GITHUB_WORKSPACE when set and valid."""
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        (workspace_root / "Cargo.toml").write_text("[package]")

        with patch.dict(os.environ, {"GITHUB_WORKSPACE": str(workspace_root)}):
            result = __main__.get_workspace_root()
            assert result == workspace_root.resolve()

    def test_falls_back_to_recursive_search_when_github_workspace_not_set(
        self, tmp_path
    ):
        """Test that function falls back to recursive search when GITHUB_WORKSPACE not set."""
        # Create workspace structure
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        (workspace_root / "Cargo.toml").write_text("[package]")

        # Create script location in nested directory
        script_dir = workspace_root / ".github" / "scripts" / "release-notes" / "src" / "release_notes"
        script_dir.mkdir(parents=True)

        # Mock __file__ to point to script location
        script_file = script_dir / "__main__.py"
        with patch.object(__main__, "__file__", str(script_file)):
            # Remove GITHUB_WORKSPACE if set
            env = {k: v for k, v in os.environ.items() if k != "GITHUB_WORKSPACE"}
            with patch.dict(os.environ, env, clear=True):
                result = __main__.get_workspace_root()
                assert result == workspace_root.resolve()

    def test_warns_when_github_workspace_points_to_nonexistent_directory(
        self, tmp_path, capsys
    ):
        """Test that function warns when GITHUB_WORKSPACE points to non-existent directory."""
        nonexistent_path = tmp_path / "nonexistent"
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        (workspace_root / "Cargo.toml").write_text("[package]")

        # Create script location in nested directory
        script_dir = workspace_root / ".github" / "scripts" / "release-notes" / "src" / "release_notes"
        script_dir.mkdir(parents=True)

        # Mock __file__ to point to script location
        script_file = script_dir / "__main__.py"
        with patch.object(__main__, "__file__", str(script_file)):
            with patch.dict(os.environ, {"GITHUB_WORKSPACE": str(nonexistent_path)}):
                result = __main__.get_workspace_root()
                # Should fall back to recursive search and find workspace root
                assert result == workspace_root.resolve()
                # Should print warning
                captured = capsys.readouterr()
                assert "Warning: GITHUB_WORKSPACE points to non-existent directory" in captured.err

    def test_raises_runtime_error_when_workspace_root_cannot_be_determined(
        self, tmp_path
    ):
        """Test that function raises RuntimeError when workspace root cannot be determined."""
        # Create directory structure without Cargo.toml
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Create script location
        script_dir = test_dir / "scripts" / "release-notes" / "src" / "release_notes"
        script_dir.mkdir(parents=True)

        # Mock __file__ to point to script location
        script_file = script_dir / "__main__.py"
        with patch.object(__main__, "__file__", str(script_file)):
            # Remove GITHUB_WORKSPACE if set
            env = {k: v for k, v in os.environ.items() if k != "GITHUB_WORKSPACE"}
            with patch.dict(os.environ, env, clear=True):
                with pytest.raises(RuntimeError) as exc_info:
                    __main__.get_workspace_root()
                assert "Could not determine workspace root" in str(exc_info.value)
                assert "Cargo.toml" in str(exc_info.value)
                assert "GITHUB_WORKSPACE" in str(exc_info.value)

    def test_handles_github_workspace_with_trailing_slash(self, tmp_path):
        """Test that function handles GITHUB_WORKSPACE with trailing slash."""
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        (workspace_root / "Cargo.toml").write_text("[package]")

        # GITHUB_WORKSPACE might have trailing slash
        with patch.dict(os.environ, {"GITHUB_WORKSPACE": str(workspace_root) + "/"}):
            result = __main__.get_workspace_root()
            assert result == workspace_root.resolve()

    def test_handles_relative_paths_in_github_workspace(self, tmp_path):
        """Test that function handles relative paths in GITHUB_WORKSPACE."""
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        (workspace_root / "Cargo.toml").write_text("[package]")

        # Change to workspace directory and use relative path
        original_cwd = os.getcwd()
        try:
            os.chdir(workspace_root.parent)
            with patch.dict(os.environ, {"GITHUB_WORKSPACE": "workspace"}):
                result = __main__.get_workspace_root()
                assert result == workspace_root.resolve()
        finally:
            os.chdir(original_cwd)
