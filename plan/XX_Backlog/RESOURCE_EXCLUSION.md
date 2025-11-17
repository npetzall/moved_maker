# Resource and Module Block Exclusion

## Purpose
Add ability to exclude specific resource blocks or module blocks from processing, allowing users to selectively move blocks while keeping certain blocks in their original location.

## Use Cases
- Exclude critical resources that shouldn't be moved
- Keep certain modules in place during refactoring
- Selective block migration
- Preserve specific block locations for organizational reasons

## Proposed Features

### Exclusion Methods

1. **Command-line flags**
   - `--exclude-resource "aws_instance.example"`
   - `--exclude-module "web_server"`
   - `--exclude-file "critical.tf"`

2. **Configuration file**
   - `.moved_maker.toml` or similar
   - Pattern-based exclusions
   - File-level exclusions

3. **Pattern matching**
   - Support wildcards: `--exclude-resource "aws_*"`
   - Support regex patterns
   - Support multiple exclusions

## Implementation Considerations

### Parser Changes
- No changes needed - parser already identifies blocks
- Exclusion logic happens in processor

### Processor Changes
- Add exclusion filtering before processing blocks
- Support multiple exclusion criteria:
  - Block type (resource, data, module)
  - Block name/identifier
  - File path
  - Pattern matching

### CLI Changes
- Add exclusion flags to CLI arguments
- Support multiple exclusion values
- Validate exclusion patterns

### Configuration File

Example `.moved_maker.toml`:

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

# Exclude by pattern
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

## Example Usage

### Command-line

```bash
# Exclude specific resource
move_maker --exclude-resource "aws_instance.critical" input.tf

# Exclude multiple resources
move_maker \
  --exclude-resource "aws_instance.critical" \
  --exclude-resource "aws_db_instance.prod" \
  input.tf

# Exclude module
move_maker --exclude-module "legacy_module" input.tf

# Exclude by pattern
move_maker --exclude-pattern "aws_*_backup" input.tf
```

### Configuration File

```bash
# Use .moved_maker.toml for exclusions
move_maker input.tf
```

## Pros
- Flexible block selection
- Supports various exclusion patterns
- Can exclude at resource, module, or file level
- Useful for incremental refactoring
- Allows preserving critical blocks

## Cons
- Additional complexity in CLI and processor
- Need to handle exclusion conflicts
- Pattern matching may be complex
- Configuration file adds another file to manage

## Recommendation
Implement exclusion support with:
1. Command-line flags for simple use cases
2. Configuration file for complex exclusions
3. Pattern matching support (wildcards and regex)
4. Clear documentation on exclusion precedence

Start with command-line flags, then add configuration file support.

## Related Features
- Module block support (see MODULE_BLOCK_SUPPORT.md)
- Resource block processing (existing)
- Data block processing (existing)

## Implementation Priority
Medium - Useful feature but not critical for core functionality. Can be added after module block support is implemented.
