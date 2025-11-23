Added from GitHub Issue: https://github.com/npetzall/moved_maker/issues/9

When fixed it should be mentioned in git commit. Make sure implementation plan includes instructing the user to include "fixes #9" in commit message.

The current PR labeling workflow relies on bash scripts that use the gh CLI to inspect PR commits and apply version bump labels. While this works, it introduces a few problems:

- Bash parsing can be brittle and error-prone, especially with multi-line or unusual commit messages.
- The GitHub CLI (gh) relies on the runner image, which may change at any time. Even with version checks, a silent upgrade or image change could break labeling unexpectedly.

**Proposal:**
- Replace the labeling logic with a small Python project in `.github/scripts/pr-labels` using **uv** and the PyGithub package, matching the existing structure and style of other uv projects in `.github/scripts` (e.g., `release-notes` and `release-version`).
- The project should follow the same pattern as existing uv projects:
  - Use `uv` for dependency management with a `pyproject.toml` file
  - Follow the same directory structure (e.g., `src/` for source code, `tests/` for tests)
  - Include a `uv.lock` file for deterministic builds
  - **Write comprehensive tests** using pytest (configured in `pyproject.toml`)
- The new labeler should:
  - Analyze all PR commits for Conventional Commit patterns and breaking changes;
  - Remove conflicting previous version labels;
  - Ensure target labels exist (and create them if they don't);
  - Apply the correct version bump and semantic labels.
- Update `.github/dependabot.yml` to include a pip package ecosystem entry for `.github/scripts/pr-labels` (matching the pattern used for `release-version`).
- Document constraints and install/run steps for this script in the repository.

**Benefits:**
- Robust, maintainable labeling logic (parsing done in Python, not bash)
- Trackable Python environment using uv for deterministic builds
- Avoids breakage from image/tooling drift with gh in CI
- Aligns with existing best practices seen in `.github/scripts`.
