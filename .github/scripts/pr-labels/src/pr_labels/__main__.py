#!/usr/bin/env python3
"""
PR labeler using PyGithub. Entrypoint: python -m pr_labels
"""
import os
import sys
import argparse
import logging
from typing import List
from github import Github, GithubException
import re

VERSION_LABELS = {
    "major": "version: major",
    "minor": "version: minor",
    "patch": "version: patch",
}
ALT_LABELS = {
    "major": "breaking",
    "minor": "feature",
    "patch": None,
}
LABEL_META = {
    "version: major": {"color": "b60205", "description": "Indicates a breaking (major) change"},
    "version: minor": {"color": "0e8a16", "description": "Indicates a new feature (minor)"},
    "version: patch": {"color": "c2e0c6", "description": "Indicates a bug fix / patch"},
    "breaking": {"color": "5319e7", "description": "Breaking change"},
    "feature": {"color": "0366d6", "description": "New feature"},
}

logger = logging.getLogger("pr_labels")


def parse_args():
    p = argparse.ArgumentParser(description="Label PRs with semantic version labels based on commit messages")
    p.add_argument("pr", nargs="?", help="PR number (or provide via PR_NUM env)")
    p.add_argument("--dry-run", action="store_true", help="Do not modify GitHub, just log actions")
    return p.parse_args()


def determine_bump_from_commits(messages: List[str], pr_title: str = "", pr_body: str = "") -> str:
    """Return 'major' | 'minor' | 'patch'"""
    best = "patch"
    for message in messages:
        if not message:
            continue
        lines = message.splitlines()
        header = lines[0] if lines else ""
        body = "\n".join(lines[1:]) if len(lines) > 1 else ""
        # Major: explicit BREAKING CHANGE in body or '!' in header per Conventional Commits
        if "breaking change" in body.lower():
            return "major"
        # Match feat!: or feat(scope)!: patterns
        if re.search(r"^[a-zA-Z]+(\([^)]+\))?!:", header):
            return "major"
        # Minor: feat:
        if header.lower().startswith("feat:") or header.lower().startswith("feat("):
            best = "minor" if best != "major" else best
            continue
        # Patch: fix:
        if header.lower().startswith("fix:") or header.lower().startswith("fix("):
            if best not in ("major", "minor"):
                best = "patch"
    # Supplemental signals from PR title/body
    if best != "major":
        if "BREAKING CHANGE" in pr_title or "BREAKING CHANGE" in pr_body:
            return "major"
        # Check for Conventional Commits breaking change indicator in title
        if re.search(r"^[a-zA-Z]+(\([^)]+\))?!:", pr_title):
            return "major"
    return best


def ensure_label(repo, label_name: str, dry_run: bool = False):
    try:
        repo.get_label(label_name)
        logger.debug("Label exists: %s", label_name)
    except GithubException as e:
        if e.status == 404:
            meta = LABEL_META.get(label_name, {"color": "ffffff", "description": ""})
            logger.info("Creating label %s", label_name)
            if not dry_run:
                repo.create_label(name=label_name, color=meta["color"], description=meta["description"])
        else:
            raise


def remove_labels_from_issue(issue, labels: List[str], dry_run: bool = False):
    for lab in labels:
        if lab in [l.name for l in issue.get_labels()]:
            logger.info("Removing label %s from PR #%s", lab, issue.number)
            if not dry_run:
                issue.remove_from_labels(lab)


def add_labels_to_issue(issue, labels: List[str], dry_run: bool = False):
    if not labels:
        return
    current = [l.name for l in issue.get_labels()]
    to_add = [l for l in labels if l not in current]
    if not to_add:
        logger.info("No new labels to add")
        return
    logger.info("Adding labels %s to PR #%s", to_add, issue.number)
    if not dry_run:
        issue.add_to_labels(*to_add)


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        logger.error("GITHUB_TOKEN must be set in environment")
        sys.exit(1)
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    if not repo_name:
        logger.error("GITHUB_REPOSITORY must be set in environment")
        sys.exit(1)

    pr_num = args.pr or os.environ.get("PR_NUM") or os.environ.get("PR_NUMBER")
    if not pr_num:
        logger.error("PR number must be provided as arg or PR_NUM/PR_NUMBER env")
        sys.exit(1)
    try:
        pr_number = int(pr_num)
    except ValueError:
        logger.error("Invalid PR number: %s", pr_num)
        sys.exit(1)

    gh = Github(token)
    repo = gh.get_repo(repo_name)
    pull = repo.get_pull(pr_number)
    issue = pull.get_issue()

    # Collect commit messages
    commits = pull.get_commits()
    messages = []
    for c in commits:
        cm = c.commit.message
        messages.append(cm)
    logger.info("Fetched %d commits for PR #%d", len(messages), pr_number)

    bump = determine_bump_from_commits(messages, pr_title=pull.title or "", pr_body=pull.body or "")
    logger.info("Determined bump: %s", bump)

    desired = [VERSION_LABELS[bump]]
    alt = ALT_LABELS.get(bump)
    if alt:
        desired.append(alt)

    # Remove existing version/alt labels
    existing = [l.name for l in issue.get_labels()]
    remove_cands = list(VERSION_LABELS.values()) + [v for v in ALT_LABELS.values() if v]
    for lab in remove_cands:
        if lab in existing and lab not in desired:
            logger.info("Removing label %s", lab)
            if not args.dry_run:
                issue.remove_from_labels(lab)

    # Ensure desired labels exist
    for lab in desired:
        ensure_label(repo, lab, dry_run=args.dry_run)

    # Add labels
    add_labels_to_issue(issue, desired, dry_run=args.dry_run)

    logger.info("Done")


if __name__ == "__main__":
    main()
