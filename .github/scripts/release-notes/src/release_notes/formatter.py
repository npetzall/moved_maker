"""Markdown release notes formatter."""

from collections import defaultdict
from typing import Optional

from release_notes import parser

# Emoji mapping for commit types
TYPE_EMOJI = {
    "feat": "✨",
    "fix": "🐛",
    "docs": "📚",
    "style": "💄",
    "refactor": "♻️",
    "perf": "⚡",
    "test": "✅",
    "chore": "🔧",
    "ci": "👷",
    "build": "🏗️",
    "revert": "⏪",
    "breaking": "💥",
    "other": "📝",
}

# Type labels for display
TYPE_LABELS = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "docs": "Documentation",
    "style": "Style",
    "refactor": "Refactoring",
    "perf": "Performance",
    "test": "Tests",
    "chore": "Maintenance",
    "ci": "CI/CD",
    "build": "Build",
    "revert": "Reverts",
    "breaking": "Breaking Changes",
    "other": "Other",
}


def group_by_type(commits: list) -> dict:
    """
    Group commits by Conventional Commits type.

    Args:
        commits: List of commit objects

    Returns:
        Dictionary mapping types to commit lists
    """
    grouped = defaultdict(list)
    breaking_commits = []

    for commit in commits:
        if parser.is_breaking_change(commit):
            breaking_commits.append(commit)
        else:
            category = parser.categorize_commit(commit)
            grouped[category].append(commit)

    # Add breaking changes as separate group
    if breaking_commits:
        grouped["breaking"] = breaking_commits

    return dict(grouped)


def format_commit_entry(commit: object, repo_url: Optional[str] = None) -> str:
    """
    Format individual commit with links and metadata.

    Args:
        commit: Commit object
        repo_url: Repository URL for generating links (optional)

    Returns:
        Formatted commit entry string
    """
    message = commit.commit.message if hasattr(commit, "commit") else str(commit)
    parsed = parser.parse_commit_message(message)
    subject = parsed.subject

    # Get commit SHA (short version)
    sha = commit.sha[:7] if hasattr(commit, "sha") else "unknown"

    # Build commit link
    if repo_url and hasattr(commit, "html_url"):
        commit_link = f"[`{sha}`]({commit.html_url})"
    elif repo_url and hasattr(commit, "sha"):
        commit_link = f"[`{sha}`]({repo_url}/commit/{commit.sha})"
    else:
        commit_link = f"`{sha}`"

    # Get author
    author = ""
    if hasattr(commit, "commit") and hasattr(commit.commit, "author"):
        if commit.commit.author:
            author_name = commit.commit.author.name or ""
            if author_name:
                author = f" by {author_name}"

    return f"- {subject} ({commit_link}){author}"


def format_section_header(commit_type: str, emoji: Optional[str] = None) -> str:
    """
    Create formatted section header with emoji.

    Args:
        commit_type: Commit type (feat, fix, etc.)
        emoji: Optional emoji override

    Returns:
        Formatted header string
    """
    emoji_char = emoji or TYPE_EMOJI.get(commit_type, "📝")
    label = TYPE_LABELS.get(commit_type, commit_type.capitalize())
    return f"### {emoji_char} {label}"


def format_breaking_changes(commits: list, repo_url: Optional[str] = None) -> str:
    """
    Special formatting for breaking changes.

    Args:
        commits: List of breaking change commits
        repo_url: Repository URL for generating links (optional)

    Returns:
        Formatted breaking changes section
    """
    if not commits:
        return ""

    lines = [format_section_header("breaking")]
    lines.append("")

    for commit in commits:
        message = commit.commit.message if hasattr(commit, "commit") else str(commit)
        parsed = parser.parse_commit_message(message)
        subject = parsed.subject

        # Get commit SHA
        sha = commit.sha[:7] if hasattr(commit, "sha") else "unknown"

        # Build commit link
        if repo_url and hasattr(commit, "html_url"):
            commit_link = f"[`{sha}`]({commit.html_url})"
        elif repo_url and hasattr(commit, "sha"):
            commit_link = f"[`{sha}`]({repo_url}/commit/{commit.sha})"
        else:
            commit_link = f"`{sha}`"

        # Get author
        author = ""
        if hasattr(commit, "commit") and hasattr(commit.commit, "author"):
            if commit.commit.author:
                author_name = commit.commit.author.name or ""
                if author_name:
                    author = f" by {author_name}"

        lines.append(f"- **{subject}** ({commit_link}){author}")

        # Add migration notes if available in body
        if parsed.body and "BREAKING CHANGE:" in parsed.body:
            migration_note = parsed.body.split("BREAKING CHANGE:")[-1].strip()
            if migration_note:
                lines.append(f"  - {migration_note}")

    return "\n".join(lines)


