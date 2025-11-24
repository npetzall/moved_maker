# Module Block Support

## Purpose
Extend the application to include moved blocks for module blocks in addition to the existing support for resource blocks.

## Current State
The application currently supports:
- Resource blocks (`resource "type" "name" { ... }`)

Note: Data blocks are not supported (and should not be moved) because they are lookup blocks that don't maintain state and will be re-evaluated when needed.

## Proposed Feature
Add support for module blocks:
- Module blocks (`module "name" { ... }`)

## Use Cases
- Refactoring Terraform code that uses modules
- Moving modules between files or directories
- Reorganizing module structure
- Updating module references

## Implementation Considerations

### Parser Changes
- Extend HCL parser to recognize module blocks
- Module blocks have similar structure to resource blocks:
  ```hcl
  module "example" {
    source = "./modules/example"

    variable1 = "value1"
    variable2 = "value2"
  }
  ```

### Processor Changes
- Add module block handling to block processor
- Only module addresses are used in the `moved` block output (similar to resource blocks)
- Module-specific attributes (source, version, variables, etc.) are not included in the output

### Output Changes
- Include module blocks in moved block output
- Format module blocks appropriately in output

### Testing
- Add test fixtures with module blocks
- Test module block detection and processing
- Test module block output formatting
- Test edge cases (nested modules, module calls, etc.)

## Example

### Input
```hcl
# main.tf
module "web_server" {
  source = "./modules/web"

  instance_count = 3
  instance_type  = "t3.medium"
}
```

### Expected Output
When moving the module block to a module named "a", the output would be:

```hcl
moved {
  from = module.web_server
  to   = module.a.module.web_server
}
```

Note: Only the module addresses are used in the `moved` block; other module attributes (source, version, variables, etc.) are not included in the output.

## Pros
- Completes support for all major Terraform block types
- Enables refactoring of module-based Terraform code
- Consistent behavior across block types
- More comprehensive tool for Terraform code management

## Cons
- Additional complexity in parser and processor
- Module blocks may have different semantics than resources
- Need to handle module-specific attributes
- May require additional testing for edge cases

## Recommendation
Implement module block support to make the tool more comprehensive. Start with basic module block detection and processing, then extend to handle module-specific attributes and edge cases.

## Implementation

This plan has been combined with the streaming refactor into a single implementation plan following OOP and TDD principles:

- **Implementation Plan**: `work/25W47/STREAMING_REFACTOR_AND_MODULE_SUPPORT.md`

The combined plan integrates both module block support and the streaming refactor, with a phased TDD approach.

## Related Features
- Resource block support (existing)
- Block exclusion feature (see RESOURCE_EXCLUSION.md)
- Streaming refactor (see STREAMING_REFACTOR.md)

## References
- [Terraform Module Blocks Documentation](https://developer.hashicorp.com/terraform/language/modules/syntax)
