# BUG: cargo-geiger output format syntax incorrect in workflows and documentation

**Status**: ✅ Complete

## Description

`cargo-geiger` is configured with incorrect syntax for the `--output-format` option in CI workflows and documentation. The current syntax uses `--output-format json` (lowercase), but the correct syntax should be `--output-format Json` (capital J). This may cause the tool to fail or not produce the expected JSON output format.

## Current State

✅ **FIXED** - `cargo-geiger` has been updated to use the correct syntax `--output-format Json` (capital J) in:
- `.github/workflows/pull_request.yaml` (line 34) ✅
- `.github/workflows/release-build.yaml` (line 38) ✅
- Documentation files (TOOLING.md, plan/25W46/REQ_SECURITY.md, work/25W46/*.md, plan/25W46/*.md) ✅

**Current (incorrect) syntax:**
```yaml
- name: Run cargo-geiger scan
  run: cargo geiger --output-format json > geiger-report.json || [ $? -eq 1 ]
```

**Documentation examples (incorrect):**
```bash
cargo geiger --output-format json > geiger-report.json
```

## Expected State

`cargo-geiger` should use the correct syntax `--output-format Json` (capital J) in:
1. **Workflow files**: Both `.github/workflows/pull_request.yaml` and `.github/workflows/release-build.yaml`
2. **Documentation files**: All documentation that references the geiger output format option

**Expected (correct) syntax:**
```yaml
- name: Run cargo-geiger scan
  run: cargo geiger --output-format Json > geiger-report.json || [ $? -eq 1 ]
```

**Documentation examples (correct):**
```bash
cargo geiger --output-format Json > geiger-report.json
```

## Impact

### Functionality Impact
- **Severity**: Medium
- **Priority**: Medium

Current issues:
- `cargo-geiger` may fail to recognize the output format option with lowercase `json`
- JSON output may not be generated correctly, causing downstream processing issues
- Documentation is incorrect and may mislead developers
- Inconsistent syntax across codebase and documentation

### Potential Consequences
- Geiger reports may not be generated in JSON format
- Artifact uploads may fail if JSON format is not produced
- Developers following documentation will use incorrect syntax
- CI workflows may fail silently or produce unexpected output


## Related Implementation Plan

See `work/25W46/BUG_WORKFLOWS_GEIGER_OUTPUT_FORMAT_SYNTAX.md` for the detailed implementation plan.