def add_installation_section(current_tag: str, repo_url: Optional[str] = None) -> str:
    """
    Generate installation section with download links.

    Args:
        current_tag: Current tag name (e.g., "v1.2.0")
        repo_url: Repository URL for generating links (optional)

    Returns:
        Formatted installation section
    """
    if not repo_url:
        repo_url = "https://github.com/owner/repo"

    lines = [
        "## 📦 Installation",
        "",
        "Download the appropriate binary for your platform:",
        "",
        f"- **Linux (x86_64)**: [`moved_maker-linux-x86_64`]({repo_url}/releases/download/{current_tag}/moved_maker-linux-x86_64)",
        f"- **Linux (ARM64)**: [`moved_maker-linux-aarch64`]({repo_url}/releases/download/{current_tag}/moved_maker-linux-aarch64)",
        f"- **macOS (Intel)**: [`moved_maker-macos-x86_64`]({repo_url}/releases/download/{current_tag}/moved_maker-macos-x86_64)",
        f"- **macOS (Apple Silicon)**: [`moved_maker-macos-aarch64`]({repo_url}/releases/download/{current_tag}/moved_maker-macos-aarch64)",
    ]

    return "\n".join(lines)


def generate_markdown(
    commits: list,
    previous_tag: Optional[str],
    current_tag: str,
    repo_url: Optional[str] = None,
    installation_section: bool = True,
    application_commits: Optional[list] = None,
    other_commits: Optional[list] = None,
) -> str:
    """
    Generate full Markdown release notes document with Application and Other sections.

    Args:
        commits: List of all commit objects (for statistics)
        previous_tag: Previous tag name (None for first release)
        current_tag: Current tag name
        repo_url: Repository URL for generating links (optional)
        installation_section: Whether to include installation section
        application_commits: Commits that modify application code (if None, uses all commits)
        other_commits: Commits that don't modify application code (if None, empty)

    Returns:
        Complete Markdown document
    """
    if not repo_url:
        repo_url = "https://github.com/owner/repo"

    lines = [f"# Release {current_tag}", ""]

    # Use provided splits or default to all commits in application section
    if application_commits is None:
        application_commits = commits
    if other_commits is None:
        other_commits = []

    lines.append("## 🎉 What's New")
    lines.append("")

    # Format Application section
    if application_commits:
        lines.append("### 📦 Application")
        lines.append("")

        app_grouped = group_by_type(application_commits)

        # Format breaking changes first if present
        if "breaking" in app_grouped:
            lines.append(format_breaking_changes(app_grouped["breaking"], repo_url))
            lines.append("")
            del app_grouped["breaking"]

        # Format other sections in order
        section_order = ["feat", "fix", "docs", "refactor", "perf", "test", "chore", "ci", "build", "style", "revert", "other"]
        for commit_type in section_order:
            if commit_type in app_grouped:
                lines.append(format_section_header(commit_type))
                lines.append("")
                for commit in app_grouped[commit_type]:
                    lines.append(format_commit_entry(commit, repo_url))
                lines.append("")
    else:
        lines.append("### 📦 Application")
        lines.append("")
        lines.append("No application changes.")
        lines.append("")

    # Format Other section
    if other_commits:
        lines.append("### 🔧 Other")
        lines.append("")

        other_grouped = group_by_type(other_commits)

        section_order = ["feat", "fix", "docs", "refactor", "perf", "test", "chore", "ci", "build", "style", "revert", "other"]
        for commit_type in section_order:
            if commit_type in other_grouped:
                lines.append(format_section_header(commit_type))
                lines.append("")
                for commit in other_grouped[commit_type]:
                    lines.append(format_commit_entry(commit, repo_url))
                lines.append("")

    # Add installation section
    if installation_section:
        lines.append(add_installation_section(current_tag, repo_url))
        lines.append("")

    # Add statistics
    lines.append("## 📊 Statistics")
    lines.append("")
    lines.append(f"- **Total Commits**: {len(commits)}")
    lines.append(f"- **Application Commits**: {len(application_commits)}")
    lines.append(f"- **Other Commits**: {len(other_commits)}")

    # Count unique contributors
    contributors = set()
    for commit in commits:
        if hasattr(commit, "commit") and hasattr(commit.commit, "author"):
            if commit.commit.author:
                author_name = commit.commit.author.name or commit.commit.author.login
                if author_name:
                    contributors.add(author_name)
    lines.append(f"- **Contributors**: {len(contributors)}")

    if previous_tag:
        lines.append(f"- **Changes Since**: {previous_tag}")
    else:
        lines.append("- **Changes Since**: First release")

    lines.append("")

    # Add full changelog link
    if previous_tag:
        lines.append("---")
        lines.append("")
        lines.append(f"**Full Changelog**: [`{previous_tag}...{current_tag}`]({repo_url}/compare/{previous_tag}...{current_tag})")
    else:
        lines.append("---")
        lines.append("")
        lines.append(f"**Full Changelog**: See all commits in this release")

    return "\n".join(lines)
