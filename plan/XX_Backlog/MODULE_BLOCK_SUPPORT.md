# Module Block Support

## Purpose
Extend the application to include moved blocks for module blocks in addition to the existing support for resource and data blocks.

## Current State
The application currently supports:
- Resource blocks (`resource "type" "name" { ... }`)
- Data blocks (`data "type" "name" { ... }`)

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
- Module blocks have similar structure to resource/data blocks:
  ```hcl
  module "example" {
    source = "./modules/example"

    variable1 = "value1"
    variable2 = "value2"
  }
  ```

### Processor Changes
- Add module block handling to block processor
- Module blocks may have different attributes than resources/data
- Need to handle module-specific attributes (source, version, etc.)

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
After moving the module block, it should be included in the moved blocks output similar to how resource and data blocks are handled.

## Pros
- Completes support for all major Terraform block types
- Enables refactoring of module-based Terraform code
- Consistent behavior across block types
- More comprehensive tool for Terraform code management

## Cons
- Additional complexity in parser and processor
- Module blocks may have different semantics than resources/data
- Need to handle module-specific attributes
- May require additional testing for edge cases

## Recommendation
Implement module block support to make the tool more comprehensive. Start with basic module block detection and processing, then extend to handle module-specific attributes and edge cases.

## Related Features
- Resource block support (existing)
- Data block support (existing)
- Block exclusion feature (see RESOURCE_EXCLUSION.md)

## References
- [Terraform Module Blocks Documentation](https://developer.hashicorp.com/terraform/language/modules/syntax)
