# Workflow Error Annotations

## Purpose
Add GitHub Actions annotations for all errors that can occur in workflows to make them clearly visible in the workflow run summary. Annotations provide inline error messages, warnings, and notices directly in the workflow UI.

## Features
- Inline error messages in workflow UI
- File and line number references
- Warning and notice annotations
- Clear visibility of issues in run summary
- Better developer experience for debugging

## Compatibility
- ✅ GitHub Actions: Native support via workflow commands
- ✅ All platforms: Works on any GitHub Actions runner

## Usage

### Error Annotations

```bash
# Error annotation
echo "::error file=src/main.rs,line=42,col=5::Missing semicolon"

# Warning annotation
echo "::warning file=src/parser.rs,line=10::Deprecated function usage"

# Notice annotation
echo "::notice file=tests/integration_test.rs::Test execution time: 5.2s"
```

### Format

```
::error file={name},line={line},col={col}::{message}
::warning file={name},line={line},col={col}::{message}
::notice file={name},line={line},col={col}::{message}
```

All parameters are optional except the message.

### Examples

```bash
# Simple error
echo "::error::Build failed"

# Error with file and line
echo "::error file=src/main.rs,line=10::Syntax error"

# Error with file, line, and column
echo "::error file=src/parser.rs,line=25,col=8::Unexpected token"

# Warning
echo "::warning::Code coverage below threshold"

# Notice
echo "::notice::Using cached dependencies"
```

## Integration Notes
- Annotations appear in the "Annotations" tab of workflow runs
- Can be created from any step in a workflow
- Support file, line, and column references
- Can be used for errors, warnings, and notices
- Multiple annotations can be created per workflow run

## Workflow Integration

### Build Errors

```yaml
- name: Build
  run: |
    if ! cargo build 2>&1 | tee build.log; then
      # Parse build errors and create annotations
      grep "error\[" build.log | while read line; do
        echo "::error::$line"
      done
      exit 1
    fi
```

### Test Failures

```yaml
- name: Run tests
  run: |
    cargo nextest run --workspace --test-threads 1 2>&1 | tee test.log
    if [ $? -ne 0 ]; then
      # Parse test failures and create annotations
      grep -A 5 "FAILED" test.log | while read line; do
        echo "::error::$line"
      done
      exit 1
    fi
```

### Linting Errors

```yaml
- name: Run clippy
  run: |
    cargo clippy --all-targets -- -D warnings 2>&1 | tee clippy.log
    if [ $? -ne 0 ]; then
      # Parse clippy warnings and create annotations
      while IFS= read -r line; do
        if [[ $line =~ ^(.+):([0-9]+):([0-9]+):.*warning:(.+)$ ]]; then
          file="${BASH_REMATCH[1]}"
          line_num="${BASH_REMATCH[2]}"
          col="${BASH_REMATCH[3]}"
          msg="${BASH_REMATCH[4]}"
          echo "::warning file=$file,line=$line_num,col=$col::$msg"
        fi
      done < clippy.log
      exit 1
    fi
```

### Coverage Warnings

```yaml
- name: Check coverage
  run: |
    COVERAGE=$(cargo llvm-cov --json | jq -r '.data[0].totals.lines.percent')
    THRESHOLD=80

    if (( $(echo "$COVERAGE < $THRESHOLD" | bc -l) )); then
      echo "::warning::Code coverage ($COVERAGE%) is below threshold ($THRESHOLD%)"
    fi
```

### Formatting Errors

```yaml
- name: Check formatting
  run: |
    if ! cargo fmt --check; then
      echo "::error::Code formatting check failed. Run 'cargo fmt' to fix."
      exit 1
    fi
```

### Security Scan Results

```yaml
- name: Security scan
  run: |
    cargo audit --json > audit.json
    if [ $? -ne 0 ]; then
      # Parse vulnerabilities and create annotations
      jq -r '.vulnerabilities[] | "::error::Vulnerability: \(.advisory.id) - \(.advisory.title)"' audit.json
      exit 1
    fi
```

## Pros
- Clear visibility of errors in workflow UI
- File and line number references for quick navigation
- Better developer experience
- Native GitHub Actions feature, no additional dependencies
- Supports errors, warnings, and notices
- Annotations appear in dedicated tab in workflow run

## Cons
- Requires parsing tool output to extract error details
- May need custom scripts for complex error formats
- Can generate many annotations for large codebases
- Need to handle different error formats from different tools

## Recommendation
Add annotations for all major workflow steps:
- Build errors (cargo build)
- Test failures (cargo nextest)
- Linting issues (clippy, rustfmt)
- Coverage warnings
- Security vulnerabilities (cargo audit)
- Dependency issues (cargo tree, cargo outdated)

Use appropriate annotation types:
- `::error::` for failures that block the workflow
- `::warning::` for issues that should be addressed but don't block
- `::notice::` for informational messages

## Implementation Considerations

### Error Parsing
- Different tools output errors in different formats
- May need custom parsers for each tool
- Consider using existing tools that output GitHub Actions format
- Some tools (like clippy) can output in machine-readable formats

### Annotation Limits
- GitHub Actions may have limits on number of annotations
- Consider batching or summarizing for large outputs
- Focus on actionable errors rather than all warnings

### Tool-Specific Integration
- **cargo clippy**: Can use `--message-format=json` for structured output
- **cargo test**: Parse test output or use nextest JSON format
- **cargo fmt**: Simple pass/fail, add annotation on failure
- **cargo audit**: Parse JSON output for vulnerabilities

## References
- [GitHub Actions: Workflow Commands](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions)
- [GitHub Actions: Setting an error message](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-error-message)
