"""Conventional Commits parser."""

import re
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class ParsedCommit:
    """Parsed commit message structure."""

    type: str
    scope: Optional[str]
    subject: str
    body: Optional[str]
    footer: Optional[str]
    is_breaking: bool


def parse_commit_message(message: str) -> ParsedCommit:
    """
    Parse Conventional Commits format: type(scope): subject.

    Args:
        message: Full commit message (subject + body)

    Returns:
        ParsedCommit object with parsed components
    """
    # Split message into subject and body
    lines = message.split("\n")
    subject = lines[0] if lines else ""
    body_lines = lines[1:] if len(lines) > 1 else []
    body = "\n".join(body_lines) if body_lines else None

    # Parse subject: type(scope): subject or type: subject
    pattern = r"^(\w+)(?:\(([^)]+)\))?(!)?:\s*(.+)$"
    match = re.match(pattern, subject)

    if match:
        commit_type = match.group(1)
        scope = match.group(2)
        breaking_indicator = match.group(3)  # '!' if present
        subject_text = match.group(4)

        # Check for breaking change in footer
        is_breaking = breaking_indicator == "!" or _has_breaking_change_footer(body)

        return ParsedCommit(
            type=commit_type,
            scope=scope,
            subject=subject_text,
            body=body,
            footer=_extract_footer(body),
            is_breaking=is_breaking,
        )

    # Fallback: not a conventional commit
    return ParsedCommit(
        type="other",
        scope=None,
        subject=subject,
        body=body,
        footer=None,
        is_breaking=False,
    )


def _has_breaking_change_footer(body: Optional[str]) -> bool:
    """Check if commit has BREAKING CHANGE in footer."""
    if not body:
        return False
    return "BREAKING CHANGE:" in body or "BREAKING-CHANGE:" in body


def _extract_footer(body: Optional[str]) -> Optional[str]:
    """Extract footer from commit body."""
    if not body:
        return None
    # Footer is typically after a blank line
    parts = body.split("\n\n")
    if len(parts) > 1:
        return parts[-1]
    return None


def categorize_commit(commit: object) -> str:
    """
    Categorize commit by Conventional Commits type.

    Args:
        commit: Commit object with commit.message attribute

    Returns:
        Category string (feat, fix, docs, etc.)
    """
    message = commit.commit.message if hasattr(commit, "commit") else str(commit)
    parsed = parse_commit_message(message)

    # Map types to categories
    type_mapping = {
        "feat": "feat",
        "feature": "feat",
        "fix": "fix",
        "bugfix": "fix",
        "docs": "docs",
        "documentation": "docs",
        "style": "style",
        "refactor": "refactor",
        "perf": "perf",
        "performance": "perf",
        "test": "test",
        "tests": "test",
        "chore": "chore",
        "ci": "ci",
        "build": "build",
        "revert": "revert",
    }

    commit_type = parsed.type.lower()
    return type_mapping.get(commit_type, "other")


def is_breaking_change(commit: object) -> bool:
    """
    Check if commit is a breaking change.

    Args:
        commit: Commit object with commit.message attribute

    Returns:
        True if commit is a breaking change
    """
    message = commit.commit.message if hasattr(commit, "commit") else str(commit)
    parsed = parse_commit_message(message)
    return parsed.is_breaking


def extract_scope_and_subject(message: str) -> Tuple[Optional[str], str]:
    """
    Extract scope and subject from commit message.

    Args:
        message: Commit message

    Returns:
        Tuple of (scope, subject)
    """
    parsed = parse_commit_message(message)
    return parsed.scope, parsed.subject
