# REQ: Exclude Resources and Modules from Moved Blocks

**Status**: 📋 Planned

## Overview
Add ability to exclude specific resource blocks or module blocks from processing, allowing users to selectively move blocks while keeping certain blocks in their original location.

## Motivation
During Terraform refactoring, users may need to preserve certain resources or modules in their original locations for various reasons:
- Critical resources that shouldn't be moved (e.g., production databases, stateful resources)
- Legacy modules that need to remain in place
- Incremental refactoring where only specific blocks should be moved
- Organizational constraints requiring certain blocks to stay in specific files

Currently, the tool processes all resources and modules it finds, generating moved blocks for everything. This feature would provide fine-grained control over which blocks are included in the refactoring.

## Current Behavior
The application processes all resource blocks and module blocks found in the input Terraform files and generates moved blocks for all of them. There is no mechanism to exclude specific blocks from processing.

## Proposed Behavior
Add exclusion capabilities that allow users to specify which resources or modules should be excluded from moved block generation. Exclusions can be specified via:
1. Command-line flags for simple use cases
2. Configuration file (`.moved_maker.toml`) for complex exclusions
3. Pattern matching support (wildcards and regex) for flexible exclusion rules

Excluded blocks will be completely skipped during processing and will not appear in the output moved blocks.

## Use Cases
- Exclude critical resources that shouldn't be moved (e.g., `aws_db_instance.production`)
- Keep certain modules in place during refactoring (e.g., `legacy_module`)
- Selective block migration for incremental refactoring
- Preserve specific block locations for organizational reasons
- Exclude entire files from processing (e.g., `critical.tf`)
- Pattern-based exclusions (e.g., exclude all backup resources: `aws_*_backup`)

## Implementation Considerations

### Parser Changes
- No changes needed - parser already identifies blocks
- Exclusion logic happens in processor layer

### Processor Changes
- Add exclusion filtering before processing blocks
- Support multiple exclusion criteria:
  - Block type (resource, data, module)
  - Block name/identifier (e.g., `aws_instance.example`)
  - File path (e.g., `critical.tf`, `legacy/*.tf`)
  - Pattern matching (wildcards and regex)
- Filter blocks based on exclusion rules before generating moved blocks

### CLI Changes
- Add exclusion flags to CLI arguments:
  - `--exclude-resource "aws_instance.example"` (can be specified multiple times)
  - `--exclude-module "web_server"` (can be specified multiple times)
  - `--exclude-file "critical.tf"` (can be specified multiple times)
  - `--exclude-pattern "aws_*_backup"` (can be specified multiple times)
- Support multiple exclusion values per flag
- Validate exclusion patterns
- Provide clear error messages for invalid patterns

### Configuration File Support
Add support for `.moved_maker.toml` configuration file:

```toml
[exclusions]
# Exclude specific resources
exclude-resources = [
    "aws_instance.critical",
    "aws_db_instance.production",
]

# Exclude specific modules
exclude-modules = [
    "legacy_module",
    "shared_infrastructure",
]

# Exclude by pattern (wildcards)
exclude-patterns = [
    "aws_*_backup",
    "module.*_legacy",
]

# Exclude entire files
exclude-files = [
    "critical.tf",
    "legacy/*.tf",
]
```

### Pattern Matching
- Support wildcard patterns (e.g., `aws_*_backup`)
- Support regex patterns for advanced matching
- Pattern matching applies to block identifiers (resource type + name, module name)
- Clear precedence rules when multiple exclusion methods are used

## Alternatives Considered
- **Include-only approach**: Instead of excluding, allow users to specify which blocks to include. Rejected because exclusion is more intuitive for "preserve these blocks" use cases.
- **Terraform comments**: Use special comments in Terraform files to mark exclusions. Rejected because it requires modifying source files and is less flexible.
- **Separate exclusion file**: Use a dedicated exclusion file instead of configuration file. Rejected because configuration file approach is more maintainable and follows common tool patterns.

## Impact
- **Breaking Changes**: No - this is a new feature that doesn't change existing behavior
- **Documentation**:
  - Update README with exclusion examples
  - Document configuration file format
  - Add examples for common exclusion patterns
- **Testing**:
  - Unit tests for exclusion filtering logic
  - Integration tests with various exclusion patterns
  - Test exclusion precedence and conflicts
  - Test pattern matching (wildcards and regex)
- **Dependencies**:
  - May need a TOML parsing library (e.g., `toml` crate) for configuration file support
  - May need regex library if not already present (e.g., `regex` crate)

## Example Usage

### Command-line

```bash
# Exclude specific resource
moved_maker --exclude-resource "aws_instance.critical" input.tf

# Exclude multiple resources
moved_maker \
  --exclude-resource "aws_instance.critical" \
  --exclude-resource "aws_db_instance.prod" \
  input.tf

# Exclude module
moved_maker --exclude-module "legacy_module" input.tf

# Exclude by pattern
moved_maker --exclude-pattern "aws_*_backup" input.tf

# Combine multiple exclusion types
moved_maker \
  --exclude-resource "aws_instance.critical" \
  --exclude-module "legacy_module" \
  --exclude-file "critical.tf" \
  input.tf
```

### Configuration File

```bash
# Use .moved_maker.toml for exclusions
moved_maker input.tf
```

## References
- Related features:
  - Module block support (see `plan/25W47/REQ_MODULE_BLOCK_SUPPORT.md`)
  - Resource block processing (existing)
  - Data block processing (existing)
- Implementation priority: Medium - Useful feature but not critical for core functionality. Can be added after module block support is implemented.
